import random
import requests
import cv2
import numpy as np
import os
import time
import json
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, status, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import motor.motor_asyncio
from bson import ObjectId
from model import SpeechModel
import uvicorn
from contextlib import asynccontextmanager
import google.generativeai as genai
from dotenv import load_dotenv
from cache_manager import cache_manager, cached_query

# Load environment variables
load_dotenv()

# Configuration from environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'college_app')
PORT = int(os.getenv('PORT', 5001))
HOST = os.getenv('HOST', '0.0.0.0')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# CORS origins from environment
CORS_ORIGINS_STR = os.getenv('CORS_ORIGINS', '["http://localhost:3000"]')
try:
    import ast
    CORS_ORIGINS = ast.literal_eval(CORS_ORIGINS_STR)
except:
    CORS_ORIGINS = ["http://localhost:3000", "https://classtrack-p2msj4dip-kumar-ankit369s-projects.vercel.app"]

# Google Gemini AI Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# Import attendance system components
try:
    import base64
    from io import BytesIO
    from PIL import Image
except ImportError:
    print("⚠️ Some optional dependencies not available. Attendance features may be limited.")

# MongoDB Connection with connection pooling optimization
client = motor.motor_asyncio.AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=50,  # Increase connection pool size
    minPoolSize=10,
    maxIdleTimeMS=30000,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000
)
db = client[DATABASE_NAME]

# Initialize speech model for RAG functionality
try:
    speech_model = SpeechModel()
    print("✅ Speech model initialized for RAG functionality")
except Exception as e:
    print(f"⚠️ Speech model initialization failed: {e}")
    speech_model = None
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print("✅ Google Gemini AI configured successfully")
else:
    print("⚠️ GOOGLE_API_KEY not found. AI features may be limited.")

# Initialize RAG and AI services
class RAGService:
    """Retrieval-Augmented Generation Service for educational content"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash') if GOOGLE_API_KEY else None
        self.knowledge_base = []
        
    async def add_document(self, document: str, metadata: dict = None):
        """Add document to knowledge base"""
        doc_entry = {
            "content": document,
            "metadata": metadata or {},
            "timestamp": datetime.now(),
            "id": ObjectId()
        }
        self.knowledge_base.append(doc_entry)
        
        # Store in MongoDB for persistence
        await db.knowledge_base.insert_one(doc_entry)
        return str(doc_entry["id"])
        
    async def query_knowledge(self, query: str) -> str:
        """Query knowledge base with RAG"""
        if not self.model:
            return "AI service not available"
            
        # Simple semantic search (can be enhanced with embeddings)
        relevant_docs = []
        for doc in self.knowledge_base:
            if any(term.lower() in doc["content"].lower() for term in query.split()):
                relevant_docs.append(doc["content"])
        
        # Get from MongoDB if local cache is empty
        if not relevant_docs:
            cursor = db.knowledge_base.find({
                "$text": {"$search": query}
            }).limit(5)
            async for doc in cursor:
                relevant_docs.append(doc["content"])
        
        context = "\n".join(relevant_docs[:3])  # Use top 3 relevant docs
        
        prompt = f"""
        Based on the following context, answer the question:
        
        Context: {context}
        Question: {query}
        
        Provide a comprehensive educational answer.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Initialize services
rag_service = RAGService()

