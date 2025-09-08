# Multi-Document RAG With Hybrid Retrieval

An advanced retrieval-augmented generation (RAG) system that enables users to upload documents and query them using natural language. The platform combines hybrid retrieval algorithms with large language models to deliver precise, context-aware answers with full source attribution and session-based document management.

## Features

- **Multi-PDF Upload**: Upload and process multiple PDF documents simultaneously
- **Hybrid Retrieval Engine**: Combines BM25 (keyword-based) and semantic embeddings for optimal search accuracy
- **Session-Based Querying**: Intelligent document scoping with session isolation and filtering
- **AI-Powered Q&A**: Uses Google Gemini API for intelligent answer generation with context
- **Source Attribution**: Complete citations with document references, page numbers, and relevance scores
- **Real-Time Processing**: Instant document ingestion with chunking and embedding generation
- **Customizable Search**: Adjustable retrieval weights and search parameters (BM25 vs embeddings)
- **Modern UI**: Clean, responsive React interface with professional research-focused design
- **RESTful API**: Complete API for integration and automation
- **Dashboard Analytics**: View uploaded documents, system statistics, and performance metrics

## 🏗️ How It Works

### Document Ingestion Pipeline

1. **Document Upload**: PDF files are uploaded through the web interface or API
2. **Text Extraction**: PyMuPDF extracts text content while preserving structure and metadata
3. **Intelligent Chunking**: Text is split into semantic chunks (500 tokens) with overlap for context preservation
4. **Dual Indexing**: 
   - **BM25 Index**: Traditional keyword-based search for exact matches
   - **Vector Embeddings**: Semantic embeddings using Sentence Transformers
5. **Metadata Storage**: Document metadata, chunks, and relationships stored in SQLite
6. **Vector Database**: Embeddings indexed in ChromaDB for fast similarity search

### Query Processing Engine

1. **Natural Language Input**: Users submit questions through the chat interface
2. **Hybrid Search**: 
   - Query processed through both BM25 and embedding models
   - Results combined using configurable weights (default: 50/50)
   - Advanced filtering by session, document scope, or recency
3. **Context Retrieval**: Top-K most relevant chunks retrieved with metadata
4. **Relevance Scoring**: Multi-factor scoring including semantic similarity and keyword matching

### Answer Generation

1. **Context Synthesis**: Retrieved chunks passed to Google Gemini LLM
2. **Intelligent Response**: LLM generates comprehensive answers using provided context
3. **Source Attribution**: Automatic citation with document names, page numbers, and relevance scores
4. **Response Formatting**: Structured output with answer, sources, and metadata

<br>
   <img width="500" height="500" alt="image" src="https://github.com/user-attachments/assets/de660578-3664-4ca3-bc1c-2530e801d589" />



## 🛠️ Technical Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  Storage Layer  │
│                 │    │                 │    │                 │
│ • Upload UI     │◄──►│ • PDF Processing│◄──►│ • ChromaDB      │
│ • Chat Interface│    │ • Hybrid Search │    │ • SQLite        │
│ • Dashboard     │    │ • LLM Integration│    │ • File System   │
│ • Session Mgmt  │    │ • Session Logic │    │ • BM25 Index    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

- **Frontend**: React 18 with modern hooks and responsive design
- **Backend**: FastAPI with async support and automatic API documentation
- **Vector Database**: ChromaDB for high-performance similarity search
- **Search Engine**: rank-bm25 for traditional keyword matching
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2) for semantic understanding
- **LLM**: Google Gemini API for answer generation
- **Storage**: SQLite for metadata and session management

## 📁 Project Structure

