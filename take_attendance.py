#!/usr/bin/env python3
"""
Real-Time AI Attendance System - Main Attendance Script
======================================================

This script runs the real-time attendance system with Firebase integration.
It can handle multiple faces simultaneously and logs attendance individually.

Author: SmartClass AI
Date: September 2025
"""

import face_recognition
import cv2
import numpy as np
import pickle
from pymongo import MongoClient
from datetime import datetime
import os
import json

class RealTimeAttendanceSystem:
    def __init__(self):
        """Initialize the Real-Time Attendance System."""
        self.known_encodings = []
        self.known_names = []
        self.present_students = set()
        self.cap = None
        self.mongodb_client = None
        self.db = None
        self.mongodb_initialized = False
        
        print("🎓 SmartClass AI - Real-Time Attendance System")
        print("=" * 55)
        
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
    
    def initialize_mongodb(self):
        """Initialize MongoDB connection."""
        try:
            print("🍃 Initializing MongoDB connection...")
            
            # Check if mongodb_config.json exists
            if not os.path.exists("mongodb_config.json"):
                print("❌ Error: mongodb_config.json not found!")
                print("💡 Please create mongodb_config.json with your MongoDB connection details")
                print("📝 Instructions:")
                print("   1. Create mongodb_config.json in this directory")
                print("   2. Add your MongoDB connection string and database name")
                print("   3. Example format: {'connection_string': 'mongodb://localhost:27017/', 'database_name': 'smartclass_attendance'}")
                return False
            
            # Load MongoDB configuration
            with open("mongodb_config.json", "r") as f:
                config = json.load(f)
            
            connection_string = config.get("connection_string", "mongodb://localhost:27017/")
            database_name = config.get("database_name", "smartclass_attendance")
            
            # Connect to MongoDB
            self.mongodb_client = MongoClient(connection_string)
            
            # Test connection
            self.mongodb_client.admin.command('ping')
            
            # Get database
            self.db = self.mongodb_client[database_name]
            
            print(f"✅ MongoDB connected successfully!")
            print(f"📊 Database: {database_name}")
            self.mongodb_initialized = True
            return True
            
        except json.JSONDecodeError:
            print("❌ Error: Invalid mongodb_config.json file!")
            print("💡 Please ensure the file is valid JSON with connection_string and database_name")
            return False
        except Exception as e:
            print(f"❌ MongoDB connection failed: {str(e)}")
            print("💡 Please check your MongoDB connection string and ensure MongoDB is running")
            return False
    
    def initialize_camera(self):
        """Initialize the webcam."""
        try:
            print("📹 Initializing camera...")
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print("❌ Error: Could not access camera!")
                print("💡 Please check if your camera is connected and not being used by another application")
                return False
            
            # Set camera properties for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print("✅ Camera initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Camera initialization failed: {str(e)}")
            return False
    
    def mark_attendance(self, name):
        """Mark attendance for a student in MongoDB."""
        if not self.mongodb_initialized:
            print(f"⚠️  MongoDB not available - {name} attendance logged locally only")
            return
        
        try:
            # Get current date and time
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            
            # Create attendance record
            attendance_record = {
                'student_name': name,
                'date': date_str,
                'time': time_str,
                'status': 'Present',
                'timestamp': now
            }
            
            # Insert into MongoDB collection
            collection = self.db['attendance']
            result = collection.insert_one(attendance_record)
            
            print(f"🍃 [MONGODB] {name} attendance saved to database (ID: {result.inserted_id})")
            
        except Exception as e:
            print(f"❌ Error saving to MongoDB: {str(e)}")
            print(f"📝 [LOCAL] {name} marked present at {datetime.now().strftime('%H:%M:%S')}")
    
    def process_frame(self, frame):
        """Process a single frame for face recognition."""
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        
        # Find face locations and encodings
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        
        face_names = []
        
        # Process each face found in the frame
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_encodings, face_encoding)
            name = "Unknown"
            
            # Use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.known_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            
            if matches[best_match_index] and face_distances[best_match_index] < 0.6:
                name = self.known_names[best_match_index]
                
                # Mark attendance if not already present
                if name not in self.present_students:
                    self.present_students.add(name)
                    print(f"📝 [ATTENDANCE] {name} marked present.")
                    self.mark_attendance(name)
            
            face_names.append(name)
        
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        face_locations = [(top * 4, right * 4, bottom * 4, left * 4) 
                         for (top, right, bottom, left) in face_locations]
        
        return face_locations, face_names
    
    def draw_faces(self, frame, face_locations, face_names):
        """Draw rectangles and names around detected faces."""
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Choose color based on recognition status
            if name == "Unknown":
                color = (0, 0, 255)  # Red for unknown
                status = "Unknown"
            elif name in self.present_students:
                color = (0, 255, 0)  # Green for already present
                status = "Present ✓"
            else:
                color = (255, 255, 0)  # Yellow for newly detected
                status = "Detected"
            
            # Draw rectangle around face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label background
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            
            # Draw name and status
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, f"{name}", (left + 6, bottom - 18), font, 0.6, (255, 255, 255), 1)
            cv2.putText(frame, status, (left + 6, bottom - 6), font, 0.4, (255, 255, 255), 1)
        
        return frame
    
    def display_info(self, frame):
        """Display system information on the frame."""
        # Display attendance count
        info_text = f"Present: {len(self.present_students)} | Total Registered: {len(set(self.known_names))}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Display present students list
        if self.present_students:
            y_offset = 60
            cv2.putText(frame, "Present Students:", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            for i, student in enumerate(sorted(self.present_students)):
                y_offset += 20
                cv2.putText(frame, f"• {student}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # Display controls
        controls_text = "Press 'q' to quit | 'r' to reset attendance"
        cv2.putText(frame, controls_text, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame
    
    def run(self):
        """Main loop for the attendance system."""
        # Initialize all components
        if not self.load_face_encodings():
            return
        
        if not self.initialize_mongodb():
            print("⚠️  Continuing without MongoDB (offline mode)")
        
        if not self.initialize_camera():
            return
        
        print("\n🚀 Starting Real-Time Attendance System...")
        print("👥 System can detect multiple people simultaneously")
        print("📝 Attendance will be logged automatically on first detection")
        print("🎮 Controls: 'q' to quit, 'r' to reset attendance")
        print("=" * 55)
        
        frame_skip = 0
        
        try:
            while True:
                # Read frame from camera
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: Could not read from camera!")
                    break
                
                # Process every 3rd frame for better performance
                if frame_skip % 3 == 0:
                    face_locations, face_names = self.process_frame(frame)
                
                # Draw faces and information
                frame = self.draw_faces(frame, face_locations, face_names)
                frame = self.display_info(frame)
                
                # Display the frame
                cv2.imshow('Real-Time Attendance', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Shutting down attendance system...")
                    break
                elif key == ord('r'):
                    print("\n🔄 Resetting attendance for this session...")
                    self.present_students.clear()
                
                frame_skip += 1
                
        except KeyboardInterrupt:
            print("\n⚠️  System interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
        finally:
            # Cleanup
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            
            # Close MongoDB connection
            if self.mongodb_client:
                self.mongodb_client.close()
                print("🍃 MongoDB connection closed")
            
            print("\n📊 Session Summary:")
            print(f"   👥 Total students present: {len(self.present_students)}")
            if self.present_students:
                print(f"   📝 Present students: {', '.join(sorted(self.present_students))}")
            print("   ✅ System shutdown complete")

def main():
    """Main function to run the attendance system."""
    system = RealTimeAttendanceSystem()
    system.run()

if __name__ == "__main__":
    main()