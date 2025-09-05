import requests
import json
from typing import List, Dict, Optional
from ..utils.config import config

class GeminiLLMService:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
    
    def generate_answer(self, query: str, context_chunks: List[Dict], max_tokens: int = 1000) -> Dict:
        """
        Generate answer using Gemini API with retrieved context
        
        Args:
            query: User's question
            context_chunks: List of relevant chunks from retrieval
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict with answer and metadata
        """
        try:
            # Prepare context from chunks
            context = self._prepare_context(context_chunks)
            
            # Create prompt
            prompt = self._create_prompt(query, context)
            
            # Call Gemini API
            response = self._call_gemini_api(prompt, max_tokens)
            
            # Process response
            answer = self._extract_answer(response)
            
            # Prepare sources
            sources = self._prepare_sources(context_chunks)
            
            return {
                "answer": answer,
                "sources": sources,
                "context_used": len(context_chunks),
                "success": True
            }
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "context_used": 0,
                "success": False,
                "error": str(e)
            }
    
    def _prepare_context(self, chunks: List[Dict]) -> str:
        """Prepare context string from retrieved chunks"""
        if not chunks:
            return "No relevant context found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            source_file = metadata.get("source_file", "Unknown")
            page_number = metadata.get("page_number", "Unknown")
            
            context_part = f"""
Context {i} (Source: {source_file}, Page: {page_number}):
{chunk.get("text", "")}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create a well-structured prompt for Gemini"""
        prompt = f"""You are a helpful AI assistant that answers questions based on provided context from PDF documents. 

CONTEXT:
{context}

QUESTION: {query}

INSTRUCTIONS:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Be specific and cite which source document and page number your answer comes from
4. Provide a clear, well-structured answer
5. If multiple sources support your answer, mention all relevant sources

ANSWER:"""
        
        return prompt
    
    def _call_gemini_api(self, prompt: str, max_tokens: int) -> Dict:
        """Make API call to Gemini"""
        url = f"{self.base_url}?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for factual responses
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": max_tokens,
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    def _extract_answer(self, response: Dict) -> str:
        """Extract answer text from Gemini response"""
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                return "I couldn't generate a response. Please try rephrasing your question."
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                return "I couldn't generate a response. Please try rephrasing your question."
            
            answer = parts[0].get("text", "").strip()
            
            if not answer:
                return "I couldn't generate a response. Please try rephrasing your question."
            
            return answer
            
        except Exception as e:
            return f"Error processing response: {str(e)}"
    
    def _prepare_sources(self, chunks: List[Dict]) -> List[Dict]:
        """Prepare source information for the response"""
        sources = []
        seen_sources = set()
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            source_file = metadata.get("source_file", "Unknown")
            page_number = metadata.get("page_number", "Unknown")
            
            # Create unique identifier for source
            source_id = f"{source_file}_{page_number}"
            
            if source_id not in seen_sources:
                sources.append({
                    "source_file": source_file,
                    "page_number": page_number,
                    "chunk_text": chunk.get("text", "")[:200] + "..." if len(chunk.get("text", "")) > 200 else chunk.get("text", ""),
                    "relevance_score": chunk.get("combined_score", chunk.get("score", 0.0))
                })
                seen_sources.add(source_id)
        
        # Sort by relevance score
        sources.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return sources
    
    def summarize_document(self, chunks: List[Dict], max_tokens: int = 500) -> Dict:
        """Generate a summary of document chunks"""
        try:
            if not chunks:
                return {
                    "summary": "No content available to summarize.",
                    "success": False
                }
            
            # Prepare content for summarization
            content = "\n\n".join([chunk.get("text", "") for chunk in chunks[:10]])  # Limit to first 10 chunks
            
            prompt = f"""Please provide a concise summary of the following document content:

CONTENT:
{content}

INSTRUCTIONS:
1. Provide a clear, structured summary
2. Highlight the main topics and key points
3. Keep the summary concise but informative
4. Use bullet points if appropriate

SUMMARY:"""
            
            response = self._call_gemini_api(prompt, max_tokens)
            summary = self._extract_answer(response)
            
            return {
                "summary": summary,
                "chunks_processed": len(chunks),
                "success": True
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "success": False,
                "error": str(e)
            }
