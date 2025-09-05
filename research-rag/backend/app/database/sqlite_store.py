import sqlite3
import json
from typing import List, Dict, Optional
from ..utils.config import config

class SQLiteStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.SQLITE_DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_pages INTEGER,
                total_chunks INTEGER,
                file_size INTEGER
            )
        ''')
        
        # Chunks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                chunk_id INTEGER,
                page_number INTEGER,
                text TEXT,
                token_count INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_document(self, filename: str, total_pages: int, total_chunks: int, file_size: int) -> int:
        """Add document metadata and return document ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (filename, total_pages, total_chunks, file_size)
            VALUES (?, ?, ?, ?)
        ''', (filename, total_pages, total_chunks, file_size))
        
        document_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return document_id
    
    def add_chunks(self, chunks: List[Dict]):
        """Add chunk metadata to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for chunk in chunks:
            metadata = chunk["metadata"]
            cursor.execute('''
                INSERT INTO chunks (chunk_id, page_number, text, token_count)
                VALUES (?, ?, ?, ?)
            ''', (
                metadata["chunk_id"],
                metadata["page_number"],
                chunk["text"],
                chunk.get("tokens", 0)
            ))
        
        conn.commit()
        conn.close()
    
    def get_documents(self) -> List[Dict]:
        """Get all documents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents ORDER BY upload_date DESC')
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "filename": row[1],
                "upload_date": row[2],
                "total_pages": row[3],
                "total_chunks": row[4],
                "file_size": row[5]
            })
        
        conn.close()
        return documents
    
    def get_chunk_by_id(self, chunk_id: int) -> Optional[Dict]:
        """Get chunk by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM chunks WHERE chunk_id = ?', (chunk_id,))
        row = cursor.fetchone()
        
        if row:
            chunk = {
                "id": row[0],
                "document_id": row[1],
                "chunk_id": row[2],
                "page_number": row[3],
                "text": row[4],
                "token_count": row[5],
                "created_date": row[6]
            }
        else:
            chunk = None
        
        conn.close()
        return chunk
