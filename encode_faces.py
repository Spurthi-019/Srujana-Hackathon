#!/usr/bin/env python3
"""
Real-Time AI Attendance System - Face Encoding Script
====================================================

This script processes known face images and creates encodings for face recognition.
It creates a pickle file containing face encodings and corresponding names.

Author: SmartClass AI
Date: September 2025
"""

import face_recognition
import os
import pickle
import cv2
from pathlib import Path

def encode_known_faces():
    """
    Process all images in the known_faces directory and create face encodings.
    Saves the encodings and names to encodings.pickle file.
    """
    print("🎓 SmartClass AI - Face Encoding System")
    print("=" * 50)
    
    # Known faces directory
    known_faces_dir = "known_faces"
    
    # Check if directory exists
    if not os.path.exists(known_faces_dir):
        print(f"❌ Error: '{known_faces_dir}' directory not found!")
        print(f"💡 Please create a '{known_faces_dir}' directory and add student photos")
        return False
    
    # Initialize lists to store encodings and names
    known_encodings = []
    known_names = []
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    # Get all image files
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(known_faces_dir).glob(f"*{ext}"))
        image_files.extend(Path(known_faces_dir).glob(f"*{ext.upper()}"))
    
    if not image_files:
        print(f"❌ No image files found in '{known_faces_dir}' directory!")
        print("💡 Please add student photos (jpg, png, etc.) to the known_faces directory")
        print("📝 Format: student_name.jpg (e.g., john_doe.jpg, jane_smith.png)")
        return False
    
    print(f"📸 Found {len(image_files)} image files to process...")
    print()
    
    processed_count = 0
    failed_count = 0
    
    for image_path in image_files:
        try:
            # Extract name from filename (remove extension)
            name = image_path.stem.replace('_', ' ').title()
            
            print(f"🔍 Processing: {image_path.name} -> {name}")
            
            # Load image using multiple methods for better compatibility
            image = None
            try:
                # Method 1: Try cv2 first
                image_cv2 = cv2.imread(str(image_path))
                if image_cv2 is not None:
                    # Convert BGR to RGB
                    image = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2RGB)
                else:
                    # Method 2: Try PIL as fallback
                    from PIL import Image as PILImage
                    pil_image = PILImage.open(str(image_path))
                    # Convert to RGB if not already
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    # Convert PIL to numpy array
                    import numpy as np
                    image = np.array(pil_image)
                    
            except Exception as load_error:
                print(f"⚠️  Could not load image {image_path.name}: {load_error}")
                failed_count += 1
                continue
                
            if image is None:
                print(f"⚠️  Failed to load {image_path.name}")
                failed_count += 1
                continue
            
            # Find face locations
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                print(f"⚠️  No faces found in {image_path.name}")
                failed_count += 1
                continue
            elif len(face_locations) > 1:
                print(f"⚠️  Multiple faces found in {image_path.name}, using the first one")
            
            # Get face encoding (use the first face if multiple found)
            face_encoding = face_recognition.face_encodings(image, face_locations)[0]
            
            # Store encoding and name
            known_encodings.append(face_encoding)
            known_names.append(name)
            processed_count += 1
            
            print(f"✅ Successfully encoded face for {name}")
            
        except Exception as e:
            print(f"❌ Error processing {image_path.name}: {str(e)}")
            failed_count += 1
        
        print()
    
    if processed_count == 0:
        print("❌ No faces were successfully processed!")
        return False
    
    # Save encodings to pickle file
    print(f"💾 Saving encodings to 'encodings.pickle'...")
    
    data = {
        "encodings": known_encodings,
        "names": known_names
    }
    
    try:
        with open("encodings.pickle", "wb") as f:
            pickle.dump(data, f)
        
        print("✅ Face encodings saved successfully!")
        print()
        print("📊 Summary:")
        print(f"   ✅ Successfully processed: {processed_count} faces")
        print(f"   ❌ Failed to process: {failed_count} images")
        print(f"   📁 Total students registered: {len(set(known_names))}")
        print()
        print("🎯 Ready for attendance! Run 'take_attendance.py' to start the system.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving encodings: {str(e)}")
        return False

def verify_encodings():
    """
    Verify that the encodings.pickle file was created and can be loaded.
    """
    try:
        with open("encodings.pickle", "rb") as f:
            data = pickle.load(f)
        
        print("🔍 Verification Results:")
        print(f"   📊 Total encodings: {len(data['encodings'])}")
        print(f"   👥 Registered students:")
        for i, name in enumerate(data['names'], 1):
            print(f"      {i}. {name}")
        print()
        
    except FileNotFoundError:
        print("❌ encodings.pickle file not found!")
    except Exception as e:
        print(f"❌ Error loading encodings: {str(e)}")

if __name__ == "__main__":
    # Encode faces
    success = encode_known_faces()
    
    if success:
        # Verify the encodings
        verify_encodings()
    
    print("🎓 Face encoding process completed!")