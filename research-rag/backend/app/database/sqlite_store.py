import sqlite3
import json
from typing import List, Dict, Optional
from ..utils.config import config

class SQLiteStore:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.SQLITE_DB_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables and apply migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create schema version table first
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Documents table (initial version without session_id)
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
        
        # Apply migrations
        self._apply_migrations(conn, cursor)
        
        conn.close()
    
    def _get_current_schema_version(self, cursor) -> int:
        """Get the current schema version"""
        try:
            cursor.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
        except sqlite3.OperationalError:
            # schema_version table doesn't exist, this is version 0
            return 0
    
    def _apply_migrations(self, conn, cursor):
        """Apply database migrations"""
        current_version = self._get_current_schema_version(cursor)
        
        # Migration 1: Add session_id column to documents table
        if current_version < 1:
            self._migration_001_add_session_id(cursor)
            cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
            print("Applied migration 001: Added session_id column")
        
        conn.commit()
    
    def _migration_001_add_session_id(self, cursor):
        """Migration 001: Add session_id column to documents table"""
        # Check if session_id column already exists
        cursor.execute("PRAGMA table_info(documents)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'session_id' not in columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN session_id TEXT")
            print("Added session_id column to documents table")
        else:
            print("session_id column already exists")
    
    def add_document(self, filename: str, total_pages: int, total_chunks: int, file_size: int, session_id: str = None) -> int:
        """Add document metadata and return document ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (filename, total_pages, total_chunks, file_size, session_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (filename, total_pages, total_chunks, file_size, session_id))
        
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
                "file_size": row[5],
                "session_id": row[6]
            })
        
        conn.close()
        return documents
    
    def get_documents_by_session(self, session_id: str) -> List[Dict]:
        """Get documents by session ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM documents WHERE session_id = ? ORDER BY upload_date DESC', (session_id,))
        rows = cursor.fetchall()
        
        documents = []
        for row in rows:
            documents.append({
                "id": row[0],
                "filename": row[1],
                "upload_date": row[2],
                "total_pages": row[3],
                "total_chunks": row[4],
                "file_size": row[5],
                "session_id": row[6]
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
