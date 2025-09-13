"""
Gemini LLM Quiz Generator for RAG Pipeline
==========================================

This module generates quizzes using Google's Gemini LLM with retrieved context
from ChromaDB vector database.
"""

import google.generativeai as genai
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCQQuestion:
    """Multiple Choice Question structure"""
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option (0-based)
    explanation: str
    difficulty: str  # easy, medium, hard
    topic: str

@dataclass
class ShortQuestion:
    """Short Answer Question structure"""
    question: str
    sample_answer: str
    explanation: str
    difficulty: str
    topic: str

@dataclass
class Quiz:
    """Complete quiz structure"""
    id: str
    title: str
    description: str
    source_file: str
    mcq_questions: List[MCQQuestion]
    short_questions: List[ShortQuestion]
    total_questions: int
    estimated_time: int  # in minutes
    created_at: str
    metadata: Dict[str, Any]

class GeminiQuizGenerator:
    """Quiz generator using Google Gemini LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini quiz generator
        
        Args:
            api_key: Google API key (if not provided, will look for GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("✅ Gemini Quiz Generator initialized")
    
    def generate_mcq_questions(self, context: str, topic: str, num_questions: int = 5) -> List[MCQQuestion]:
        """
        Generate Multiple Choice Questions from context
        
        Args:
            context: Retrieved document context
            topic: Topic/theme for questions
            num_questions: Number of MCQ questions to generate
        
        Returns:
            List of MCQQuestion objects
        """
        try:
            prompt = self._create_mcq_prompt(context, topic, num_questions)
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse the response to extract MCQ questions
            mcq_questions = self._parse_mcq_response(response_text, topic)
            
            logger.info(f"✅ Generated {len(mcq_questions)} MCQ questions")
            return mcq_questions
            
        except Exception as e:
            logger.error(f"❌ Failed to generate MCQ questions: {e}")
            return []
    
    def generate_short_questions(self, context: str, topic: str, num_questions: int = 3) -> List[ShortQuestion]:
        """
        Generate Short Answer Questions from context
        
        Args:
            context: Retrieved document context
            topic: Topic/theme for questions
            num_questions: Number of short questions to generate
        
        Returns:
            List of ShortQuestion objects
        """
        try:
            prompt = self._create_short_prompt(context, topic, num_questions)
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Parse the response to extract short questions
            short_questions = self._parse_short_response(response_text, topic)
            
            logger.info(f"✅ Generated {len(short_questions)} short answer questions")
            return short_questions
            
        except Exception as e:
            logger.error(f"❌ Failed to generate short questions: {e}")
            return []
    
    def _create_mcq_prompt(self, context: str, topic: str, num_questions: int) -> str:
        """Create prompt for MCQ generation"""
        return f"""
You are an expert quiz generator. Based on the provided context, create {num_questions} high-quality multiple choice questions.

CONTEXT:
{context}

TOPIC: {topic}

REQUIREMENTS:
1. Generate exactly {num_questions} multiple choice questions
2. Each question should have 4 options (A, B, C, D)
3. Questions should test understanding, not just memorization
4. Include a mix of difficulty levels (easy, medium, hard)
5. Provide clear explanations for correct answers
6. Questions should be directly related to the provided context

OUTPUT FORMAT (JSON):
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Explanation for why this is correct",
      "difficulty": "medium"
    }}
  ]
}}

Generate the questions now:
"""
    
    def _create_short_prompt(self, context: str, topic: str, num_questions: int) -> str:
        """Create prompt for short answer generation"""
        return f"""
You are an expert quiz generator. Based on the provided context, create {num_questions} high-quality short answer questions.

CONTEXT:
{context}

TOPIC: {topic}

REQUIREMENTS:
1. Generate exactly {num_questions} short answer questions
2. Questions should require 2-3 sentence answers
3. Include sample answers that demonstrate expected depth
4. Questions should encourage critical thinking and explanation
5. Provide explanations for the sample answers
6. Questions should be directly related to the provided context

OUTPUT FORMAT (JSON):
{{
  "questions": [
    {{
      "question": "Question text here?",
      "sample_answer": "Sample answer demonstrating expected response",
      "explanation": "Explanation of key points the answer should cover",
      "difficulty": "medium"
    }}
  ]
}}

Generate the questions now:
"""
    
    def _parse_mcq_response(self, response_text: str, topic: str) -> List[MCQQuestion]:
        """Parse MCQ response from Gemini"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            data = json.loads(json_text)
            
            mcq_questions = []
            for q_data in data.get('questions', []):
                question = MCQQuestion(
                    question=q_data.get('question', ''),
                    options=q_data.get('options', []),
                    correct_answer=q_data.get('correct_answer', 0),
                    explanation=q_data.get('explanation', ''),
                    difficulty=q_data.get('difficulty', 'medium'),
                    topic=topic
                )
                mcq_questions.append(question)
            
            return mcq_questions
            
        except Exception as e:
            logger.error(f"❌ Failed to parse MCQ response: {e}")
            # Return empty list if parsing fails
            return []
    
    def _parse_short_response(self, response_text: str, topic: str) -> List[ShortQuestion]:
        """Parse short answer response from Gemini"""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_text = response_text[json_start:json_end]
            data = json.loads(json_text)
            
            short_questions = []
            for q_data in data.get('questions', []):
                question = ShortQuestion(
                    question=q_data.get('question', ''),
                    sample_answer=q_data.get('sample_answer', ''),
                    explanation=q_data.get('explanation', ''),
                    difficulty=q_data.get('difficulty', 'medium'),
                    topic=topic
                )
                short_questions.append(question)
            
            return short_questions
            
        except Exception as e:
            logger.error(f"❌ Failed to parse short answer response: {e}")
            return []

