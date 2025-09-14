#!/usr/bin/env python3
"""
MongoDB Attendance Data Viewer
==============================

View your attendance data directly from MongoDB database at localhost:27017

Author: SmartClass AI  
Date: September 2025
"""

import json
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import datetime
import pandas as pd

def connect_to_mongodb():
    """Connect to MongoDB and return database collection."""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        db = client["smartclass_attendance"]
        collection = db["attendance_records"]
        
        print("✅ Connected to MongoDB")
        print(f"🗄️  Database: smartclass_attendance")
        print(f"📋 Collection: attendance_records")
        
        return collection, client
        
    except ConnectionFailure:
        print("❌ Could not connect to MongoDB at localhost:27017")
        print("💡 Make sure MongoDB is running:")
        print("   • Start service: net start MongoDB")
        print("   • Or start manually: mongod --dbpath C:\\data\\db")
        return None, None

def view_all_records(collection):
    """View all attendance records from MongoDB."""
    print("\n📋 ALL ATTENDANCE RECORDS FROM MONGODB:")
    print("=" * 80)
    
    try:
        records = list(collection.find().sort("timestamp", 1))
        
        if not records:
            print("❌ No records found in MongoDB!")
            print("💡 Run 'python transfer_to_mongodb.py' to transfer your data")
            return
        
        print(f"{'#':<3} {'Name':<15} {'Date':<12} {'Time':<10} {'Status':<8} {'MongoDB ID':<15}")
        print("-" * 80)
        
        for i, record in enumerate(records, 1):
            name = record['name']
            date = record['date']
            time = record['time']
            status = record['status']
            mongo_id = str(record['_id'])
            
            print(f"{i:<3} {name:<15} {date:<12} {time:<10} {status:<8} {mongo_id[:12]}...")
        
        print(f"\n📊 Total records: {len(records)}")
        
    except Exception as e:
        print(f"❌ Error reading records: {e}")

def view_statistics(collection):
    """View attendance statistics."""
    print("\n📊 ATTENDANCE STATISTICS:")
    print("=" * 40)
    
    try:
        # Total records
        total_records = collection.count_documents({})
        print(f"📈 Total attendance records: {total_records}")
        
        # Unique students
        students = collection.distinct("name")
        print(f"👥 Unique students: {len(students)}")
        print(f"📝 Student names: {', '.join(students)}")
        
        # Today's attendance
        today = datetime.now().strftime("%Y-%m-%d")
        today_count = collection.count_documents({"date": today})
        print(f"📅 Today's attendance ({today}): {today_count}")
        
        # Student-wise count
        print(f"\n👥 STUDENT-WISE ATTENDANCE:")
        print("-" * 30)
        for student in students:
            count = collection.count_documents({"name": student})
            print(f"👤 {student:<15}: {count} times")
        
        # Date range
        all_records = list(collection.find({}, {"date": 1}).sort("date", 1))
        if all_records:
            first_date = all_records[0]['date']
            last_date = all_records[-1]['date']
            print(f"\n📅 Date range: {first_date} to {last_date}")
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")

def view_recent_records(collection, limit=10):
    """View recent attendance records."""
    print(f"\n🕐 RECENT {limit} RECORDS:")
    print("=" * 60)
    
    try:
        recent = list(collection.find().sort("timestamp", -1).limit(limit))
        
        if not recent:
            print("❌ No recent records found!")
            return
        
        print(f"{'Name':<15} {'Date':<12} {'Time':<10} {'Status':<8}")
        print("-" * 60)
        
        for record in recent:
            name = record['name']
            date = record['date']
            time = record['time']
            status = record['status']
            print(f"{name:<15} {date:<12} {time:<10} {status:<8}")
        
    except Exception as e:
        print(f"❌ Error getting recent records: {e}")

