#!/usr/bin/env python3
"""
Enhanced Real-Time AI Attendance System with MongoDB Integration
===============================================================

This enhanced version provides multiple MongoDB options:
1. Local MongoDB server
2. MongoDB Atlas (cloud)
3. Local JSON backup (fallback)

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
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from collections import defaultdict
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedAttendanceSystem:
    def __init__(self):
        """Initialize the enhanced attendance system with MongoDB."""
        print("🎓 Enhanced AI Attendance System with MongoDB")
        print("=" * 50)
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load configuration
        self.load_config()
        
        # MongoDB connection with multiple options
        self.setup_mongodb()
        
        # Load face templates
        self.load_face_templates()
        
        # Attendance tracking
        self.attendance_cooldown = 30  # seconds
        self.last_attendance = defaultdict(float)
        
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Local backup
        self.local_backup_file = "attendance_records.json"
        
    def load_config(self):
        """Load MongoDB configuration with multiple options."""
        self.mongodb_configs = [
            # Option 1: MongoDB Atlas (Cloud)
            {
                "name": "MongoDB Atlas (Cloud)",
                "connection_string": "mongodb+srv://username:password@cluster0.mongodb.net/",
                "database_name": "smartclass_attendance"
            },
            # Option 2: Local MongoDB
            {
                "name": "Local MongoDB",
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "smartclass_attendance"
            },
            # Option 3: MongoDB with authentication
            {
                "name": "Local MongoDB with Auth",
                "connection_string": "mongodb://admin:password@localhost:27017/",
                "database_name": "smartclass_attendance"
            }
        ]
        
        # Try to load custom config
        try:
            with open("mongodb_config.json", "r") as f:
                custom_config = json.load(f)
                custom_config["name"] = "Custom Configuration"
                self.mongodb_configs.insert(0, custom_config)  # Put custom config first
                print(f"✅ Custom MongoDB config loaded")
        except FileNotFoundError:
            print("⚠️  No custom mongodb_config.json found, using defaults")
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
    
    def setup_mongodb(self):
        """Setup MongoDB connection with fallback options."""
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.mongodb_connected = False
        
        print("\n🗄️  Setting up MongoDB connection...")
        
        for config in self.mongodb_configs:
            try:
                print(f"🔄 Trying {config['name']}...")
                
                # Create client with shorter timeout for faster failover
                client = MongoClient(
                    config["connection_string"], 
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000
                )
                
                # Test connection
                client.admin.command('ping')
                
                # Setup database and collection
                self.mongo_client = client
                self.db = client[config["database_name"]]
                self.collection = self.db["attendance_records"]
                
                # Create indexes for better performance
                self.collection.create_index([("date", 1), ("name", 1)])
                self.collection.create_index([("timestamp", -1)])
                
                self.mongodb_connected = True
                print(f"✅ Connected to {config['name']}")
                print(f"📊 Database: {config['database_name']}")
                print(f"📋 Collection: attendance_records")
                
                # Test write operation
                test_record = {
                    "test": True,
                    "timestamp": datetime.datetime.now(),
                    "connection_test": config['name']
                }
                result = self.collection.insert_one(test_record)
                print(f"✅ Write test successful (ID: {result.inserted_id})")
                
                # Clean up test record
                self.collection.delete_one({"_id": result.inserted_id})
                
                return True
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                print(f"❌ {config['name']} failed: Connection timeout")
                continue
            except Exception as e:
                print(f"❌ {config['name']} failed: {str(e)}")
                continue
        
        print("⚠️  No MongoDB connection available")
        print("📝 Falling back to local JSON storage only")
        return False
    
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
        
        print(f"\n📸 Loading {len(image_files)} face templates...")
        
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
        
        print(f"\n✅ Loaded {len(self.face_templates)} face templates:")
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
    
    def save_to_local_backup(self, attendance_record):
        """Save attendance record to local JSON file."""
        try:
            # Load existing records
            if os.path.exists(self.local_backup_file):
                with open(self.local_backup_file, 'r') as f:
                    records = json.load(f)
            else:
                records = []
            
            # Convert datetime to string for JSON serialization
            record_copy = attendance_record.copy()
            if 'timestamp' in record_copy and isinstance(record_copy['timestamp'], datetime.datetime):
                record_copy['timestamp'] = record_copy['timestamp'].isoformat()
            
            # Add new record
            records.append(record_copy)
            
            # Save back to file
            with open(self.local_backup_file, 'w') as f:
                json.dump(records, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving to local backup: {e}")
            return False
    
    def mark_attendance(self, name):
        """Mark attendance for a student with real-time MongoDB storage."""
        current_time = time.time()
        
        # Check cooldown
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
            "status": "Present",
            "recognition_method": "opencv_template_matching",
            "system_version": "enhanced_v1.0"
        }
        
        # Save to MongoDB (real-time)
        mongodb_success = False
        if self.mongodb_connected and self.collection:
            try:
                result = self.collection.insert_one(attendance_record.copy())
                mongodb_success = True
                print(f"✅ MongoDB: Attendance saved for {name} (ID: {result.inserted_id})")
                logger.info(f"MongoDB attendance saved for {name}")
                
            except Exception as e:
                print(f"❌ MongoDB error: {e}")
                logger.error(f"MongoDB save failed for {name}: {e}")
                self.mongodb_connected = False  # Mark as disconnected for retry
        
        # Save to local backup (always)
        local_success = self.save_to_local_backup(attendance_record)
        if local_success:
            print(f"✅ Local: Attendance backed up for {name}")
        else:
            print(f"❌ Local backup failed for {name}")
        
        # Console log
        print(f"📋 ATTENDANCE: {name} - {attendance_record['time']}")
        
        # Show storage status
        storage_status = []
        if mongodb_success:
            storage_status.append("MongoDB")
        if local_success:
            storage_status.append("Local")
        
        print(f"💾 Stored in: {', '.join(storage_status) if storage_status else 'None'}")
        
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
    
    def get_mongodb_status(self):
        """Get current MongoDB connection status."""
        if self.mongodb_connected and self.collection:
            try:
                # Test connection
                self.mongo_client.admin.command('ping')
                count = self.collection.count_documents({})
                return f"Connected ({count} records)"
            except:
                self.mongodb_connected = False
                return "Disconnected"
        return "Not Available"
    
    def show_statistics(self):
        """Show attendance statistics from both MongoDB and local storage."""
        print("\n📊 ATTENDANCE STATISTICS")
        print("=" * 40)
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # MongoDB Statistics
        if self.mongodb_connected and self.collection:
            try:
                # Today's attendance from MongoDB
                mongodb_count = self.collection.count_documents({"date": today})
                print(f"🗄️  MongoDB - Today's attendance: {mongodb_count}")
                
                # Get today's attendees from MongoDB
                attendees = self.collection.find({"date": today}, {"name": 1, "time": 1}).sort("timestamp", -1)
                print("📋 MongoDB attendees today:")
                for record in attendees:
                    print(f"   👤 {record['name']} - {record['time']}")
                
            except Exception as e:
                print(f"❌ MongoDB statistics error: {e}")
        
        # Local backup statistics
        try:
            if os.path.exists(self.local_backup_file):
                with open(self.local_backup_file, 'r') as f:
                    local_records = json.load(f)
                
                today_local = [r for r in local_records if r.get('date') == today]
                print(f"\n💾 Local backup - Today's attendance: {len(today_local)}")
                
                print("📋 Local backup attendees today:")
                for record in today_local:
                    print(f"   👤 {record['name']} - {record['time']}")
        
        except Exception as e:
            print(f"❌ Local statistics error: {e}")
        
        print(f"\n🔗 MongoDB Status: {self.get_mongodb_status()}")
        print("=" * 40)
    
    def run_attendance_system(self):
        """Run the main attendance system."""
        print(f"\n🎥 Starting camera...")
        print("📋 Enhanced Attendance System Active!")
        print("   - Green box: Recognized student")
        print("   - Yellow box: Attendance just marked")
        print("   - Red box: Unknown person")
        print("   - Press 'q' to quit")
        print("   - Press 's' to show statistics")
        print("   - Press 'r' to reconnect MongoDB")
        
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
                mongo_status = "✅" if self.mongodb_connected else "❌"
                info_text = f"Runtime: {runtime:.0f}s | MongoDB: {mongo_status} | Templates: {len(self.face_templates)}"
                cv2.putText(frame, info_text, (10, 30), self.font, 0.5, (255, 255, 255), 1)
                
                # Add instructions
                cv2.putText(frame, "q:quit | s:stats | r:reconnect", (10, frame.shape[0]-20), 
                           self.font, 0.5, (255, 255, 255), 1)
                
                # Show frame
                cv2.imshow('Enhanced AI Attendance System', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n👋 Shutting down attendance system...")
                    break
                elif key == ord('s'):
                    self.show_statistics()
                elif key == ord('r'):
                    print("\n🔄 Attempting to reconnect to MongoDB...")
                    self.setup_mongodb()
                
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            if self.mongo_client:
                self.mongo_client.close()
            print("✅ System shutdown complete")

def main():
    """Main function."""
    # Initialize attendance system
    system = EnhancedAttendanceSystem()
    
    # Check if face templates were loaded
    if not hasattr(system, 'face_templates') or not system.face_templates:
        print("❌ No face templates loaded!")
        print("🔧 Please ensure you have face images in the 'known_faces' directory")
        return
    
    # Run the system
    system.run_attendance_system()

if __name__ == "__main__":
    main()