import React, { useState } from 'react';
import { askQuestion } from '../services/api';
import '../styles/Chatbox.css';

const ChatBox = ({ onNewAnswer, isLoading, setIsLoading, hasDocuments, currentSession }) => {
  const [question, setQuestion] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!question.trim()) {
      setError('Please enter a question');
      return;
    }

    if (!hasDocuments) {
      setError('Please upload some PDF documents first');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Build request with session-based search by default
      const requestData = {
        question: question.trim(),
        top_k: 5,
        bm25_weight: 0.5,
        embedding_weight: 0.5,
        search_scope: "session", // Default to session-based search
        session_id: currentSession?.session_id || null
      };

      const response = await askQuestion(requestData);

      onNewAnswer(question, response);
      setQuestion('');
    } catch (error) {
      setError(`Failed to get answer: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox-container">
      <h2>Ask a Question</h2>
      
      {currentSession && (
        <div className="session-info">
          <p><strong>Current Session:</strong> {currentSession.uploaded_files.length} files uploaded</p>
          <p><small>Files: {currentSession.uploaded_files.join(', ')}</small></p>
          <p><small>Search scope: Session-based (only searching recently uploaded documents)</small></p>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="question-form">
        <div className="input-group">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your uploaded documents..."
            className="question-input"
            rows="3"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            disabled={isLoading || !question.trim()}
            className="ask-btn"
          >
            {isLoading ? 'Thinking...' : 'Ask Question'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Searching documents and generating answer...</p>
        </div>
      )}
    </div>
  );
};

export default ChatBox;
