#!/usr/bin/env python3
"""
Initialize face names pickle file
"""
import pickle
import os

# Create a simple face names mapping
face_id_to_name = {
    0: "Student_1",
    1: "Student_2", 
    2: "Student_3"
}

# Save to pickle file
with open("face_names.pickle", "wb") as f:
    pickle.dump(face_id_to_name, f)

print("✅ Created face_names.pickle file")