class AttendanceSystem:
    """Simple AI Attendance System Integration"""
    
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_faces_dir = "known_faces"
        self.model_file = "opencv_face_model.yml"
        self.face_names_file = "face_names.pickle"
        self.face_id_to_name = {}
        self.attendance_cooldown = 30  # seconds
        self.last_attendance = defaultdict(float)
        
        # Load model if exists
        self.load_face_model()
        
    def load_face_model(self):
        """Load trained face recognition model"""
        try:
            if os.path.exists(self.model_file) and os.path.exists(self.face_names_file):
                self.face_recognizer.read(self.model_file)
                import pickle
                with open(self.face_names_file, 'rb') as f:
                    self.face_id_to_name = pickle.load(f)
                print(f"✅ Loaded face model with {len(self.face_id_to_name)} known faces")
                return True
        except Exception as e:
            print(f"⚠️ Could not load face model: {e}")
        return False
        
    def detect_faces(self, frame):
        """Detect and recognize faces in frame"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        detected_people = []
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            if hasattr(self.face_recognizer, 'predict'):
                try:
                    label, confidence = self.face_recognizer.predict(face_roi)
                    if confidence < 100 and label in self.face_id_to_name:
                        name = self.face_id_to_name[label]
                        detected_people.append({
                            'name': name,
                            'confidence': confidence,
                            'bbox': [x, y, w, h]
                        })
                except Exception as e:
                    print(f"Recognition error: {e}")
        
        return detected_people

# Initialize attendance system
attendance_system = AttendanceSystem()

class ChatbotService:
    """Enhanced Educational Chatbot Service with RAG integration"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash') if GOOGLE_API_KEY else None
        
    async def generate_response(self, question: str, context: str = "", use_rag: bool = True) -> str:
        """Generate educational response using Gemini with optional RAG"""
        try:
            if use_rag and rag_service:
                # Use RAG for enhanced responses
                return await rag_service.query_knowledge(question)
            
            # Fallback to direct AI response
            if not self.model:
                return "AI service not available. Please check your configuration."
                
            prompt = f"""
            You are an educational assistant for a smart classroom system called ClassTrack. 
            Answer the following question in an educational context.
            
            Context: {context}
            Question: {question}
            
            Provide a helpful, educational response suitable for students and teachers.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
            
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your question right now. Error: {str(e)}"

# Initialize chatbot service
chatbot_service = ChatbotService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        await client.server_info()
        print("✅ MongoDB connected successfully!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB is running on localhost:27017")
    yield
    # Shutdown
    client.close()
    print("✅ MongoDB connection closed")

app = FastAPI(
    title="ClassTrack API",
    description="Smart Classroom Management System with AI, RAG, and Face Recognition",
    version="1.0.0",
    lifespan=lifespan
)

# Enhanced CORS middleware with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if ENVIRONMENT == "production" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health check endpoint for deployment platforms
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment platforms"""
    try:
        # Test database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "connected",
                "api": "running"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "error": str(e)
            }
        )



class UserData(BaseModel):
    name: str
    email: str
    usn: str

class FacultyData(BaseModel):
    name: str
    email: str
    teacher_code: str

class AttendanceRecord(BaseModel):
    student_name: str
    timestamp: datetime
    class_id: Optional[str] = None
    
class ChatRequest(BaseModel):
    question: str
    context: Optional[str] = ""
    
class ChatResponse(BaseModel):
    answer: str
    timestamp: datetime
    
class FaceRecognitionRequest(BaseModel):
    image_data: str  # base64 encoded image
    
class AttendanceResponse(BaseModel):
    detected_faces: List[Dict[str, Any]]
    attendance_marked: List[str]

class QuizData(BaseModel):
    topic: str

class QuizAttemptData(BaseModel):
    usn: str
    score: int

class MaterialData(BaseModel):
    classroom_id: str
    type: str
    url: str
    title: str
    assigned_to: list = []

class MarksData(BaseModel):
    classroom_id: str
    usn: str
    marks: dict

@app.get("/")
async def index():
    return "FastAPI app is running and connected to MongoDB!"

@app.get("/ping-db")
async def ping_db():
    try:
        # Test MongoDB connection by inserting and retrieving a test document
        result = await db.test_connection.insert_one({"test": "connection_check", "timestamp": "2025-09-14"})
        user = await db.test_connection.find_one({"_id": result.inserted_id})
        # Clean up test document
        await db.test_connection.delete_one({"_id": result.inserted_id})
        return {"connected": True, "message": "MongoDB connection successful!", "test_document": {"_id": str(user["_id"]), "test": user["test"]}}
    except Exception as e:
        return {"connected": False, "error": str(e)}

@app.post("/users", status_code=201)
async def create_user(user_data: dict):
    result = await db.users.insert_one(user_data)
    return {"id": str(result.inserted_id)}

@app.get("/users")
@cached_query("users_list", ttl=120)  # Cache for 2 minutes
async def get_users():
    users = []
    cursor = db.users.find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])
        users.append(user)
    return users

