"""
Educational RAG Pipeline - Strict Educational Content Only
=========================================================

This pipeline ONLY responds to educational questions about uploaded PDFs.
It validates queries and ensures responses are strictly educational.

Features:
- Validates if query is educational
- Checks if query relates to uploaded content
- Rejects non-educational queries politely
- Only generates responses from PDF content
"""

import os
import re
import chromadb
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import uuid
from pathlib import Path
import PyPDF2
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EducationalQueryValidator:
    """Validates if queries are educational and relevant to uploaded content"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Educational keywords and patterns - expanded and improved
        self.educational_keywords = {
            'concepts': ['concept', 'definition', 'meaning', 'what is', 'explain', 'describe', 'theory', 'principle', 'idea', 'notion'],
            'learning': ['learn', 'study', 'understand', 'knowledge', 'education', 'teaching', 'instruction', 'training'],
            'academic': ['subject', 'course', 'module', 'chapter', 'lesson', 'topic', 'curriculum', 'syllabus', 'material', 'content'],
            'questions': ['how', 'why', 'what', 'when', 'where', 'which', 'who', 'can you', 'tell me', 'help me'],
            'analysis': ['analyze', 'compare', 'evaluate', 'discuss', 'examine', 'assess', 'review', 'identify'],
            'processes': ['process', 'method', 'procedure', 'approach', 'technique', 'way', 'steps', 'implementation'],
            'systems': ['system', 'model', 'framework', 'structure', 'design', 'architecture', 'pattern'],
            'requirements': ['requirement', 'specification', 'criteria', 'standard', 'guideline', 'rule'],
            'development': ['development', 'engineering', 'analysis', 'design', 'implementation', 'testing'],
            'stakeholders': ['stakeholder', 'user', 'client', 'customer', 'actor', 'participant', 'role']
        }
        
        # Non-educational patterns to reject
        self.non_educational_patterns = [
            r'\b(weather|movie|game|sports|celebrity|entertainment)\b',
            r'\b(shopping|buy|sell|price|money|financial)\b',
            r'\b(personal|private|relationship|dating)\b',
            r'\b(politics|political|government|election)\b',
            r'\b(religion|religious|spiritual)\b',
            r'\b(gossip|news|current events)\b'
        ]
    
    def is_educational_query(self, query: str) -> Tuple[bool, str]:
        """
        Enhanced validation if query is educational with multiple validation layers
        Returns: (is_educational, reason)
        """
        try:
            query_lower = query.lower().strip()
            
            # Quick rejection for obvious non-educational patterns
            for pattern in self.non_educational_patterns:
                if re.search(pattern, query_lower):
                    return False, "Query contains non-educational content patterns"
            
            # Enhanced educational keyword scoring
            educational_score = 0
            matched_categories = []
            
            for category, keywords in self.educational_keywords.items():
                category_matches = 0
                for keyword in keywords:
                    if keyword in query_lower:
                        category_matches += 1
                        educational_score += 1
                if category_matches > 0:
                    matched_categories.append(category)
            
            # Context-based validation - expanded
            academic_context_indicators = [
                'course', 'module', 'chapter', 'lesson', 'syllabus', 'curriculum',
                'assignment', 'homework', 'exam', 'test', 'quiz', 'study',
                'lecture', 'notes', 'textbook', 'material', 'content', 'document',
                'pdf', 'bcs501', 'establishing', 'groundwork', 'stakeholder',
                'requirement', 'engineering', 'software', 'system', 'analysis',
                'design', 'model', 'use case', 'actor', 'function', 'deployment'
            ]
            
            context_score = sum(1 for indicator in academic_context_indicators if indicator in query_lower)
            
            # Question type analysis - more comprehensive
            question_patterns = [
                r'\bwhat\s+(is|are|do|does|can|will|would|about)\b',
                r'\bhow\s+(to|do|does|can|will|would|is|are)\b',
                r'\bwhy\s+(is|are|do|does|did|would)\b',
                r'\bwhen\s+(is|are|do|does|did|will)\b',
                r'\bwhere\s+(is|are|do|does|can)\b',
                r'\bwhich\s+(is|are|do|does|would)\b',
                r'\bexplain\b', r'\bdescribe\b', r'\bdefine\b', r'\bdiscuss\b',
                r'\btell me about\b', r'\bcan you\b', r'\bhelp me\b',
                r'\bidentify\b', r'\bestablish\b', r'\blist\b'
            ]
            
            has_question_pattern = any(re.search(pattern, query_lower) for pattern in question_patterns)
            
            # Combined scoring with lower thresholds for better acceptance
            total_score = educational_score + (context_score * 1.5) + (1.5 if has_question_pattern else 0)
            
            # Much more lenient threshold logic
            if total_score >= 2 or len(matched_categories) >= 1:
                return True, f"Educational query detected (score: {total_score}, categories: {matched_categories})"
            elif context_score > 0 or has_question_pattern:
                # More lenient - accept if has any context or question pattern
                return True, f"Educational context detected (context_score: {context_score}, question_pattern: {has_question_pattern})"
            elif educational_score > 0:
                # Accept any query with educational keywords
                return True, f"Educational keywords found (score: {educational_score})"
            else:
                # Use AI validation as fallback for borderline cases
                return self._ai_validate_educational(query)
            
        except Exception as e:
            logger.error(f"Error validating query: {e}")
            # Default to accepting educational queries on error
            return True, "Validation error - defaulting to educational"
    
    def _ai_validate_educational(self, query: str) -> Tuple[bool, str]:
        """Use AI to validate if query is educational"""
        try:
            validation_prompt = f"""
