import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./metadata.db")
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is required")

config = Config()
