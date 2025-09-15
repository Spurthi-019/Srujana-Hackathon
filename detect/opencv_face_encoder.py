#!/usr/bin/env python3
"""
Alternative Face Recognition using OpenCV and Simple Matching
============================================================

Since face_recognition is having compatibility issues, let's use OpenCV for face detection
and create a simpler matching system that works reliably.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import pickle
import os
from pathlib import Path

class OpenCVFaceRecognizer:
    def __init__(self):
        """Initialize OpenCV Face Recognizer."""
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Initialize face recognizer
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.known_faces = []
        self.known_names = []
        self.face_id_to_name = {}
        
    def load_and_train_faces(self):
        """Load face images and train the recognizer."""
        print("AI OpenCV Face Recognition System")
        print("=" * 40)
        
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
        
        print(f"📸 Found {len(image_files)} images to process...")
        
        faces = []
        labels = []
        
        for idx, image_path in enumerate(image_files):
            name = image_path.stem.replace('_', ' ').title()
            self.face_id_to_name[idx] = name
            
            print(f"🔍 Processing: {image_path.name} -> {name}")
            
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"⚠️  Could not load {image_path.name}")
                continue
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            face_locations = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(face_locations) == 0:
                print(f"⚠️  No face detected in {image_path.name}")
                continue
            
            # Use the largest face if multiple detected
            if len(face_locations) > 1:
                areas = [w * h for (x, y, w, h) in face_locations]
                largest_idx = np.argmax(areas)
                face_locations = [face_locations[largest_idx]]
            
            # Extract face region
            x, y, w, h = face_locations[0]
            face_roi = gray[y:y+h, x:x+w]
            
            # Resize to standard size
            face_roi = cv2.resize(face_roi, (100, 100))
            
            faces.append(face_roi)
            labels.append(idx)
            
            print(f"✅ Face extracted for {name}")
        
        if len(faces) == 0:
            print("❌ No faces were successfully processed!")
            return False
        
        # Train the recognizer
        print(f"\n🧠 Training recognizer with {len(faces)} faces...")
        self.face_recognizer.train(faces, np.array(labels))
        
        # Save the trained model
        self.face_recognizer.save("opencv_face_model.yml")
        
        # Save the name mapping
        with open("face_names.pickle", "wb") as f:
            pickle.dump(self.face_id_to_name, f)
        
        print("✅ Training completed!")
        print(f"📊 Registered students: {', '.join(self.face_id_to_name.values())}")
        print("🎯 Ready for attendance! Run the attendance system.")
        
        return True
    
    def load_trained_model(self):
        """Load previously trained model."""
        try:
            self.face_recognizer.read("opencv_face_model.yml")
            with open("face_names.pickle", "rb") as f:
                self.face_id_to_name = pickle.load(f)
            return True
        except:
            return False

def main():
    recognizer = OpenCVFaceRecognizer()
    success = recognizer.load_and_train_faces()
    
    if success:
        print("\n🎯 Next steps:")
        print("   1. Run: python opencv_attendance.py (for the attendance system)")
        print("   2. Or test with: python test_opencv_recognition.py")

if __name__ == "__main__":
    main()