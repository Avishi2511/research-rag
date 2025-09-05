import React, { useState, useRef } from 'react';
import { uploadPDFs } from '../services/api';
import '../styles/Upload.css';

const Upload = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    const pdfFiles = selectedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== selectedFiles.length) {
      setUploadStatus('Only PDF files are allowed');
      setTimeout(() => setUploadStatus(''), 3000);
    }
    
    setFiles(pdfFiles);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    const pdfFiles = droppedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length !== droppedFiles.length) {
      setUploadStatus('Only PDF files are allowed');
      setTimeout(() => setUploadStatus(''), 3000);
    }
    
    setFiles(pdfFiles);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setUploadStatus('Please select files to upload');
      return;
    }

    setUploading(true);
    setUploadStatus('Uploading and processing files...');

    try {
      const response = await uploadPDFs(files);
      setUploadStatus(`Successfully processed ${response.files_processed} files with ${response.total_chunks} chunks`);
      setFiles([]);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      onUploadSuccess(response);
    } catch (error) {
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setUploading(false);
    }
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  return (
    <div className="upload-container">
      <h2>Upload PDF Documents</h2>
      
      <div 
        className="drop-zone"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <div className="drop-zone-content">
          <p>Drag and drop PDF files here, or</p>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelect}
            className="file-input"
            id="file-input"
          />
          <label htmlFor="file-input" className="file-input-label">
            Choose Files
          </label>
        </div>
      </div>

      {files.length > 0 && (
        <div className="file-list">
          <h3>Selected Files:</h3>
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <span className="file-name">{file.name}</span>
              <span className="file-size">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
              <button 
                onClick={() => removeFile(index)}
                className="remove-file-btn"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      <button 
        onClick={handleUpload}
        disabled={uploading || files.length === 0}
        className="upload-btn"
      >
        {uploading ? 'Processing...' : 'Upload and Process'}
      </button>

      {uploadStatus && (
        <div className={`upload-status ${uploadStatus.includes('failed') ? 'error' : 'success'}`}>
          {uploadStatus}
        </div>
      )}
    </div>
  );
};

export default Upload;