@app.post("/quizzes", status_code=201)
async def create_quiz(quiz_data: dict):
    result = await db.quizzes.insert_one(quiz_data)
    # Invalidate related cache
    cache_manager.invalidate("quiz")
    return {"id": str(result.inserted_id)}

@app.get("/quizzes/{quiz_id}")
@cached_query("quiz_detail", ttl=300)  # Cache for 5 minutes
async def get_quiz(quiz_id: str):
    quiz = await db.quizzes.find_one({"_id": ObjectId(quiz_id)})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz["_id"] = str(quiz["_id"])
    return quiz

@app.post("/login/student")
async def student_login(data: dict):
    student_usn = data.get('usn')
    classroom_id = data.get('classroom_id')
    if not all([student_usn, classroom_id]):
        raise HTTPException(status_code=400, detail="USN and Classroom ID are required.")
    student = await db.students.find_one({"usn": student_usn})
    if not student:
        raise HTTPException(status_code=401, detail="Invalid student USN.")
    classroom = await db.classrooms.find_one({"_id": classroom_id})
    if not classroom or not classroom.get("is_active"):
        raise HTTPException(status_code=404, detail="Classroom not found or is not active.")
    return {"success": True, "message": "Student logged in successfully!"}

@app.post("/signup/student", status_code=201)
async def student_signup(data: dict):
    usn = data.get('usn')
    name = data.get('name')
    email = data.get('email')
    if not all([usn, name, email]):
        raise HTTPException(status_code=400, detail="USN, name, and email are required for signup.")
    existing = await db.students.find_one({"usn": usn})
    if existing:
        raise HTTPException(status_code=409, detail="Student with this USN already exists.")
    await db.students.insert_one({"usn": usn, "name": name, "email": email})
    return {"success": True, "message": "Student profile created successfully!"}

@app.get("/student/profile/{usn}")
async def get_student_profile(usn: str):
    student = await db.students.find_one({"usn": usn})
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    attendance_cursor = db.attendance.find({"usn": usn})
    attendance_data, total_classes, classes_attended = [], 0, 0
    async for att in attendance_cursor:
        attendance_data.append(att)
        total_classes += 1
        if att.get("present", False):
            classes_attended += 1
    attendance_percentage = (classes_attended / total_classes * 100) if total_classes > 0 else 0
    performance_cursor = db.student_performance.find({"usn": usn})
    weekly_performance = [perf async for perf in performance_cursor]
    documents_cursor = db.study_materials.find({"assigned_to": usn})
    assigned_documents = [doc async for doc in documents_cursor]
    return {
        "student_info": student,
        "attendance": {
            "total_classes": total_classes,
            "classes_attended": classes_attended,
            "attendance_percentage": attendance_percentage,
            "attendance_history": attendance_data
        },
        "weekly_performance": weekly_performance,
        "assigned_documents": assigned_documents
    }

@app.post("/student/chat")
async def student_chat(data: dict):
    student_query = data.get('query')
    document_id = data.get('document_id')
    response = {
        "answer": f"This is a placeholder response for: {student_query}",
        "related_documents": []
    }
    return response

@app.post("/signup/faculty", status_code=201)
async def faculty_signup(data: dict):
    teacher_code = data.get('teacher_code')
    name = data.get('name')
    email = data.get('email')
    if not all([teacher_code, name, email]):
        raise HTTPException(status_code=400, detail="Teacher code, name, and email are required for signup.")
    existing = await db.teachers.find_one({"teacher_code": teacher_code})
    if existing:
        raise HTTPException(status_code=409, detail="Faculty with this teacher code already exists.")
    await db.teachers.insert_one({"teacher_code": teacher_code, "name": name, "email": email})
    return {"success": True, "message": "Faculty profile created successfully!"}

@app.get("/faculty/profile/{teacher_code}")
async def get_faculty_profile(teacher_code: str):
    faculty = await db.teachers.find_one({"teacher_code": teacher_code})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")
    return faculty

