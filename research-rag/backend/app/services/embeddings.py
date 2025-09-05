from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from ..utils.config import config

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embedding = self.model.encode([text])
        return embedding[0]
    
    def process_chunks_to_embeddings(self, chunks: List[Dict]) -> tuple:
        """
        Process chunks and return embeddings with metadata
        Returns: (embeddings_array, chunk_data_list)
        """
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        # Prepare chunk data with embeddings
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "embedding": embeddings[i]
            })
        
        return embeddings, chunk_data
