from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import tempfile
from datetime import datetime
import uuid

from .services.pdf_loader import PDFLoader
from .services.text_splitter import TextSplitter
from .services.retriever import HybridRetriever
from .services.llm import GeminiLLMService
from .database.sqlite_store import SQLiteStore
from .utils.config import config

# Initialize FastAPI app
app = FastAPI(
    title="Multi-PDF Q&A Assistant",
    description="A hybrid retrieval system for PDF question answering using BM25 and embeddings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_loader = PDFLoader()
text_splitter = TextSplitter()
retriever = HybridRetriever()
llm_service = GeminiLLMService()
db_store = SQLiteStore()

# Create upload directory
os.makedirs(config.UPLOAD_DIR, exist_ok=True)

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5
    bm25_weight: Optional[float] = 0.5
    embedding_weight: Optional[float] = 0.5
    search_scope: Optional[str] = "session"  # "session", "selected", "all"
    selected_documents: Optional[List[str]] = None
    session_id: Optional[str] = None

class QuestionResponse(BaseModel):
    answer: str
    sources: List[dict]
    context_used: int
    success: bool
    error: Optional[str] = None

class UploadResponse(BaseModel):
    message: str
    files_processed: int
    total_chunks: int
    success: bool
    session_id: str
    uploaded_files: List[str]
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Multi-PDF Q&A Assistant API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    try:
        stats = retriever.get_collection_stats()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "collections": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/upload", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Generate session ID for this upload batch
        session_id = str(uuid.uuid4())
        
        processed_files = 0
        total_chunks = 0
        all_chunks = []
        uploaded_files = []
        
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                temp_path = temp_file.name
            
            try:
                # Pass the original filename to preserve it in metadata
                pages_data = pdf_loader.extract_text_from_pdf(temp_path, file.filename)
                if not pages_data:
                    continue
                
                chunks = text_splitter.process_pages_to_chunks(pages_data)
                if chunks:
                    # Add session_id to each chunk for filtering
                    for chunk in chunks:
                        chunk['session_id'] = session_id
                    
                    all_chunks.extend(chunks)
                    total_chunks += len(chunks)
                    processed_files += 1
                    uploaded_files.append(file.filename)
                    
                    file_size = os.path.getsize(temp_path)
                    db_store.add_document(
                        filename=file.filename,
                        total_pages=len(pages_data),
                        total_chunks=len(chunks),
                        file_size=file_size,
                        session_id=session_id
                    )
                    db_store.add_chunks(chunks)
                
            finally:
                os.unlink(temp_path)
        
        if all_chunks:
            retriever.add_documents(all_chunks)
        
        return UploadResponse(
            message=f"Successfully processed {processed_files} files with {total_chunks} chunks",
            files_processed=processed_files,
            total_chunks=total_chunks,
            success=True,
            session_id=session_id,
            uploaded_files=uploaded_files
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    try:
        if not request.question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Prepare filter criteria based on search scope
        filter_criteria = None
        if request.search_scope == "session" and request.session_id:
            filter_criteria = {"session_id": request.session_id}
        elif request.search_scope == "selected" and request.selected_documents:
            filter_criteria = {"source": {"$in": request.selected_documents}}
        # For "all" scope, no filter is applied (filter_criteria remains None)
        
        retrieved_chunks = retriever.hybrid_search(
            query=request.question,
            top_k=request.top_k,
            bm25_weight=request.bm25_weight,
            embedding_weight=request.embedding_weight,
            filter_criteria=filter_criteria
        )
        
        if not retrieved_chunks:
            scope_message = ""
            if request.search_scope == "session":
                scope_message = " in the current session"
            elif request.search_scope == "selected":
                scope_message = " in the selected documents"
            
            return QuestionResponse(
                answer=f"I couldn't find any relevant information{scope_message} to answer your question.",
                sources=[],
                context_used=0,
                success=True
            )
        
        llm_response = llm_service.generate_answer(
            query=request.question,
            context_chunks=retrieved_chunks
        )
        
        return QuestionResponse(
            answer=llm_response["answer"],
            sources=llm_response["sources"],
            context_used=llm_response["context_used"],
            success=llm_response["success"],
            error=llm_response.get("error")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/documents")
async def get_documents():
    try:
        documents = db_store.get_documents()
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving documents: {str(e)}")

@app.get("/sessions/{session_id}/documents")
async def get_session_documents(session_id: str):
    try:
        documents = db_store.get_documents_by_session(session_id)
        return {"session_id": session_id, "documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session documents: {str(e)}")

@app.get("/stats")
async def get_stats():
    try:
        collection_stats = retriever.get_collection_stats()
        documents = db_store.get_documents()
        
        return {
            "total_documents": len(documents),
            "total_chunks": collection_stats.get("chroma_count", 0),
            "bm25_index_size": collection_stats.get("bm25_count", 0),
            "chroma_collection_size": collection_stats.get("chroma_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")

@app.delete("/clear")
async def clear_all_data():
    try:
        retriever.clear_indices()
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
