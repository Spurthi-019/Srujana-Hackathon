#!/usr/bin/env python3
"""
Simple AI Attendance System
===========================

Clean and simple attendance marking system without confidence calculations
and debug information. Just marks attendance with time and date.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import pickle
import json
import datetime
import time
from pymongo import MongoClient
from collections import defaultdict
import os

class SimpleAttendanceSystem:
    def __init__(self):
        """Initialize the simple attendance system."""
        print("Simple AI Attendance System")
        print("=" * 30)
        
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
        self.attendance_cooldown = 10  # seconds (reduced for faster marking)
        self.last_attendance = defaultdict(float)
        
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.confidence_threshold = 100  # Simple threshold
        
    def load_config(self):
        """Load MongoDB configuration."""
        try:
            with open("mongodb_config.json", "r") as f:
                config = json.load(f)
                self.mongo_uri = config.get("connection_string", "mongodb://localhost:27017")
                self.database_name = config.get("database_name", "smartclass_attendance")
                self.collection_name = "attendance_records"
                print(f"MongoDB config loaded: {self.database_name}")
        except FileNotFoundError:
            print("MongoDB config not found, using defaults")
            self.mongo_uri = "mongodb://localhost:27017"
            self.database_name = "smartclass_attendance"
            self.collection_name = "attendance_records"
    
    def connect_to_mongodb(self):
        """Connect to MongoDB."""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # Test connection
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            print("MongoDB connected successfully!")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.collection = None
    
    def load_face_model(self):
        """Load the trained face recognition model."""
        try:
            # Load face recognizer model
            self.face_recognizer.read("opencv_face_model.yml")
            
            # Load face ID to name mapping
            with open("face_names.pickle", "rb") as f:
                self.face_id_to_name = pickle.load(f)
            
            print(f"Face model loaded with {len(self.face_id_to_name)} students:")
            for name in self.face_id_to_name.values():
                print(f"   {name}")
            
            return True
            
        except Exception as e:
            print(f"Error loading face model: {e}")
            return False
    
    def mark_attendance(self, name):
        """Mark attendance for a student."""
        current_time = time.time()
        
        # Check cooldown period
        if current_time - self.last_attendance[name] < self.attendance_cooldown:
            return False
        
        self.last_attendance[name] = current_time
        
        # Create attendance record
        now = datetime.datetime.now()
        attendance_record = {
            "name": name,
            "timestamp": now,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "status": "Present"
        }
        
        # Save to MongoDB
        if self.db is not None:
            try:
                self.collection.insert_one(attendance_record)
                print(f"✓ {name} - {attendance_record['time']}")
            except Exception as e:
                print(f"MongoDB save error: {e}")
        
        # Save to local JSON file
        try:
            attendance_file = "attendance_records.json"
            
            # Load existing records
            if os.path.exists(attendance_file):
                with open(attendance_file, 'r') as f:
                    records = json.load(f)
            else:
                records = []
            
            # Create clean record for JSON
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
            
        except Exception as e:
            print(f"JSON save error: {e}")
        
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
            minSize=(80, 80),
            maxSize=(300, 300)
        )
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Recognize face
            label, confidence = self.face_recognizer.predict(face_roi)
            
            name = "Unknown"
            color = (0, 0, 255)  # Red for unknown
            
            if confidence < self.confidence_threshold:
                name = self.face_id_to_name.get(label, "Unknown")
                color = (0, 255, 0)  # Green for recognized
                
                # Mark attendance
                attendance_marked = self.mark_attendance(name)
                if attendance_marked:
                    color = (0, 255, 255)  # Yellow for new attendance
            
            # Draw rectangle and name
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, name, (x, y-10), self.font, 0.6, color, 2)
        
        return frame
    
    def show_today_attendance(self):
        """Show today's attendance summary."""
        print("\nToday's Attendance:")
        print("-" * 20)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Try to get from MongoDB first
        if self.db is not None:
            try:
                today_records = list(self.collection.find({"date": today}))
                if today_records:
                    for record in today_records:
                        print(f"  {record['name']} - {record['time']}")
                    print(f"Total: {len(today_records)} students")
                    return
            except Exception as e:
                print(f"MongoDB read error: {e}")
        
        # Fallback to JSON file
        try:
            if os.path.exists("attendance_records.json"):
                with open("attendance_records.json", 'r') as f:
                    records = json.load(f)
                
                today_records = [r for r in records if r['date'] == today]
                if today_records:
                    for record in today_records:
                        print(f"  {record['name']} - {record['time']}")
                    print(f"Total: {len(today_records)} students")
                else:
                    print("  No attendance marked today")
            else:
                print("  No attendance records found")
        except Exception as e:
            print(f"Error reading records: {e}")
    
    def run_attendance_system(self):
        """Run the main attendance system."""
        print("\nStarting camera...")
        print("Controls:")
        print("  - Press 'q' to quit")
        print("  - Press 's' to show today's attendance")
        print("  - System will automatically mark attendance")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Process frame
                processed_frame = self.process_frame(frame)
                
                # Show frame
                cv2.imshow('AI Attendance System - Press Q to quit, S for stats', processed_frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.show_today_attendance()
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            if self.db is not None:
                self.client.close()
            print("System shutdown complete")

def main():
    """Main function."""
    system = SimpleAttendanceSystem()
    system.run_attendance_system()

if __name__ == "__main__":
    main()