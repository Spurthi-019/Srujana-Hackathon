# Attendance System Test - Create sample face images
import os
import cv2
import numpy as np

# Create known_faces directory
os.makedirs("known_faces", exist_ok=True)

# Create sample placeholder images for testing
print("📸 Creating sample face images for testing...")

for i in range(3):
    # Create a simple colored rectangle as placeholder
    img = np.zeros((150, 150, 3), dtype=np.uint8)
    color = [(255, 100, 100), (100, 255, 100), (100, 100, 255)][i]
    img[:] = color
    
    # Add some text
    cv2.putText(img, f"Student_{i+1}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Save image
    filename = f"known_faces/Student_{i+1}.jpg"
    cv2.imwrite(filename, img)
    print(f"Created: {filename}")

print("✅ Sample face images created for testing")