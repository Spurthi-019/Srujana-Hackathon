# Quick Setup Instructions
# ========================

# STEP 1: Add Face Images
# -----------------------
# 1. Find or take clear face photos of people you want to recognize
# 2. Name them: firstname_lastname.jpg (e.g., john_doe.jpg, jane_smith.png)
# 3. Place them in the known_faces/ directory
# 4. Requirements: Clear, front-facing, good lighting, one person per image

# STEP 2: Generate Face Encodings
# --------------------------------
# Run: python encode_faces.py

# STEP 3: Test System (Offline Mode)
# -----------------------------------
# Run: python test_offline.py
# This tests face recognition without needing MongoDB

# STEP 4: Set Up MongoDB (After testing works)
# ---------------------------------------------
# Option A: Docker (Easiest)
#   1. Install Docker Desktop
#   2. Run: docker run -d -p 27017:27017 --name mongodb mongo:latest

# Option B: Download MongoDB Community Server
#   1. Download from: https://www.mongodb.com/try/download/community
#   2. Install and start MongoDB service

# Option C: Use MongoDB Atlas (Cloud)
#   1. Go to: https://www.mongodb.com/atlas
#   2. Create free cluster
#   3. Update mongodb_config.json with Atlas connection string

# STEP 5: Run Full System (With MongoDB)
# ---------------------------------------
# Run: python take_attendance.py

# Current Status:
# ✅ Python environment ready (smartclass-ai)
# ✅ Dependencies installed (pymongo, face_recognition, opencv)
# ⏳ Need to add face images to known_faces/
# ⏳ Need to set up MongoDB