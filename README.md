# 🎓 Real-Time AI Attendance System

A sophisticated real-time face recognition attendance system with MongoDB database integration. This system can simultaneously identify multiple people in a camera feed and automatically log their attendance to a MongoDB database.

## ✨ Features

- **🤖 Multi-Face Detection**: Simultaneously recognizes multiple people in a single camera frame
- **☁️ MongoDB Integration**: Flexible database storage for attendance records
- **🔄 Real-Time Processing**: Live camera feed with instant face recognition
- **📊 Visual Feedback**: On-screen display of recognized faces with status indicators
- **🚫 Duplicate Prevention**: Prevents multiple attendance entries for the same person in one session
- **📱 Modern Interface**: Clean, professional display with attendance statistics
- **🔧 Flexible Configuration**: Easy setup for any number of students/employees

## 🏗️ System Architecture

```
📁 realtime-ai-attendance/
├── 📄 encode_faces.py          # Face encoding preprocessing script
├── 📄 take_attendance.py       # Main real-time attendance system
├── 📄 requirements.txt         # Python dependencies
├── 📄 README.md               # This documentation
├── 📄 mongodb_config.json      # MongoDB connection configuration (you create)
├── 📁 known_faces/            # Directory for student/employee photos
│   ├── 🖼️ john_doe.jpg
│   ├── 🖼️ jane_smith.png
│   └── 🖼️ ...
└── 📄 encodings.pickle        # Generated face encodings (auto-created)
```

## 📋 Prerequisites

- **Python 3.7+**
- **Webcam/Camera** connected to your system
- **MongoDB** installed and running (local or cloud)
- **MongoDB Compass** for database visualization (optional but recommended)

## 🛠️ Installation & Setup

### Step 1: Clone or Download the Project

```bash
# Create project directory
mkdir realtime-ai-attendance
cd realtime-ai-attendance

# Copy the provided files to this directory
```

### Step 2: Install Python Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Note: If you encounter issues with dlib on Windows:
# Option 1: Install Visual Studio Build Tools
# Option 2: Use conda - conda install -c conda-forge dlib
# Option 3: Install pre-compiled wheel
```

### Step 3: MongoDB Configuration

#### 3.1 Install and Start MongoDB
```bash
# Option 1: Download and install MongoDB Community Server
# Visit: https://www.mongodb.com/try/download/community

# Option 2: Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Option 3: Using MongoDB Atlas (Cloud)
# Visit: https://www.mongodb.com/atlas and create a free cluster
```

#### 3.2 Install MongoDB Compass (Optional)
1. Download from [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Install and connect to your MongoDB instance
3. Create a database named `smartclass_attendance`

#### 3.3 Configure Database Connection
1. Copy `mongodb_config.json.example` to `mongodb_config.json`
2. Update the configuration:

```json
{
  "connection_string": "mongodb://localhost:27017/",
  "database_name": "smartclass_attendance"
}
```

**For MongoDB Atlas (Cloud):**
```json
{
  "connection_string": "mongodb+srv://username:password@cluster.mongodb.net/",
  "database_name": "smartclass_attendance"
}
```

**For MongoDB with authentication:**
```json
{
  "connection_string": "mongodb://username:password@localhost:27017/",
  "database_name": "smartclass_attendance"
}
```

### Step 4: Prepare Student/Employee Photos

1. Create photos of each person you want to recognize
2. Save them in the `known_faces/` directory
3. **Naming Convention**: `firstname_lastname.jpg` (e.g., `john_doe.jpg`, `jane_smith.png`)
4. **Photo Requirements**:
   - Clear, front-facing photos
   - Good lighting
   - Single person per photo
   - Supported formats: JPG, PNG, BMP, TIFF, WEBP

```bash
known_faces/
├── john_doe.jpg
├── jane_smith.png
├── alice_johnson.jpg
├── bob_wilson.png
└── emma_davis.jpg
```

## 🚀 Usage

### Step 1: Encode Known Faces

```bash
python encode_faces.py
```

**Expected Output:**
```
🎓 SmartClass AI - Face Encoding System
==================================================
📸 Found 5 image files to process...

🔍 Processing: john_doe.jpg -> John Doe
✅ Successfully encoded face for John Doe

🔍 Processing: jane_smith.png -> Jane Smith
✅ Successfully encoded face for Jane Smith

💾 Saving encodings to 'encodings.pickle'...
✅ Face encodings saved successfully!

📊 Summary:
   ✅ Successfully processed: 5 faces
   ❌ Failed to process: 0 images
   📁 Total students registered: 5

🎯 Ready for attendance! Run 'take_attendance.py' to start the system.
```

### Step 2: Run Real-Time Attendance

```bash
python take_attendance.py
```

**Expected Output:**
```
🎓 SmartClass AI - Real-Time Attendance System
=======================================================
📂 Loading face encodings...
✅ Loaded 5 face encodings
👥 Registered students: John Doe, Jane Smith, Alice Johnson, Bob Wilson, Emma Davis
🍃 Initializing MongoDB connection...
✅ MongoDB connected successfully!
� Database: smartclass_attendance
�📹 Initializing camera...
✅ Camera initialized successfully!

🚀 Starting Real-Time Attendance System...
👥 System can detect multiple people simultaneously
📝 Attendance will be logged automatically on first detection
🎮 Controls: 'q' to quit, 'r' to reset attendance
=======================================================

