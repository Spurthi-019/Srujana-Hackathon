"""
FastAPI endpoints for Chatbot RAG operations
============================================

This module provides REST API endpoints for:
1. Document upload and processing
2. Student Q&A interactions
3. Quiz generation from context
4. Conversation management
5. Knowledge base administration
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil
import tempfile
from pathlib import Path
import logging
from datetime import datetime

# Import our chatbot components
try:
    from .enhanced_chatbot import EnhancedGeminiChatbot
    from .chatbot_vector_db import ChatbotVectorDB
    from .error_handler import check_system_health, repair_system, error_reporter
except ImportError:
    # Handle direct execution
    from enhanced_chatbot import EnhancedGeminiChatbot
    from chatbot_vector_db import ChatbotVectorDB
    from error_handler import check_system_health, repair_system, error_reporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class ChatQuestion(BaseModel):
    question: str
    conversation_id: Optional[str] = None
    include_quiz: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    follow_up_questions: List[str]
    quiz: Optional[Dict[str, Any]] = None
    confidence_score: float

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"

class ConversationHistoryRequest(BaseModel):
    conversation_id: str
    limit: int = 10

class DocumentUploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_added: int
    file_type: str
    message: str

class KnowledgeBaseStats(BaseModel):
    total_chunks: int
    unique_sources: int
    source_files: List[str]
    file_types: List[str]
    collection_name: str

# Initialize FastAPI app
app = FastAPI(
    title="SmartClass AI Chatbot API",
    description="RAG-powered chatbot for student Q&A and quiz generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
chatbot = None
vector_db = None

def initialize_chatbot():
    """Initialize chatbot components"""
    global chatbot, vector_db
    try:
        vector_db = ChatbotVectorDB()
        chatbot = EnhancedGeminiChatbot(vector_db=vector_db)
        logger.info("✅ Enhanced chatbot components initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize chatbot: {e}")
        raise

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    initialize_chatbot()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with error reporting"""
    try:
        # Get comprehensive system health
        system_health = check_system_health()
        
        # Get chatbot status
        chatbot_status = {}
        if chatbot:
            try:
                chatbot_status = chatbot.get_system_status()
            except Exception as e:
                chatbot_status = {"error": str(e)}
        
        # Get vector DB stats
        vector_stats = {}
        if vector_db:
            try:
                vector_stats = vector_db.get_chatbot_stats()
            except Exception as e:
                vector_stats = {"error": str(e)}
        
        # Get error summary
        error_summary = error_reporter.get_error_summary()
        
        return {
            "status": "healthy" if system_health.get("status") == "healthy" else "degraded",
            "timestamp": datetime.now().isoformat(),
            "chatbot_ready": chatbot is not None,
            "vector_db_ready": vector_db is not None,
            "system_health": system_health,
            "chatbot_status": chatbot_status,
            "knowledge_base_stats": vector_stats,
            "error_summary": error_summary,
            "api_version": "2.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "api_version": "2.0.0"
        }

