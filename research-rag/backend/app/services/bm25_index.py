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
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Search using BM25"""
        if not self.bm25:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get scores
        scores = self.bm25.get_scores(query_tokens)
        
        # Get top results
        top_indices = scores.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only return results with positive scores
                chunk_text = " ".join(self.corpus[idx])
                result = {
                    "text": chunk_text,
                    "metadata": self.chunk_metadata[idx],
                    "score": float(scores[idx])
                }
                results.append((result, scores[idx]))
        
        return results
    
    def add_chunks(self, new_chunks: List[Dict]):
        """Add new chunks to existing index"""
        # Add to corpus
        for chunk in new_chunks:
            tokens = chunk["text"].lower().split()
            self.corpus.append(tokens)
            self.chunk_metadata.append(chunk["metadata"])
        
        # Rebuild index
        self.bm25 = BM25Okapi(self.corpus)
        self.save_index()
