# Multi-PDF Q&A Assistant with Hybrid Retrieval

A full-stack web application that allows users to upload multiple PDF documents and ask questions using hybrid retrieval (BM25 + embeddings) powered by Google Gemini API.

## Features

- **Multi-PDF Upload**: Upload and process multiple PDF documents
- **Hybrid Retrieval**: Combines BM25 (keyword-based) and embeddings (semantic) search
- **AI-Powered Q&A**: Uses Google Gemini API for intelligent answer generation
- **Source Citations**: Provides references to specific documents and pages
- **Modern UI**: Clean React interface with responsive design
- **Dashboard**: View uploaded documents and system statistics

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **ChromaDB**: Vector database for embeddings
- **BM25**: Keyword-based search using rank_bm25
- **Sentence Transformers**: For generating embeddings
- **PyMuPDF**: PDF text extraction
- **SQLite**: Metadata storage
- **Google Gemini**: LLM for answer generation

### Frontend
- **React**: UI framework
- **Axios**: HTTP client
- **Plain CSS**: Custom styling

## Project Structure

```
research-rag/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── services/            # Core services
│   │   │   ├── pdf_loader.py    # PDF processing
│   │   │   ├── text_splitter.py # Text chunking
│   │   │   ├── bm25_index.py    # BM25 search
│   │   │   ├── embeddings.py    # Embedding generation
│   │   │   ├── retriever.py     # Hybrid retrieval
│   │   │   └── llm.py           # Gemini API integration
│   │   ├── database/            # Data storage
│   │   │   ├── chroma_store.py  # Vector database
│   │   │   └── sqlite_store.py  # Metadata storage
│   │   └── utils/               # Utilities
│   │       ├── config.py        # Configuration
│   │       └── preprocessing.py # Text processing
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env                     # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   └── styles/              # CSS styles
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API key
- Docker (optional)

### Method 1: Local Development

#### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Update `.env` file with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   UPLOAD_DIR=./uploads
   CHROMA_DB_PATH=./chroma_db
   SQLITE_DB_PATH=./metadata.db
   ```

4. **Run the backend:**
   ```bash
   python -m app.main
   ```
   
   The backend will be available at `http://localhost:8000`

#### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

### Method 2: Docker

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Access the application:**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

## Usage

### 1. Upload Documents
- Click on the upload area or drag and drop PDF files
- Multiple files can be uploaded simultaneously
- Files are processed automatically (text extraction, chunking, indexing)

### 2. Ask Questions
- Type your question in the chat interface
- The system will search through uploaded documents using hybrid retrieval
- Receive AI-generated answers with source citations

### 3. View Dashboard
- Switch to the Dashboard tab to see:
  - System statistics
  - List of uploaded documents
  - Collection information

## API Endpoints

### Core Endpoints

- `POST /upload` - Upload and process PDF files
- `POST /ask` - Ask questions and get answers
- `GET /documents` - List uploaded documents
- `GET /stats` - Get system statistics
- `GET /health` - Health check
- `DELETE /clear` - Clear all data

### Example API Usage

```python
import requests

# Upload PDFs
files = [('files', open('document.pdf', 'rb'))]
response = requests.post('http://localhost:8000/upload', files=files)

# Ask a question
question_data = {
    "question": "What is machine learning?",
    "top_k": 5,
    "bm25_weight": 0.5,
    "embedding_weight": 0.5
}
response = requests.post('http://localhost:8000/ask', json=question_data)
```

## Testing

### Component Testing

Run individual component tests:

```bash
cd backend
python test_components.py
```

This will test:
- PDF processing and text extraction
- BM25 indexing and search
- Embedding generation and ChromaDB
- Hybrid retrieval system
- SQLite metadata storage

### Manual Testing

1. Create a sample PDF file with some text content
2. Upload it through the web interface
3. Ask questions related to the content
4. Verify answers and source citations

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `UPLOAD_DIR` | Directory for uploaded files | `./uploads` |
| `CHROMA_DB_PATH` | ChromaDB storage path | `./chroma_db` |
| `SQLITE_DB_PATH` | SQLite database path | `./metadata.db` |

### Retrieval Parameters

- **Chunk Size**: 500 tokens per chunk
- **Chunk Overlap**: 50 tokens
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Default Weights**: BM25 (0.5) + Embeddings (0.5)

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all `__init__.py` files are present
2. **API Key Issues**: Verify Gemini API key is correctly set
3. **Port Conflicts**: Check if ports 3000/8000 are available
4. **Memory Issues**: Large PDFs may require more RAM

### Logs and Debugging

- Backend logs: Check console output when running the FastAPI server
- Frontend logs: Check browser developer console
- API documentation: Visit `http://localhost:8000/docs`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Google Gemini API for language model capabilities
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- FastAPI for the backend framework
- React for the frontend framework
