import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Firebase with environment variables or service account file
def initialize_firebase():
    try:
        # Try to use environment variables first
        if all(os.getenv(key) for key in ['FIREBASE_PROJECT_ID', 'FIREBASE_PRIVATE_KEY', 'FIREBASE_CLIENT_EMAIL']):
            # Create credentials from environment variables
            firebase_config = {
                "type": "service_account",
                "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('FIREBASE_CLIENT_EMAIL').replace('@', '%40')}"
            }
            cred = credentials.Certificate(firebase_config)
            firebase_admin.initialize_app(cred)
            print("Connected to Firebase using environment variables!")
            return firestore.client()
        else:
            # Fallback to service account file
            if os.path.exists("serviceAccountKey.json"):
                with open("serviceAccountKey.json", 'r') as f:
                    service_account_data = json.load(f)
                    # Check if it's a dummy file
                    if service_account_data.get('project_id') == 'dummy-project':
                        raise Exception("Using dummy service account file")
                
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred)
                print("Connected to Firebase using service account file!")
                return firestore.client()
            else:
                raise Exception("No Firebase configuration found")
    except Exception as e:
        print(f"Firebase connection failed: {e}")
        print("Running in mock mode - no Firebase connection")
        return None

# Initialize Firebase
db = initialize_firebase()

@app.route('/')
def index():
    return "Flask app is running and connected to Firebase!" if db else "Flask app running in mock mode!"

# Clerk webhook to sync user data
@app.route('/webhooks/clerk', methods=['POST'])
def clerk_webhook():
    data = request.json
    event_type = data.get('type')
    user_data = data.get('data')
    
    if event_type == 'user.created':
        # Store user data in Firebase when a new user signs up via Clerk
        if db:
            users_ref = db.collection('users')
            doc_ref = users_ref.document(user_data['id'])
            doc_ref.set({
                'clerk_id': user_data['id'],
                'email': user_data['email_addresses'][0]['email_address'] if user_data['email_addresses'] else '',
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'created_at': firestore.SERVER_TIMESTAMP,
                'role': 'student'  # Default role, can be updated
            })
    
    return jsonify({"success": True}), 200

# Get user profile by Clerk ID
@app.route('/users/<clerk_id>', methods=['GET'])
def get_user_by_clerk_id(clerk_id):
    if not db:
        return jsonify({
            "clerk_id": clerk_id,
            "email": "mock@example.com",
            "first_name": "Mock",
            "last_name": "User",
            "role": "teacher"
        }), 200
    
    try:
        users_ref = db.collection('users')
        docs = users_ref.where('clerk_id', '==', clerk_id).stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            return jsonify(user_data), 200
        
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update user role (teacher/student)
@app.route('/users/<clerk_id>/role', methods=['PUT'])
def update_user_role(clerk_id):
    data = request.json
    new_role = data.get('role')
    
    if new_role not in ['student', 'teacher']:
        return jsonify({"error": "Invalid role. Must be 'student' or 'teacher'"}), 400
    
    if not db:
        return jsonify({"success": True, "message": f"Role updated to {new_role} (mock mode)"}), 200
    
    try:
        users_ref = db.collection('users')
        docs = users_ref.where('clerk_id', '==', clerk_id).stream()
        
        for doc in docs:
            doc.reference.update({'role': new_role})
            return jsonify({"success": True, "message": f"Role updated to {new_role}"}), 200
        
        return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Teacher Dashboard - Get teacher's classes and data
