#!/usr/bin/env python3
"""
MongoDB Atlas Quick Setup for Attendance System
==============================================

Quick guide and script to set up MongoDB Atlas for real-time attendance storage.

Author: SmartClass AI
Date: September 2025
"""

import json
import time
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def test_mongodb_atlas():
    """Test MongoDB Atlas connection with a sample connection string."""
    print("🧪 Testing MongoDB Atlas Connection")
    print("=" * 40)
    
    # Sample Atlas connection string (replace with your actual one)
    atlas_examples = [
        "mongodb+srv://smartclass:password@cluster0.mongodb.net/",
        "mongodb+srv://attendance:mypassword@cluster0.mongodb.net/",
        "mongodb+srv://student:attendance123@cluster0.mongodb.net/"
    ]
    
    print("📝 Sample MongoDB Atlas connection strings:")
    for i, example in enumerate(atlas_examples, 1):
        print(f"   {i}. {example}")
    
    print("\n⚠️  To get your actual connection string:")
    print("   1. Go to https://www.mongodb.com/atlas")
    print("   2. Create a free account and cluster")
    print("   3. Click 'Connect' → 'Connect your application'")
    print("   4. Copy the connection string")
    print("   5. Replace <password> with your actual password")
    
    return False

def create_mongodb_config():
    """Create MongoDB configuration file."""
    print("\n⚙️  Creating MongoDB Configuration")
    print("=" * 40)
    
    print("Choose your MongoDB option:")
    print("1. 🌐 MongoDB Atlas (Cloud) - Recommended")
    print("2. 🏠 Local MongoDB")
    print("3. 🔧 Custom connection string")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        print("\n📋 MongoDB Atlas Setup:")
        username = input("Enter MongoDB Atlas username: ").strip()
        password = input("Enter MongoDB Atlas password: ").strip()
        cluster = input("Enter cluster name (e.g., cluster0): ").strip() or "cluster0"
        
        config = {
            "connection_string": f"mongodb+srv://{username}:{password}@{cluster}.mongodb.net/",
            "database_name": "smartclass_attendance"
        }
        
    elif choice == "2":
        print("\n📋 Local MongoDB Setup:")
        config = {
            "connection_string": "mongodb://localhost:27017/",
            "database_name": "smartclass_attendance"
        }
        
    else:
        print("\n📋 Custom MongoDB Setup:")
        connection_string = input("Enter connection string: ").strip()
        database_name = input("Enter database name: ").strip() or "smartclass_attendance"
        
        config = {
            "connection_string": connection_string,
            "database_name": database_name
        }
    
    # Save configuration
    with open("mongodb_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to mongodb_config.json")
    print(f"📊 Database: {config['database_name']}")
    
    return config

def test_connection(config):
    """Test MongoDB connection."""
    print(f"\n🧪 Testing connection to {config['database_name']}...")
    
    try:
        client = MongoClient(config["connection_string"], serverSelectionTimeoutMS=10000)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Test database operations
        db = client[config["database_name"]]
        collection = db["attendance_records"]
        
        # Insert test record
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
        
        # Read test record
        found = collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test read successful: {found['name']}")
        
        # Clean up test record
        collection.delete_one({"_id": result.inserted_id})
        print("✅ Test cleanup successful")
        
        # Get collection stats
        count = collection.count_documents({})
        print(f"📊 Current attendance records: {count}")
        
        client.close()
        return True
        
    except ConnectionFailure:
        print("❌ Connection failed: Unable to connect to MongoDB")
        print("   Check your connection string and network connectivity")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def demonstrate_realtime_storage():
    """Demonstrate real-time attendance storage."""
    print("\n🎬 Demonstrating Real-Time Attendance Storage")
    print("=" * 50)
    
    # Load configuration
    try:
        with open("mongodb_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ No configuration found. Run setup first.")
        return
    
    try:
        client = MongoClient(config["connection_string"], serverSelectionTimeoutMS=5000)
        db = client[config["database_name"]]
        collection = db["attendance_records"]
        
        print(f"🗄️  Connected to: {config['database_name']}")
        print("📝 Simulating real-time attendance marking...")
        
        # Simulate attendance for sample students
        students = ["Abhishek", "Ayush", "Priya", "Rahul", "Sneha"]
        
        for i, student in enumerate(students):
            now = datetime.datetime.now()
            
            # Create attendance record
            attendance_record = {
                "name": student,
                "timestamp": now,
                "date": now.strftime("%Y-%m-%d"),
                "time": now.strftime("%H:%M:%S"),
                "status": "Present",
                "recognition_method": "opencv_template_matching",
                "system_version": "enhanced_v1.0",
                "demo": True
            }
            
            # Insert into MongoDB (real-time)
            result = collection.insert_one(attendance_record)
            
            print(f"✅ {student} - Attendance marked (MongoDB ID: {result.inserted_id})")
            
            time.sleep(1)  # Simulate time between detections
        
        # Show statistics
        print(f"\n📊 Real-Time Statistics:")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_count = collection.count_documents({"date": today, "demo": True})
        print(f"📅 Demo attendance records today: {today_count}")
        
        # Show recent records
        recent_records = collection.find({"demo": True}).sort("timestamp", -1).limit(5)
        print("📋 Recent demo attendance:")
        for record in recent_records:
            print(f"   👤 {record['name']} - {record['time']}")
        
        # Cleanup demo records
        cleanup = input("\n🧹 Clean up demo records? (y/n): ")
        if cleanup.lower() == 'y':
            result = collection.delete_many({"demo": True})
            print(f"✅ Cleaned up {result.deleted_count} demo records")
        
        client.close()
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def main():
    """Main function."""
    print("🎓 MongoDB Setup for AI Attendance System")
    print("=" * 50)
    
    print("This script helps you set up MongoDB for real-time attendance storage.")
    print("\nOptions:")
    print("1. 🧪 Test MongoDB Atlas connection")
    print("2. ⚙️  Create MongoDB configuration")
    print("3. 🔗 Test existing configuration")
    print("4. 🎬 Demonstrate real-time storage")
    print("5. ❌ Exit")
    
    while True:
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            test_mongodb_atlas()
        elif choice == "2":
            config = create_mongodb_config()
            if input("Test this configuration now? (y/n): ").lower() == 'y':
                test_connection(config)
        elif choice == "3":
            try:
                with open("mongodb_config.json", "r") as f:
                    config = json.load(f)
                test_connection(config)
            except FileNotFoundError:
                print("❌ No configuration file found. Create one first.")
        elif choice == "4":
            demonstrate_realtime_storage()
        elif choice == "5":
            print("👋 Setup completed!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()