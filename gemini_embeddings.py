"""
Google Gemini Embedding Service
===============================

This module provides embedding generation using Google's Gemini text-embedding-004 model.
"""

import google.generativeai as genai
import os
import numpy as np
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    """Container for embedding results"""
    text: str
    embedding: np.ndarray
    model: str
    dimension: int

class GeminiEmbeddingService:
    """Service for generating embeddings using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini embedding service
        
        Args:
            api_key: Google API key (if not provided, will look for GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model_name = "models/text-embedding-004"
        
        # Test the connection
        try:
            # Test with a simple embedding
            test_result = genai.embed_content(
                model=self.model_name,
                content="Test connection",
                task_type="retrieval_document"
            )
            self.embedding_dimension = len(test_result['embedding'])
            logger.info(f"✅ Gemini embedding service initialized. Dimension: {self.embedding_dimension}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini embedding service: {e}")
            raise
    
    def generate_embedding(self, text: str, task_type: str = "retrieval_document") -> EmbeddingResult:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            task_type: Task type for embedding (retrieval_document, retrieval_query, semantic_similarity, etc.)
        
        Returns:
            EmbeddingResult containing the embedding and metadata
        """
        try:
            # Clean and validate text
            text = text.strip()
            if not text:
                raise ValueError("Text cannot be empty")
            
            # Generate embedding
            result = genai.embed_content(
                model=self.model_name,
                content=text,
                task_type=task_type
            )
            
            embedding = np.array(result['embedding'], dtype=np.float32)
            
            return EmbeddingResult(
                text=text,
                embedding=embedding,
                model=self.model_name,
                dimension=len(embedding)
            )
            
        except Exception as e:
            logger.error(f"Error generating embedding for text: {e}")
            raise
    
    def generate_batch_embeddings(self, texts: List[str], task_type: str = "retrieval_document") -> List[EmbeddingResult]:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            task_type: Task type for embedding
        
        Returns:
            List of EmbeddingResult objects
        """
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.generate_embedding(text, task_type)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated embeddings for {i + 1}/{len(texts)} texts")
                    
            except Exception as e:
                logger.error(f"Failed to generate embedding for text {i}: {e}")
                # Create a dummy embedding to maintain list structure
                dummy_embedding = np.zeros(self.embedding_dimension, dtype=np.float32)
                results.append(EmbeddingResult(
                    text=text,
                    embedding=dummy_embedding,
                    model=self.model_name,
                    dimension=self.embedding_dimension
                ))
        
        logger.info(f"✅ Generated {len(results)} embeddings")
        return results
    
    def generate_query_embedding(self, query: str) -> EmbeddingResult:
        """
        Generate embedding optimized for query (retrieval)
        
        Args:
            query: Query text to embed
        
        Returns:
            EmbeddingResult for the query
        """
        return self.generate_embedding(query, task_type="retrieval_query")
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this model"""
        return self.embedding_dimension

# Test function
def test_gemini_embeddings():
    """Test the Gemini embedding service"""
    try:
        print("🧪 Testing Gemini Embedding Service...")
        
        # Initialize service
        service = GeminiEmbeddingService()
        
        # Test single embedding
        test_text = "This is a test document about artificial intelligence and machine learning."
        result = service.generate_embedding(test_text)
        
        print(f"✅ Single embedding test:")
        print(f"   Text: {result.text[:50]}...")
        print(f"   Embedding dimension: {result.dimension}")
        print(f"   Model: {result.model}")
        print(f"   Embedding shape: {result.embedding.shape}")
        
        # Test batch embeddings
        test_texts = [
            "Machine learning is a subset of artificial intelligence.",
            "Natural language processing helps computers understand human language.",
            "Deep learning uses neural networks with multiple layers."
        ]
        
        batch_results = service.generate_batch_embeddings(test_texts)
        print(f"✅ Batch embedding test: {len(batch_results)} embeddings generated")
        
        # Test query embedding
        query_result = service.generate_query_embedding("What is machine learning?")
        print(f"✅ Query embedding test: dimension {query_result.dimension}")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    test_gemini_embeddings()