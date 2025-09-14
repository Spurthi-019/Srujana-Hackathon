#!/usr/bin/env python3
"""
Camera Test and Face Capture Tool
================================

This script helps you capture face images for the attendance system.
It will take photos of faces detected by the camera and save them to known_faces directory.

Author: SmartClass AI
Date: September 2025
"""

import cv2
import os
from datetime import datetime

def capture_faces():
    """Capture face images using the camera."""
    print("🎓 SmartClass AI - Face Capture Tool")
    print("=" * 40)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: Could not access camera!")
        return
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    print("📹 Camera started!")
    print("🎮 Controls:")
    print("   - Press 's' to save face image")
    print("   - Press 'q' to quit")
    print("   - Make sure your face is clearly visible")
    
    captured_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face detected - Press 's' to save", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Display info
        cv2.putText(frame, f"Captured: {captured_count} faces", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Press 's' to save face, 'q' to quit", (10, frame.shape[0] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Face Capture - SmartClass AI', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s') and len(faces) > 0:
            # Save the captured face
            name = input(f"\n📝 Enter name for this person (person_{captured_count + 1}): ").strip()
            if not name:
                name = f"person_{captured_count + 1}"
            
            # Clean the name for filename
            filename = name.replace(" ", "_").lower() + ".jpg"
            filepath = os.path.join("known_faces", filename)
            
            cv2.imwrite(filepath, frame)
            captured_count += 1
            print(f"✅ Saved face image: {filepath}")
            print("👤 Continue capturing or press 'q' to finish\n")
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n📊 Capture Summary:")
    print(f"   📸 Total faces captured: {captured_count}")
    if captured_count > 0:
        print(f"   📁 Images saved in: known_faces/")
        print(f"   🎯 Ready to run: python encode_faces.py")
    else:
        print("   ⚠️  No faces captured. Try again with better lighting.")

if __name__ == "__main__":
    # Ensure known_faces directory exists
    os.makedirs("known_faces", exist_ok=True)
    capture_faces()