@app.get("/dashboard/faculty/{teacher_code}")
async def faculty_dashboard(teacher_code: str):
    faculty = await db.teachers.find_one({"teacher_code": teacher_code})
    if not faculty:
        raise HTTPException(status_code=404, detail="Faculty profile not found.")
    classes_cursor = db.classrooms.find({"teacher_code": teacher_code})
    my_classes = []
    async for doc in classes_cursor:
        performance_cursor = db.student_performance.find({"classroom_id": doc["_id"]})
        class_performance = [perf async for perf in performance_cursor]
        attendance_cursor = db.attendance.find({"classroom_id": doc["_id"]})
        attendance_data = [att async for att in attendance_cursor]
        total_students = len(doc.get("students", []))
        avg_attendance = sum(len(att.get("present_students", [])) for att in attendance_data) / len(attendance_data) if attendance_data else 0
        doc.update({
            "total_students": total_students,
            "average_attendance": avg_attendance,
            "performance_data": class_performance,
            "attendance_history": attendance_data
        })
        my_classes.append(doc)
    return {"success": True, "message": "Faculty dashboard data retrieved.", "profile": faculty, "my_classes": my_classes}

@app.post("/create_class", status_code=201)
async def create_class(data: dict):
    classroom_id = data.get('classroom_id')
    teacher_code = data.get('teacher_code')
    college_name = data.get('college_name')
    subject = data.get('subject', '')
    max_students = data.get('max_students', 60)
    if not all([classroom_id, teacher_code, college_name]):
        raise HTTPException(status_code=400, detail="Classroom ID, teacher code, and college name are required.")
    teacher = await db.teachers.find_one({"teacher_code": teacher_code})
    if not teacher:
        raise HTTPException(status_code=401, detail="Invalid teacher code.")
    existing_class = await db.classrooms.find_one({"_id": classroom_id})
    if existing_class:
        raise HTTPException(status_code=409, detail="Classroom ID already exists.")
    await db.classrooms.insert_one({
        "_id": classroom_id,
        "teacher_code": teacher_code,
        "college_name": college_name,
        "subject": subject,
        "max_students": max_students,
        "current_students": 0,
        "students": [],
        "is_active": True
    })
    return {"success": True, "message": "Class created successfully!"}

@app.get("/my_classes/{teacher_code}")
async def get_my_classes(teacher_code: str):
    cursor = db.classrooms.find({"teacher_code": teacher_code})
    class_list = []
    async for doc in cursor:
        class_list.append(doc)
    return class_list

@app.post("/speech/listen")
async def start_listening():
    text = speech_model.listen_from_microphone()
    if text:
        transcript_data = {"text": text, "type": "teacher_speech"}
        result = await db.transcripts.insert_one(transcript_data)
        return {"success": True, "text": text, "transcript_id": str(result.inserted_id)}
    else:
        raise HTTPException(status_code=400, detail="Could not understand audio")

@app.post("/speech/speak")
async def text_to_speech(data: dict):
    text = data.get('text', '')
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    speech_model.text_to_speech(text)
    return {"success": True, "message": "Text converted to speech successfully"}

@app.get("/speech/transcripts")
async def get_transcripts():
    transcripts = []
    cursor = db.transcripts.find({})
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        transcripts.append(doc)
    return {"success": True, "transcripts": transcripts}

@app.get("/speech/test-microphone")
async def test_microphone():
    return {"success": True, "message": "Speech recognition is ready", "engines": speech_model.get_available_engines()}

