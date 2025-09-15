from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import motor.motor_asyncio
from bson import ObjectId
import uvicorn
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import json

# Load environment variables
load_dotenv()

# Configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'college_app')
PORT = int(os.getenv('PORT', 5001))

# Create FastAPI app
app = FastAPI(title="ClassTrack API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://classtrack-1nmce8d4g-kumar-ankit369s-projects.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client
client = None
db = None

@app.on_event("startup")
async def startup_event():
    global client, db
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    global client
    if client:
        client.close()
        print("✅ MongoDB connection closed")

# Pydantic models
class Student(BaseModel):
    name: str
    email: str
    student_id: str
    class_code: Optional[str] = None

class Faculty(BaseModel):
    name: str
    email: str
    employee_id: str
    department: str

class ClassRoom(BaseModel):
    name: str
    code: str
    teacher_id: str
    students: List[str] = []

# API Routes
@app.get("/")
async def root():
    return {"message": "ClassTrack API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    try:
        # Test database connection
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected", "message": "All systems operational"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# Student endpoints
@app.get("/api/students")
async def get_students():
    try:
        students = []
        async for student in db.students.find():
            student["_id"] = str(student["_id"])
            students.append(student)
        return {"students": students, "count": len(students)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/students")
async def create_student(student: Student):
    try:
        student_dict = student.dict()
        result = await db.students.insert_one(student_dict)
        student_dict["_id"] = str(result.inserted_id)
        return {"message": "Student created successfully", "student": student_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Faculty endpoints
@app.get("/api/faculty")
async def get_faculty():
    try:
        faculty = []
        async for member in db.faculty.find():
            member["_id"] = str(member["_id"])
            faculty.append(member)
        return {"faculty": faculty, "count": len(faculty)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/faculty")
async def create_faculty(faculty: Faculty):
    try:
        faculty_dict = faculty.dict()
        result = await db.faculty.insert_one(faculty_dict)
        faculty_dict["_id"] = str(result.inserted_id)
        return {"message": "Faculty created successfully", "faculty": faculty_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Class endpoints
@app.get("/api/classes")
async def get_classes():
    try:
        classes = []
        async for classroom in db.classes.find():
            classroom["_id"] = str(classroom["_id"])
            classes.append(classroom)
        return {"classes": classes, "count": len(classes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/classes")
async def create_class(classroom: ClassRoom):
    try:
        class_dict = classroom.dict()
        result = await db.classes.insert_one(class_dict)
        class_dict["_id"] = str(result.inserted_id)
        return {"message": "Class created successfully", "class": class_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Teacher Dashboard endpoint
@app.get("/api/teacher/dashboard/{teacher_id}")
async def get_teacher_dashboard(teacher_id: str):
    try:
        # Get teacher info
        teacher = await db.faculty.find_one({"employee_id": teacher_id}) or await db.faculty.find_one({"_id": teacher_id})
        
        # Get teacher's classes
        classes = []
        async for classroom in db.classes.find({"teacher_id": teacher_id}):
            classroom["_id"] = str(classroom["_id"])
            classroom["is_active"] = True  # Default for now
            classes.append(classroom)
        
        return {
            "teacher": teacher,
            "my_classes": classes,
            "total_classes": len(classes),
            "active_classes": len([c for c in classes if c.get("is_active", True)])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Student Dashboard endpoint  
@app.get("/api/student/dashboard/{student_id}")
async def get_student_dashboard(student_id: str):
    try:
        # Get student info
        student = await db.students.find_one({"student_id": student_id}) or await db.students.find_one({"_id": student_id})
        
        # Get student's classes
        classes = []
        if student and student.get("class_code"):
            async for classroom in db.classes.find({"code": student["class_code"]}):
                classroom["_id"] = str(classroom["_id"])
                classes.append(classroom)
        
        return {
            "student": student,
            "enrolled_classes": classes,
            "total_classes": len(classes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting ClassTrack Backend Server...")
    print(f"📡 Server will be available at: http://localhost:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, reload=False)