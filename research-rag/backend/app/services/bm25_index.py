from rank_bm25 import BM25Okapi
import pickle
import os
from typing import List, Dict, Tuple
import json

class BM25Index:
    def __init__(self, index_path: str = "./bm25_index.pkl"):
        self.index_path = index_path
        self.corpus = []
        self.bm25 = None
        self.chunk_metadata = []
        
    def build_index(self, chunks: List[Dict]):
        """Build BM25 index from text chunks"""
        # Extract text and tokenize
        corpus = []
        self.chunk_metadata = []
        
        for chunk in chunks:
            # Simple tokenization (you can improve this)
            tokens = chunk["text"].lower().split()
            corpus.append(tokens)
            self.chunk_metadata.append(chunk["metadata"])
        
        self.corpus = corpus
        self.bm25 = BM25Okapi(corpus)
        
        # Save index
        self.save_index()
    
    def save_index(self):
        """Save BM25 index to disk"""
        index_data = {
            "corpus": self.corpus,
            "chunk_metadata": self.chunk_metadata
        }
        
        with open(self.index_path, 'wb') as f:
            pickle.dump(index_data, f)
        
        # Also save metadata separately for easier access
        metadata_path = self.index_path.replace('.pkl', '_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(self.chunk_metadata, f, indent=2)
    
    def load_index(self):
        """Load BM25 index from disk"""
        if not os.path.exists(self.index_path):
            return False
            
        with open(self.index_path, 'rb') as f:
            index_data = pickle.load(f)
        
        self.corpus = index_data["corpus"]
        self.chunk_metadata = index_data["chunk_metadata"]
        self.bm25 = BM25Okapi(self.corpus)
        
        return True
    
    def search(self, query: str, top_k: int = 5, filter_criteria: Dict = None) -> List[Tuple[Dict, float]]:
        """Search using BM25 with optional filtering"""
        if not self.bm25:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Apply filtering if criteria provided
        valid_indices = []
        for idx, metadata in enumerate(self.chunk_metadata):
            if self._matches_filter(metadata, filter_criteria):
                valid_indices.append(idx)
        
        # Filter scores to only include valid indices
        if filter_criteria and valid_indices:
            filtered_scores = [(idx, scores[idx]) for idx in valid_indices if scores[idx] > 0]
            filtered_scores.sort(key=lambda x: x[1], reverse=True)
            top_results = filtered_scores[:top_k]
        else:
            # Get top results from all indices
            top_indices = scores.argsort()[-top_k:][::-1]
            top_results = [(idx, scores[idx]) for idx in top_indices if scores[idx] > 0]
        
        results = []
        for idx, score in top_results:
            chunk_text = " ".join(self.corpus[idx])
            result = {
                "text": chunk_text,
                "metadata": self.chunk_metadata[idx],
                "score": float(score)
            }
            results.append((result, score))
        
        return results
    
    def _matches_filter(self, metadata: Dict, filter_criteria: Dict) -> bool:
        """Check if metadata matches filter criteria"""
        if not filter_criteria:
            return True
        
        for key, value in filter_criteria.items():
            if key == "session_id":
                # Check if chunk has session_id in metadata or as a direct field
                chunk_session_id = metadata.get("session_id")
                if chunk_session_id != value:
                    return False
            elif key == "source":
                if isinstance(value, dict) and "$in" in value:
                    # Handle $in operator for multiple sources
                    if metadata.get("source") not in value["$in"]:
                        return False
                else:
                    if metadata.get("source") != value:
                        return False
            else:
                if metadata.get(key) != value:
                    return False
        
        return True
    
    def add_chunks(self, new_chunks: List[Dict]):
        """Add new chunks to existing index"""
        # Add to corpus
        for chunk in new_chunks:
            tokens = chunk["text"].lower().split()
            self.corpus.append(tokens)
            
            # Include session_id in metadata if present
            metadata = chunk["metadata"].copy()
            if "session_id" in chunk:
                metadata["session_id"] = chunk["session_id"]
            
            self.chunk_metadata.append(metadata)
        
        # Rebuild index
        self.bm25 = BM25Okapi(self.corpus)
        self.save_index()
