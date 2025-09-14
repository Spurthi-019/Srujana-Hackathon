# Adding New Members to AI Attendance System

## Quick Steps:

### 1. Add Photo
- Place a clear photo in: `known_faces/newname.jpg`
- Photo should be: clear, front-facing, good lighting, single person
- Naming: Use lowercase (e.g., `priya.jpg`, `john.jpg`)

### 2. Retrain Model
```bash
python opencv_face_encoder.py
```

### 3. Test System
```bash
python opencv_attendance.py
```

## Detailed Example:

### Adding "Priya" to the system:

1. **Add Photo:**
   ```
   known_faces/priya.jpg
   ```

2. **Run Encoder:**
   ```bash
   python opencv_face_encoder.py
   ```
   
   Expected output:
   ```
   🎓 OpenCV Face Recognition System
   ========================================
   📸 Found 3 images to process...
   🔍 Processing: abhishek.jpg -> Abhishek
   ✅ Face extracted for Abhishek
   🔍 Processing: ayush.jpg -> Ayush
   ✅ Face extracted for Ayush
   🔍 Processing: priya.jpg -> Priya
   ✅ Face extracted for Priya
   
   🧠 Training recognizer with 3 faces...
   ✅ Training completed!
   📊 Registered students: Abhishek, Ayush, Priya
   ```

3. **Test Recognition:**
   ```bash
   python opencv_attendance.py
   ```
   
   The system will now recognize Priya and mark attendance!

## Current Registered Members:
- Abhishek
- Ayush

## Files Updated Automatically:
- `opencv_face_model.yml` - Contains the trained model
- System will recognize all members in `known_faces/` folder

## Troubleshooting:

### If face is not detected:
- Ensure photo is clear and well-lit
- Face should be front-facing
- Try a different photo with better quality

### If recognition accuracy is low:
- Add multiple photos of the same person with different angles
- Ensure good lighting in photos
- Remove any photos with multiple people

### If system doesn't start:
- Make sure you ran `python opencv_face_encoder.py` after adding photos
- Check that the photo file name doesn't have spaces or special characters