```
research-rag/
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── Upload.js       # File upload interface
│   │   │   ├── Chatbox.js      # Query input and processing
│   │   │   └── Answer.js       # Response display with sources
│   │   ├── pages/              # Main application pages
│   │   │   └── Home.js         # Dashboard and analytics
│   │   ├── services/           # API integration
│   │   │   └── api.js          # HTTP client and endpoints
│   │   └── styles/             # Component styling
│   ├── package.json            # Dependencies and scripts
│   └── Dockerfile              # Container configuration
├── backend/                    # Python FastAPI server
│   ├── app/
│   │   ├── main.py             # FastAPI application and routes
│   │   ├── services/           # Core business logic
│   │   │   ├── pdf_loader.py   # Document parsing and extraction
│   │   │   ├── text_splitter.py# Intelligent text chunking
│   │   │   ├── bm25_index.py   # Keyword search implementation
│   │   │   ├── embeddings.py   # Vector embedding generation
│   │   │   ├── retriever.py    # Hybrid search orchestration
│   │   │   └── llm.py          # LLM integration and prompting
│   │   ├── database/           # Data persistence layer
│   │   │   ├── chroma_store.py # Vector database operations
│   │   │   └── sqlite_store.py # Metadata and session storage
│   │   └── utils/              # Shared utilities
│   │       ├── config.py       # Environment configuration
│   │       └── preprocessing.py# Text processing utilities
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile              # Container configuration
│   └── .env                    # Environment variables
├── docker-compose.yml          # Multi-container orchestration
└── README.md                   # Project documentation
```

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+** with pip
- **Node.js 18+** with npm
- **Google Gemini API Key** ([Get one here](https://makersuite.google.com/app/apikey))
- **Docker** (optional, for containerized deployment)

### Method 1: Local Development

#### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Avishi2511/research-rag.git
cd research-rag/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your Gemini API key
```

**Environment Configuration (.env):**
```env
GEMINI_API_KEY=your_gemini_api_key_here
UPLOAD_DIR=./uploads
CHROMA_DB_PATH=./chroma_db
SQLITE_DB_PATH=./metadata.db
```

```bash
# Start the backend server
python -m app.main
# Server available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# Start development server
npm start
# Application available at http://localhost:3000
```

### Method 2: Docker Deployment

```bash
# Clone and navigate to project
git clone https://github.com/Avishi2511/research-rag.git
cd research-rag

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Build and run with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```


## 🔧 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload and process PDF documents |
| `POST` | `/ask` | Submit questions and get AI-generated answers |
| `GET` | `/documents` | List all uploaded documents |
| `GET` | `/stats` | Get system statistics and metrics |
| `GET` | `/health` | Health check and system status |
| `DELETE` | `/clear` | Clear all data and reset system |

### Request/Response Examples

**Upload Documents:**
```json
// Request: POST /upload (multipart/form-data)
// Response:
{
  "message": "Successfully processed 2 files with 45 chunks",
  "files_processed": 2,
  "total_chunks": 45,
  "success": true,
  "session_id": "uuid-string",
  "uploaded_files": ["document1.pdf", "document2.pdf"]
}
```

**Ask Question:**
```json
// Request: POST /ask
{
  "question": "What is the methodology used in the study?",
  "top_k": 5,
  "bm25_weight": 0.5,
  "embedding_weight": 0.5,
  "search_scope": "session",
  "session_id": "uuid-string"
}

// Response:
{
  "answer": "The study employs a mixed-methods approach...",
  "sources": [
    {
      "source": "research_paper.pdf",
      "page": 3,
      "content": "Our methodology combines quantitative...",
      "relevance_score": 0.89
    }
  ],
  "context_used": 3,
  "success": true
}
```

## ⚙️ Configuration & Tuning

### Retrieval Parameters

```python
# Adjust search weights for different use cases
{
  "bm25_weight": 0.7,      # Higher for keyword-heavy queries
  "embedding_weight": 0.3,  # Lower for exact term matching
  "top_k": 10              # More context for complex questions
}

# For semantic queries
{
  "bm25_weight": 0.3,      # Lower for conceptual queries
  "embedding_weight": 0.7,  # Higher for semantic understanding
  "top_k": 5               # Focused context
}
```

### Text Processing Settings

- **Chunk Size**: 500 tokens (optimal for most documents)
- **Chunk Overlap**: 50 tokens (maintains context continuity)
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Max Document Size**: 50MB per file

### Performance Optimization

```env
# Environment variables for optimization
CHUNK_SIZE=500
CHUNK_OVERLAP=50
MAX_CONCURRENT_UPLOADS=5
EMBEDDING_BATCH_SIZE=32
VECTOR_SEARCH_TIMEOUT=30
```


### Development Setup

```bash
# Fork the repository
git clone https://github.com/yourusername/research-rag.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
# Submit pull request
```
