import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quiz.gemini_quiz_gen import GeminiQuizGenerator
from dotenv import load_dotenv

def test_quiz_generation():
    """Test quiz generation functionality"""
    load_dotenv()
    
    try:
        print("🧪 Testing Quiz Generation System...")
        
        # Initialize quiz generator
        generator = GeminiQuizGenerator()
        print("✅ Quiz Generator initialized successfully!")
        
        # Test sample content
        sample_content = """
        Object-Oriented Programming (OOP) is a programming paradigm based on the concept of "objects",
        which can contain data (attributes) and code (methods). The four main principles of OOP are:
        
        1. Encapsulation: Bundling data and methods that work on that data within one unit
        2. Inheritance: Creating new classes based on existing classes
        3. Polymorphism: Using one interface for different underlying forms
        4. Abstraction: Hiding complex implementation details
        """
        
        print("🎯 Generating quiz from sample content...")
        
        # Generate MCQ questions
        mcq_questions = generator.generate_mcq_questions(
            context=sample_content,
            topic="Object-Oriented Programming",
            num_questions=2
        )
        
        # Generate short questions
        short_questions = generator.generate_short_questions(
            context=sample_content,
            topic="Object-Oriented Programming", 
            num_questions=1
        )
        
        if mcq_questions or short_questions:
            print(f"✅ Quiz generated successfully!")
            print(f"   MCQ Questions: {len(mcq_questions)}")
            print(f"   Short Questions: {len(short_questions)}")
            
            # Display first MCQ question as example
            if mcq_questions:
                q1 = mcq_questions[0]
                print(f"\n📋 Sample MCQ Question:")
                print(f"   Q: {q1.question}")
                for i, option in enumerate(q1.options):
                    print(f"   {chr(65+i)}) {option}")
                print(f"   Correct Answer: {chr(65+q1.correct_answer)}")
            
            # Display first short question as example
            if short_questions:
                sq1 = short_questions[0]
                print(f"\n📝 Sample Short Question:")
                print(f"   Q: {sq1.question}")
                print(f"   Sample Answer: {sq1.sample_answer}")
            
            return True
        else:
            print("❌ Quiz generation failed - no questions generated")
            return False
            
    except Exception as e:
        print(f"❌ Quiz Generation Error: {e}")
        return False

def test_vector_database():
    """Test vector database functionality"""
    try:
        print("\n🗄️ Testing Vector Database (ChromaDB)...")
        
        from quiz.chroma_vector_db import ChromaVectorDB, DocumentChunk
        
        # Initialize vector database
        vector_db = ChromaVectorDB(collection_name="test_collection")
        print("✅ Vector Database initialized successfully!")
        
        # Test adding documents
        test_chunks = [
            DocumentChunk(
                id="test_1",
                text="Python is a high-level programming language",
                embedding=None,
                source_file="test_doc_1.txt",
                chunk_index=0,
                metadata={"topic": "Programming"},
                created_at="2025-09-15"
            ),
            DocumentChunk(
                id="test_2",
                text="JavaScript is used for web development", 
                embedding=None,
                source_file="test_doc_2.txt",
                chunk_index=0,
                metadata={"topic": "Web Development"},
                created_at="2025-09-15"
            ),
            DocumentChunk(
                id="test_3",
                text="Machine learning uses algorithms to analyze data",
                embedding=None,
                source_file="test_doc_3.txt", 
                chunk_index=0,
                metadata={"topic": "AI"},
                created_at="2025-09-15"
            )
        ]
        
        # Add documents
        ids = vector_db.add_document_chunks(test_chunks)
        print(f"✅ Test documents added to vector database: {len(ids)} chunks")
        
        # Test collection stats
        stats = vector_db.get_collection_stats()
        print(f"✅ Collection stats: {stats}")
        
        return True
            
    except Exception as e:
        print(f"❌ Vector Database Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI Features...")
    
    quiz_ok = test_quiz_generation()
    vector_ok = test_vector_database()
    
    print(f"\n📊 AI Features Test Results:")
    print(f"   Quiz Generation: {'✅' if quiz_ok else '❌'}")
    print(f"   Vector Database: {'✅' if vector_ok else '❌'}")
    
    if quiz_ok and vector_ok:
        print("\n🎉 All AI features are working correctly!")
    else:
        print("\n⚠️ Some AI features have issues!")