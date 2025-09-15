import os
import random
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Mock database for testing
mock_db = {
    'teachers': {},
    'students': {},
    'classrooms': {},
    'attendance': {},
    'materials': {},
    'quizzes': {}
}

@app.route('/')
def index():
    return "Flask app is running (Mock Mode - No Firebase)!"

@app.route('/signup/faculty', methods=['POST'])
def faculty_signup():
    try:
        data = request.json
        teacher_code = data.get('teacher_code')
        name = data.get('name')
        email = data.get('email')
        
        if not all([teacher_code, name, email]):
            return jsonify({"error": "Teacher code, name, and email are required for signup."}), 400

        if teacher_code in mock_db['teachers']:
            return jsonify({"error": "Faculty with this teacher code already exists."}), 409

        mock_db['teachers'][teacher_code] = {
            "name": name,
            "email": email,
            "teacher_code": teacher_code,
            "created_at": "2025-09-14T00:00:00Z"
        }
        
        return jsonify({"success": True, "message": "Faculty profile created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login/faculty', methods=['POST'])
def faculty_login():
    try:
        data = request.json
        teacher_code = data.get('teacher_code')
        college_name = data.get('college_name')

        if not all([teacher_code, college_name]):
            return jsonify({"error": "Teacher code and college name are required."}), 400

        # For demo, accept any teacher code
        if teacher_code not in mock_db['teachers']:
            # Auto-create teacher for demo
            mock_db['teachers'][teacher_code] = {
                "name": f"Teacher {teacher_code}",
                "email": f"{teacher_code}@college.edu",
                "teacher_code": teacher_code,
                "created_at": "2025-09-14T00:00:00Z"
            }

        # Generate a classroom ID
        classroom_id = f"{college_name.replace(' ', '_')}_{teacher_code}"
        
        return jsonify({
            "success": True, 
            "message": "Faculty logged in successfully!",
            "classroom_id": classroom_id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/faculty/profile/<teacher_code>', methods=['GET'])
def get_faculty_profile(teacher_code):
    try:
        if teacher_code not in mock_db['teachers']:
            return jsonify({"error": "Faculty profile not found."}), 404
        
        return jsonify(mock_db['teachers'][teacher_code]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard/faculty/<teacher_code>', methods=['GET'])
def faculty_dashboard(teacher_code):
    try:
        if teacher_code not in mock_db['teachers']:
            return jsonify({"error": "Faculty profile not found."}), 404
        
        # Get classes for this teacher
        teacher_classes = []
        for classroom_id, classroom_data in mock_db['classrooms'].items():
            if classroom_data.get('teacher_code') == teacher_code:
                classroom_data['classroom_id'] = classroom_id
                teacher_classes.append(classroom_data)
        
        return jsonify({
            "success": True,
            "message": "Faculty dashboard data retrieved.",
            "profile": mock_db['teachers'][teacher_code],
            "my_classes": teacher_classes
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create_class', methods=['POST'])
def create_class():
    try:
        data = request.json
        classroom_id = data.get('classroom_id')
        teacher_code = data.get('teacher_code')
        college_name = data.get('college_name')
        subject = data.get('subject', '')
        max_students = data.get('max_students', 60)
        
        if not all([classroom_id, teacher_code, college_name]):
            return jsonify({"error": "Classroom ID, teacher code, and college name are required."}), 400

        # Check if classroom already exists
        if classroom_id in mock_db['classrooms']:
            return jsonify({"error": "Classroom ID already exists."}), 409

        # Save the new class
        mock_db['classrooms'][classroom_id] = {
            "teacher_code": teacher_code,
            "college_name": college_name,
            "subject": subject,
            "max_students": max_students,
            "current_students": 0,
            "students": [],
            "is_active": True,
            "created_at": "2025-09-14T00:00:00Z"
        }
        
        return jsonify({"success": True, "message": "Class created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/my_classes/<teacher_code>', methods=['GET'])
def get_my_classes(teacher_code):
    try:
        teacher_classes = []
        for classroom_id, classroom_data in mock_db['classrooms'].items():
            if classroom_data.get('teacher_code') == teacher_code:
                class_data = classroom_data.copy()
                class_data['classroom_id'] = classroom_id
                teacher_classes.append(class_data)
        
        return jsonify(teacher_classes), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/class_details/<classroom_id>', methods=['GET'])
def get_class_details(classroom_id):
    try:
        if classroom_id not in mock_db['classrooms']:
            return jsonify({"error": "Classroom not found."}), 404

        class_details = mock_db['classrooms'][classroom_id].copy()
        class_details['classroom_id'] = classroom_id

        return jsonify({
            "success": True,
            "class_details": class_details,
            "enrolled_students": [],
            "recent_materials": []
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Additional endpoints for completeness
@app.route('/signup/student', methods=['POST'])
def student_signup():
    try:
        data = request.json
        usn = data.get('usn')
        name = data.get('name')
        email = data.get('email')
        
        if not all([usn, name, email]):
            return jsonify({"error": "USN, name, and email are required for signup."}), 400

        if usn in mock_db['students']:
            return jsonify({"error": "Student with this USN already exists."}), 409

        mock_db['students'][usn] = {
            "name": name,
            "email": email,
            "usn": usn,
            "created_at": "2025-09-14T00:00:00Z"
        }
        
        return jsonify({"success": True, "message": "Student profile created successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/login/student', methods=['POST'])
def student_login():
    try:
        data = request.json
        student_usn = data.get('usn')
        classroom_id = data.get('classroom_id')
        
        if not all([student_usn, classroom_id]):
            return jsonify({"error": "USN and Classroom ID are required."}), 400

        # For demo, auto-create student if doesn't exist
        if student_usn not in mock_db['students']:
            mock_db['students'][student_usn] = {
                "name": f"Student {student_usn}",
                "email": f"{student_usn}@student.edu",
                "usn": student_usn,
                "created_at": "2025-09-14T00:00:00Z"
            }
            
        if classroom_id not in mock_db['classrooms']:
            return jsonify({"error": "Classroom not found or is not active."}), 404
        
        return jsonify({"success": True, "message": "Student logged in successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server in Mock Mode (No Firebase)")
    app.run(debug=True, host='0.0.0.0', port=5000)