class GeminiRAGQuizPipeline:
    """Complete RAG pipeline for quiz generation using Gemini and ChromaDB"""
    
    def __init__(self, 
                 quiz_generator: Optional[GeminiQuizGenerator] = None):
        """
        Initialize the RAG quiz pipeline
        
        Args:
            quiz_generator: Gemini quiz generator instance
        """
        self.quiz_generator = quiz_generator or GeminiQuizGenerator()
        
        logger.info("🚀 Gemini RAG Quiz Pipeline initialized")
    
    def generate_quiz_from_context(self, 
                                  retrieved_chunks: List[Dict[str, Any]],
                                  source_file: str,
                                  quiz_title: Optional[str] = None,
                                  num_mcq: int = 5,
                                  num_short: int = 3) -> Quiz:
        """
        Generate a complete quiz from retrieved context chunks
        
        Args:
            retrieved_chunks: List of relevant document chunks
            source_file: Name of source document
            quiz_title: Optional custom title
            num_mcq: Number of MCQ questions
            num_short: Number of short answer questions
        
        Returns:
            Complete Quiz object
        """
        try:
            # Combine context from all chunks
            context_texts = [chunk['text'] for chunk in retrieved_chunks]
            combined_context = "\n\n".join(context_texts)
            
            # Extract topic from chunks
            topics = [chunk.get('metadata', {}).get('topic', '') for chunk in retrieved_chunks]
            main_topic = topics[0] if topics else source_file
            
            # Generate title if not provided
            if not quiz_title:
                quiz_title = f"Quiz: {main_topic}"
            
            logger.info(f"📝 Generating quiz from {len(retrieved_chunks)} context chunks")
            
            # Generate MCQ questions
            mcq_questions = self.quiz_generator.generate_mcq_questions(
                combined_context, main_topic, num_mcq
            )
            
            # Generate short answer questions
            short_questions = self.quiz_generator.generate_short_questions(
                combined_context, main_topic, num_short
            )
            
            # Create quiz object
            quiz = Quiz(
                id=str(uuid.uuid4()),
                title=quiz_title,
                description=f"AI-generated quiz from {source_file}",
                source_file=source_file,
                mcq_questions=mcq_questions,
                short_questions=short_questions,
                total_questions=len(mcq_questions) + len(short_questions),
                estimated_time=self._estimate_time(len(mcq_questions), len(short_questions)),
                created_at=datetime.now().isoformat(),
                metadata={
                    'num_context_chunks': len(retrieved_chunks),
                    'context_length': len(combined_context),
                    'main_topic': main_topic,
                    'generation_model': 'gemini-1.5-flash'
                }
            )
            
            logger.info(f"✅ Generated complete quiz: {quiz.total_questions} questions")
            return quiz
            
        except Exception as e:
            logger.error(f"❌ Failed to generate quiz: {e}")
            raise
    
    def _estimate_time(self, num_mcq: int, num_short: int) -> int:
        """Estimate time to complete quiz in minutes"""
        # Assume 1 minute per MCQ and 3 minutes per short answer
        return num_mcq * 1 + num_short * 3
    
    def quiz_to_dict(self, quiz: Quiz) -> Dict[str, Any]:
        """Convert Quiz object to dictionary for storage/API response"""
        return {
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'source_file': quiz.source_file,
            'mcq_questions': [asdict(q) for q in quiz.mcq_questions],
            'short_questions': [asdict(q) for q in quiz.short_questions],
            'total_questions': quiz.total_questions,
            'estimated_time': quiz.estimated_time,
            'created_at': quiz.created_at,
            'metadata': quiz.metadata
        }

# Test function
def test_gemini_quiz_generator():
    """Test the Gemini quiz generator"""
    try:
        print("🧪 Testing Gemini Quiz Generator...")
        
        # Initialize generator
        generator = GeminiQuizGenerator()
        
        # Test context
        test_context = """
        Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled data to train models, while unsupervised learning finds patterns in unlabeled data. Reinforcement learning involves an agent learning through trial and error by receiving rewards or penalties.
        """
        
        # Test MCQ generation
        mcq_questions = generator.generate_mcq_questions(test_context, "Machine Learning", 2)
        print(f"✅ Generated {len(mcq_questions)} MCQ questions")
        
        if mcq_questions:
            print(f"Sample MCQ: {mcq_questions[0].question}")
        
        # Test short answer generation
        short_questions = generator.generate_short_questions(test_context, "Machine Learning", 1)
        print(f"✅ Generated {len(short_questions)} short answer questions")
        
        if short_questions:
            print(f"Sample Short: {short_questions[0].question}")
        
        print("🎉 Gemini quiz generator test passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_gemini_quiz_generator()