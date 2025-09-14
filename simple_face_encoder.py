#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple OpenCV Face Encoder
==========================

Simple face recognition training without Unicode characters to avoid encoding issues.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import os
from pathlib import Path
import pickle

class SimpleFaceEncoder:
    def __init__(self):
        """Initialize the face encoder."""
        # Initialize face detector and recognizer
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Store face data
        self.faces = []
        self.labels = []
        self.face_id_to_name = {}
        
    def load_and_train_faces(self):
        """Load face images and train the recognizer."""
        print("OpenCV Face Recognition System")
        print("=" * 40)
        
        known_faces_dir = "known_faces"
        if not os.path.exists(known_faces_dir):
            print(f"Error: '{known_faces_dir}' directory not found!")
            return False
            
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(Path(known_faces_dir).glob(ext))
            
        if not image_files:
            print("Error: No face images found!")
            return False
            
        print(f"Found {len(image_files)} images to process...")
        
        face_id = 0
        
        for image_path in image_files:
            # Skip temporary files
            if image_path.stem.endswith(('_1', '_2', '_3', '_4', '_5')):
                continue
                
            # Extract name from filename
            name = image_path.stem.replace("_", " ").title()
            print(f"Processing: {image_path.name} -> {name}")
            
            # Load image
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"Error: Could not load {image_path}")
                continue
                
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces_in_image = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces_in_image) == 0:
                print(f"Warning: No face detected in {image_path.name}")
                continue
            elif len(faces_in_image) > 1:
                print(f"Warning: Multiple faces in {image_path.name}, using largest")
            
            # Use the largest face
            largest_face = max(faces_in_image, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Extract and resize face
            face_roi = gray[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Store face data
            self.faces.append(face_roi)
            self.labels.append(face_id)
            self.face_id_to_name[face_id] = name
            
            print(f"Face extracted for {name}")
            face_id += 1
        
        if len(self.faces) == 0:
            print("Error: No valid faces found!")
            return False
            
        print(f"\nTraining recognizer with {len(self.faces)} faces...")
        
        # Train the recognizer
        self.face_recognizer.train(self.faces, np.array(self.labels))
        
        # Save the trained model
        model_path = "opencv_face_model.yml"
        self.face_recognizer.save(model_path)
        
        print("Training completed!")
        print(f"Registered students: {', '.join(self.face_id_to_name.values())}")
        print("Ready for attendance! Run the attendance system.")
        
        return True
        
    def save_face_names(self):
        """Save face ID to name mapping."""
        with open("face_names.pickle", "wb") as f:
            pickle.dump(self.face_id_to_name, f)

def main():
    """Main function."""
    recognizer = OpenCVFaceRecognizer()
    
    success = recognizer.load_and_train_faces()
    
    if success:
        recognizer.save_face_names()
        print("\nNext steps:")
        print("   1. Run: python opencv_attendance.py (for the attendance system)")
        print("   2. Or test with: python test_opencv_recognition.py")
    else:
        print("Training failed! Please check your images and try again.")

# Keep the old class name for compatibility
class OpenCVFaceRecognizer(SimpleFaceEncoder):
    pass

if __name__ == "__main__":
    main()