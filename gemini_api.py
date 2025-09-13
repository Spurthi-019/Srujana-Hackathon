"""
FastAPI Backend for Gemini-ChromaDB RAG Quiz Generation System
=============================================================

This module provides a complete RAG pipeline API using:
- Google Gemini for embeddings and quiz generation
- ChromaDB for vector storage
- Enhanced document parsing with intelligent chunking

API Endpoints:
- POST /upload-document: Upload PDF/PPT for processing and quiz generation
- GET /quiz/{quiz_id}: Retrieve generated quiz
- GET /quizzes: List all quizzes
- POST /search-content: Search document content
- GET /database-stats: Get vector database statistics
"""

import os
import shutil
import time
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from datetime import datetime
from pydantic import BaseModel

# Import our enhanced RAG pipeline components
from ppt_parser import EnhancedDocumentParser
from gemini_embeddings import GeminiEmbeddingService
from chroma_vector_db import ChromaVectorDB
from gemini_quiz_gen import GeminiRAGQuizPipeline, Quiz

# Pydantic models for API requests/responses
class DocumentUploadResponse(BaseModel):
    status: str
    message: str
    quiz_id: str
    processing_summary: Dict[str, Any]

class SearchRequest(BaseModel):
    query: str
    source_file: Optional[str] = None
    top_k: int = 5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    total_results: int

# Initialize FastAPI app
app = FastAPI(
    title="SmartClass AI - Gemini RAG Quiz Generator",
    description="AI-powered quiz generation using Gemini LLM and ChromaDB vector database",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
UPLOAD_DIR = "uploads"
DB_PATH = "gemini_quizzes.db"

# Create directories
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize RAG pipeline components
try:
    embedding_service = GeminiEmbeddingService()
    vector_db = ChromaVectorDB()
    document_parser = EnhancedDocumentParser(embedding_service, vector_db)
    quiz_pipeline = GeminiRAGQuizPipeline()
    
    print("✅ All RAG components initialized successfully")
    SYSTEM_READY = True
except Exception as e:
    print(f"❌ Failed to initialize RAG components: {e}")
    print("💡 Make sure GOOGLE_API_KEY is set in your .env file")
    SYSTEM_READY = False

class GeminiQuizDatabase:
    """SQLite database for storing Gemini-generated quizzes"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gemini_quizzes (
                quiz_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                source_file TEXT NOT NULL,
                quiz_data TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                estimated_time INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_quiz(self, quiz: Quiz):
        """Save quiz to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert quiz to JSON
        quiz_data = {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "source_file": quiz.source_file,
            "mcq_questions": [
                {
                    "question": mcq.question,
                    "options": mcq.options,
                    "correct_answer": mcq.correct_answer,
                    "explanation": mcq.explanation,
                    "difficulty": mcq.difficulty,
                    "topic": mcq.topic
                }
                for mcq in quiz.mcq_questions
            ],
            "short_questions": [
                {
                    "question": sq.question,
                    "sample_answer": sq.sample_answer,
                    "explanation": sq.explanation,
                    "difficulty": sq.difficulty,
                    "topic": sq.topic
                }
                for sq in quiz.short_questions
            ],
            "total_questions": quiz.total_questions,
            "estimated_time": quiz.estimated_time,
            "created_at": quiz.created_at,
            "metadata": quiz.metadata
        }
        
        cursor.execute("""
            INSERT OR REPLACE INTO gemini_quizzes 
            (quiz_id, title, description, source_file, quiz_data, total_questions, estimated_time, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz.id,
            quiz.title,
            quiz.description,
            quiz.source_file,
            json.dumps(quiz_data),
            quiz.total_questions,
            quiz.estimated_time,
            quiz.created_at,
            json.dumps(quiz.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve quiz by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT quiz_data FROM gemini_quizzes WHERE quiz_id = ?", (quiz_id,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def get_all_quizzes(self) -> List[Dict[str, Any]]:
        """Get all quiz summaries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT quiz_id, title, source_file, total_questions, estimated_time, created_at 
            FROM gemini_quizzes ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "quiz_id": row[0],
                "title": row[1],
                "source_file": row[2],
                "total_questions": row[3],
                "estimated_time": row[4],
                "created_at": row[5]
            }
            for row in results
        ]

