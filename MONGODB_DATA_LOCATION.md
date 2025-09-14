# 🗄️ Where to Find Your Attendance Data in MongoDB

## 📍 Database Location

**MongoDB Server:** `mongodb://localhost:27017`
**Database Name:** `smartclass_attendance`
**Collection Name:** `attendance_records`

## 🔧 How to View Your Data

### Method 1: MongoDB Compass (GUI - Easiest) 🖥️

1. **Download MongoDB Compass** (if not installed):
   - Go to: https://www.mongodb.com/products/compass
   - Download and install the free GUI tool

2. **Connect to your database:**
   - Open MongoDB Compass
   - Connection String: `mongodb://localhost:27017`
   - Click "Connect"

3. **Navigate to your data:**
   - Database: `smartclass_attendance`
   - Collection: `attendance_records`
   - You'll see all your attendance data in a table!

### Method 2: Command Line (MongoDB Shell) 💻

```bash
# Open MongoDB shell
mongosh

# Switch to your database
use smartclass_attendance

# View all attendance records
db.attendance_records.find()

# View records in pretty format
db.attendance_records.find().pretty()

# Count total records
db.attendance_records.count()

# Find specific student
db.attendance_records.find({"name": "Abhishek"})

# Find today's records
db.attendance_records.find({"date": "2025-09-14"})
```

### Method 3: Python Viewer Script 🐍

```bash
# Use our custom viewer
python view_mongodb_data.py
```

### Method 4: Transfer Your Current Data 📤

```bash
# Transfer your JSON data to MongoDB
python transfer_to_mongodb.py
```

## 📊 Your Data Structure in MongoDB

Each attendance record in MongoDB looks like this:

```json
{
  "_id": ObjectId("..."),
  "name": "Abhishek",
  "timestamp": ISODate("2025-09-14T16:32:08.894Z"),
  "date": "2025-09-14",
  "time": "16:32:08",
  "status": "Present",
  "recognition_method": "opencv_template_matching",
  "system_version": "enhanced_v1.0"
}
```

## 🚀 Quick Start Steps

1. **Start MongoDB** (if not running):
   ```bash
   net start MongoDB
   ```

2. **Transfer your data:**
   ```bash
   python transfer_to_mongodb.py
   ```

3. **View your data:**
   ```bash
   python view_mongodb_data.py
   ```

## 📱 Real-time Updates

When you run the attendance system (`enhanced_attendance.py`):
- ✅ New detections are saved instantly to MongoDB
- ✅ Data appears immediately in MongoDB Compass
- ✅ You can monitor live updates with the viewer script

## 🔍 MongoDB Query Examples

```javascript
// Find all students present today
db.attendance_records.find({"date": "2025-09-14"})

// Count Abhishek's total attendance
db.attendance_records.count({"name": "Abhishek"})

// Get unique student names
db.attendance_records.distinct("name")

// Find latest 5 records
db.attendance_records.find().sort({"timestamp": -1}).limit(5)

// Find records by time range
db.attendance_records.find({
  "timestamp": {
    "$gte": ISODate("2025-09-14T16:30:00.000Z"),
    "$lt": ISODate("2025-09-14T17:00:00.000Z")
  }
})
```

## 🎯 Summary

**Your attendance data will be stored at:**
- 🌐 **Server:** localhost:27017
- 🗄️ **Database:** smartclass_attendance  
- 📋 **Collection:** attendance_records

**Access it via:**
- 🖥️ MongoDB Compass (GUI)
- 💻 MongoDB Shell (command line)
- 🐍 Python scripts (viewer/transfer)
- 🌐 Web dashboard (when built)

**Real-time updates happen automatically when the attendance system runs!** ✨