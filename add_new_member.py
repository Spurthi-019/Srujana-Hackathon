#!/usr/bin/env python3
"""
Add New Member Helper Script
===========================

This script helps you add new members to the AI attendance system.
It will guide you through the process and automatically retrain the model.

Usage:
    python add_new_member.py

Author: SmartClass AI
Date: September 2025
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class NewMemberHelper:
    def __init__(self):
        self.known_faces_dir = "known_faces"
        self.encoder_script = "opencv_face_encoder.py"
        self.attendance_script = "opencv_attendance.py"
        
    def check_setup(self):
        """Check if the required directories and files exist."""
        print("🔍 Checking system setup...")
        
        if not os.path.exists(self.known_faces_dir):
            print(f"❌ Directory '{self.known_faces_dir}' not found!")
            return False
            
        if not os.path.exists(self.encoder_script):
            print(f"❌ Script '{self.encoder_script}' not found!")
            return False
            
        print("✅ System setup looks good!")
        return True
    
    def list_current_members(self):
        """List currently registered members."""
        print("\n👥 Currently registered members:")
        print("=" * 35)
        
        members = []
        for file in os.listdir(self.known_faces_dir):
            if file.lower().endswith(('.jpg', '.jpeg', '.png')) and file != '.gitkeep':
                name = os.path.splitext(file)[0].title()
                members.append(name)
                print(f"   👤 {name}")
        
        if not members:
            print("   No members found!")
        
        return members
    
    def get_new_member_info(self):
        """Get information about the new member."""
        print("\n➕ Adding New Member")
        print("=" * 25)
        
        while True:
            name = input("Enter new member's name: ").strip()
            if name:
                # Convert to proper format (lowercase for filename)
                filename = name.lower().replace(" ", "_") + ".jpg"
                display_name = name.title()
                return filename, display_name
            else:
                print("❌ Please enter a valid name!")
    
    def add_photo_instructions(self, filename):
        """Provide instructions for adding the photo."""
        photo_path = os.path.join(self.known_faces_dir, filename)
        
        print(f"\n📸 Photo Instructions:")
        print("=" * 25)
        print(f"1. Take a clear, front-facing photo of the new member")
        print(f"2. Save it as: {photo_path}")
        print(f"3. Photo requirements:")
        print(f"   - Clear, well-lit image")
        print(f"   - Front-facing (not profile)")
        print(f"   - Only one person in the photo")
        print(f"   - JPG format preferred")
        
        input("\nPress Enter when you've added the photo...")
        
        return photo_path
    
    def verify_photo(self, photo_path):
        """Verify that the photo has been added."""
        if os.path.exists(photo_path):
            print(f"✅ Photo found: {photo_path}")
            return True
        else:
            print(f"❌ Photo not found: {photo_path}")
            print("Please add the photo and try again.")
            return False
    
    def retrain_model(self):
        """Retrain the face recognition model."""
        print("\n🧠 Retraining face recognition model...")
        print("=" * 40)
        
        try:
            result = subprocess.run([sys.executable, self.encoder_script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Model training completed successfully!")
                print("\nTraining output:")
                print(result.stdout)
                return True
            else:
                print("❌ Model training failed!")
                print("Error output:")
                print(result.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error running encoder: {e}")
            return False
    
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
                    subprocess.run([sys.executable, self.attendance_script])
                except KeyboardInterrupt:
                    print("\n✅ System test completed!")
                break
                
            elif test in ['n', 'no']:
                print("\n✅ You can test the system later by running:")
                print(f"   python {self.attendance_script}")
                break
            else:
                print("Please enter 'y' or 'n'")
    
    def run(self):
        """Run the new member addition process."""
        print("🎓 AI Attendance System - Add New Member")
        print("=" * 45)
        
        # Check system setup
        if not self.check_setup():
            return
        
        # List current members
        current_members = self.list_current_members()
        
        # Get new member info
        filename, display_name = self.get_new_member_info()
        
        # Check if member already exists
        if display_name.lower() in [m.lower() for m in current_members]:
            print(f"⚠️  Member '{display_name}' already exists!")
            overwrite = input("Do you want to replace the existing photo? (y/n): ")
            if overwrite.lower() not in ['y', 'yes']:
                print("Operation cancelled.")
                return
        
        # Photo instructions
        photo_path = self.add_photo_instructions(filename)
        
        # Verify photo
        if not self.verify_photo(photo_path):
            return
        
        # Retrain model
        if not self.retrain_model():
            return
        
        # Test system
        self.test_system()
        
        print(f"\n🎉 Successfully added '{display_name}' to the attendance system!")

if __name__ == "__main__":
    helper = NewMemberHelper()
    helper.run()