# Attendance System Endpoints
@app.post("/attendance/detect-faces")
async def detect_faces_endpoint(request: FaceRecognitionRequest):
    """Detect and recognize faces from uploaded image"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_data.split(',')[1] if ',' in request.image_data else request.image_data)
        image = Image.open(BytesIO(image_data))
        frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Detect faces
        detected_faces = attendance_system.detect_faces(frame)
        
        # Mark attendance for recognized faces
        attendance_marked = []
        current_time = time.time()
        
        for face in detected_faces:
            name = face['name']
            if current_time - attendance_system.last_attendance[name] > attendance_system.attendance_cooldown:
                # Mark attendance in database
                attendance_record = {
                    "student_name": name,
                    "timestamp": datetime.now(),
                    "confidence": face['confidence'],
                    "method": "face_recognition"
                }
                
                await db.attendance.insert_one(attendance_record)
                attendance_system.last_attendance[name] = current_time
                attendance_marked.append(name)
        
        return AttendanceResponse(
            detected_faces=detected_faces,
            attendance_marked=attendance_marked
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Face detection failed: {str(e)}")

@app.get("/attendance/today")
async def get_today_attendance():
    """Get today's attendance records"""
    try:
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        
        attendance_records = []
        async for record in db.attendance.find({
            "timestamp": {"$gte": today_start, "$lte": today_end}
        }).sort("timestamp", -1):
            record["_id"] = str(record["_id"])
            attendance_records.append(record)
        
        return {
            "success": True,
            "date": today_start.strftime("%Y-%m-%d"),
            "total_present": len(set(record["student_name"] for record in attendance_records)),
            "attendance_records": attendance_records
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance: {str(e)}")

@app.get("/attendance/student/{student_name}")
async def get_student_attendance(student_name: str, days: int = 30):
    """Get attendance history for a specific student"""
    try:
        from datetime import timedelta
        start_date = datetime.now() - timedelta(days=days)
        
        attendance_records = []
        async for record in db.attendance.find({
            "student_name": student_name,
            "timestamp": {"$gte": start_date}
        }).sort("timestamp", -1):
            record["_id"] = str(record["_id"])
            attendance_records.append(record)
        
        # Calculate attendance statistics
        total_days = days
        days_present = len(set(record["timestamp"].date() for record in attendance_records))
        attendance_percentage = (days_present / total_days) * 100 if total_days > 0 else 0
        
        return {
            "success": True,
            "student_name": student_name,
            "period_days": days,
            "days_present": days_present,
            "attendance_percentage": round(attendance_percentage, 2),
            "attendance_records": attendance_records
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student attendance: {str(e)}")

# Chatbot System Endpoints
@app.post("/chatbot/ask")
async def chatbot_ask(request: ChatRequest):
    """Ask a question to the educational chatbot"""
    try:
        # Generate response using Gemini
        response_text = chatbot_service.generate_response(request.question, request.context)
        
        # Save chat history to database
        chat_record = {
            "question": request.question,
            "answer": response_text,
            "context": request.context,
            "timestamp": datetime.now()
        }
        
        await db.chat_history.insert_one(chat_record)
        
        return ChatResponse(
            answer=response_text,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

@app.get("/chatbot/history")
async def get_chat_history(limit: int = 20):
    """Get recent chat history"""
    try:
        chat_history = []
        async for record in db.chat_history.find().sort("timestamp", -1).limit(limit):
            record["_id"] = str(record["_id"])
            chat_history.append(record)
        
        return {
            "success": True,
            "chat_history": chat_history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")

@app.post("/chatbot/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Upload document for chatbot knowledge base"""
    try:
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Save file info to database
        document_record = {
            "filename": file.filename,
            "file_path": file_path,
            "upload_timestamp": datetime.now(),
            "file_size": len(content),
            "content_type": file.content_type
        }
        
        result = await db.documents.insert_one(document_record)
        
        return {
            "success": True,
            "message": "Document uploaded successfully",
            "document_id": str(result.inserted_id),
            "filename": file.filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document upload failed: {str(e)}")

@app.get("/chatbot/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = []
        async for doc in db.documents.find().sort("upload_timestamp", -1):
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        
        return {
            "success": True,
            "documents": documents
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")

# Face Registration Endpoint
@app.post("/attendance/register-face")
async def register_face(request: dict):
    """Register a new face for attendance system"""
    try:
        name = request.get("name")
        image_data = request.get("image_data")
        
        if not name or not image_data:
            raise HTTPException(status_code=400, detail="Name and image_data are required")
        
        # Save face image
        os.makedirs(attendance_system.known_faces_dir, exist_ok=True)
        
        # Decode and save image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        image_path = os.path.join(attendance_system.known_faces_dir, f"{name}.jpg")
        
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        
        return {
            "success": True,
            "message": f"Face registered for {name}",
            "image_path": image_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face registration failed: {str(e)}")

# ============================================================================
# COMPREHENSIVE INTEGRATION ENDPOINTS
# ============================================================================

# RAG Knowledge Base Endpoints
@app.post("/rag/add-document")
async def add_document_to_rag(request: dict):
    """Add document to RAG knowledge base"""
    try:
        content = request.get("content")
        metadata = request.get("metadata", {})
        
        if not content:
            raise HTTPException(status_code=400, detail="Content is required")
        
        doc_id = await rag_service.add_document(content, metadata)
        
        return {
            "success": True,
            "message": "Document added to knowledge base",
            "document_id": doc_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add document: {str(e)}")

@app.post("/rag/query")
async def query_rag_knowledge(request: dict):
    """Query RAG knowledge base"""
    try:
        query = request.get("query")
        
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        response = await rag_service.query_knowledge(query)
        
        return {
            "success": True,
            "query": query,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

# Enhanced Chat with RAG integration
@app.post("/chat/enhanced")
async def enhanced_chat(request: dict):
    """Enhanced chat with RAG integration"""
    try:
        message = request.get("message")
        use_rag = request.get("use_rag", True)
        context = request.get("context", "")
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        chatbot = ChatbotService()
        response = await chatbot.generate_response(message, context, use_rag)
        
        # Store conversation in database
        conversation_record = {
            "message": message,
            "response": response,
            "use_rag": use_rag,
            "timestamp": datetime.now(),
            "context": context
        }
        await db.conversations.insert_one(conversation_record)
        
        return {
            "success": True,
            "message": message,
            "response": response,
            "rag_used": use_rag
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced chat failed: {str(e)}")

# Clerk Integration Endpoints
@app.get("/users/{clerk_id}")
async def get_user_by_clerk_id(clerk_id: str):
    """Get user by Clerk ID"""
    try:
        user = await db.users.find_one({"clerk_id": clerk_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user["_id"] = str(user["_id"])
        return {"success": True, "user": user}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.put("/users/{clerk_id}/role")
async def update_user_role(clerk_id: str, request: dict):
    """Update user role"""
    try:
        role = request.get("role")
        if role not in ["student", "teacher"]:
            raise HTTPException(status_code=400, detail="Role must be 'student' or 'teacher'")
        
        result = await db.users.update_one(
            {"clerk_id": clerk_id},
            {"$set": {"role": role, "updated_at": datetime.now()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"success": True, "message": f"User role updated to {role}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")

# Dashboard Endpoints
@app.get("/dashboard/teacher/{clerk_id}")
async def get_teacher_dashboard(clerk_id: str):
    """Get teacher dashboard data"""
    try:
        # Get teacher's classes
        classes = []
        async for cls in db.classes.find({"teacher_clerk_id": clerk_id}):
            cls["_id"] = str(cls["_id"])
            classes.append(cls)
        
        # Get attendance stats
        total_students = await db.students.count_documents({})
        present_today = await db.attendance.count_documents({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "status": "present"
        })
        
        # Get recent quizzes
        recent_quizzes = []
        async for quiz in db.quizzes.find().sort("created_at", -1).limit(5):
            quiz["_id"] = str(quiz["_id"])
            recent_quizzes.append(quiz)
        
        return {
            "success": True,
            "dashboard": {
                "teacher_clerk_id": clerk_id,
                "classes": classes,
                "stats": {
                    "total_students": total_students,
                    "present_today": present_today,
                    "total_classes": len(classes)
                },
                "recent_quizzes": recent_quizzes
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get teacher dashboard: {str(e)}")

@app.get("/dashboard/student/{clerk_id}")
async def get_student_dashboard(clerk_id: str):
    """Get student dashboard data"""
    try:
        # Get student's classes
        student_classes = []
        async for cls in db.classes.find({"students": {"$in": [clerk_id]}}):
            cls["_id"] = str(cls["_id"])
            student_classes.append(cls)
        
        # Get attendance history
        attendance_history = []
        async for record in db.attendance.find({"student_clerk_id": clerk_id}).sort("date", -1).limit(10):
            record["_id"] = str(record["_id"])
            attendance_history.append(record)
        
        # Get quiz results
        quiz_results = []
        async for result in db.quiz_results.find({"student_clerk_id": clerk_id}).sort("completed_at", -1).limit(5):
            result["_id"] = str(result["_id"])
            quiz_results.append(result)
        
        return {
            "success": True,
            "dashboard": {
                "student_clerk_id": clerk_id,
                "classes": student_classes,
                "attendance_history": attendance_history,
                "recent_quiz_results": quiz_results,
                "stats": {
                    "total_classes": len(student_classes),
                    "attendance_rate": len([a for a in attendance_history if a.get("status") == "present"]) / max(len(attendance_history), 1) * 100
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get student dashboard: {str(e)}")

# Class Management
@app.post("/create_class")
async def create_class(request: dict):
    """Create a new class"""
    try:
        classroom_id = request.get("classroom_id")
        teacher_clerk_id = request.get("teacher_clerk_id")
        college_name = request.get("college_name")
        subject = request.get("subject", "")
        max_students = request.get("max_students", 50)
        
        if not all([classroom_id, teacher_clerk_id, college_name]):
            raise HTTPException(status_code=400, detail="classroom_id, teacher_clerk_id, and college_name are required")
        
        # Check if class already exists
        existing_class = await db.classes.find_one({"classroom_id": classroom_id})
        if existing_class:
            raise HTTPException(status_code=400, detail="Class already exists")
        
        class_data = {
            "classroom_id": classroom_id,
            "teacher_clerk_id": teacher_clerk_id,
            "college_name": college_name,
            "subject": subject,
            "max_students": max_students,
            "students": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = await db.classes.insert_one(class_data)
        
        return {
            "success": True,
            "message": "Class created successfully",
            "class_id": str(result.inserted_id),
            "classroom_id": classroom_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create class: {str(e)}")

@app.get("/class_details/{classroom_id}")
async def get_class_details(classroom_id: str):
    """Get class details"""
    try:
        class_data = await db.classes.find_one({"classroom_id": classroom_id})
        if not class_data:
            raise HTTPException(status_code=404, detail="Class not found")
        
        class_data["_id"] = str(class_data["_id"])
        
        # Get student count
        student_count = len(class_data.get("students", []))
        
        # Get recent attendance
        recent_attendance = []
        async for record in db.attendance.find({"classroom_id": classroom_id}).sort("date", -1).limit(5):
            record["_id"] = str(record["_id"])
            recent_attendance.append(record)
        
        return {
            "success": True,
            "class": class_data,
            "stats": {
                "student_count": student_count,
                "max_students": class_data.get("max_students", 50)
            },
            "recent_attendance": recent_attendance
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get class details: {str(e)}")

# System Status Endpoint
@app.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Test MongoDB connection
        mongodb_status = "connected"
        try:
            await client.server_info()
        except:
            mongodb_status = "disconnected"
        
        # Test AI services
        ai_status = "available" if GOOGLE_API_KEY else "unavailable"
        
        # Test RAG service
        rag_status = "available" if rag_service and rag_service.model else "unavailable"
        
        # Test face recognition
        face_recognition_status = "available" if attendance_system else "unavailable"
        
        # Get database stats
        total_users = await db.users.count_documents({})
        total_classes = await db.classes.count_documents({})
        total_quizzes = await db.quizzes.count_documents({})
        
        return {
            "success": True,
            "system_status": {
                "services": {
                    "mongodb": mongodb_status,
                    "ai_gemini": ai_status,
                    "rag_service": rag_status,
                    "face_recognition": face_recognition_status
                },
                "database_stats": {
                    "total_users": total_users,
                    "total_classes": total_classes,
                    "total_quizzes": total_quizzes
                },
                "environment": ENVIRONMENT,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

# ===== CAMERA & ATTENDANCE ENDPOINTS =====

from fastapi.responses import StreamingResponse
import base64
import io

# Global camera state
camera_active = False
camera_cap = None

@app.get("/camera/status")
async def get_camera_status():
    """Get camera status"""
    try:
        global camera_active, camera_cap
        return {
            "success": True,
            "camera_active": camera_active,
            "camera_available": camera_cap is not None if camera_cap else cv2.VideoCapture(0).isOpened()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/camera/start")
async def start_camera():
    """Start camera for attendance"""
    try:
        global camera_active, camera_cap
        
        if camera_active:
            return {"success": True, "message": "Camera already active"}
        
        camera_cap = cv2.VideoCapture(0)
        if not camera_cap.isOpened():
            raise HTTPException(status_code=500, detail="Unable to access camera")
        
        camera_active = True
        return {
            "success": True, 
            "message": "Camera started successfully",
            "camera_id": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start camera: {str(e)}")

@app.post("/camera/stop")
async def stop_camera():
    """Stop camera"""
    try:
        global camera_active, camera_cap
        
        if camera_cap:
            camera_cap.release()
            camera_cap = None
        
        camera_active = False
        cv2.destroyAllWindows()
        
        return {"success": True, "message": "Camera stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop camera: {str(e)}")

@app.get("/camera/frame")
async def get_camera_frame():
    """Get single frame from camera with face detection"""
    try:
        global camera_cap, camera_active
        
        if not camera_active or not camera_cap:
            raise HTTPException(status_code=400, detail="Camera not active")
        
        ret, frame = camera_cap.read()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces using the attendance system
        detected_faces = attendance_system.detect_faces(frame)
        
        # Draw rectangles around detected faces
        for face_info in detected_faces:
            x, y, w, h = face_info['box']
            name = face_info['name']
            
            # Choose color based on recognition
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw name
            cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "frame": frame_base64,
            "detected_faces": detected_faces,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get frame: {str(e)}")

@app.post("/attendance/mark")
async def mark_attendance():
    """Mark attendance based on current camera frame"""
    try:
        global camera_cap, camera_active
        
        if not camera_active or not camera_cap:
            raise HTTPException(status_code=400, detail="Camera not active")
        
        ret, frame = camera_cap.read()
        if not ret:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Detect faces
        detected_faces = attendance_system.detect_faces(frame)
        marked_attendance = []
        
        for face_info in detected_faces:
            name = face_info['name']
            if name != "Unknown":
                # Mark attendance in database
                attendance_record = {
                    "student_name": name,
                    "timestamp": datetime.now(),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "status": "present",
                    "marked_by": "face_recognition"
                }
                
                # Insert into MongoDB
                await db.attendance.insert_one(attendance_record)
                marked_attendance.append(name)
        
        return {
            "success": True,
            "marked_attendance": marked_attendance,
            "total_detected": len(detected_faces),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark attendance: {str(e)}")

@app.get("/attendance/today")
async def get_today_attendance():
    """Get today's attendance records"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        attendance_cursor = db.attendance.find({"date": today})
        attendance_records = []
        
        async for record in attendance_cursor:
            record['_id'] = str(record['_id'])
            attendance_records.append(record)
        
        return {
            "success": True,
            "date": today,
            "attendance_records": attendance_records,
            "total_present": len(attendance_records)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get attendance: {str(e)}")

@app.get("/students/registered")
async def get_registered_students():
    """Get list of registered students for attendance"""
    try:
        # Get students from database
        students_cursor = db.users.find({"role": "student"})
        students = []
        
        async for student in students_cursor:
            students.append({
                "name": f"{student.get('first_name', '')} {student.get('last_name', '')}".strip(),
                "email": student.get('email', ''),
                "clerk_id": student.get('clerk_id', ''),
                "id": str(student['_id'])
            })
        
        # Also add students from the face recognition model
        if hasattr(attendance_system, 'label_names'):
            for name in attendance_system.label_names:
                if name != "Unknown" and name not in [s['name'] for s in students]:
                    students.append({
                        "name": name,
                        "email": f"{name.lower().replace(' ', '.')}@college.edu",
                        "clerk_id": f"face_rec_{name.lower().replace(' ', '_')}",
                        "id": f"face_{name.lower().replace(' ', '_')}"
                    })
        
        return {
            "success": True,
            "students": students,
            "total_registered": len(students)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get students: {str(e)}")

if __name__ == '__main__':
    print("🚀 Starting FastAPI Server...")
    print(f"📡 Server will be available at:")
    print(f"   • http://localhost:5001")
    print(f"   • http://127.0.0.1:5001")
    print(f"   • http://0.0.0.0:5001")
    print("🔄 Auto-reload enabled for development")
    print("=" * 50)
    
    try:
        # Get port from environment variable (for production deployment)
        port = int(os.getenv('PORT', 5001))
        
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=port, 
            reload=True,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: pip install uvicorn fastapi motor")
        input("Press Enter to exit...")