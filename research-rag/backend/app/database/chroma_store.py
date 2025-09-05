import chromadb
from chromadb.config import Settings
import numpy as np
import os
from typing import List, Dict, Tuple, Optional
import uuid
from ..utils.config import config

class ChromaStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.CHROMA_DB_PATH
        self.client = None
        self.collection = None
        self.collection_name = "pdf_chunks"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Chroma client and collection"""
        # Create directory if it doesn't exist
        os.makedirs(self.db_path, exist_ok=True)
        
        # Initialize Chroma client with persistent storage
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception:
            # Collection doesn't exist, create it
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "PDF document chunks for Q&A"}
            )
    
    def add_chunks(self, chunks: List[Dict], embeddings: Optional[np.ndarray] = None):
        """Add chunks to Chroma collection"""
        if not chunks:
            return
        
        # Prepare data for Chroma
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            # Generate unique ID for each chunk
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            # Document text
            documents.append(chunk["text"])
            
            # Metadata (Chroma requires string values)
            metadata = {
                "source_file": str(chunk["metadata"]["source_file"]),
                "page_number": str(chunk["metadata"]["page_number"]),
                "chunk_id": str(chunk["metadata"]["chunk_id"]),
                "tokens": str(chunk.get("tokens", 0))
            }
            metadatas.append(metadata)
        
        # Add to collection
        if embeddings is not None:
            # Use provided embeddings
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings.tolist()
            )
        else:
            # Let Chroma generate embeddings
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    def search(self, query: str, top_k: int = 5, query_embedding: Optional[np.ndarray] = None) -> List[Tuple[Dict, float]]:
        """Search for similar chunks"""
        if not self.collection:
            return []
        
        try:
            if query_embedding is not None:
                # Use provided embedding for search
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                # Use text query (Chroma will generate embedding)
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"]
                )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    result = {
                        "text": results["documents"][0][i],
                        "metadata": {
                            "source_file": results["metadatas"][0][i]["source_file"],
                            "page_number": int(results["metadatas"][0][i]["page_number"]),
                            "chunk_id": int(results["metadatas"][0][i]["chunk_id"]),
                            "tokens": int(results["metadatas"][0][i]["tokens"])
                        },
                        "score": 1.0 - results["distances"][0][i]  # Convert distance to similarity
                    }
                    formatted_results.append((result, result["score"]))
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching Chroma: {str(e)}")
            return []
    
    def get_collection_count(self) -> int:
        """Get number of documents in collection"""
        if not self.collection:
            return 0
        return self.collection.count()
    
    def delete_collection(self):
        """Delete the entire collection"""
        if self.collection:
            self.client.delete_collection(name=self.collection_name)
            self.collection = None
    
    def reset_collection(self):
        """Reset collection (delete and recreate)"""
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass  # Collection might not exist
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "PDF document chunks for Q&A"}
        )
    
    def get_chunk_by_metadata(self, source_file: str, page_number: int) -> List[Dict]:
        """Get chunks by source file and page number"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.get(
                where={
                    "$and": [
                        {"source_file": {"$eq": source_file}},
                        {"page_number": {"$eq": str(page_number)}}
                    ]
                },
                include=["documents", "metadatas"]
            )
            
            chunks = []
            if results["documents"]:
                for i in range(len(results["documents"])):
                    chunk = {
                        "text": results["documents"][i],
                        "metadata": {
                            "source_file": results["metadatas"][i]["source_file"],
                            "page_number": int(results["metadatas"][i]["page_number"]),
                            "chunk_id": int(results["metadatas"][i]["chunk_id"]),
                            "tokens": int(results["metadatas"][i]["tokens"])
                        }
                    }
                    chunks.append(chunk)
            
            return chunks
            
        except Exception as e:
            print(f"Error retrieving chunks: {str(e)}")
            return []
    
    def update_chunk_metadata(self, chunk_id: str, new_metadata: Dict):
        """Update metadata for a specific chunk"""
        try:
            # Convert metadata values to strings
            string_metadata = {k: str(v) for k, v in new_metadata.items()}
            
            self.collection.update(
                ids=[chunk_id],
                metadatas=[string_metadata]
            )
        except Exception as e:
            print(f"Error updating chunk metadata: {str(e)}")