📝 [ATTENDANCE] John Doe marked present.
🍃 [MONGODB] John Doe attendance saved to database (ID: 64f8b2a1c45d6f123456789a)
📝 [ATTENDANCE] Jane Smith marked present.
🍃 [MONGODB] Jane Smith attendance saved to database (ID: 64f8b2a1c45d6f123456789b)
```

## 🎮 Controls

- **'q'**: Quit the application
- **'r'**: Reset attendance for current session
- **Mouse**: Click on the camera window to ensure it's in focus

## 📊 Database Structure

The system creates the following structure in MongoDB:

**Collection: `attendance`**
```json
{
  "_id": "64f8b2a1c45d6f123456789a",
  "student_name": "John Doe",
  "date": "2025-09-14",
  "time": "09:15:30",
  "status": "Present",
  "timestamp": "2025-09-14T09:15:30.000Z"
}
```

**Sample Data:**
```json
[
  {
    "_id": "64f8b2a1c45d6f123456789a",
    "student_name": "John Doe",
    "date": "2025-09-14",
    "time": "09:15:30",
    "status": "Present",
    "timestamp": "2025-09-14T09:15:30.000Z"
  },
  {
    "_id": "64f8b2a1c45d6f123456789b",
    "student_name": "Jane Smith",
    "date": "2025-09-14",
    "time": "09:16:45",
    "status": "Present",
    "timestamp": "2025-09-14T09:16:45.000Z"
  }
]
```

**MongoDB Compass Visualization:**
- Collection: `smartclass_attendance.attendance`
- Documents showing attendance records with timestamps
- Easy filtering by date, student name, or status

## 🎨 Visual Interface

The system displays:

- **📹 Live Camera Feed**: Real-time video with face detection
- **🟢 Green Rectangles**: Already present students
- **🟡 Yellow Rectangles**: Newly detected students
- **🔴 Red Rectangles**: Unknown faces
- **📊 Statistics**: Present count and total registered
- **📝 Present List**: Names of students currently marked present
- **🎮 Controls**: Keyboard shortcuts information

## 🔧 Troubleshooting

### Camera Issues
```bash
❌ Error: Could not access camera!
```
**Solutions:**
- Check camera connection
- Close other applications using the camera
- Try different camera index: `cv2.VideoCapture(1)` instead of `cv2.VideoCapture(0)`

### MongoDB Issues
```bash
❌ Error: mongodb_config.json not found!
```
**Solutions:**
- Create `mongodb_config.json` file in project directory
- Copy from `mongodb_config.json.example` and update connection details
- Ensure MongoDB is running on the specified port

```bash
❌ MongoDB connection failed
```
**Solutions:**
- Check if MongoDB service is running
- Verify connection string in `mongodb_config.json`
- For MongoDB Atlas, check network access and credentials
- Test connection using MongoDB Compass

### Face Recognition Issues
```bash
⚠️ No faces found in image.jpg
```
**Solutions:**
- Ensure photos have clear, front-facing faces
- Good lighting in photos
- Single person per photo
- Try different image formats

### Installation Issues
```bash
❌ Error installing dlib
```
**Solutions:**
```bash
# Windows - Install Visual Studio Build Tools or use conda
conda install -c conda-forge dlib

# Alternative: Install cmake first
pip install cmake
pip install dlib

# Or use pre-compiled wheel
pip install https://pypi.org/simple/dlib/
```

## 📈 Performance Optimization

- **Frame Skipping**: Processes every 3rd frame for better performance
- **Image Resizing**: Scales down images for faster processing
- **Efficient Comparison**: Uses face distance optimization
- **Memory Management**: Proper cleanup of resources

## 🔒 Security & Privacy

- **Local Processing**: Face recognition happens locally
- **Secure MongoDB**: Uses official PyMongo driver with authentication support
- **No Face Storage**: Only mathematical encodings are stored
- **Controlled Access**: MongoDB access control and user authentication

## 🧪 Testing

### Test with Sample Images
1. Add test images to `known_faces/`
2. Run encoding: `python encode_faces.py`
3. Test recognition: `python take_attendance.py`
4. Show face to camera and verify detection

### Offline Mode
If MongoDB is unavailable, the system continues working in offline mode with local logging.

## 📝 Customization

### Adding New Students
1. Add their photo to `known_faces/` directory
2. Re-run `python encode_faces.py`
3. Restart the attendance system

### Changing Recognition Sensitivity
In `take_attendance.py`, modify the threshold:
```python
if matches[best_match_index] and face_distances[best_match_index] < 0.6:  # Lower = stricter
```

### Custom Database Structure
Modify the record creation in `mark_attendance()`:
```python
attendance_record = {
    'student_name': name,
    'date': date_str,
    'time': time_str,
    'status': 'Present',
    'timestamp': now,
    'class_id': 'CS101',  # Add custom fields
    'teacher': 'Dr. Smith'
}
```

### MongoDB Queries
Use MongoDB Compass or command line to query attendance:
```javascript
// Find all attendance for a specific date
db.attendance.find({"date": "2025-09-14"})

// Find attendance for a specific student
db.attendance.find({"student_name": "John Doe"})

// Count daily attendance
db.attendance.aggregate([
  { $group: { _id: "$date", count: { $sum: 1 } } }
])
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Ensure proper file placement and naming
4. Check Firebase configuration

## 📄 License

This project is part of the SmartClass AI education technology suite.

---

**🎓 SmartClass AI - Revolutionizing Education with Technology**