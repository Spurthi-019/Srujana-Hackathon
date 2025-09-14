#!/usr/bin/env python3
"""
Automated Face Capture for New Member Registration
================================================

This script automatically detects and captures faces from the camera
to register new members in the AI attendance system.

Features:
- Real-time face detection
- Automatic photo capture
- Quality validation
- Multiple photo capture for better training
- Automatic model retraining

Usage:
    python auto_add_member.py

Author: SmartClass AI
Date: September 2025
"""

import cv2
import numpy as np
import os
import time
import subprocess
import sys
from datetime import datetime

class AutoFaceCapture:
    def __init__(self):
        """Initialize the automatic face capture system."""
        print("🎓 AI Attendance System - Auto Add Member")
        print("=" * 45)
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Configuration
        self.known_faces_dir = "known_faces"
        self.min_face_size = (150, 150)  # Minimum face size for good quality
        self.capture_count = 5  # Number of photos to capture per person
        self.quality_threshold = 0.7  # Face quality threshold
        
        # Create known_faces directory if it doesn't exist
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
            
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
    def check_face_quality(self, face_img):
        """Check if the captured face is of good quality."""
        # Check if face is large enough
        if face_img.shape[0] < self.min_face_size[0] or face_img.shape[1] < self.min_face_size[1]:
            return False, "Face too small"
        
        # Check if face is not too blurry (using Laplacian variance)
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if laplacian_var < 100:  # Threshold for blur detection
            return False, "Image too blurry"
        
        # Check brightness (not too dark or too bright)
        mean_brightness = np.mean(gray)
        if mean_brightness < 50:
            return False, "Image too dark"
        elif mean_brightness > 200:
            return False, "Image too bright"
        
        return True, "Good quality"
    
    def get_member_name(self):
        """Get the name of the new member."""
        print("\n➕ Adding New Member")
        print("=" * 25)
        
        while True:
            name = input("Enter new member's name: ").strip()
            if name:
                # Convert to proper format
                clean_name = name.lower().replace(" ", "_")
                display_name = name.title()
                return clean_name, display_name
            else:
                print("❌ Please enter a valid name!")
    
    def list_current_members(self):
        """List currently registered members."""
        print("\n👥 Currently registered members:")
        print("=" * 35)
        
        members = []
        for file in os.listdir(self.known_faces_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')) and file != '.gitkeep':
                name = os.path.splitext(file)[0].replace("_", " ").title()
                members.append(name)
                print(f"   👤 {name}")
        
        if not members:
            print("   No members found!")
        
        return members
    
    def capture_faces(self, member_name, display_name):
        """Capture faces automatically from camera."""
        print(f"\n📸 Capturing photos for {display_name}")
        print("=" * 35)
        print(f"Instructions:")
        print(f"- Look directly at the camera")
        print(f"- Keep your face well-lit")
        print(f"- Stay still when capturing")
        print(f"- We'll capture {self.capture_count} photos automatically")
        print(f"- Press 'q' to quit, 'c' to capture manually")
        print(f"- Press SPACE to start auto-capture")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return False
        
        captured_photos = 0
        auto_capture_mode = False
        last_capture_time = 0
        capture_interval = 1.5  # Seconds between auto captures
        
        photos_saved = []
        
        try:
            while captured_photos < self.capture_count:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error reading from camera")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert to grayscale for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, 
                    scaleFactor=1.1, 
                    minNeighbors=5, 
                    minSize=(100, 100)
                )
                
                current_time = time.time()
                
                # Draw interface
                info_text = f"Photos captured: {captured_photos}/{self.capture_count}"
                cv2.putText(frame, info_text, (10, 30), self.font, 0.7, (0, 255, 0), 2)
                
                if auto_capture_mode:
                    mode_text = "AUTO CAPTURE MODE - Stay still!"
                    cv2.putText(frame, mode_text, (10, 60), self.font, 0.6, (0, 0, 255), 2)
                else:
                    mode_text = "Press SPACE to start auto-capture"
                    cv2.putText(frame, mode_text, (10, 60), self.font, 0.6, (255, 0, 0), 2)
                
                # Process detected faces
                for (x, y, w, h) in faces:
                    # Draw rectangle around face
                    color = (0, 255, 0) if len(faces) == 1 else (0, 0, 255)  # Green if single face, red if multiple
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Check if single face and good size
                    if len(faces) == 1 and w > 100 and h > 100:
                        # Extract face
                        face_img = frame[y:y+h, x:x+w]
                        
                        # Check quality
                        is_good, quality_msg = self.check_face_quality(face_img)
                        
                        # Display quality status
                        quality_color = (0, 255, 0) if is_good else (0, 0, 255)
                        cv2.putText(frame, quality_msg, (x, y-10), self.font, 0.5, quality_color, 2)
                        
                        # Auto capture if conditions are met
                        if (auto_capture_mode and is_good and 
                            current_time - last_capture_time > capture_interval):
                            
                            # Save the photo
                            filename = f"{member_name}_{captured_photos + 1}.jpg"
                            filepath = os.path.join(self.known_faces_dir, filename)
                            
                            # Resize face to standard size
                            face_resized = cv2.resize(face_img, (200, 200))
                            
                            if cv2.imwrite(filepath, face_resized):
                                photos_saved.append(filepath)
                                captured_photos += 1
                                last_capture_time = current_time
                                
                                print(f"✅ Captured photo {captured_photos}: {filename}")
                                
                                # Visual feedback
                                cv2.rectangle(frame, (x-5, y-5), (x+w+5, y+h+5), (0, 255, 255), 3)
                                
                                if captured_photos >= self.capture_count:
                                    break
                    
                    elif len(faces) > 1:
                        cv2.putText(frame, "Multiple faces detected!", (10, 90), self.font, 0.6, (0, 0, 255), 2)
                
                # Show frame
                cv2.imshow(f'Capturing {display_name} - Press SPACE to start, Q to quit', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("❌ Capture cancelled by user")
                    break
                elif key == ord(' '):  # Space to start/stop auto capture
                    auto_capture_mode = not auto_capture_mode
                    if auto_capture_mode:
                        print("🔄 Auto capture started!")
                    else:
                        print("⏸️  Auto capture paused")
                elif key == ord('c'):  # Manual capture
                    if len(faces) == 1:
                        x, y, w, h = faces[0]
                        face_img = frame[y:y+h, x:x+w]
                        is_good, quality_msg = self.check_face_quality(face_img)
                        
                        if is_good:
                            filename = f"{member_name}_{captured_photos + 1}.jpg"
                            filepath = os.path.join(self.known_faces_dir, filename)
                            face_resized = cv2.resize(face_img, (200, 200))
                            
                            if cv2.imwrite(filepath, face_resized):
                                photos_saved.append(filepath)
                                captured_photos += 1
                                print(f"✅ Manually captured photo {captured_photos}: {filename}")
                        else:
                            print(f"❌ Photo quality too low: {quality_msg}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        return captured_photos > 0, photos_saved
    
    def create_primary_photo(self, member_name, photos_saved):
        """Create the primary photo for the member (used by the system)."""
        if not photos_saved:
            return False
        
        # Use the first captured photo as the primary one
        primary_source = photos_saved[0]
        primary_target = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        
        # Copy the first photo as the primary one
        import shutil
        shutil.copy2(primary_source, primary_target)
        
        print(f"✅ Primary photo created: {primary_target}")
        return True
    
    def retrain_model(self):
        """Retrain the face recognition model."""
        print("\n** Retraining face recognition model...")
        print("=" * 40)
        
        try:
            result = subprocess.run([sys.executable, "simple_face_encoder.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("** Model training completed successfully!")
                print("\nTraining output:")
                print(result.stdout)
                return True
            else:
                print("** Model training failed!")
                print("Error output:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"** Error running encoder: {e}")
            return False
    
    def cleanup_temp_photos(self, member_name, photos_saved):
        """Clean up temporary photos, keep only the primary one."""
        print(f"\n🧹 Cleaning up temporary photos...")
        
        primary_photo = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        
        for photo in photos_saved:
            if photo != primary_photo and os.path.exists(photo):
                try:
                    os.remove(photo)
                    print(f"🗑️  Removed: {os.path.basename(photo)}")
                except Exception as e:
                    print(f"❌ Error removing {photo}: {e}")
    
    def test_system(self):
        """Offer to test the system."""
        print("\n🎯 System Update Complete!")
        print("=" * 30)
        
        while True:
            test = input("Would you like to test the attendance system now? (y/n): ").lower()
            
            if test in ['y', 'yes']:
                print("\n🚀 Starting attendance system...")
                print("Press 'q' in the camera window to quit when done testing.")
                
                try:
                    subprocess.run([sys.executable, "opencv_attendance.py"])
                except KeyboardInterrupt:
                    print("\n✅ System test completed!")
                break
                
            elif test in ['n', 'no']:
                print("\n✅ You can test the system later by running:")
                print("   python opencv_attendance.py")
                break
            else:
                print("Please enter 'y' or 'n'")
    
    def run(self):
        """Run the automated member addition process."""
        # List current members
        current_members = self.list_current_members()
        
        # Get new member info
        member_name, display_name = self.get_member_name()
        
        # Check if member already exists
        existing_file = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        if os.path.exists(existing_file):
            print(f"⚠️  Member '{display_name}' already exists!")
            overwrite = input("Do you want to replace with new photos? (y/n): ").lower()
            if overwrite not in ['y', 'yes']:
                print("Operation cancelled.")
                return
        
        # Capture faces
        success, photos_saved = self.capture_faces(member_name, display_name)
        
        if not success or not photos_saved:
            print("❌ No photos were captured. Operation cancelled.")
            return
        
        # Create primary photo
        if not self.create_primary_photo(member_name, photos_saved):
            print("❌ Failed to create primary photo.")
            return
        
        # Clean up temporary photos
        self.cleanup_temp_photos(member_name, photos_saved)
        
        # Retrain model
        if not self.retrain_model():
            print("❌ Failed to retrain model. Please run 'python opencv_face_encoder.py' manually.")
            return
        
        # Test system
        self.test_system()
        
        print(f"\n🎉 Successfully added '{display_name}' to the attendance system!")
        print(f"📊 Total photos captured and processed: {len(photos_saved)}")

if __name__ == "__main__":
    try:
        capture_system = AutoFaceCapture()
        capture_system.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please make sure your camera is working and try again.")