@app.route('/dashboard/teacher/<clerk_id>', methods=['GET'])
def teacher_dashboard(clerk_id):
    if not db:
        # Mock data for development
        return jsonify({
            "success": True,
            "profile": {
                "name": "Dr. Mock Teacher",
                "email": "teacher@mock.com",
                "employee_id": "T001"
            },
            "my_classes": [
                {
                    "classroom_id": "CS101_A_101",
                    "subject": "Computer Science",
                    "college_name": "Mock College",
                    "total_students": 45,
                    "average_attendance": 85.5,
                    "is_active": True
                }
            ]
        }), 200
    
    try:
        # Get teacher profile
        users_ref = db.collection('users')
        teacher_docs = users_ref.where('clerk_id', '==', clerk_id).where('role', '==', 'teacher').stream()
        
        teacher_profile = None
        for doc in teacher_docs:
            teacher_profile = doc.to_dict()
            break
        
        if not teacher_profile:
            return jsonify({"error": "Teacher profile not found"}), 404
        
        # Get teacher's classes
        classes_ref = db.collection('classrooms').where('teacher_clerk_id', '==', clerk_id)
        classes_docs = classes_ref.stream()
        
        my_classes = []
        for doc in classes_docs:
            class_data = doc.to_dict()
            class_data['classroom_id'] = doc.id
            my_classes.append(class_data)
        
        return jsonify({
            "success": True,
            "profile": teacher_profile,
            "my_classes": my_classes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Create class (updated for Clerk)
@app.route('/create_class', methods=['POST'])
def create_class():
    data = request.json
    classroom_id = data.get('classroom_id')
    teacher_clerk_id = data.get('teacher_clerk_id')  # Use Clerk ID instead of teacher code
    college_name = data.get('college_name')
    subject = data.get('subject', '')
    max_students = data.get('max_students', 60)
    
    if not all([classroom_id, teacher_clerk_id, college_name]):
        return jsonify({"error": "Classroom ID, teacher Clerk ID, and college name are required."}), 400

    if not db:
        return jsonify({
            "success": True, 
            "message": "Class created successfully! (mock mode)",
            "classroom_id": classroom_id
        }), 201

    try:
        # Check if teacher exists
        users_ref = db.collection('users')
        teacher_docs = users_ref.where('clerk_id', '==', teacher_clerk_id).where('role', '==', 'teacher').stream()
        
        teacher_exists = False
        for doc in teacher_docs:
            teacher_exists = True
            break
        
        if not teacher_exists:
            return jsonify({"error": "Invalid teacher Clerk ID or user is not a teacher."}), 401

        # Check if classroom already exists
        existing_class = db.collection('classrooms').document(classroom_id).get()
        if existing_class.exists:
            return jsonify({"error": "Classroom ID already exists."}), 409

        # Save the new class to the database
        classroom_ref = db.collection('classrooms').document(classroom_id)
        classroom_ref.set({
            "teacher_clerk_id": teacher_clerk_id,
            "college_name": college_name,
            "subject": subject,
            "max_students": max_students,
            "current_students": 0,
            "students": [],
            "is_active": True,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_updated": firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({"success": True, "message": "Class created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Student Dashboard
@app.route('/dashboard/student/<clerk_id>', methods=['GET'])
def student_dashboard(clerk_id):
    if not db:
        return jsonify({
            "success": True,
            "profile": {
                "name": "Mock Student",
                "email": "student@mock.com",
                "usn": "1AB20CS001"
            },
            "enrolled_classes": [],
            "attendance_summary": {
                "total_classes": 45,
                "attended": 38,
                "percentage": 84.4
            }
        }), 200
    
    try:
        # Get student profile
        users_ref = db.collection('users')
        student_docs = users_ref.where('clerk_id', '==', clerk_id).stream()
        
        student_profile = None
        for doc in student_docs:
            student_profile = doc.to_dict()
            break
        
        if not student_profile:
            return jsonify({"error": "Student profile not found"}), 404
        
        return jsonify({
            "success": True,
            "profile": student_profile,
            "enrolled_classes": [],  # Can be expanded
            "attendance_summary": {
                "total_classes": 0,
                "attended": 0,
                "percentage": 0
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# All the existing endpoints remain the same...
@app.route('/users', methods=['POST'])
def create_user():
    user_data = request.json
    if db:
        users_ref = db.collection('users')
        doc_ref = users_ref.document()
        doc_ref.set(user_data)
        return jsonify({"id": doc_ref.id}), 201
    else:
        return jsonify({"id": "mock_id", "message": "User created (mock mode)"}), 201

@app.route('/users', methods=['GET'])
def get_users():
    if db:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        all_users = [doc.to_dict() for doc in docs]
        return jsonify(all_users), 200
    else:
        return jsonify([{"id": "mock_id", "name": "Mock User"}]), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)