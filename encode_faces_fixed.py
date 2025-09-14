#!/usr/bin/env python3
"""
Fixed Face Encoding Script with dlib compatibility
=================================================
"""

import face_recognition
import os
import pickle
import cv2
import numpy as np
from pathlib import Path
from PIL import Image as PILImage

def encode_known_faces():
    """Process all images and create face encodings with compatibility fixes."""
    print("🎓 SmartClass AI - Face Encoding System (Fixed)")
    print("=" * 55)
    
    known_faces_dir = "known_faces"
    
    if not os.path.exists(known_faces_dir):
        print(f"❌ Error: '{known_faces_dir}' directory not found!")
        return False
    
    known_encodings = []
    known_names = []
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(Path(known_faces_dir).glob(f"*{ext}"))
        image_files.extend(Path(known_faces_dir).glob(f"*{ext.upper()}"))
    
    # Filter out .gitkeep
    image_files = [f for f in image_files if f.name != '.gitkeep']
    
    if not image_files:
        print(f"❌ No image files found!")
        return False
    
    print(f"📸 Found {len(image_files)} image files to process...")
    print()
    
    processed_count = 0
    failed_count = 0
    
    for image_path in image_files:
        try:
            name = image_path.stem.replace('_', ' ').title()
            print(f"🔍 Processing: {image_path.name} -> {name}")
            
            # Load and ensure proper format for dlib
            img = cv2.imread(str(image_path))
            if img is None:
                print(f"⚠️  Could not load {image_path.name}")
                failed_count += 1
                continue
            
            # Ensure image is in the right format for dlib
            # Convert to RGB and ensure it's contiguous and uint8
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Ensure the array is contiguous and proper type
            if not img_rgb.flags['C_CONTIGUOUS']:
                img_rgb = np.ascontiguousarray(img_rgb)
            
            # Ensure uint8 type
            if img_rgb.dtype != np.uint8:
                img_rgb = img_rgb.astype(np.uint8)
            
            # Resize if too large (dlib works better with smaller images)
            height, width = img_rgb.shape[:2]
            if width > 800 or height > 800:
                scale = 800 / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                img_rgb = cv2.resize(img_rgb, (new_width, new_height))
                print(f"   📏 Resized from {width}x{height} to {new_width}x{new_height}")
            
            print(f"   🖼️  Image shape: {img_rgb.shape}, dtype: {img_rgb.dtype}")
            
            # Find face locations
            face_locations = face_recognition.face_locations(img_rgb, model="hog")
            
            if len(face_locations) == 0:
                print(f"⚠️  No faces found in {image_path.name}")
                failed_count += 1
                continue
            elif len(face_locations) > 1:
                print(f"⚠️  Multiple faces found, using the largest one")
                # Find the largest face
                face_areas = [(bottom - top) * (right - left) for top, right, bottom, left in face_locations]
                largest_face_idx = np.argmax(face_areas)
                face_locations = [face_locations[largest_face_idx]]
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(img_rgb, face_locations, model="small")
            
            if len(face_encodings) == 0:
                print(f"⚠️  Could not encode face in {image_path.name}")
                failed_count += 1
                continue
            
            # Store encoding and name
            known_encodings.append(face_encodings[0])
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
    
    # Save encodings
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
        print("🎯 Ready for attendance! Run 'python test_offline.py' to test.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving encodings: {str(e)}")
        return False

if __name__ == "__main__":
    encode_known_faces()