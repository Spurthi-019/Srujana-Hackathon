#!/usr/bin/env python3
"""
Transfer Attendance Data to MongoDB and Show Database Location
============================================================

This script transfers your existing attendance data to MongoDB and shows you
exactly where to find it in your MongoDB database.

Author: SmartClass AI
Date: September 2025
"""

import json
import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def transfer_to_mongodb():
    """Transfer existing attendance data to MongoDB."""
    print("🗄️  Transferring Attendance Data to MongoDB")
    print("=" * 50)
    
    # Connect to MongoDB
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=10000)
        client.admin.command('ping')
        print("✅ Connected to MongoDB at localhost:27017")
    except ConnectionFailure:
        print("❌ Could not connect to MongoDB!")
        print("💡 Make sure MongoDB is running:")
        print("   • Windows: net start MongoDB")
        print("   • Manual: mongod --dbpath C:\\data\\db")
        return False
    
    # Access database and collection
    db = client["smartclass_attendance"]
    collection = db["attendance_records"]
    
    print(f"🗄️  Database: smartclass_attendance")
    print(f"📋 Collection: attendance_records")
    
    # Load existing attendance data
    try:
        with open("attendance_records.json", "r") as f:
            attendance_data = json.load(f)
        print(f"📁 Loaded {len(attendance_data)} records from local file")
    except FileNotFoundError:
        print("❌ No local attendance data found!")
        return False
    
    # Convert timestamp strings to datetime objects for MongoDB
    for record in attendance_data:
        if isinstance(record['timestamp'], str):
            record['timestamp'] = datetime.datetime.fromisoformat(record['timestamp'])
    
    # Check if data already exists in MongoDB
    existing_count = collection.count_documents({})
    print(f"📊 Existing records in MongoDB: {existing_count}")
    
    if existing_count > 0:
        choice = input("⚠️  MongoDB already has data. Clear and reload? (y/n): ")
        if choice.lower() == 'y':
            collection.delete_many({})
            print("🗑️  Cleared existing data")
    
    # Insert attendance data into MongoDB
    try:
        result = collection.insert_many(attendance_data)
        print(f"✅ Successfully inserted {len(result.inserted_ids)} records")
        
        # Show where the data is located
        print("\n📍 YOUR DATA LOCATION IN MONGODB:")
        print("=" * 40)
        print(f"🌐 MongoDB Server: localhost:27017")
        print(f"🗄️  Database Name: smartclass_attendance")
        print(f"📋 Collection Name: attendance_records")
        print(f"🔗 Full Path: mongodb://localhost:27017/smartclass_attendance.attendance_records")
        
        return True
        
    except Exception as e:
        print(f"❌ Error inserting data: {e}")
        return False
    
    finally:
        client.close()

def show_mongodb_data():
    """Show how to view the data in MongoDB."""
    print("\n👀 HOW TO VIEW YOUR DATA IN MONGODB:")
    print("=" * 50)
    
    print("🔧 METHOD 1: MongoDB Compass (GUI - Recommended)")
    print("-" * 30)
    print("1. Open MongoDB Compass")
    print("2. Connect to: mongodb://localhost:27017")
    print("3. Navigate to Database: 'smartclass_attendance'")
    print("4. Open Collection: 'attendance_records'")
    print("5. You'll see all your attendance data in a table format!")
    
    print("\n💻 METHOD 2: MongoDB Shell (Command Line)")
    print("-" * 30)
    print("1. Open Command Prompt/PowerShell")
    print("2. Type: mongosh")
    print("3. Type: use smartclass_attendance")
    print("4. Type: db.attendance_records.find()")
    print("5. Or for pretty format: db.attendance_records.find().pretty()")
    
    print("\n🐍 METHOD 3: Python Script")
    print("-" * 30)
    print("Use the viewing script I'll create for you!")
    
    print("\n📊 METHOD 4: Web Dashboard")
    print("-" * 30)
    print("Run: python view_mongodb_data.py")

def query_mongodb_data():
    """Query and display MongoDB data."""
    print("\n🔍 QUERYING YOUR MONGODB DATA:")
    print("=" * 40)
    
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client["smartclass_attendance"]
        collection = db["attendance_records"]
        
        # Show all records
        print("📋 ALL ATTENDANCE RECORDS:")
        print("-" * 70)
        print(f"{'Name':<12} {'Date':<12} {'Time':<10} {'Status':<8} {'MongoDB ID'}")
        print("-" * 70)
        
        for record in collection.find().sort("timestamp", 1):
            name = record['name']
            date = record['date']
            time = record['time']
            status = record['status']
            mongo_id = str(record['_id'])[:8] + "..."
            print(f"{name:<12} {date:<12} {time:<10} {status:<8} {mongo_id}")
        
        # Show statistics
        print(f"\n📊 STATISTICS:")
        total_records = collection.count_documents({})
        unique_students = len(collection.distinct("name"))
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_records = collection.count_documents({"date": today})
        
        print(f"📈 Total records: {total_records}")
        print(f"👥 Unique students: {unique_students}")
        print(f"📅 Today's records: {today_records}")
        
        # Show recent records
        print(f"\n🕐 RECENT RECORDS (Last 5):")
        print("-" * 50)
        recent = collection.find().sort("timestamp", -1).limit(5)
        for record in recent:
            print(f"👤 {record['name']} - {record['time']} ({record['date']})")
        
        client.close()
        return True
        
    except ConnectionFailure:
        print("❌ Could not connect to MongoDB!")
        return False
    except Exception as e:
        print(f"❌ Error querying data: {e}")
        return False

def main():
    """Main function."""
    print("🎓 MongoDB Data Transfer & Viewing Guide")
    print("=" * 50)
    
    print("This script will:")
    print("1. Transfer your attendance data to MongoDB")
    print("2. Show you exactly where to find it")
    print("3. Demonstrate how to view the data")
    
    proceed = input("\nProceed with data transfer? (y/n): ")
    if proceed.lower() != 'y':
        print("❌ Transfer cancelled.")
        return
    
    # Transfer data
    success = transfer_to_mongodb()
    
    if success:
        # Show viewing methods
        show_mongodb_data()
        
        # Query and display data
        query_mongodb_data()
        
        print("\n🎉 SUCCESS! Your attendance data is now in MongoDB!")
        print("\n📍 QUICK ACCESS:")
        print("🔗 MongoDB URI: mongodb://localhost:27017/smartclass_attendance")
        print("🗄️  Database: smartclass_attendance")
        print("📋 Collection: attendance_records")
        
    else:
        print("\n❌ Transfer failed. Please check MongoDB connection.")

if __name__ == "__main__":
    main()