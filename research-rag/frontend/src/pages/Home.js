import React, { useState, useEffect } from 'react';
import { getDocuments, getStats, clearAllData } from '../services/api';
import '../styles/Home.css';

const Home = () => {
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [docsResponse, statsResponse] = await Promise.all([
        getDocuments(),
        getStats()
      ]);
      
      setDocuments(docsResponse.documents || []);
      setStats(statsResponse);
    } catch (err) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearData = async () => {
    if (window.confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
      try {
        await clearAllData();
        await fetchData(); // Refresh data
        alert('All data cleared successfully');
      } catch (err) {
        setError('Failed to clear data');
        console.error(err);
      }
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <button onClick={handleClearData} className="clear-data-btn">
          Clear All Data
        </button>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      {/* Statistics Cards */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-number">{stats.total_documents}</div>
            <div className="stat-label">Documents</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_chunks}</div>
            <div className="stat-label">Text Chunks</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.bm25_index_size}</div>
            <div className="stat-label">BM25 Index</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.chroma_collection_size}</div>
            <div className="stat-label">Chroma Collection</div>
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="documents-section">
        <h3>Uploaded Documents</h3>
        
        {documents.length === 0 ? (
          <div className="empty-state">
            <p>No documents uploaded yet.</p>
            <p>Upload some PDF files to get started!</p>
          </div>
        ) : (
          <div className="documents-table">
            <div className="table-header">
              <div className="header-cell">Document Name</div>
              <div className="header-cell">Pages</div>
              <div className="header-cell">Chunks</div>
              <div className="header-cell">Size</div>
              <div className="header-cell">Upload Date</div>
            </div>
            
            {documents.map((doc) => (
              <div key={doc.id} className="table-row">
                <div className="table-cell document-name">
                  <span className="file-icon">📄</span>
                  {doc.filename}
                </div>
                <div className="table-cell">{doc.total_pages}</div>
                <div className="table-cell">{doc.total_chunks}</div>
                <div className="table-cell">{formatFileSize(doc.file_size)}</div>
                <div className="table-cell">{formatDate(doc.upload_date)}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System Info */}
      <div className="system-info">
        <h3>System Information</h3>
        <div className="info-grid">
          <div className="info-item">
            <span className="info-label">Backend:</span>
            <span className="info-value">FastAPI + Python</span>
          </div>
          <div className="info-item">
            <span className="info-label">Vector Store:</span>
            <span className="info-value">ChromaDB</span>
          </div>
          <div className="info-item">
            <span className="info-label">Search:</span>
            <span className="info-value">BM25 + Embeddings</span>
          </div>
          <div className="info-item">
            <span className="info-label">LLM:</span>
            <span className="info-value">Google Gemini</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
