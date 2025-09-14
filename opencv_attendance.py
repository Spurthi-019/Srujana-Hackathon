#!/usr/bin/env python3
"""
OpenCV-based Real-Time AI Attendance System with MongoDB
========================================================

This is a working alternative to the face_recognition library that uses OpenCV
for both face detection and recognition.

Features:
- Real-time face detection and recognition
- MongoDB integration for attendance tracking
- Multiple face detection in single frame
- Auto-attendance marking
- User-friendly interface

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import pickle
import json
import datetime
import threading
import time
from pymongo import MongoClient
from collections import defaultdict
import os

class OpenCVAttendanceSystem:
    def __init__(self):
        """Initialize the attendance system."""
        print("🎓 OpenCV AI Attendance System")
        print("=" * 40)
        
        # Initialize face detector and recognizer
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Load configuration
        self.load_config()
        
        # MongoDB connection
        self.connect_to_mongodb()
        
        # Load trained model
        self.load_face_model()
        
        # Attendance tracking
        self.attendance_cooldown = 30  # seconds
        self.last_attendance = defaultdict(float)
        
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.confidence_threshold = 100  # Adjusted for better recognition (was 50)
        
    def load_config(self):
        """Load MongoDB configuration."""
        try:
            with open("mongodb_config.json", "r") as f:
                config = json.load(f)
                self.connection_string = config["connection_string"]
                self.database_name = config["database_name"]
                print(f"✅ MongoDB config loaded: {self.database_name}")
        except:
            print("⚠️  Using default MongoDB config")
            self.connection_string = "mongodb://localhost:27017/"
            self.database_name = "smartclass_attendance"
    
    def connect_to_mongodb(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.database_name]
            self.collection = self.db["attendance_records"]
            
            # Test connection
            self.client.server_info()
            print("✅ MongoDB connected successfully!")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("📝 Attendance will be logged to console only")
            self.db = None
    
    def load_face_model(self):
        """Load the trained face recognition model."""
        try:
            self.face_recognizer.read("opencv_face_model.yml")
            with open("face_names.pickle", "rb") as f:
                self.face_id_to_name = pickle.load(f)
            
            print(f"✅ Face model loaded with {len(self.face_id_to_name)} students:")
            for name in self.face_id_to_name.values():
                print(f"   👤 {name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Could not load face model: {e}")
            print("🔧 Please run 'python opencv_face_encoder.py' first!")
            return False
    
    def mark_attendance(self, name):
        """Mark attendance for a student."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_attendance[name] < self.attendance_cooldown:
            return False
        
        self.last_attendance[name] = current_time
        
        # Create attendance record
        attendance_record = {
            "name": name,
            "timestamp": datetime.datetime.now(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "status": "Present"
        }
        
        # Save to MongoDB
        if self.db is not None:
            try:
                self.collection.insert_one(attendance_record)
                print(f"✅ MongoDB: Attendance marked for {name}")
            except Exception as e:
                print(f"❌ MongoDB error: {e}")
        
        # Save to local JSON file (backup)
        try:
            attendance_file = "attendance_records.json"
            
            # Load existing records
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r') as f:
                    records = json.load(f)
            else:
                records = []
            
            # Create clean record for JSON (without MongoDB ObjectId)
            json_record = {
                "name": name,
                "timestamp": attendance_record['timestamp'].isoformat(),
                "date": attendance_record['date'],
                "time": attendance_record['time'],
                "status": attendance_record['status']
            }
            
            # Add new record
            records.append(json_record)
            
            # Save back to file
            with open(attendance_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            print(f"✅ JSON: Attendance saved to {attendance_file}")
            
        except Exception as e:
            print(f"❌ JSON save error: {e}")
        
        # Console log
        print(f"📋 ATTENDANCE: {name} - {attendance_record['time']}")
        
        return True
    
    def process_frame(self, frame):
        """Process a single frame for face recognition."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=3, 
            minSize=(30, 30),
            maxSize=(300, 300)
        )
        
        recognized_names = []
        
        if len(faces) > 0:
            print(f"🔍 Detected {len(faces)} face(s)")  # Debug output
        
        for i, (x, y, w, h) in enumerate(faces):
            print(f"  Face {i+1}: size={w}x{h}, position=({x},{y})")  # Debug output
            
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face_roi)
            
            print(f"👤 Face prediction: label={label}, confidence={confidence:.1f}")  # Debug output
            
            name = "Unknown"
            color = (0, 0, 255)  # Red for unknown
            
            if confidence < self.confidence_threshold:
                name = self.face_id_to_name.get(label, "Unknown")
                color = (0, 255, 0)  # Green for recognized
                recognized_names.append(name)
                print(f"✅ Recognized: {name} (confidence: {confidence:.1f})")  # Debug output
                
                # Mark attendance
                attendance_marked = self.mark_attendance(name)
                if attendance_marked:
                    color = (0, 255, 255)  # Yellow for new attendance
                    print(f"📝 Attendance marked for {name}")  # Debug output
            else:
                print(f"❌ Confidence too low: {confidence:.1f} > {self.confidence_threshold}")  # Debug output
            
            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Prepare text
            text = f"{name}"
            if confidence < self.confidence_threshold:
                text += f" ({100-confidence:.1f}%)"
            
            # Draw text background
            text_size = cv2.getTextSize(text, self.font, 0.6, 2)[0]
            cv2.rectangle(frame, (x, y-30), (x + text_size[0], y), color, -1)
            
            # Draw text
            cv2.putText(frame, text, (x, y-10), self.font, 0.6, (255, 255, 255), 2)
        
        return frame, recognized_names
    
    def run_attendance_system(self):
        """Run the main attendance system."""
        print("\n🎥 Starting camera...")
        print("📋 Attendance System Active!")
        print("   - Green box: Recognized student")
        print("   - Yellow box: Attendance marked")
        print("   - Red box: Unknown person")
        print("   - Press 'q' to quit")
        print("   - Press 's' to show statistics")
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Could not open camera!")
            return
        
        frame_count = 0
        start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Failed to read from camera")
                    break
                
                # Process every 3rd frame for performance
                if frame_count % 3 == 0:
                    frame, recognized_names = self.process_frame(frame)
                
                frame_count += 1
                
                # Add system info
                runtime = time.time() - start_time
                info_text = f"Runtime: {runtime:.0f}s | Frame: {frame_count}"
                cv2.putText(frame, info_text, (10, 30), self.font, 0.6, (255, 255, 255), 2)
                
                # Add instructions
                cv2.putText(frame, "Press 'q' to quit | 's' for stats", (10, frame.shape[0]-20), 
                           self.font, 0.5, (255, 255, 255), 1)
                
                # Show frame
                cv2.imshow('OpenCV AI Attendance System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Shutting down attendance system...")
                    break
                elif key == ord('s'):
                    self.show_statistics()
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            if self.db is not None:
                self.client.close()
            print("✅ System shutdown complete")
    
    def show_statistics(self):
        """Show attendance statistics."""
        print("\n📊 ATTENDANCE STATISTICS")
        print("=" * 30)
        
        if self.db is None:
            print("❌ No database connection for statistics")
            return
        
        try:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Today's attendance
            today_count = self.collection.count_documents({"date": today})
            print(f"📅 Today's attendance: {today_count}")
            
            # Get today's attendees
            attendees = self.collection.find({"date": today}, {"name": 1, "time": 1})
            for record in attendees:
                print(f"   👤 {record['name']} - {record['time']}")
            
            print("=" * 30)
            
        except Exception as e:
            print(f"❌ Statistics error: {e}")

def main():
    # Check if face model exists
    if not os.path.exists("opencv_face_model.yml"):
        print("❌ Face model not found!")
        print("🔧 Please run 'python opencv_face_encoder.py' first to train the system")
        return
    
    # Initialize and run attendance system
    system = OpenCVAttendanceSystem()
    
    if hasattr(system, 'face_id_to_name') and system.face_id_to_name:
        system.run_attendance_system()
    else:
        print("❌ Could not load face recognition model")
        print("🔧 Please run 'python opencv_face_encoder.py' first")

if __name__ == "__main__":
    main()