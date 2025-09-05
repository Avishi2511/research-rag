import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.pdf_loader import PDFLoader
from app.services.text_splitter import TextSplitter
from app.services.bm25_index import BM25Index
from app.services.embeddings import EmbeddingService
from app.database.chroma_store import ChromaStore
from app.services.retriever import HybridRetriever
from app.database.sqlite_store import SQLiteStore
from app.utils.config import config

def test_pdf_processing():
    print("Testing PDF Processing...")
    pdf_path = "sample.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Please create a sample PDF file at {pdf_path}")
        return
    
    loader = PDFLoader()
    pages_data = loader.extract_text_from_pdf(pdf_path)
    
    print(f"Extracted {len(pages_data)} pages")
    for i, page in enumerate(pages_data[:2]):
        print(f"Page {page['page_number']}: {page['text'][:200]}...")
    
    splitter = TextSplitter()
    chunks = splitter.process_pages_to_chunks(pages_data)
    
    print(f"\nCreated {len(chunks)} chunks")
    for i, chunk in enumerate(chunks[:3]):
        print(f"Chunk {i}: {chunk['text'][:150]}...")
        print(f"Tokens: {chunk['tokens']}, Metadata: {chunk['metadata']}")
        print("-" * 50)

def test_bm25_indexing():
    print("\nTesting BM25 Indexing...")
    
    sample_chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 0}
        },
        {
            "text": "Deep learning uses neural networks with multiple layers to learn patterns.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 1}
        },
        {
            "text": "Natural language processing helps computers understand human language.",
            "metadata": {"source_file": "test.pdf", "page_number": 2, "chunk_id": 2}
        }
    ]
    
    bm25_index = BM25Index("./test_bm25_index.pkl")
    bm25_index.build_index(sample_chunks)
    
    print("BM25 index built successfully!")
    
    query = "machine learning algorithms"
    results = bm25_index.search(query, top_k=2)
    
    print(f"\nSearch results for '{query}':")
    for result, score in results:
        print(f"Score: {score:.4f}")
        print(f"Text: {result['text'][:100]}...")
        print(f"Source: {result['metadata']['source_file']}, Page: {result['metadata']['page_number']}")
        print("-" * 50)

def test_chroma_and_embeddings():
    print("\nTesting Embeddings and Chroma...")
    
    sample_chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 0}
        },
        {
            "text": "Deep learning uses neural networks with multiple layers to learn patterns.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 1}
        },
        {
            "text": "Natural language processing helps computers understand human language.",
            "metadata": {"source_file": "test.pdf", "page_number": 2, "chunk_id": 2}
        }
    ]
    
    embedding_service = EmbeddingService()
    texts = [chunk["text"] for chunk in sample_chunks]
    embeddings = embedding_service.generate_embeddings(texts)
    
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    chroma_store = ChromaStore("./test_chroma_db")
    chroma_store.add_chunks(sample_chunks, embeddings)
    
    print("Chroma collection created successfully!")
    
    query = "neural networks and deep learning"
    query_embedding = embedding_service.generate_single_embedding(query)
    results = chroma_store.search(query, top_k=2, query_embedding=query_embedding)
    
    print(f"\nChroma search results for '{query}':")
    for result, score in results:
        print(f"Score: {score:.4f}")
        print(f"Source: {result['metadata']['source_file']}, Page: {result['metadata']['page_number']}")
        print("-" * 50)

def test_hybrid_retrieval():
    print("\nTesting Hybrid Retrieval...")
    
    sample_chunks = [
        {
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 0}
        },
        {
            "text": "Deep learning uses neural networks with multiple layers to learn patterns.",
            "metadata": {"source_file": "test.pdf", "page_number": 1, "chunk_id": 1}
        },
        {
            "text": "Natural language processing helps computers understand human language.",
            "metadata": {"source_file": "test.pdf", "page_number": 2, "chunk_id": 2}
        }
    ]
    
    retriever = HybridRetriever("./test_bm25_hybrid.pkl", "./test_chroma_hybrid")
    retriever.build_indices(sample_chunks)
    
    print("Hybrid indices built successfully!")
    
    query = "machine learning and neural networks"
    results = retriever.hybrid_search(query, top_k=2)
    
    print(f"\nHybrid search results for '{query}':")
    for result in results:
        print(f"Combined Score: {result['combined_score']:.4f}")
        print(f"BM25 Score: {result['bm25_score']:.4f}")
        print(f"Embedding Score: {result['embedding_score']:.4f}")
        print(f"Text: {result['text'][:100]}...")
        print(f"Source: {result['metadata']['source_file']}, Page: {result['metadata']['page_number']}")
        print("-" * 50)

def test_sqlite_store():
    print("\nTesting SQLite Store...")
    
    db_store = SQLiteStore("./test_metadata.db")
    
    doc_id = db_store.add_document("test.pdf", 5, 10, 1024000)
    print(f"Added document with ID: {doc_id}")
    
    sample_chunks = [
        {
            "text": "Sample chunk 1",
            "tokens": 50,
            "metadata": {"chunk_id": 0, "page_number": 1}
        },
        {
            "text": "Sample chunk 2", 
            "tokens": 45,
            "metadata": {"chunk_id": 1, "page_number": 1}
        }
    ]
    
    db_store.add_chunks(sample_chunks)
    print("Added chunks to database")
    
    documents = db_store.get_documents()
    print(f"Retrieved {len(documents)} documents:")
    for doc in documents:
        print(f"  {doc['filename']} - {doc['total_pages']} pages, {doc['total_chunks']} chunks")

if __name__ == "__main__":
    print("Running Component Tests...")
    print("=" * 60)
    
    # Run tests
    test_pdf_processing()
    test_bm25_indexing()
    test_chroma_and_embeddings()
    test_hybrid_retrieval()
    test_sqlite_store()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
