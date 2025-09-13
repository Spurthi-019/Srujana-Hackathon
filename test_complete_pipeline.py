"""
Comprehensive Test for Gemini-ChromaDB RAG Pipeline
===================================================

This script tests the complete RAG pipeline:
1. PDF upload and processing
2. Chunking and embedding generation
3. Vector storage in ChromaDB
4. Content retrieval and quiz generation
"""

import os
import sys
import time
from pathlib import Path

# Add the quiz directory to path
sys.path.append(str(Path(__file__).parent))

from gemini_embeddings import GeminiEmbeddingService
from chroma_vector_db import ChromaVectorDB
from ppt_parser import EnhancedDocumentParser
from gemini_quiz_gen import GeminiRAGQuizPipeline

def test_complete_rag_pipeline():
    """Test the complete RAG pipeline with a sample PDF"""
    
    print("🧪 Testing Complete Gemini-ChromaDB RAG Pipeline")
    print("=" * 60)
    
    try:
        # Step 1: Initialize all components
        print("\n📋 Step 1: Initializing RAG Components...")
        
        print("  🧠 Initializing Gemini Embedding Service...")
        embedding_service = GeminiEmbeddingService()
        
        print("  📊 Initializing ChromaDB Vector Database...")
        vector_db = ChromaVectorDB(collection_name="test_smartclass", persist_directory="./test_chroma_db")
        
        print("  📄 Initializing Enhanced Document Parser...")
        document_parser = EnhancedDocumentParser(embedding_service, vector_db)
        
        print("  🎯 Initializing Gemini Quiz Pipeline...")
        quiz_pipeline = GeminiRAGQuizPipeline()
        
        print("  ✅ All components initialized successfully!")
        
        # Step 2: Find a PDF file to test with
        print("\n📋 Step 2: Looking for PDF files to test...")
        
        # Look for PDF files in common locations
        test_files = []
        search_locations = [
            ".",
            "..",
            "../..",
            "uploads",
            "../uploads"
        ]
        
        for location in search_locations:
            location_path = Path(location)
            if location_path.exists():
                pdf_files = list(location_path.glob("*.pdf"))
                test_files.extend(pdf_files)
        
        if not test_files:
            print("  ❌ No PDF files found for testing")
            print("  💡 Please add a PDF file to the current directory or provide a path")
            
            # Create a sample text file for testing
            sample_text = """
            Artificial Intelligence and Machine Learning
            
            Artificial Intelligence (AI) is a broad field of computer science that aims to create systems capable of performing tasks that typically require human intelligence. Machine Learning (ML) is a subset of AI that focuses on algorithms that can learn and improve from experience without being explicitly programmed.
            
            Types of Machine Learning:
            1. Supervised Learning: Uses labeled data to train models
            2. Unsupervised Learning: Finds patterns in unlabeled data  
            3. Reinforcement Learning: Learns through trial and error with rewards
            
            Applications include natural language processing, computer vision, robotics, and data analysis.
            """
            
            print("  📝 Creating sample content for testing...")
            return test_with_sample_content(sample_text, document_parser, quiz_pipeline)
        
        # Use the first PDF found
        test_pdf = test_files[0]
        print(f"  📄 Found PDF for testing: {test_pdf}")
        
        # Step 3: Process the document
        print(f"\n📋 Step 3: Processing document: {test_pdf.name}")
        start_time = time.time()
        
        processing_summary = document_parser.process_and_store_document(str(test_pdf))
        
        processing_time = time.time() - start_time
        
        if not processing_summary.get('success'):
            print(f"  ❌ Document processing failed: {processing_summary.get('error')}")
            return False
        
        print(f"  ✅ Document processed successfully in {processing_time:.2f}s")
        print(f"     📦 Total chunks: {processing_summary.get('total_chunks', 0)}")
        print(f"     📄 Total pages: {processing_summary.get('total_pages', 0)}")
        
        # Step 4: Test content search
        print(f"\n📋 Step 4: Testing semantic content search...")
        
        search_queries = [
            f"main topics from {test_pdf.name}",
            "key concepts and important information",
            "definitions and explanations"
        ]
        
        all_search_results = []
        for query in search_queries:
            print(f"  🔍 Searching: '{query}'")
            results = document_parser.search_document_content(
                query=query,
                source_file_filter=test_pdf.name,
                top_k=3
            )
            
            print(f"     📊 Found {len(results)} relevant chunks")
            all_search_results.extend(results)
        
        # Remove duplicates based on chunk_id
        unique_results = []
        seen_ids = set()
        for result in all_search_results:
            chunk_id = result.get('chunk_id')
            if chunk_id not in seen_ids:
                unique_results.append(result)
                seen_ids.add(chunk_id)
        
        print(f"  ✅ Total unique chunks for quiz generation: {len(unique_results)}")
        
        # Step 5: Generate quiz
        print(f"\n📋 Step 5: Generating quiz from retrieved content...")
        
        if not unique_results:
            print("  ❌ No content found for quiz generation")
            return False
        
        quiz_start_time = time.time()
        
        quiz = quiz_pipeline.generate_quiz_from_context(
            retrieved_chunks=unique_results[:8],  # Use top 8 chunks
            source_file=test_pdf.name,
            quiz_title=f"AI-Generated Quiz: {test_pdf.stem}",
            num_mcq=3,  # Generate fewer questions for testing
            num_short=2
        )
        
        quiz_time = time.time() - quiz_start_time
        
        print(f"  ✅ Quiz generated successfully in {quiz_time:.2f}s")
        print(f"     🎯 Quiz ID: {quiz.id}")
        print(f"     📝 Title: {quiz.title}")
        print(f"     ❓ Total Questions: {quiz.total_questions}")
        print(f"     ⏱️ Estimated Time: {quiz.estimated_time} minutes")
        
        # Step 6: Display sample questions
        print(f"\n📋 Step 6: Sample Generated Questions")
        print("-" * 40)
        
        if quiz.mcq_questions:
            print("\n🔸 Multiple Choice Question:")
            mcq = quiz.mcq_questions[0]
            print(f"Q: {mcq.question}")
            for i, option in enumerate(mcq.options):
                marker = "✅" if i == mcq.correct_answer else "  "
                print(f"   {marker} {chr(65+i)}) {option}")
            print(f"   💡 Explanation: {mcq.explanation}")
        
        if quiz.short_questions:
            print("\n🔸 Short Answer Question:")
            sq = quiz.short_questions[0]
            print(f"Q: {sq.question}")
            print(f"   📝 Sample Answer: {sq.sample_answer}")
            print(f"   💡 Explanation: {sq.explanation}")
        
        # Step 7: Test database statistics
        print(f"\n📋 Step 7: Database Statistics")
        stats = document_parser.get_database_stats()
        print(f"  📊 Vector Database:")
        print(f"     📦 Total chunks: {stats.get('total_chunks', 0)}")
        print(f"     📂 Unique sources: {stats.get('unique_sources', 0)}")
        print(f"     📄 Source files: {', '.join(stats.get('source_files', []))}")
        
        total_time = time.time() - start_time
        print(f"\n🎉 Complete RAG Pipeline Test Successful!")
        print(f"⏱️ Total processing time: {total_time:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_sample_content(sample_text, document_parser, quiz_pipeline):
    """Test pipeline with sample text content"""
    
    print("  📝 Testing with sample AI/ML content...")
    
    try:
        # Create sample chunks manually
        from chroma_vector_db import DocumentChunk
        import uuid
        from datetime import datetime
        
        # Generate embedding for sample text
        embedding_result = document_parser.embedding_service.generate_embedding(sample_text)
        
        # Create document chunk
        chunk = DocumentChunk(
            id=str(uuid.uuid4()),
            text=sample_text,
            embedding=embedding_result.embedding,
            metadata={
                'topic': 'Artificial Intelligence and Machine Learning',
                'word_count': len(sample_text.split()),
                'char_count': len(sample_text),
                'page_type': 'text',
                'original_page_number': 1,
                'processing_timestamp': datetime.now().isoformat()
            },
            source_file="sample_ai_content.txt",
            chunk_index=0,
            created_at=datetime.now().isoformat()
        )
        
        # Store in vector database
        chunk_ids = document_parser.vector_db.add_document_chunks([chunk])
        print(f"  ✅ Sample content stored with ID: {chunk_ids[0]}")
        
        # Search for content
        search_results = document_parser.search_document_content(
            query="machine learning types and applications",
            source_file_filter="sample_ai_content.txt",
            top_k=5
        )
        
        print(f"  🔍 Found {len(search_results)} relevant chunks")
        
        # Generate quiz
        if search_results:
            quiz = quiz_pipeline.generate_quiz_from_context(
                retrieved_chunks=search_results,
                source_file="sample_ai_content.txt",
                quiz_title="AI/ML Concepts Quiz",
                num_mcq=2,
                num_short=1
            )
            
            print(f"  ✅ Quiz generated: {quiz.total_questions} questions")
            
            # Show sample question
            if quiz.mcq_questions:
                mcq = quiz.mcq_questions[0]
                print(f"\n  📝 Sample Question: {mcq.question}")
                for i, option in enumerate(mcq.options):
                    print(f"     {chr(65+i)}) {option}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"  ❌ Sample content test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting RAG Pipeline Test...")
    success = test_complete_rag_pipeline()
    
    if success:
        print("\n🎉 All tests passed! Your RAG pipeline is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    print("\n💡 Next steps:")
    print("   1. Start the API server: python gemini_api.py")
    print("   2. Upload your PDF through the API")
    print("   3. Generate quizzes from your documents")