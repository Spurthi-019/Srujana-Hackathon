#!/usr/bin/env python3
"""
Debug Face Recognition Issues
============================
"""

import cv2
import numpy as np
from PIL import Image as PILImage
import face_recognition
from pathlib import Path

def debug_images():
    """Debug image loading and face recognition issues."""
    print("🔍 Debugging Face Recognition Issues")
    print("=" * 40)
    
    known_faces_dir = "known_faces"
    image_files = list(Path(known_faces_dir).glob("*.jpg")) + list(Path(known_faces_dir).glob("*.png"))
    
    for image_path in image_files:
        if image_path.name == '.gitkeep':
            continue
            
        print(f"\n📸 Testing: {image_path.name}")
        
        # Test 1: Basic file info
        file_size = image_path.stat().st_size
        print(f"   File size: {file_size} bytes")
        
        # Test 2: OpenCV loading
        try:
            img_cv2 = cv2.imread(str(image_path))
            if img_cv2 is not None:
                print(f"   ✅ OpenCV loaded: {img_cv2.shape}")
                # Convert to RGB
                img_rgb = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
                print(f"   ✅ RGB conversion: {img_rgb.shape}")
            else:
                print("   ❌ OpenCV failed to load")
                continue
        except Exception as e:
            print(f"   ❌ OpenCV error: {e}")
            continue
        
        # Test 3: PIL loading
        try:
            pil_img = PILImage.open(str(image_path))
            print(f"   ✅ PIL loaded: {pil_img.size}, mode: {pil_img.mode}")
            
            # Convert to RGB if needed
            if pil_img.mode != 'RGB':
                pil_img = pil_img.convert('RGB')
                print(f"   ✅ PIL converted to RGB")
            
            # Convert to numpy
            np_img = np.array(pil_img)
            print(f"   ✅ NumPy array: {np_img.shape}, dtype: {np_img.dtype}")
            
        except Exception as e:
            print(f"   ❌ PIL error: {e}")
            continue
        
        # Test 4: Face detection
        try:
            face_locations = face_recognition.face_locations(img_rgb)
            print(f"   👤 Faces found: {len(face_locations)}")
            
            if len(face_locations) > 0:
                # Test face encoding
                face_encodings = face_recognition.face_encodings(img_rgb, face_locations)
                print(f"   🧠 Face encodings: {len(face_encodings)}")
                if len(face_encodings) > 0:
                    print(f"   ✅ Face encoding successful!")
                else:
                    print(f"   ❌ Face encoding failed")
            else:
                print(f"   ⚠️  No faces detected in image")
                
        except Exception as e:
            print(f"   ❌ Face recognition error: {e}")
            print(f"   💡 This might be a dlib/face_recognition compatibility issue")

if __name__ == "__main__":
    debug_images()