Analyze this query and determine if it's educational/academic in nature:

Query: "{query}"

Educational queries include:
- Questions about concepts, theories, definitions, processes
- Academic subjects and learning topics (including technical topics)
- How-to questions related to study/learning/understanding
- Questions about course content, educational materials, or documents
- Questions about systems, methods, procedures, requirements
- Questions about stakeholders, actors, users, roles
- Questions starting with "discuss", "explain", "identify", "establish"
- Any question that seeks to learn or understand something

Be LENIENT - if there's any educational aspect, respond YES.

Respond with ONLY "YES" or "NO" followed by a brief reason.

Response format: YES/NO - reason
"""
            
            response = self.model.generate_content(validation_prompt)
            result = response.text.strip()
            
            if result.startswith("YES"):
                return True, "AI validated as educational"
            else:
                # Even if AI says no, be more lenient for borderline cases
                if any(word in query.lower() for word in ['what', 'how', 'why', 'explain', 'discuss', 'identify', 'establish', 'stakeholder']):
                    return True, "Lenient validation - contains educational question words"
                return False, "AI determined non-educational"
                
        except Exception as e:
            logger.error(f"AI validation error: {e}")
            # Default to accepting on error
            return True, "AI validation failed - defaulting to educational"

class EducationalVectorDB:
    """Vector database specifically for educational content"""
    
    def __init__(self, collection_name: str = "educational_content"):
        try:
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            
            genai.configure(api_key=self.api_key)
            self.embedding_model = 'models/text-embedding-004'
            
            # Initialize ChromaDB
            chatbot_dir = Path(__file__).parent
            chroma_path = chatbot_dir / "educational_chroma_db"
            chroma_path.mkdir(exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(path=str(chroma_path))
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(collection_name)
                logger.info(f"✅ Connected to existing educational collection: {collection_name}")
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=collection_name,
                    metadata={"description": "Educational content from PDFs"}
                )
                logger.info(f"✅ Created new educational collection: {collection_name}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize EducationalVectorDB: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate high-quality embedding using Gemini with educational focus"""
        try:
            text = text.strip()
            if not text:
                raise ValueError("Empty text provided for embedding")
            
            # Enhance text with educational context for better embeddings
            educational_prefix = "Educational content: "
            enhanced_text = educational_prefix + text
            
            # Generate embedding with document retrieval task
            result = genai.embed_content(
                model=self.embedding_model,
                content=enhanced_text,
                task_type="retrieval_document",
                title="Educational Course Material"
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def extract_pdf_content(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract content from PDF with educational focus"""
        try:
            content_chunks = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text()
                    
                    if text.strip() and len(text.strip()) > 50:  # Only meaningful content
                        # Clean and prepare text
                        cleaned_text = self._clean_educational_text(text)
                        
                        if cleaned_text:
                            content_chunks.append({
                                "content": cleaned_text,
                                "page": page_num,
                                "source_file": Path(pdf_path).name,
                                "type": "educational_content"
                            })
            
            logger.info(f"✅ Extracted {len(content_chunks)} educational pages from PDF")
            return content_chunks
            
        except Exception as e:
            logger.error(f"Error extracting PDF content: {e}")
            return []
    
    def _clean_educational_text(self, text: str) -> str:
        """Clean and prepare educational text"""
        try:
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Remove page numbers and headers/footers (basic patterns)
            text = re.sub(r'\bPage \d+\b', '', text)
            text = re.sub(r'\d+\s*$', '', text)  # Remove trailing page numbers
            
            # Keep only text that seems educational
            if len(text) < 100:  # Too short to be meaningful educational content
                return ""
            
            # Check if content seems educational
            educational_indicators = [
                'definition', 'concept', 'theory', 'principle', 'method', 'algorithm',
                'chapter', 'section', 'example', 'figure', 'table', 'formula',
                'introduction', 'conclusion', 'summary', 'objective', 'learning'
            ]
            
            text_lower = text.lower()
            if any(indicator in text_lower for indicator in educational_indicators):
                return text
            
            # If it's long enough and doesn't contain obvious non-educational content
            non_educational = ['advertisement', 'commercial', 'sale', 'buy now']
            if not any(term in text_lower for term in non_educational):
                return text
            
            return ""
            
        except Exception as e:
            logger.error(f"Error cleaning text: {e}")
            return text
    
    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 75) -> List[str]:
        """Split text into optimized educational chunks with better overlap"""
        try:
            if not text or len(text.strip()) < 50:
                return []
            
            # Clean and normalize text
            text = re.sub(r'\s+', ' ', text.strip())
            
            # Split into sentences first for better chunk boundaries
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= 3:  # Short content, return as single chunk
                return [text]
            
            chunks = []
            current_chunk = []
            current_word_count = 0
            
            for sentence in sentences:
                sentence_words = sentence.split()
                
                # If adding this sentence would exceed chunk size, save current chunk
                if current_word_count + len(sentence_words) > chunk_size and current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if len(chunk_text.strip()) > 100:  # Only meaningful chunks
                        chunks.append(chunk_text.strip())
                    
                    # Start new chunk with overlap (keep last few sentences)
                    overlap_sentences = current_chunk[-2:] if len(current_chunk) > 2 else current_chunk
                    current_chunk = overlap_sentences + [sentence]
                    current_word_count = sum(len(s.split()) for s in current_chunk)
                else:
                    current_chunk.append(sentence)
                    current_word_count += len(sentence_words)
            
            # Add the last chunk
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text.strip()) > 100:
                    chunks.append(chunk_text.strip())
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [text] if text else []
    
    def add_educational_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Add educational PDF to the knowledge base"""
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                return {"success": False, "error": f"PDF file not found: {pdf_path}"}
            
            # Extract educational content
            extracted_pages = self.extract_pdf_content(str(pdf_path))
            
            if not extracted_pages:
                return {"success": False, "error": "No educational content could be extracted"}
            
            # Process and store chunks
            documents = []
            metadatas = []
            ids = []
            embeddings = []
            
            total_chunks = 0
            
            for page_data in extracted_pages:
                chunks = self.chunk_text(page_data["content"])
                
                for chunk_idx, chunk in enumerate(chunks):
                    try:
                        # Generate embedding
                        embedding = self.generate_embedding(chunk)
                        
                        # Create unique ID
                        doc_id = f"edu_{pdf_path.stem}_p{page_data['page']}_c{chunk_idx}_{uuid.uuid4().hex[:8]}"
                        
                        documents.append(chunk)
                        embeddings.append(embedding)
                        ids.append(doc_id)
                        
                        # Create metadata
                        metadata = {
                            "source_file": pdf_path.name,
                            "page": page_data["page"],
                            "chunk_index": chunk_idx,
                            "content_type": "educational",
                            "timestamp": datetime.now().isoformat(),
                            "word_count": len(chunk.split()),
                            "file_path": str(pdf_path)
                        }
                        
                        metadatas.append(metadata)
                        total_chunks += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to process chunk {chunk_idx}: {e}")
                        continue
            
            if not documents:
                return {"success": False, "error": "No valid educational chunks could be created"}
            
            # Add to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )
            
            logger.info(f"✅ Added {total_chunks} educational chunks from {pdf_path.name}")
            
            return {
                "success": True,
                "chunks_added": total_chunks,
                "file_name": pdf_path.name,
                "pages_processed": len(extracted_pages)
            }
            
        except Exception as e:
            logger.error(f"Error adding educational PDF: {e}")
            return {"success": False, "error": str(e)}
    
    def search_educational_content(self, query: str, top_k: int = 8) -> List[Dict[str, Any]]:
        """Enhanced search for educational content with query expansion"""
        try:
            if not query.strip():
                return []
            
            # Expand query with educational synonyms and context
            expanded_query = self._expand_educational_query(query)
            
            # Generate embedding for the expanded query
            query_embedding = self.generate_embedding(expanded_query)
            
            # Search collection with more results for better filtering
            search_count = min(top_k * 2, max(10, self.collection.count()))
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=search_count,
                include=["documents", "metadatas", "distances"]
            )
            
            # Enhanced filtering and ranking
            educational_chunks = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i]
                    similarity_score = 1 - distance
                    content = results["documents"][0][i]
                    
                    # Calculate relevance score with multiple factors
                    relevance_score = self._calculate_relevance_score(
                        query, content, similarity_score
                    )
                    
                    # Include chunks with good relevance
                    if relevance_score > 0.15:  # Adaptive threshold
                        chunk = {
                            "content": content,
                            "source_file": results["metadatas"][0][i].get("source_file", "Unknown"),
                            "page": results["metadatas"][0][i].get("page", 0),
                            "similarity_score": similarity_score,
                            "relevance_score": relevance_score,
                            "chunk_index": results["metadatas"][0][i].get("chunk_index", 0)
                        }
                        educational_chunks.append(chunk)
            
            # Sort by relevance score and return top results
            educational_chunks.sort(key=lambda x: x["relevance_score"], reverse=True)
            final_chunks = educational_chunks[:top_k]
            
            logger.info(f"✅ Found {len(final_chunks)} high-relevance educational chunks")
            return final_chunks
            
        except Exception as e:
            logger.error(f"Error searching educational content: {e}")
            return []
    
    def _expand_educational_query(self, query: str) -> str:
        """Expand query with educational context and synonyms"""
        try:
            # Educational query expansion mapping
            expansions = {
                'definition': ['meaning', 'explanation', 'concept', 'what is'],
                'explain': ['describe', 'clarify', 'elaborate', 'detail'],
                'process': ['method', 'procedure', 'steps', 'approach'],
                'types': ['kinds', 'categories', 'classifications', 'varieties'],
                'examples': ['instances', 'cases', 'illustrations', 'samples'],
                'principles': ['rules', 'fundamentals', 'basics', 'foundations'],
                'advantages': ['benefits', 'pros', 'strengths', 'merits'],
                'disadvantages': ['drawbacks', 'cons', 'limitations', 'weaknesses']
            }
            
            query_lower = query.lower()
            expanded_terms = [query]
            
            # Add relevant expansions
            for key, synonyms in expansions.items():
                if key in query_lower:
                    expanded_terms.extend(synonyms[:2])  # Add top 2 synonyms
            
            # Create expanded query
            expanded_query = f"Educational topic: {' '.join(expanded_terms)}"
            return expanded_query
            
        except Exception:
            return query
    
    def _calculate_relevance_score(self, query: str, content: str, similarity_score: float) -> float:
        """Calculate enhanced relevance score using multiple factors"""
        try:
            query_lower = query.lower()
            content_lower = content.lower()
            
            # Base similarity score (0.0 - 1.0)
            relevance = similarity_score * 0.6
            
            # Keyword matching bonus (0.0 - 0.3)
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            content_words = set(re.findall(r'\b\w+\b', content_lower))
            
            if query_words:
                keyword_overlap = len(query_words.intersection(content_words)) / len(query_words)
                relevance += keyword_overlap * 0.3
            
            # Educational content quality bonus (0.0 - 0.1)
            educational_indicators = [
                'definition', 'concept', 'principle', 'method', 'process',
                'example', 'important', 'key', 'main', 'primary', 'essential',
                'fundamental', 'basic', 'advanced', 'theory', 'practice'
            ]
            
            educational_score = sum(1 for indicator in educational_indicators 
                                  if indicator in content_lower) / len(educational_indicators)
            relevance += educational_score * 0.1
            
            return min(relevance, 1.0)  # Cap at 1.0
            
        except Exception:
            return similarity_score
    
    def get_content_stats(self) -> Dict[str, Any]:
        """Get statistics about educational content"""
        try:
            count = self.collection.count()
            
            if count == 0:
                return {
                    "total_chunks": 0,
                    "source_files": [],
                    "pages_count": 0
                }
            
            # Get sample to analyze sources
            sample_results = self.collection.get(limit=min(count, 50))
            
            sources = set()
            if sample_results["metadatas"]:
                for meta in sample_results["metadatas"]:
                    sources.add(meta.get("source_file", "Unknown"))
            
            return {
                "total_chunks": count,
                "source_files": list(sources),
                "unique_sources": len(sources)
            }
            
        except Exception as e:
            logger.error(f"Error getting content stats: {e}")
            return {"error": str(e)}

