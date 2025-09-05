import React, { useState } from 'react';
import { askQuestion } from '../services/api';
import '../styles/Chatbox.css';

const ChatBox = ({ onNewAnswer, isLoading, setIsLoading, hasDocuments }) => {
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
      const response = await askQuestion({
        question: question.trim(),
        top_k: 5,
        bm25_weight: 0.5,
        embedding_weight: 0.5
      });

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
