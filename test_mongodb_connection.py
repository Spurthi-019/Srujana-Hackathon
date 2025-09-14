#!/usr/bin/env python3
"""
MongoDB Connection and Attendance Test
=====================================

This script tests MongoDB connectivity and demonstrates real-time attendance storage.

Author: SmartClass AI
Date: September 2025
"""

import json
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_mongodb_connection():
    """Test MongoDB connection."""
    print("🧪 Testing MongoDB Connection")
    print("=" * 40)
    
    # Load config
    try:
        with open("mongodb_config.json", "r") as f:
            config = json.load(f)
        print(f"✅ Config loaded: {config['database_name']}")
    except FileNotFoundError:
        print("❌ mongodb_config.json not found!")
        print("📝 Create it with your MongoDB connection details.")
        return False
    
    try:
        # Connect with timeout
        client = MongoClient(config["connection_string"], serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get server info
        server_info = client.server_info()
        print(f"📊 MongoDB version: {server_info['version']}")
        
        # Access database and collection
        db = client[config["database_name"]]
        collection = db["attendance_records"]
        
        print(f"🗄️  Database: {config['database_name']}")
        print(f"📋 Collection: attendance_records")
        
        # Test write operation
        test_record = {
            "name": "Test Student",
            "timestamp": datetime.datetime.now(),
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "status": "Present",
            "test": True
        }
        
        result = collection.insert_one(test_record)
        print(f"✅ Test write successful (ID: {result.inserted_id})")
        
        # Test read operation
        found_record = collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test read successful: {found_record['name']}")
        
        # Count existing records
        total_records = collection.count_documents({})
        print(f"📊 Total attendance records: {total_records}")
        
        # Clean up test record
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Test cleanup successful")
        
        # Show recent real attendance (non-test)
        recent_records = collection.find({"test": {"$ne": True}}).sort("timestamp", -1).limit(5)
        print("\n📋 Recent real attendance records:")
        for record in recent_records:
            print(f"   👤 {record['name']} - {record['time']} ({record['date']})")
        
        client.close()
        return True
        
    except ConnectionFailure:
        print("❌ Connection failed: Unable to connect to MongoDB")
        print("💡 Make sure MongoDB is running:")
        print("   • Local: net start MongoDB")
        print("   • Manual: mongod --dbpath C:\\data\\db")
        print("   • Atlas: Check internet connection and credentials")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def simulate_realtime_attendance():
    """Simulate real-time attendance storage to MongoDB."""
    print("\n🎬 Simulating Real-Time Attendance Storage")
    print("=" * 50)
    
    # Load config
    try:
        with open("mongodb_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Configuration not found.")
        return
    
    try:
        client = MongoClient(config["connection_string"], serverSelectionTimeoutMS=5000)
        db = client[config["database_name"]]
        collection = db["attendance_records"]
        
        print(f"🗄️  Connected to: {config['database_name']}")
        print("📝 Storing real-time attendance...")
        
        # Sample students (same as in your face templates)
        students = ["Abhishek", "Ayush"]
        
        for student in students:
            now = datetime.datetime.now()
            
            # Create attendance record (same format as your attendance system)
            attendance_record = {
                "name": student,
                "timestamp": now,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "status": "Present",
                "recognition_method": "opencv_template_matching",
                "system_version": "enhanced_v1.0"
            }
            
            # Insert into MongoDB (real-time storage)
            result = collection.insert_one(attendance_record)
            
            print(f"✅ {student} - Attendance stored (MongoDB ID: {result.inserted_id})")
        
        # Show updated statistics
        print(f"\n📊 Updated Statistics:")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_count = collection.count_documents({"date": today})
        print(f"📅 Total attendance records today: {today_count}")
        
        client.close()
        print("✅ Real-time storage simulation completed!")
        
    except Exception as e:
        print(f"❌ Simulation failed: {e}")

def show_attendance_dashboard():
    """Show attendance dashboard from MongoDB."""
    print("\n📊 Attendance Dashboard")
    print("=" * 30)
    
    try:
        with open("mongodb_config.json", "r") as f:
            config = json.load(f)
        
        client = MongoClient(config["connection_string"], serverSelectionTimeoutMS=5000)
        db = client[config["database_name"]]
        collection = db["attendance_records"]
        
        # Today's statistics
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_count = collection.count_documents({"date": today})
        print(f"📅 Today ({today}): {today_count} attendance records")
        
        # Get today's unique students
        today_students = collection.distinct("name", {"date": today})
        print(f"👥 Students present today: {len(today_students)}")
        for student in today_students:
            print(f"   👤 {student}")
        
        # Recent attendance (last 10)
        print(f"\n📋 Recent attendance:")
        recent = collection.find().sort("timestamp", -1).limit(10)
        for record in recent:
            print(f"   📝 {record['name']} - {record['time']} ({record['date']})")
        
        # Total statistics
        total_records = collection.count_documents({})
        print(f"\n📈 Total attendance records: {total_records}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")

def main():
    """Main test function."""
    print("🎓 MongoDB + AI Attendance System Test")
    print("=" * 50)
    
    print("This script tests your MongoDB setup and demonstrates real-time storage.")
    print("\nSelect test:")
    print("1. 🧪 Test MongoDB connection")
    print("2. 🎬 Simulate real-time attendance storage")
    print("3. 📊 Show attendance dashboard")
    print("4. 🚀 Run all tests")
    print("5. ❌ Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            success = test_mongodb_connection()
            if success:
                print("\n🎉 MongoDB is ready for your attendance system!")
        elif choice == "2":
            simulate_realtime_attendance()
        elif choice == "3":
            show_attendance_dashboard()
        elif choice == "4":
            print("🚀 Running all tests...\n")
            if test_mongodb_connection():
                simulate_realtime_attendance()
                show_attendance_dashboard()
                print("\n🎉 All tests completed successfully!")
        elif choice == "5":
            print("👋 Testing completed!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()