#!/usr/bin/env python3
"""
Test OpenCV Face Recognition System
==================================

Simple test script to verify the OpenCV face recognition is working
without the full attendance system.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import pickle
import os

def test_opencv_recognition():
    """Test the OpenCV face recognition system."""
    print("🧪 Testing OpenCV Face Recognition")
    print("=" * 40)
    
    # Check if model files exist
    if not os.path.exists("opencv_face_model.yml"):
        print("❌ Face model not found!")
        print("🔧 Please run 'python opencv_face_encoder.py' first")
        return
    
    if not os.path.exists("face_names.pickle"):
        print("❌ Face names file not found!")
        print("🔧 Please run 'python opencv_face_encoder.py' first")
        return
    
    # Initialize face detector and recognizer
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Load trained model
    try:
        face_recognizer.read("opencv_face_model.yml")
        with open("face_names.pickle", "rb") as f:
            face_id_to_name = pickle.load(f)
        
        print(f"✅ Model loaded with {len(face_id_to_name)} students:")
        for name in face_id_to_name.values():
            print(f"   👤 {name}")
        
    except Exception as e:
        print(f"❌ Could not load model: {e}")
        return
    
    # Test with camera
    print("\n🎥 Starting camera test...")
    print("   - Press SPACE to test recognition")
    print("   - Press 'q' to quit")
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Could not open camera!")
        return
    
    confidence_threshold = 50
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (100, 100))
                
                # Recognize face
                label, confidence = face_recognizer.predict(face_roi)
                
                name = "Unknown"
                color = (0, 0, 255)  # Red
                
                if confidence < confidence_threshold:
                    name = face_id_to_name.get(label, "Unknown")
                    color = (0, 255, 0)  # Green
                
                # Draw rectangle and label
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                text = f"{name} ({100-confidence:.1f}%)" if confidence < confidence_threshold else name
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Add instructions
            cv2.putText(frame, "SPACE: Test | Q: Quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('OpenCV Face Recognition Test', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):  # Space bar
                print(f"🧪 Testing recognition at {cv2.getTickCount()}")
                
        print("✅ Camera test completed")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

def test_image_recognition():
    """Test recognition on known face images."""
    print("\n🖼️  Testing image recognition...")
    
    if not os.path.exists("known_faces"):
        print("❌ known_faces directory not found!")
        return
    
    # Load model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    try:
        face_recognizer.read("opencv_face_model.yml")
        with open("face_names.pickle", "rb") as f:
            face_id_to_name = pickle.load(f)
    except:
        print("❌ Could not load model files")
        return
    
    # Test on known images
    image_files = []
    for ext in ['.jpg', '.jpeg', '.png']:
        image_files.extend([f for f in os.listdir("known_faces") if f.lower().endswith(ext)])
    
    for image_file in image_files:
        print(f"\n🔍 Testing: {image_file}")
        
        img_path = os.path.join("known_faces", image_file)
        img = cv2.imread(img_path)
        
        if img is None:
            print(f"   ❌ Could not load {image_file}")
            continue
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            print(f"   ⚠️  No face detected")
            continue
        
        # Use first/largest face
        x, y, w, h = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (100, 100))
        
        label, confidence = face_recognizer.predict(face_roi)
        
        if confidence < 50:
            predicted_name = face_id_to_name.get(label, "Unknown")
            print(f"   ✅ Recognized as: {predicted_name} (confidence: {100-confidence:.1f}%)")
        else:
            print(f"   ❌ Not recognized (confidence too low: {100-confidence:.1f}%)")

def main():
    """Main test function."""
    print("🧪 OpenCV Face Recognition Test Suite")
    print("=" * 50)
    
    # Test 1: Load model
    test_opencv_recognition()
    
    # Test 2: Test on images
    test_image_recognition()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()