#!/usr/bin/env python3
"""
Quick Test - Real-Time AI Attendance System (Offline Mode)
==========================================================

This script tests the attendance system without requiring MongoDB.
Perfect for testing face recognition before setting up the database.

Author: SmartClass AI
Date: September 2025
"""

import face_recognition
import cv2
import numpy as np
import pickle
from datetime import datetime
import os

class OfflineAttendanceSystem:
    def __init__(self):
        """Initialize the Offline Attendance System."""
        self.known_encodings = []
        self.known_names = []
        self.present_students = set()
        self.cap = None
        
        print("🎓 SmartClass AI - Offline Attendance Test")
        print("=" * 50)
        
    def load_face_encodings(self):
        """Load face encodings from pickle file."""
        try:
            print("📂 Loading face encodings...")
            with open("encodings.pickle", "rb") as f:
                data = pickle.load(f)
            
            self.known_encodings = data["encodings"]
            self.known_names = data["names"]
            
            print(f"✅ Loaded {len(self.known_encodings)} face encodings")
            print(f"👥 Registered students: {', '.join(set(self.known_names))}")
            return True
            
        except FileNotFoundError:
            print("❌ Error: encodings.pickle not found!")
            print("💡 Please run 'encode_faces.py' first to create face encodings")
            return False
        except Exception as e:
            print(f"❌ Error loading encodings: {str(e)}")
            return False
    
    def initialize_camera(self):
        """Initialize the webcam."""
        try:
            print("📹 Initializing camera...")
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print("❌ Error: Could not access camera!")
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Camera initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {str(e)}")
            return False
    
    def mark_attendance_offline(self, name):
        """Mark attendance locally (offline mode)."""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        print(f"📝 [OFFLINE] {name} marked present at {time_str}")
        
        # Save to local file
        with open("attendance_log.txt", "a") as f:
            f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')} - {name} - Present\n")
    
    def process_frame(self, frame):
        """Process a single frame for face recognition."""
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                name = self.known_names[best_match_index]
                
                if name not in self.present_students:
                    self.present_students.add(name)
                    self.mark_attendance_offline(name)
            
            face_names.append(name)
        
        face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                         for (top, right, bottom, left) in face_locations]
        
        return face_locations, face_names
    
    def draw_faces(self, frame, face_locations, face_names):
        """Draw rectangles and names around detected faces."""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            if name == "Unknown":
                color = (0, 0, 255)  # Red
                status = "Unknown"
            elif name in self.present_students:
                color = (0, 255, 0)  # Green
                status = "Present ✓"
            else:
                color = (255, 255, 0)  # Yellow
                status = "Detected"
            
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, f"{name}", (left + 6, bottom - 18), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, status, (left + 6, bottom - 6), font, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def display_info(self, frame):
        """Display system information on the frame."""
        info_text = f"Present: {len(self.present_students)} | Mode: OFFLINE TEST"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        if self.present_students:
            y_offset = 60
            cv2.putText(frame, "Present Students:", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            for i, student in enumerate(sorted(self.present_students)):
                y_offset += 20
                cv2.putText(frame, f"• {student}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        controls_text = "Press 'q' to quit | 'r' to reset | OFFLINE MODE"
        cv2.putText(frame, controls_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        """Main loop for the attendance system."""
        if not self.load_face_encodings():
            return
        
        if not self.initialize_camera():
            return
        
        print("\n🚀 Starting Offline Attendance Test...")
        print("📝 Attendance will be logged to 'attendance_log.txt'")
        print("🎮 Controls: 'q' to quit, 'r' to reset")
        print("=" * 50)
        
        frame_skip = 0
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                if frame_skip % 3 == 0:
                    face_locations, face_names = self.process_frame(frame)
                
                frame = self.draw_faces(frame, face_locations, face_names)
                frame = self.display_info(frame)
                
                cv2.imshow('Offline Attendance Test', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Shutting down test system...")
                    break
                elif key == ord('r'):
                    print("\n🔄 Resetting attendance...")
                    self.present_students.clear()
                
                frame_skip += 1
                
        except KeyboardInterrupt:
            print("\n⚠️  Test interrupted")
        finally:
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            
            print("\n📊 Test Summary:")
            print(f"   👥 Total students present: {len(self.present_students)}")
            if self.present_students:
                print(f"   📝 Present students: {', '.join(sorted(self.present_students))}")
            print("   📄 Check 'attendance_log.txt' for detailed log")
            print("   ✅ Test completed")

def main():
    system = OfflineAttendanceSystem()
    system.run()

if __name__ == "__main__":
    main()