# Document upload endpoint
@app.post("/upload_document", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a document for the chatbot's knowledge base"""
    try:
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        # Validate file type
        allowed_types = {'.pdf', '.pptx', '.ppt'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        try:
            # Process document
            result = vector_db.add_document_to_chatbot(temp_path)
            
            if result["success"]:
                return DocumentUploadResponse(
                    success=True,
                    filename=file.filename,
                    chunks_added=result["chunks_added"],
                    file_type=result["file_type"],
                    message=f"Successfully processed {result['pages_processed']} pages/slides"
                )
            else:
                raise HTTPException(status_code=400, detail=result["error"])
                
        finally:
            # Clean up temporary file
            os.unlink(temp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System repair endpoint
@app.post("/repair_system")
async def repair_system_endpoint():
    """Attempt to repair common system issues"""
    try:
        repair_log = repair_system()
        
        # Try to reinitialize components
        try:
            initialize_chatbot()
            repair_log.append("Successfully reinitialized chatbot components")
        except Exception as e:
            repair_log.append(f"Failed to reinitialize: {e}")
        
        return {
            "success": True,
            "repair_log": repair_log,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"System repair failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Error reporting endpoint
@app.get("/error_summary")
async def get_error_summary():
    """Get system error summary"""
    try:
        return error_reporter.get_error_summary()
    except Exception as e:
        return {"error": str(e)}

# Clear errors endpoint
@app.delete("/clear_errors")
async def clear_errors():
    """Clear error history"""
    try:
        error_reporter.clear_errors()
        return {"success": True, "message": "Error history cleared"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Student question endpoint
@app.post("/ask_question", response_model=ChatResponse)
async def ask_question(request: ChatQuestion):
    """Answer a student's question using RAG"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        # Generate response
        response = chatbot.generate_contextual_response(
            question=request.question,
            conversation_id=request.conversation_id
        )
        
        # Generate follow-up questions
        follow_ups = chatbot.generate_follow_up_questions(
            question=request.question,
            context=response.get("context", "")
        )
        
        # Generate quiz if requested
        quiz = None
        if request.include_quiz and response.get("context"):
            quiz_result = chatbot.generate_quiz_from_context(
                context=response["context"],
                num_questions=3
            )
            if quiz_result.get("success"):
                quiz = quiz_result["quiz"]
        
        return ChatResponse(
            answer=response["answer"],
            sources=response["sources"],
            conversation_id=response["conversation_id"],
            follow_up_questions=follow_ups,
            quiz=quiz,
            confidence_score=response.get("confidence_score", 0.8)
        )
        
    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Quiz generation endpoint
@app.post("/generate_quiz")
async def generate_quiz(request: QuizRequest):
    """Generate a quiz based on stored knowledge"""
    try:
        if not chatbot or not vector_db:
            raise HTTPException(status_code=500, detail="Chatbot components not initialized")
        
        # Search for relevant context
        context_chunks = vector_db.search_for_answer(request.topic, top_k=10)
        
        if not context_chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No relevant content found for topic: {request.topic}"
            )
        
        # Combine context
        combined_context = "\n\n".join([chunk["content"] for chunk in context_chunks[:5]])
        
        # Generate quiz
        result = chatbot.generate_quiz_from_context(
            context=combined_context,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )
        
        if result["success"]:
            return {
                "success": True,
                "topic": request.topic,
                "quiz": result["quiz"],
                "sources": [{"source_file": chunk["source_file"]} for chunk in context_chunks[:3]]
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Quiz generation failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Conversation history endpoint
@app.post("/conversation_history")
async def get_conversation_history(request: ConversationHistoryRequest):
    """Get conversation history for a specific conversation ID"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        history = chatbot.get_conversation_history(request.conversation_id, request.limit)
        
        return {
            "conversation_id": request.conversation_id,
            "history": history,
            "total_messages": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge base stats endpoint
@app.get("/knowledge_stats", response_model=KnowledgeBaseStats)
async def get_knowledge_stats():
    """Get statistics about the chatbot's knowledge base"""
    try:
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        stats = vector_db.get_chatbot_stats()
        
        return KnowledgeBaseStats(
            total_chunks=stats.get("total_chunks", 0),
            unique_sources=stats.get("unique_sources", 0),
            source_files=stats.get("source_files", []),
            file_types=stats.get("file_types", []),
            collection_name=stats.get("collection_name", "unknown")
        )
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search documents endpoint
@app.post("/search_documents")
async def search_documents(
    query: str,
    top_k: int = 5
):
    """Search for relevant documents in the knowledge base"""
    try:
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        results = vector_db.search_for_answer(query, top_k)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Delete document endpoint
@app.delete("/delete_document/{filename}")
async def delete_document(filename: str):
    """Delete a specific document from the knowledge base"""
    try:
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        success = vector_db.delete_document(filename)
        
        if success:
            return {"success": True, "message": f"Document {filename} deleted successfully"}
        else:
            return {"success": False, "message": f"Document {filename} not found"}
            
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Clear knowledge base endpoint
@app.delete("/clear_knowledge_base")
async def clear_knowledge_base():
    """Clear all documents from the knowledge base"""
    try:
        if not vector_db:
            raise HTTPException(status_code=500, detail="Vector database not initialized")
        
        success = vector_db.clear_chatbot_knowledge()
        
        if success:
            return {"success": True, "message": "Knowledge base cleared successfully"}
        else:
            return {"success": False, "message": "Failed to clear knowledge base"}
            
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Evaluate student response endpoint
@app.post("/evaluate_response")
async def evaluate_student_response(
    question: str,
    student_answer: str,
    correct_answer: str = None
):
    """Evaluate a student's response to a question"""
    try:
        if not chatbot:
            raise HTTPException(status_code=500, detail="Chatbot not initialized")
        
        evaluation = chatbot.evaluate_student_understanding(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer
        )
        
        return evaluation
        
    except Exception as e:
        logger.error(f"Error evaluating student response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "chatbot_api:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )