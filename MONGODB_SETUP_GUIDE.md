# 🗄️ Quick MongoDB Setup Guide for Windows

## Option 1: MongoDB Community Server (Recommended)

### Step 1: Download MongoDB
1. Go to https://www.mongodb.com/try/download/community
2. Select:
   - Version: 7.0.12 (Current)
   - Platform: Windows
   - Package: msi
3. Download the installer

### Step 2: Install MongoDB
1. Run the .msi installer
2. Choose "Complete" installation
3. **Important**: Check "Install MongoDB as a Service"
4. **Important**: Check "Install MongoDB Compass" (GUI tool)
5. Finish installation

### Step 3: Verify Installation
Open Command Prompt or PowerShell and run:
```powershell
mongod --version
```

### Step 4: Start MongoDB Service
```powershell
net start MongoDB
```

### Step 5: Test Connection
```powershell
mongo
```

## Option 2: MongoDB Atlas (Cloud - Easiest)

### Step 1: Create Account
1. Go to https://www.mongodb.com/atlas
2. Click "Try Free"
3. Create account

### Step 2: Create Cluster
1. Choose "Build a Database"
2. Select "FREE" shared cluster
3. Choose AWS/Google Cloud/Azure
4. Select region closest to you
5. Click "Create Cluster"

### Step 3: Create Database User
1. Go to "Database Access"
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `smartclass`
5. Password: `SmartClass2025` (or your choice)
6. User Privileges: "Read and write to any database"

### Step 4: Configure Network Access
1. Go to "Network Access"
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for development)
4. Or add your specific IP

### Step 5: Get Connection String
1. Go to "Clusters"
2. Click "Connect"
3. Choose "Connect your application"
4. Copy connection string
5. Replace `<password>` with your actual password

Example connection string:
```
mongodb+srv://smartclass:SmartClass2025@cluster0.abc123.mongodb.net/
```

### Step 6: Update Config
Update your `mongodb_config.json`:
```json
{
  "connection_string": "mongodb+srv://smartclass:SmartClass2025@cluster0.abc123.mongodb.net/",
  "database_name": "smartclass_attendance"
}
```

## Option 3: Docker MongoDB (If you have Docker)

### Quick Start with Docker
```powershell
# Pull MongoDB image
docker pull mongo:latest

# Run MongoDB container
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Verify it's running
docker ps
```

## Testing Your MongoDB Connection

Once MongoDB is running, test the connection:

```powershell
cd "d:\1.TUTORIALS\smartclass-ai\attendance\realtime-ai-attendance"
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017'); client.admin.command('ping'); print('✅ MongoDB connected!')"
```

## Running the Enhanced Attendance System

Once MongoDB is running:

```powershell
cd "d:\1.TUTORIALS\smartclass-ai\attendance\realtime-ai-attendance"
python enhanced_attendance.py
```

You should see:
```
✅ Connected to Custom Configuration
📊 Database: smartclass_attendance
📋 Collection: attendance_records
✅ Write test successful
```

## Quick Commands Reference

### Windows Service Commands
```powershell
# Start MongoDB service
net start MongoDB

# Stop MongoDB service
net stop MongoDB

# Check service status
Get-Service MongoDB
```

### MongoDB Commands
```powershell
# Connect to MongoDB shell
mongo

# Show databases
show dbs

# Use attendance database
use smartclass_attendance

# Show collections
show collections

# Find all attendance records
db.attendance_records.find()

# Count attendance records
db.attendance_records.count()
```

## Troubleshooting

### "MongoDB service not found"
- MongoDB wasn't installed as a service
- Try: `mongod --dbpath C:\data\db` to start manually

### "Connection refused"
- MongoDB service isn't running
- Check: `Get-Service MongoDB`
- Start: `net start MongoDB`

### "Access denied"
- Run Command Prompt/PowerShell as Administrator
- Or use MongoDB Atlas (cloud) instead

## 🎉 Ready to Use!

Once MongoDB is running, your attendance system will automatically:
- ✅ Store attendance in MongoDB (real-time)
- ✅ Backup to local JSON file
- ✅ Show MongoDB status in camera feed
- ✅ Allow reconnection with 'r' key

**Your enhanced attendance system is ready for real-time MongoDB storage!**