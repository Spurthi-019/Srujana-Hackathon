# MongoDB Setup Guide for SmartClass AI Attendance System
# ======================================================

# Option 1: Docker MongoDB (Easiest)
# ----------------------------------
# 1. Install Docker Desktop: https://www.docker.com/products/docker-desktop
# 2. Run this command:
#    docker run -d -p 27017:27017 --name mongodb mongo:latest
# 3. Your config is already correct: mongodb://localhost:27017/

# Option 2: MongoDB Community Server
# ----------------------------------
# 1. Download: https://www.mongodb.com/try/download/community
# 2. Install MongoDB Community Server
# 3. Start MongoDB service:
#    Windows: net start MongoDB
#    Or use MongoDB Compass to start
# 4. Your config is already correct: mongodb://localhost:27017/

# Option 3: MongoDB Atlas (Cloud)
# -------------------------------
# 1. Go to: https://www.mongodb.com/atlas
# 2. Create free account and cluster
# 3. Get connection string like: mongodb+srv://username:password@cluster.mongodb.net/
# 4. Update mongodb_config.json with your Atlas connection string

# Current Configuration (Ready for local MongoDB):
# {
#   "connection_string": "mongodb://localhost:27017/",
#   "database_name": "smartclass_attendance"
# }