# Initialize database
quiz_db = GeminiQuizDatabase(DB_PATH)

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "SmartClass AI - Gemini RAG Quiz Generator API",
        "version": "2.0.0",
        "status": "ready" if SYSTEM_READY else "initialization_failed",
        "endpoints": {
            "upload": "/upload-document",
            "quiz": "/quiz/{quiz_id}",
            "quizzes": "/quizzes",
            "search": "/search-content",
            "stats": "/database-stats"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy" if SYSTEM_READY else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "embedding_service": embedding_service is not None,
            "vector_db": vector_db is not None,
            "document_parser": document_parser is not None,
            "quiz_pipeline": quiz_pipeline is not None
        }
    }

@app.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document and generate quiz using RAG pipeline
    
    Process: Upload → Parse → Chunk → Embed → Store → Generate Quiz
    """
    if not SYSTEM_READY:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized. Check GOOGLE_API_KEY.")
    
    try:
        start_time = time.time()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ['.pdf', '.pptx']:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"📁 Processing document: {file.filename}")
        
        # Process document through RAG pipeline
        processing_summary = document_parser.process_and_store_document(file_path)
        
        if not processing_summary.get('success'):
            raise HTTPException(status_code=500, detail=f"Document processing failed: {processing_summary.get('error')}")
        
        # Search for relevant content to generate quiz
        search_results = document_parser.search_document_content(
            query=f"main topics concepts and key information from {file.filename}",
            source_file_filter=file.filename,
            top_k=8
        )
        
        if not search_results:
            raise HTTPException(status_code=500, detail="No content found for quiz generation")
        
        print(f"🔍 Found {len(search_results)} relevant chunks for quiz generation")
        
        # Generate quiz from retrieved content
        quiz = quiz_pipeline.generate_quiz_from_context(
            retrieved_chunks=search_results,
            source_file=file.filename,
            quiz_title=f"Quiz: {os.path.splitext(file.filename)[0]}"
        )
        
        # Save quiz to database
        quiz_db.save_quiz(quiz)
        
        processing_time = time.time() - start_time
        
        print(f"✅ Quiz generated successfully: {quiz.total_questions} questions in {processing_time:.2f}s")
        
        return DocumentUploadResponse(
            status="success",
            message=f"Document processed and quiz generated successfully",
            quiz_id=quiz.id,
            processing_summary={
                "total_chunks": processing_summary.get('total_chunks', 0),
                "total_questions": quiz.total_questions,
                "mcq_questions": len(quiz.mcq_questions),
                "short_questions": len(quiz.short_questions),
                "processing_time": round(processing_time, 2),
                "source_file": file.filename,
                "estimated_time": quiz.estimated_time
            }
        )
        
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up uploaded file
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

@app.get("/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Retrieve a generated quiz by ID"""
    try:
        quiz_data = quiz_db.get_quiz(quiz_id)
        
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return quiz_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quizzes")
async def get_all_quizzes():
    """Get list of all generated quizzes"""
    try:
        quizzes = quiz_db.get_all_quizzes()
        return {
            "quizzes": quizzes,
            "total": len(quizzes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search-content", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search document content using semantic similarity"""
    if not SYSTEM_READY:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        results = document_parser.search_document_content(
            query=request.query,
            source_file_filter=request.source_file,
            top_k=request.top_k
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database-stats")
async def get_database_stats():
    """Get vector database and quiz statistics"""
    if not SYSTEM_READY:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        # Get vector database stats
        vector_stats = document_parser.get_database_stats()
        
        # Get quiz statistics
        quiz_list = quiz_db.get_all_quizzes()
        
        return {
            "vector_database": vector_stats,
            "quiz_database": {
                "total_quizzes": len(quiz_list),
                "recent_quizzes": quiz_list[:5]  # Show 5 most recent
            },
            "system_status": "ready" if SYSTEM_READY else "not_ready"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-database")
async def clear_database():
    """Clear all data from vector database (development only)"""
    if not SYSTEM_READY:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        vector_db.clear_collection()
        return {"message": "Vector database cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting SmartClass AI - Gemini RAG Quiz Generator API")
    print("📊 API Documentation: http://localhost:8001/docs")
    print("🔑 Make sure GOOGLE_API_KEY is set in your .env file")
    
    if SYSTEM_READY:
        print("✅ System ready for document processing and quiz generation")
    else:
        print("❌ System initialization failed - check your configuration")
    
    try:
        uvicorn.run(
            "gemini_api:app",
            host="0.0.0.0",
            port=8001,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Try running: uvicorn gemini_api:app --host 0.0.0.0 --port 8000")