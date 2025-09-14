#!/usr/bin/env python3
"""
Ultra Simple Attendance System
==============================

The cleanest possible attendance system - just marks attendance with time and date.
No confidence display, no debug info, just clean attendance marking.

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

class UltraSimpleAttendance:
    def __init__(self):
        """Initialize the attendance system."""
        print("AI Attendance System")
        print("=" * 20)
        
        # Initialize face detector and recognizer
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Load MongoDB config
        self.setup_mongodb()
        
        # Load trained model
        self.load_model()
        
        # Attendance settings
        self.cooldown = 10  # seconds between marking for same person
        self.last_marked = defaultdict(float)
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def setup_mongodb(self):
        """Setup MongoDB connection."""
        try:
            with open("mongodb_config.json", "r") as f:
                config = json.load(f)
                uri = config.get("connection_string", "mongodb://localhost:27017")
                db_name = config.get("database_name", "smartclass_attendance")
            
            self.client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            self.client.server_info()
            self.db = self.client[db_name]
            self.collection = self.db["attendance_records"]
            print("MongoDB: Connected")
        except:
            print("MongoDB: Not available")
            self.client = None
            self.db = None
            self.collection = None
    
    def load_model(self):
        """Load face recognition model."""
        try:
            self.face_recognizer.read("opencv_face_model.yml")
            with open("face_names.pickle", "rb") as f:
                self.face_names = pickle.load(f)
            print(f"Loaded {len(self.face_names)} students")
            return True
        except Exception as e:
            print(f"Model load error: {e}")
            return False
    
    def mark_attendance(self, name):
        """Mark attendance for a student."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_marked[name] < self.cooldown:
            return False
        
        self.last_marked[name] = current_time
        now = datetime.datetime.now()
        
        # Create record
        record = {
            "name": name,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "status": "Present",
            "timestamp": now
        }
        
        # Save to MongoDB
        if self.collection is not None:
            try:
                mongo_record = record.copy()
                self.collection.insert_one(mongo_record)
            except:
                pass
        
        # Save to JSON (backup)
        try:
            json_file = "simple_attendance.json"
            records = []
            
            # Load existing if file exists
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        records = json.load(f)
                except:
                    records = []  # Start fresh if corrupted
            
            # Add new record (without timestamp for JSON)
            json_record = {
                "name": name,
                "date": record["date"],
                "time": record["time"],
                "status": "Present"
            }
            records.append(json_record)
            
            # Save back
            with open(json_file, 'w') as f:
                json.dump(records, f, indent=2)
        except:
            pass
        
        # Display
        print(f"✓ {name} marked present at {record['time']}")
        return True
    
    def process_frame(self, frame):
        """Process frame for face recognition."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(80, 80))
        
        for (x, y, w, h) in faces:
            # Extract and resize face
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Predict
            label, confidence = self.face_recognizer.predict(face_roi)
            
            # Check if recognized
            if confidence < 100 and label in self.face_names:
                name = self.face_names[label]
                color = (0, 255, 0)  # Green
                
                # Mark attendance
                if self.mark_attendance(name):
                    color = (0, 255, 255)  # Yellow when marked
            else:
                name = "Unknown"
                color = (0, 0, 255)  # Red
            
            # Draw on frame
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, name, (x, y-10), self.font, 0.6, color, 2)
        
        return frame
    
    def show_today(self):
        """Show today's attendance."""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        print(f"\nToday's Attendance ({today}):")
        print("-" * 30)
        
        count = 0
        
        # Try MongoDB first
        if self.collection is not None:
            try:
                records = list(self.collection.find({"date": today}).sort("time", 1))
                for record in records:
                    print(f"  {record['name']} - {record['time']}")
                    count += 1
            except:
                pass
        
        # Fallback to JSON
        if count == 0:
            try:
                with open("simple_attendance.json", 'r') as f:
                    records = json.load(f)
                for record in records:
                    if record['date'] == today:
                        print(f"  {record['name']} - {record['time']}")
                        count += 1
            except:
                pass
        
        if count == 0:
            print("  No attendance marked today")
        else:
            print(f"Total: {count} students")
    
    def run(self):
        """Run the attendance system."""
        print("\nStarting camera...")
        print("Press 'q' to quit, 's' to show today's attendance")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Camera error!")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                frame = self.process_frame(frame)
                
                cv2.imshow('Attendance System - Q to quit, S for stats', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    self.show_today()
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            if self.client:
                self.client.close()
            print("System stopped")

def main():
    system = UltraSimpleAttendance()
    system.run()

if __name__ == "__main__":
    main()