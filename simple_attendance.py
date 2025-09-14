#!/usr/bin/env python3
"""
Simple Face Detection Attendance System
=======================================

A simplified attendance system using basic OpenCV face detection and 
template matching instead of complex face recognition libraries.

This approach is more reliable and doesn't require problematic dependencies.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import json
import datetime
import os
import hashlib
from pathlib import Path
from pymongo import MongoClient
from collections import defaultdict
import time

class SimpleAttendanceSystem:
    def __init__(self):
        """Initialize the simple attendance system."""
        print("🎓 Simple AI Attendance System")
        print("=" * 40)
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load configuration
        self.load_config()
        
        # MongoDB connection
        self.connect_to_mongodb()
        
        # Load face templates
        self.load_face_templates()
        
        # Attendance tracking
        self.attendance_cooldown = 30  # seconds
        self.last_attendance = defaultdict(float)
        
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
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
    
    def load_face_templates(self):
        """Load face templates for recognition."""
        self.face_templates = {}
        
        known_faces_dir = "known_faces"
        if not os.path.exists(known_faces_dir):
            print(f"❌ Error: '{known_faces_dir}' directory not found!")
            return False
        
        # Get image files
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png']:
            image_files.extend(Path(known_faces_dir).glob(f"*{ext}"))
        
        image_files = [f for f in image_files if f.name != '.gitkeep']
        
        if not image_files:
            print("❌ No face images found!")
            return False
        
        print(f"📸 Loading {len(image_files)} face templates...")
        
        for image_path in image_files:
            name = image_path.stem.replace('_', ' ').title()
            
            print(f"🔍 Processing: {image_path.name} -> {name}")
            
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"⚠️  Could not load {image_path.name}")
                continue
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                print(f"⚠️  No face detected in {image_path.name}")
                continue
            
            # Use the largest face if multiple detected
            if len(faces) > 1:
                areas = [w * h for (x, y, w, h) in faces]
                largest_idx = np.argmax(areas)
                faces = [faces[largest_idx]]
            
            # Extract face region
            x, y, w, h = faces[0]
            face_roi = gray[y:y+h, x:x+w]
            
            # Resize to standard size for comparison
            face_template = cv2.resize(face_roi, (100, 100))
            
            # Store template
            self.face_templates[name] = face_template
            
            print(f"✅ Template created for {name}")
        
        if len(self.face_templates) == 0:
            print("❌ No face templates were created!")
            return False
        
        print(f"✅ Loaded {len(self.face_templates)} face templates:")
        for name in self.face_templates.keys():
            print(f"   👤 {name}")
        
        return True
    
    def recognize_face(self, face_roi):
        """Recognize a face using template matching."""
        if not self.face_templates:
            return "Unknown", 0.0
        
        # Resize face to match template size
        face_resized = cv2.resize(face_roi, (100, 100))
        
        best_match = "Unknown"
        best_score = 0.0
        
        for name, template in self.face_templates.items():
            # Use template matching
            result = cv2.matchTemplate(face_resized, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_match = name
        
        # Threshold for recognition (adjust as needed)
        confidence_threshold = 0.4
        if best_score < confidence_threshold:
            return "Unknown", best_score
        
        return best_match, best_score
    
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
        if self.db:
            try:
                self.collection.insert_one(attendance_record)
                print(f"✅ MongoDB: Attendance marked for {name}")
            except Exception as e:
                print(f"❌ MongoDB error: {e}")
        
        # Console log
        print(f"📋 ATTENDANCE: {name} - {attendance_record['time']}")
        
        return True
    
    def process_frame(self, frame):
        """Process a single frame for face recognition."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        recognized_names = []
        
        for (x, y, w, h) in faces:
            # Extract face region
            face_roi = gray[y:y+h, x:x+w]
            
            # Recognize face
            name, confidence = self.recognize_face(face_roi)
            
            color = (0, 0, 255)  # Red for unknown
            
            if name != "Unknown":
                color = (0, 255, 0)  # Green for recognized
                recognized_names.append(name)
                
                # Mark attendance
                attendance_marked = self.mark_attendance(name)
                if attendance_marked:
                    color = (0, 255, 255)  # Yellow for new attendance
            
            # Draw rectangle and label
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Prepare text
            text = f"{name}"
            if name != "Unknown":
                text += f" ({confidence:.2f})"
            
            # Draw text background
            text_size = cv2.getTextSize(text, self.font, 0.6, 2)[0]
            cv2.rectangle(frame, (x, y-30), (x + text_size[0], y), color, -1)
            
            # Draw text
            cv2.putText(frame, text, (x, y-10), self.font, 0.6, (255, 255, 255), 2)
        
        return frame, recognized_names
    
    def run_attendance_system(self):
        """Run the main attendance system."""
        print("\n🎥 Starting camera...")
        print("📋 Simple Attendance System Active!")
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
                info_text = f"Runtime: {runtime:.0f}s | Templates: {len(self.face_templates)}"
                cv2.putText(frame, info_text, (10, 30), self.font, 0.6, (255, 255, 255), 2)
                
                # Add instructions
                cv2.putText(frame, "Press 'q' to quit | 's' for stats", (10, frame.shape[0]-20), 
                           self.font, 0.5, (255, 255, 255), 1)
                
                # Show frame
                cv2.imshow('Simple AI Attendance System', frame)
                
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
            if self.db:
                self.client.close()
            print("✅ System shutdown complete")
    
    def show_statistics(self):
        """Show attendance statistics."""
        print("\n📊 ATTENDANCE STATISTICS")
        print("=" * 30)
        
        if not self.db:
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
    """Main function."""
    # Initialize attendance system
    system = SimpleAttendanceSystem()
    
    # Check if face templates were loaded
    if not hasattr(system, 'face_templates') or not system.face_templates:
        print("❌ No face templates loaded!")
        print("🔧 Please ensure you have face images in the 'known_faces' directory")
        return
    
    # Run the system
    system.run_attendance_system()

if __name__ == "__main__":
    main()