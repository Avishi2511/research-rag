import React, { useState } from 'react';
import '../styles/Answer.css';

const Answer = ({ answer, sources }) => {
  const [showSources, setShowSources] = useState(true);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(answer);
    // You could add a toast notification here
  };

  return (
    <div className="answer-container">
      <div className="answer-header">
        <h3>Answer</h3>
        <button onClick={copyToClipboard} className="copy-btn">
          Copy Answer
        </button>
      </div>

      <div className="answer-content">
        <p>{answer}</p>
      </div>

      <div className="sources-section">
        <div className="sources-header">
          <h4>Sources ({sources.length})</h4>
          <button 
            onClick={() => setShowSources(!showSources)}
            className="toggle-sources-btn"
          >
            {showSources ? 'Hide' : 'Show'} Sources
          </button>
        </div>

        {showSources && (
          <div className="sources-list">
            {sources.map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-header">
                  <span className="source-file">{source.source_file}</span>
                  <span className="source-page">Page {source.page_number}</span>
                  <span className="relevance-score">
                    Relevance: {(source.relevance_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="source-text">
                  "{source.chunk_text}"
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Answer;
