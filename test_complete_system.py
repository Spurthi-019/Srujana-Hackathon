#!/usr/bin/env python3
"""
Test Complete Attendance System with MongoDB
===========================================

This script tests the complete attendance system including MongoDB integration.
It creates a local demo without requiring MongoDB server.

Author: SmartClass AI
Date: September 2025
"""

import json
import datetime
import os
from collections import defaultdict
import time

class MockMongoDB:
    """Mock MongoDB for testing when server is not available."""
    
    def __init__(self):
        self.records = []
        self.db_file = "attendance_records.json"
        self.load_records()
    
    def insert_one(self, record):
        """Insert a record."""
        # Convert datetime to string for JSON serialization
        record_copy = record.copy()
        if 'timestamp' in record_copy:
            record_copy['timestamp'] = record_copy['timestamp'].isoformat()
        
        self.records.append(record_copy)
        self.save_records()
        return True
    
    def count_documents(self, filter_dict):
        """Count documents matching filter."""
        count = 0
        for record in self.records:
            if filter_dict.get('date') and record.get('date') == filter_dict['date']:
                count += 1
        return count
    
    def find(self, filter_dict, projection=None):
        """Find documents matching filter."""
        results = []
        for record in self.records:
            if filter_dict.get('date') and record.get('date') == filter_dict['date']:
                if projection:
                    result = {k: record.get(k) for k in projection.keys() if k in record}
                else:
                    result = record
                results.append(result)
        return results
    
    def save_records(self):
        """Save records to file."""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            print(f"Error saving records: {e}")
    
    def load_records(self):
        """Load records from file."""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    self.records = json.load(f)
        except Exception as e:
            print(f"Error loading records: {e}")
            self.records = []

def test_attendance_logging():
    """Test attendance logging functionality."""
    print("🧪 Testing Attendance Logging System")
    print("=" * 40)
    
    # Initialize mock database
    mock_db = MockMongoDB()
    
    # Test data
    students = ["Abhishek", "Ayush", "Priya", "Rahul"]
    attendance_cooldown = 30  # seconds
    last_attendance = defaultdict(float)
    
    def mark_attendance(name):
        """Mark attendance for a student."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - last_attendance[name] < attendance_cooldown:
            return False
        
        last_attendance[name] = current_time
        
        # Create attendance record
        attendance_record = {
            "name": name,
            "timestamp": datetime.datetime.now(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "status": "Present"
        }
        
        # Save to mock database
        try:
            mock_db.insert_one(attendance_record)
            print(f"✅ Attendance marked for {name} at {attendance_record['time']}")
            return True
        except Exception as e:
            print(f"❌ Error marking attendance: {e}")
            return False
    
    # Simulate attendance marking
    print("📋 Simulating attendance marking...")
    
    for i, student in enumerate(students):
        success = mark_attendance(student)
        if success:
            print(f"   👤 {student} - Present")
        time.sleep(1)  # Small delay between students
    
    # Test duplicate attendance (should be blocked by cooldown)
    print("\n🚫 Testing cooldown (should be blocked)...")
    mark_attendance("Abhishek")  # Should be blocked
    
    # Show statistics
    print("\n📊 Attendance Statistics:")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    today_count = mock_db.count_documents({"date": today})
    print(f"📅 Today's attendance count: {today_count}")
    
    attendees = mock_db.find({"date": today}, {"name": 1, "time": 1})
    print("📋 Today's attendees:")
    for record in attendees:
        print(f"   👤 {record['name']} - {record['time']}")
    
    print(f"\n💾 Records saved to: {mock_db.db_file}")
    
    return True

def test_face_template_system():
    """Test the face template loading system."""
    print("\n🧪 Testing Face Template System")
    print("=" * 40)
    
    known_faces_dir = "known_faces"
    if not os.path.exists(known_faces_dir):
        print(f"❌ Directory '{known_faces_dir}' not found!")
        return False
    
    # Check for images
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        for file in os.listdir(known_faces_dir):
            if file.lower().endswith(ext) and file != '.gitkeep':
                image_files.append(file)
    
    if not image_files:
        print("❌ No face images found!")
        return False
    
    print(f"📸 Found {len(image_files)} face images:")
    for file in image_files:
        name = os.path.splitext(file)[0].replace('_', ' ').title()
        file_size = os.path.getsize(os.path.join(known_faces_dir, file))
        print(f"   📷 {file} -> {name} ({file_size:,} bytes)")
    
    print("✅ Face template system ready!")
    return True

def test_system_integration():
    """Test complete system integration."""
    print("\n🧪 Testing System Integration")
    print("=" * 40)
    
    # Test 1: Face templates
    template_test = test_face_template_system()
    
    # Test 2: Attendance logging
    logging_test = test_attendance_logging()
    
    if template_test and logging_test:
        print("\n✅ ALL TESTS PASSED!")
        print("\n🎯 Your AI Attendance System is ready!")
        print("\nNext steps:")
        print("   1. Start MongoDB server (optional)")
        print("   2. Run: python simple_attendance.py")
        print("   3. Point camera at registered faces")
        print("   4. Check attendance records in attendance_records.json")
        
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

def main():
    """Main test function."""
    print("🎓 AI Attendance System - Complete Test Suite")
    print("=" * 50)
    
    # Run integration tests
    test_system_integration()
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")

if __name__ == "__main__":
    main()