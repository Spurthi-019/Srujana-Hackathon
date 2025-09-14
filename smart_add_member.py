#!/usr/bin/env python3
"""
Smart Face Registration System
=============================

Advanced automatic face capture system with:
- Real-time face quality assessment
- Smart auto-capture with quality validation
- Multiple angle capture for better training
- Live feedback and guidance
- Automatic model training

Usage:
    python smart_add_member.py

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
import json

class SmartFaceRegistration:
    def __init__(self):
        """Initialize the smart face registration system."""
        print("🤖 Smart Face Registration System")
        print("=" * 40)
        
        # Initialize face detector
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Configuration
        self.known_faces_dir = "known_faces"
        self.min_face_size = (120, 120)
        self.target_captures = 3  # Reduced for better user experience
        self.quality_threshold = 100  # Laplacian variance threshold
        self.brightness_range = (60, 180)  # Good brightness range
        
        # Create directories
        if not os.path.exists(self.known_faces_dir):
            os.makedirs(self.known_faces_dir)
        
        # UI settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Face quality scoring
        self.quality_weights = {
            'size': 0.3,
            'sharpness': 0.4,
            'brightness': 0.2,
            'position': 0.1
        }
    
    def analyze_face_quality(self, face_img, face_rect, frame_shape):
        """Comprehensive face quality analysis."""
        x, y, w, h = face_rect
        frame_h, frame_w = frame_shape[:2]
        
        scores = {}
        feedback = []
        
        # 1. Size Score (0-100)
        min_size = min(self.min_face_size)
        face_size = min(w, h)
        scores['size'] = min(100, (face_size / min_size) * 50)
        
        if face_size < min_size:
            feedback.append("Move closer to camera")
        elif face_size > 300:
            feedback.append("Move back a bit")
        
        # 2. Sharpness Score (0-100)
        gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY) if len(face_img.shape) == 3 else face_img
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        scores['sharpness'] = min(100, laplacian_var / 2)
        
        if laplacian_var < self.quality_threshold:
            feedback.append("Keep still - image blurry")
        
        # 3. Brightness Score (0-100)
        mean_brightness = np.mean(gray)
        if self.brightness_range[0] <= mean_brightness <= self.brightness_range[1]:
            scores['brightness'] = 100
        else:
            distance = min(abs(mean_brightness - self.brightness_range[0]), 
                          abs(mean_brightness - self.brightness_range[1]))
            scores['brightness'] = max(0, 100 - distance * 2)
        
        if mean_brightness < self.brightness_range[0]:
            feedback.append("Need more light")
        elif mean_brightness > self.brightness_range[1]:
            feedback.append("Too bright - reduce light")
        
        # 4. Position Score (0-100)
        center_x, center_y = x + w//2, y + h//2
        frame_center_x, frame_center_y = frame_w//2, frame_h//2
        
        distance_from_center = np.sqrt((center_x - frame_center_x)**2 + (center_y - frame_center_y)**2)
        max_distance = np.sqrt(frame_center_x**2 + frame_center_y**2)
        scores['position'] = max(0, 100 - (distance_from_center / max_distance) * 100)
        
        if distance_from_center > max_distance * 0.3:
            feedback.append("Center your face")
        
        # Calculate overall score
        overall_score = sum(scores[key] * self.quality_weights[key] for key in scores)
        
        return overall_score, scores, feedback
    
    def draw_quality_interface(self, frame, face_rect, overall_score, feedback, captured_count):
        """Draw quality assessment interface on frame."""
        x, y, w, h = face_rect
        
        # Face rectangle color based on quality
        if overall_score >= 80:
            color = (0, 255, 0)  # Green - excellent
            status = "EXCELLENT"
        elif overall_score >= 60:
            color = (0, 255, 255)  # Yellow - good
            status = "GOOD"
        elif overall_score >= 40:
            color = (0, 165, 255)  # Orange - fair
            status = "FAIR"
        else:
            color = (0, 0, 255)  # Red - poor
            status = "POOR"
        
        # Draw face rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Quality score
        score_text = f"Quality: {overall_score:.0f}% - {status}"
        cv2.putText(frame, score_text, (x, y-40), self.font, 0.6, color, 2)
        
        # Progress bar for quality
        bar_w = w
        bar_h = 8
        bar_x = x
        bar_y = y - 25
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1)
        # Quality bar
        fill_w = int(bar_w * (overall_score / 100))
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), color, -1)
        
        # Feedback text
        for i, msg in enumerate(feedback[:2]):  # Show max 2 feedback messages
            cv2.putText(frame, msg, (10, 100 + i*25), self.font, 0.5, (0, 0, 255), 1)
        
        # Capture progress
        progress_text = f"Photos: {captured_count}/{self.target_captures}"
        cv2.putText(frame, progress_text, (10, 30), self.font, 0.7, (255, 255, 255), 2)
        
        return overall_score >= 70  # Ready to capture threshold
    
    def smart_capture_session(self, member_name, display_name):
        """Smart face capture session with real-time quality feedback."""
        print(f"\n📸 Smart capture session for {display_name}")
        print("=" * 40)
        print("Instructions:")
        print("• Look directly at the camera")
        print("• Keep your face centered in the frame")
        print("• Ensure good lighting")
        print("• Stay still when quality is high")
        print("• System will auto-capture when quality is good")
        print("\nControls:")
        print("• SPACEBAR: Manual capture")
        print("• Q: Quit")
        print("• A: Toggle auto-capture mode")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return False, []
        
        captured_photos = []
        auto_mode = True
        last_capture_time = 0
        capture_interval = 2.0  # Seconds between auto captures
        
        # Quality history for stability
        quality_history = []
        quality_history_size = 5
        
        try:
            while len(captured_photos) < self.target_captures:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
                )
                
                current_time = time.time()
                
                # Header info
                mode_text = "AUTO MODE" if auto_mode else "MANUAL MODE"
                mode_color = (0, 255, 0) if auto_mode else (0, 255, 255)
                cv2.putText(frame, mode_text, (10, 60), self.font, 0.6, mode_color, 2)
                
                if len(faces) == 1:
                    face_rect = faces[0]
                    x, y, w, h = face_rect
                    face_img = frame[y:y+h, x:x+w]
                    
                    # Analyze quality
                    overall_score, scores, feedback = self.analyze_face_quality(
                        face_img, face_rect, frame.shape
                    )
                    
                    # Update quality history
                    quality_history.append(overall_score)
                    if len(quality_history) > quality_history_size:
                        quality_history.pop(0)
                    
                    # Check if stable high quality
                    stable_quality = (len(quality_history) == quality_history_size and 
                                    all(q >= 70 for q in quality_history))
                    
                    # Draw interface
                    ready_to_capture = self.draw_quality_interface(
                        frame, face_rect, overall_score, feedback, len(captured_photos)
                    )
                    
                    # Auto capture logic
                    if (auto_mode and stable_quality and 
                        current_time - last_capture_time > capture_interval):
                        
                        # Capture photo
                        filename = f"{member_name}_{len(captured_photos) + 1}.jpg"
                        filepath = os.path.join(self.known_faces_dir, filename)
                        
                        # Resize and save
                        face_resized = cv2.resize(face_img, (200, 200))
                        
                        if cv2.imwrite(filepath, face_resized):
                            captured_photos.append(filepath)
                            last_capture_time = current_time
                            quality_history.clear()  # Reset for next capture
                            
                            print(f"✅ Auto-captured photo {len(captured_photos)}: {filename} (Quality: {overall_score:.0f}%)")
                            
                            # Visual feedback
                            cv2.rectangle(frame, (x-10, y-10), (x+w+10, y+h+10), (0, 255, 255), 5)
                
                elif len(faces) > 1:
                    cv2.putText(frame, "Multiple faces detected!", (10, 90), self.font, 0.6, (0, 0, 255), 2)
                    cv2.putText(frame, "Please ensure only one person is visible", (10, 115), self.font, 0.5, (0, 0, 255), 1)
                    quality_history.clear()
                
                else:
                    cv2.putText(frame, "No face detected", (10, 90), self.font, 0.6, (0, 0, 255), 2)
                    quality_history.clear()
                
                # Show completion status
                if len(captured_photos) >= self.target_captures:
                    cv2.putText(frame, "CAPTURE COMPLETE!", (10, 140), self.font, 0.8, (0, 255, 0), 2)
                
                # Display frame
                window_name = f'Smart Registration: {display_name} - Press Q to quit'
                cv2.imshow(window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("❌ Capture cancelled by user")
                    break
                elif key == ord('a'):
                    auto_mode = not auto_mode
                    print(f"🔄 Mode: {'Auto' if auto_mode else 'Manual'}")
                elif key == ord(' ') and len(faces) == 1:  # Manual capture
                    if overall_score >= 50:  # Lower threshold for manual
                        face_rect = faces[0]
                        x, y, w, h = face_rect
                        face_img = frame[y:y+h, x:x+w]
                        
                        filename = f"{member_name}_{len(captured_photos) + 1}.jpg"
                        filepath = os.path.join(self.known_faces_dir, filename)
                        face_resized = cv2.resize(face_img, (200, 200))
                        
                        if cv2.imwrite(filepath, face_resized):
                            captured_photos.append(filepath)
                            print(f"✅ Manual capture {len(captured_photos)}: {filename} (Quality: {overall_score:.0f}%)")
                    else:
                        print(f"❌ Quality too low for capture: {overall_score:.0f}%")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        return len(captured_photos) > 0, captured_photos
    
    def create_primary_photo(self, member_name, photos):
        """Create primary photo for the recognition system."""
        if not photos:
            return False
        
        # Use the first photo as primary
        primary_source = photos[0]
        primary_target = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        
        import shutil
        shutil.copy2(primary_source, primary_target)
        print(f"✅ Primary photo created: {member_name}.jpg")
        return True
    
    def retrain_system(self):
        """Retrain the face recognition system."""
        print("\n** Retraining recognition system...")
        print("=" * 35)
        
        try:
            result = subprocess.run([sys.executable, "simple_face_encoder.py"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("** Training successful!")
                print(result.stdout)
                return True
            else:
                print("** Training failed!")
                print(result.stderr)
                return False
        except Exception as e:
            print(f"** Training error: {e}")
            return False
    
    def cleanup_temp_files(self, member_name, temp_photos):
        """Clean up temporary photos."""
        primary_photo = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        
        for photo in temp_photos:
            if photo != primary_photo and os.path.exists(photo):
                try:
                    os.remove(photo)
                except Exception as e:
                    print(f"Warning: Could not remove {photo}: {e}")
    
    def run(self):
        """Run the smart face registration process."""
        print("Starting smart face registration...")
        
        # Get member name
        while True:
            name = input("\nEnter new member's name: ").strip()
            if name:
                member_name = name.lower().replace(" ", "_")
                display_name = name.title()
                break
            print("Please enter a valid name!")
        
        # Check if already exists
        existing_file = os.path.join(self.known_faces_dir, f"{member_name}.jpg")
        if os.path.exists(existing_file):
            print(f"⚠️  Member '{display_name}' already exists!")
            if input("Replace existing registration? (y/n): ").lower() not in ['y', 'yes']:
                return
        
        # Start capture session
        success, photos = self.smart_capture_session(member_name, display_name)
        
        if not success or not photos:
            print("❌ Registration cancelled - no photos captured")
            return
        
        # Create primary photo
        if not self.create_primary_photo(member_name, photos):
            print("❌ Failed to create primary photo")
            return
        
        # Clean up temporary files
        self.cleanup_temp_files(member_name, photos)
        
        # Retrain system
        if self.retrain_system():
            print(f"\n🎉 Successfully registered '{display_name}'!")
            print(f"📊 Photos captured: {len(photos)}")
            
            # Offer to test
            if input("\nTest the system now? (y/n): ").lower() in ['y', 'yes']:
                try:
                    subprocess.run([sys.executable, "opencv_attendance.py"])
                except KeyboardInterrupt:
                    pass
        else:
            print("❌ Registration completed but training failed")
            print("Please run 'python opencv_face_encoder.py' manually")

if __name__ == "__main__":
    try:
        system = SmartFaceRegistration()
        system.run()
    except KeyboardInterrupt:
        print("\n\n⏹️  Registration cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")