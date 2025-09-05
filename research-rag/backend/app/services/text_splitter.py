import tiktoken
from typing import List, Dict
from ..utils.preprocessing import TextPreprocessor
from ..utils.config import config

class TextSplitter:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.chunk_size = config.CHUNK_SIZE
        self.chunk_overlap = config.CHUNK_OVERLAP
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def split_text_into_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into chunks with metadata"""
        # Clean the text first
        cleaned_text = self.preprocessor.clean_text(text)
        
        # Split into sentences for better chunk boundaries
        sentences = self.preprocessor.split_into_sentences(cleaned_text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "tokens": current_tokens,
                    "metadata": metadata.copy()
                })
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_tokens = self.count_tokens(current_chunk)
            else:
                current_chunk += " " + sentence
                current_tokens += sentence_tokens
        
        # Add the last chunk
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "tokens": current_tokens,
                "metadata": metadata.copy()
            })
        
        return chunks
    
    def _get_overlap_text(self, text: str) -> str:
        """Get overlap text from the end of current chunk"""
        words = text.split()
        overlap_words = words[-self.chunk_overlap:] if len(words) > self.chunk_overlap else words
        return " ".join(overlap_words)
    
    def process_pages_to_chunks(self, pages_data: List[Dict]) -> List[Dict]:
        """Convert page data to chunks"""
        all_chunks = []
        chunk_id = 0
        
        for page_data in pages_data:
            metadata = {
                "source_file": page_data["source_file"],
                "page_number": page_data["page_number"],
                "chunk_id": chunk_id
            }
            
            chunks = self.split_text_into_chunks(page_data["text"], metadata)
            
            for chunk in chunks:
                chunk["metadata"]["chunk_id"] = chunk_id
                all_chunks.append(chunk)
                chunk_id += 1
        
        return all_chunks