def search_by_student(collection):
    """Search attendance by student name."""
    print("\n🔍 SEARCH BY STUDENT:")
    print("=" * 30)
    
    student_name = input("Enter student name: ").strip()
    
    if not student_name:
        print("❌ No name entered!")
        return
    
    try:
        # Case-insensitive search
        records = list(collection.find({
            "name": {"$regex": f"^{student_name}$", "$options": "i"}
        }).sort("timestamp", -1))
        
        if not records:
            print(f"❌ No records found for '{student_name}'")
            available_students = collection.distinct("name")
            print(f"💡 Available students: {', '.join(available_students)}")
            return
        
        print(f"\n📋 ATTENDANCE RECORDS FOR {student_name.upper()}:")
        print("-" * 50)
        print(f"{'Date':<12} {'Time':<10} {'Status':<8}")
        print("-" * 50)
        
        for record in records:
            date = record['date']
            time = record['time']
            status = record['status']
            print(f"{date:<12} {time:<10} {status:<8}")
        
        print(f"\n📊 Total attendance for {student_name}: {len(records)}")
        
    except Exception as e:
        print(f"❌ Error searching records: {e}")

def export_to_csv(collection):
    """Export MongoDB data to CSV."""
    print("\n📥 EXPORT TO CSV:")
    print("=" * 20)
    
    try:
        records = list(collection.find({}, {"_id": 0}).sort("timestamp", 1))
        
        if not records:
            print("❌ No data to export!")
            return
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        # Generate filename with timestamp
        filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        print(f"✅ Data exported to: {filename}")
        print(f"📊 Records exported: {len(records)}")
        
    except ImportError:
        print("❌ pandas not installed. Installing...")
        import subprocess
        subprocess.run(["pip", "install", "pandas"])
        print("✅ pandas installed. Please run export again.")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def realtime_monitor(collection):
    """Monitor real-time attendance updates."""
    print("\n👁️  REAL-TIME MONITOR:")
    print("=" * 30)
    print("Press Ctrl+C to stop monitoring...")
    
    try:
        import time
        last_count = collection.count_documents({})
        
        while True:
            current_count = collection.count_documents({})
            
            if current_count > last_count:
                # New record added
                new_records = list(collection.find().sort("timestamp", -1).limit(current_count - last_count))
                
                for record in reversed(new_records):
                    print(f"🆕 NEW: {record['name']} - {record['time']} ({record['date']})")
                
                last_count = current_count
            
            time.sleep(2)  # Check every 2 seconds
            
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped.")
    except Exception as e:
        print(f"❌ Monitoring error: {e}")

def main():
    """Main viewer function."""
    print("🎓 MongoDB Attendance Data Viewer")
    print("=" * 50)
    print("📍 MongoDB Location: mongodb://localhost:27017")
    print("🗄️  Database: smartclass_attendance")
    print("📋 Collection: attendance_records")
    print()
    
    # Connect to MongoDB
    collection, client = connect_to_mongodb()
    
    if not collection:
        print("\n💡 TROUBLESHOOTING:")
        print("1. Make sure MongoDB is installed and running")
        print("2. Check if service is running: Get-Service MongoDB")
        print("3. Start service: net start MongoDB")
        print("4. Or start manually: mongod --dbpath C:\\data\\db")
        return
    
    try:
        while True:
            print("\n🗄️  MONGODB VIEWER OPTIONS:")
            print("=" * 30)
            print("1. 📋 View all records")
            print("2. 📊 View statistics")
            print("3. 🕐 View recent records")
            print("4. 🔍 Search by student")
            print("5. 📥 Export to CSV")
            print("6. 👁️  Real-time monitor")
            print("7. ❌ Exit")
            
            choice = input("\nSelect option (1-7): ").strip()
            
            if choice == "1":
                view_all_records(collection)
            elif choice == "2":
                view_statistics(collection)
            elif choice == "3":
                view_recent_records(collection)
            elif choice == "4":
                search_by_student(collection)
            elif choice == "5":
                export_to_csv(collection)
            elif choice == "6":
                realtime_monitor(collection)
            elif choice == "7":
                print("👋 Viewer closed!")
                break
            else:
                print("❌ Invalid option. Please try again.")
    
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    main()