from flask import Flask, request, jsonify
import cv2
import numpy as np
import pickle
import os
import datetime
import json
from pymongo import MongoClient

app = Flask(__name__)

# --- Load OpenCV Face Recognition Model ---
print("[INFO] Loading OpenCV face recognition model...")
try:
    # Initialize face detector and recognizer
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Load trained model
    face_recognizer.read("opencv_face_model.yml")
    
    # Load face ID to name mapping
    with open("face_names.pickle", "rb") as f:
        face_id_to_name = pickle.load(f)
    
    print(f"[INFO] Model loaded successfully with {len(face_id_to_name)} students:")
    for name in face_id_to_name.values():
        print(f"   - {name}")
        
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    face_cascade = None
    face_recognizer = None
    face_id_to_name = {}

# --- MongoDB Setup ---
def setup_mongodb():
    try:
        with open("mongodb_config.json", "r") as f:
            config = json.load(f)
            uri = config.get("connection_string", "mongodb://localhost:27017")
            db_name = config.get("database_name", "smartclass_attendance")
        
        client = MongoClient(uri, serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client[db_name]
        collection = db["attendance_records"]
        print("[INFO] MongoDB connected successfully")
        return client, db, collection
    except Exception as e:
        print(f"[WARNING] MongoDB not available: {e}")
        return None, None, None

mongo_client, mongo_db, mongo_collection = setup_mongodb()

# --- API Endpoint to Take Attendance ---
@app.route('/take-attendance', methods=['POST'])
def take_attendance():
    # Check if model is loaded
    if face_cascade is None or face_recognizer is None:
        return jsonify({'error': 'Face recognition model not loaded'}), 500
    
    # Check if an image was sent
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    
    # Read the image file
    img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- Run Face Recognition ---
    faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(80, 80))
    
    present_students = set()
    confidence_threshold = 100
    
    for (x, y, w, h) in faces:
        # Extract face region
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))
        
        # Predict
        label, confidence = face_recognizer.predict(face_roi)
        
        # Check if recognized (confidence below threshold means good match)
        if confidence < confidence_threshold and label in face_id_to_name:
            name = face_id_to_name[label]
            present_students.add(name)

    # --- Determine Present and Absent Students ---
    all_students = set(face_id_to_name.values())
    absent_students = list(all_students - present_students)
    present_students = list(present_students)
    
    # --- Save Attendance to Database ---
    if present_students and mongo_collection is not None:
        try:
            now = datetime.datetime.now()
            for student in present_students:
                attendance_record = {
                    "name": student,
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "status": "Present",
                    "timestamp": now,
                    "method": "API"
                }
                mongo_collection.insert_one(attendance_record)
        except Exception as e:
            print(f"[WARNING] Failed to save to MongoDB: {e}")
    
    # Return the results as JSON
    return jsonify({
        'success': True,
        'present': sorted(present_students),
        'absent': sorted(absent_students),
        'total_students': len(all_students),
        'timestamp': datetime.datetime.now().isoformat()
    })

# --- Additional API Endpoints ---

@app.route('/students', methods=['GET'])
def get_students():
    """Get list of all registered students."""
    if face_id_to_name:
        return jsonify({
            'success': True,
            'students': sorted(face_id_to_name.values()),
            'total': len(face_id_to_name)
        })
    else:
        return jsonify({'error': 'No students registered'}), 404

@app.route('/attendance/today', methods=['GET'])
def get_today_attendance():
    """Get today's attendance records."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if mongo_collection is not None:
        try:
            records = list(mongo_collection.find({"date": today}).sort("time", 1))
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if 'timestamp' in record:
                    record['timestamp'] = record['timestamp'].isoformat()
            
            return jsonify({
                'success': True,
                'date': today,
                'records': records,
                'total_present': len(records)
            })
        except Exception as e:
            return jsonify({'error': f'Database error: {e}'}), 500
    else:
        return jsonify({'error': 'Database not available'}), 503

@app.route('/attendance/date/<date>', methods=['GET'])
def get_attendance_by_date(date):
    """Get attendance records for a specific date (YYYY-MM-DD)."""
    if mongo_collection is not None:
        try:
            records = list(mongo_collection.find({"date": date}).sort("time", 1))
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if 'timestamp' in record:
                    record['timestamp'] = record['timestamp'].isoformat()
            
            return jsonify({
                'success': True,
                'date': date,
                'records': records,
                'total_present': len(records)
            })
        except Exception as e:
            return jsonify({'error': f'Database error: {e}'}), 500
    else:
        return jsonify({'error': 'Database not available'}), 503

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model_loaded': face_recognizer is not None,
        'mongodb_connected': mongo_collection is not None,
        'students_count': len(face_id_to_name),
        'timestamp': datetime.datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("[INFO] Starting Flask API server...")
    print("[INFO] Available endpoints:")
    print("  POST /take-attendance - Upload image for attendance")
    print("  GET  /students - List all registered students")  
    print("  GET  /attendance/today - Get today's attendance")
    print("  GET  /attendance/date/<YYYY-MM-DD> - Get attendance by date")
    print("  GET  /health - Health check")
    print("[INFO] Server running on http://localhost:5000")
    
    # Run without debug mode to avoid socket issues
    app.run(host='0.0.0.0', port=5000, debug=False)