class EducationalChatbot:
    """Chatbot that ONLY responds to educational queries about uploaded PDFs"""
    
    def __init__(self, vector_db: EducationalVectorDB):
        self.vector_db = vector_db
        self.validator = EducationalQueryValidator()
        
        # Configure Gemini model
        self.api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Educational response templates
        self.rejection_messages = [
            "I'm sorry, but I can only help with educational questions related to the uploaded course materials. Please ask about the content in your PDFs.",
            "I'm designed to assist only with academic and educational topics from your uploaded documents. Could you please ask about the course content?",
            "I can only provide information about the educational materials you've uploaded. Please ask questions related to your course PDFs.",
            "My purpose is to help with learning from your uploaded educational content. Please ask questions about the academic materials."
        ]
    
    def chat_response(self, query: str) -> Dict[str, Any]:
        """
        Generate highly accurate response only for educational queries about PDF content
        """
        try:
            # Step 1: Enhanced educational validation
            is_educational, validation_reason = self.validator.is_educational_query(query)
            
            if not is_educational:
                import random
                return {
                    "answer": random.choice(self.rejection_messages),
                    "is_educational": False,
                    "reason": validation_reason,
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 2: Enhanced search for relevant educational content
            relevant_chunks = self.vector_db.search_educational_content(query, top_k=8)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information about your question in the uploaded educational materials. Please make sure your question relates to the content in your PDFs, or try rephrasing your question with more specific terms.",
                    "is_educational": True,
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 3: Generate enhanced educational response
            response_data = self._generate_enhanced_response(query, relevant_chunks)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error in chat response: {e}")
            return {
                "answer": "I encountered an error while processing your educational question. Please try rephrasing your question or check that it relates to your uploaded course materials.",
                "is_educational": False,
                "sources": [],
                "confidence": 0.0
            }
    
    def _generate_enhanced_response(self, query: str, relevant_chunks: List[Dict]) -> Dict[str, Any]:
        """Generate enhanced response with better context and accuracy"""
        try:
            # Sort chunks by relevance score for better context ordering
            sorted_chunks = sorted(relevant_chunks, key=lambda x: x.get("relevance_score", x.get("similarity_score", 0)), reverse=True)
            
            # Create rich context with chunk prioritization
            primary_context = "\n\n".join([chunk["content"] for chunk in sorted_chunks[:3]])
            supporting_context = "\n\n".join([chunk["content"] for chunk in sorted_chunks[3:6]])
            
            # Enhanced educational prompt with better instructions
            educational_prompt = f"""
You are an expert educational assistant helping students learn from their course materials.

PRIMARY CONTEXT (Most Relevant):
{primary_context}

SUPPORTING CONTEXT (Additional Information):
{supporting_context}

Student Question: {query}

INSTRUCTIONS FOR ACCURATE RESPONSE:
1. Answer ONLY based on the provided educational context above
2. If the context doesn't contain sufficient information, clearly state this
3. Use specific details and examples from the context when available
4. Structure your response clearly with bullet points or numbered lists when appropriate
5. Use educational language appropriate for academic learning
6. If you mention concepts, provide brief definitions from the context
7. Include relevant page references when discussing specific points
8. If the question asks for examples, provide them from the context
9. If the question asks for definitions, use exact wording from the materials when possible
10. Do NOT add information not present in the context

Educational Response:
"""
            
            try:
                response = self.model.generate_content(educational_prompt)
                answer = response.text.strip()
                
                # Calculate enhanced confidence based on multiple factors
                confidence = self._calculate_response_confidence(query, relevant_chunks, answer)
                
                # Enhance sources with better metadata
                enhanced_sources = self._enhance_source_information(relevant_chunks)
                
                return {
                    "answer": answer,
                    "is_educational": True,
                    "sources": enhanced_sources,
                    "confidence": confidence,
                    "context_used": len(relevant_chunks),
                    "primary_sources": len(sorted_chunks[:3]),
                    "query_expansion": True
                }
                
            except Exception as e:
                logger.error(f"Error generating enhanced response: {e}")
                return {
                    "answer": "I encountered an error while generating a response to your educational question. The information is available in your materials, but I'm having trouble processing it right now. Please try rephrasing your question.",
                    "is_educational": True,
                    "sources": relevant_chunks,
                    "confidence": 0.0
                }
            
        except Exception as e:
            logger.error(f"Error in enhanced response generation: {e}")
            return {
                "answer": "I encountered an error while processing your question.",
                "is_educational": True,
                "sources": [],
                "confidence": 0.0
            }
    
    def _calculate_response_confidence(self, query: str, chunks: List[Dict], answer: str) -> float:
        """Calculate enhanced confidence score for the response"""
        try:
            if not chunks:
                return 0.0
            
            # Base confidence from chunk relevance scores
            avg_relevance = sum(chunk.get("relevance_score", chunk.get("similarity_score", 0)) for chunk in chunks) / len(chunks)
            confidence = avg_relevance * 0.6
            
            # Answer quality factors
            answer_lower = answer.lower()
            query_lower = query.lower()
            
            # Query-answer alignment (0.0 - 0.2)
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            answer_words = set(re.findall(r'\b\w+\b', answer_lower))
            
            if query_words:
                word_overlap = len(query_words.intersection(answer_words)) / len(query_words)
                confidence += word_overlap * 0.2
            
            # Response completeness (0.0 - 0.1)
            if len(answer) > 100 and not any(phrase in answer_lower for phrase in [
                "i don't know", "i'm not sure", "unclear", "insufficient information"
            ]):
                confidence += 0.1
            
            # Educational language quality (0.0 - 0.1)
            educational_terms = [
                'concept', 'definition', 'principle', 'method', 'process',
                'example', 'important', 'theory', 'practice', 'analysis'
            ]
            edu_score = sum(1 for term in educational_terms if term in answer_lower) / len(educational_terms)
            confidence += edu_score * 0.1
            
            return min(confidence, 1.0)
            
        except Exception:
            return 0.5  # Default moderate confidence
    
    def _enhance_source_information(self, chunks: List[Dict]) -> List[Dict[str, Any]]:
        """Enhance source information with better metadata"""
        try:
            enhanced_sources = []
            
            for chunk in chunks:
                enhanced_source = {
                    "content": chunk["content"][:300] + "..." if len(chunk["content"]) > 300 else chunk["content"],
                    "source_file": chunk.get("source_file", "Unknown"),
                    "page": chunk.get("page", 0),
                    "similarity_score": chunk.get("similarity_score", 0),
                    "relevance_score": chunk.get("relevance_score", chunk.get("similarity_score", 0)),
                    "chunk_index": chunk.get("chunk_index", 0),
                    "word_count": len(chunk["content"].split()) if chunk.get("content") else 0
                }
                enhanced_sources.append(enhanced_source)
            
            return enhanced_sources
            
        except Exception as e:
            logger.error(f"Error enhancing source information: {e}")
            return chunks
    
    def get_educational_summary(self) -> Dict[str, Any]:
        """Get summary of available educational content"""
        try:
            stats = self.vector_db.get_content_stats()
            
            summary = f"""
📚 Educational Content Available:
- {stats.get('total_chunks', 0)} content chunks processed
- {stats.get('unique_sources', 0)} PDF documents uploaded
- Source files: {', '.join(stats.get('source_files', []))}

💡 You can ask me about:
- Concepts and definitions from your course materials
- Explanations of topics covered in the PDFs
- Examples and illustrations from the documents
- Learning questions about the academic content

❌ I cannot help with:
- Non-educational topics
- Personal questions
- Content not in your uploaded PDFs
- General knowledge outside your course materials
"""
            
            return {
                "summary": summary,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error generating educational summary: {e}")
            return {
                "summary": "Educational content summary not available",
                "stats": {}
            }

# Example usage and testing
if __name__ == "__main__":
    try:
        print("🎓 Educational RAG Pipeline - Testing")
        print("="*50)
        
        # Initialize components
        print("1️⃣ Initializing educational pipeline...")
        vector_db = EducationalVectorDB()
        chatbot = EducationalChatbot(vector_db)
        
        # Check current content
        stats = vector_db.get_content_stats()
        print(f"📊 Current content: {stats.get('total_chunks', 0)} chunks from {stats.get('unique_sources', 0)} sources")
        
        if stats.get('source_files'):
            print(f"📄 Available PDFs: {', '.join(stats['source_files'])}")
        else:
            print("⚠️ No educational content found. Upload PDFs first!")
        
        # Interactive testing
        print("\n3️⃣ Educational Chat Testing")
        print("💡 Ask educational questions about your uploaded PDFs")
        print("💡 Try non-educational questions to see rejection")
        print("💡 Type 'quit' to exit")
        
        while True:
            print("\n" + "-"*50)
            user_query = input("📝 Your question: ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                print("⚠️ Please enter a question!")
                continue
            
            print("🤔 Processing...")
            response = chatbot.chat_response(user_query)
            
            print(f"\n🤖 Response:")
            print(f"📚 Educational: {'Yes' if response['is_educational'] else 'No'}")
            print(f"💬 Answer: {response['answer']}")
            
            if response.get('sources'):
                print(f"\n📖 Sources ({len(response['sources'])} found):")
                for i, source in enumerate(response['sources'][:2], 1):
                    print(f"   {i}. {source['source_file']} (Page {source['page']}, Score: {source['similarity_score']:.2f})")
            
            if response.get('confidence', 0) > 0:
                confidence = response['confidence']
                if confidence > 0.7:
                    print(f"✅ High confidence: {confidence:.2%}")
                elif confidence > 0.5:
                    print(f"📊 Medium confidence: {confidence:.2%}")
                else:
                    print(f"⚠️ Lower confidence: {confidence:.2%}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Educational pipeline error")