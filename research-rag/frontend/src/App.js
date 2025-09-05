import React, { useState } from 'react';
import Upload from './components/Upload';
import ChatBox from './components/Chatbox';
import Answer from './components/Answer';
import Home from './pages/Home';
import './styles/App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('chat'); // 'chat' or 'home'
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);

  const handleUploadSuccess = (response) => {
    setUploadedFiles(prev => [...prev, response.files_processed]);
  };

  const handleNewAnswer = (question, answer) => {
    const newEntry = {
      id: Date.now(),
      question,
      answer: answer.answer,
      sources: answer.sources,
      timestamp: new Date().toLocaleTimeString()
    };
    
    setChatHistory(prev => [newEntry, ...prev]);
    setCurrentAnswer(answer);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Multi-PDF Q&A Assistant</h1>
        <p>Upload PDFs and ask questions using hybrid retrieval (BM25 + Embeddings)</p>
        
        <nav className="app-nav">
          <button 
            className={`nav-btn ${currentPage === 'chat' ? 'active' : ''}`}
            onClick={() => setCurrentPage('chat')}
          >
            Q&A Chat
          </button>
          <button 
            className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            Dashboard
          </button>
        </nav>
      </header>

      <main className="app-main">
        {currentPage === 'chat' ? (
          <>
            <div className="upload-section">
              <Upload onUploadSuccess={handleUploadSuccess} />
            </div>

            <div className="chat-section">
              <ChatBox 
                onNewAnswer={handleNewAnswer}
                isLoading={isLoading}
                setIsLoading={setIsLoading}
                hasDocuments={uploadedFiles.length > 0}
              />
              
              {currentAnswer && (
                <Answer 
                  answer={currentAnswer.answer}
                  sources={currentAnswer.sources}
                />
              )}
            </div>

            {chatHistory.length > 0 && (
              <div className="history-section">
                <h3>Chat History</h3>
                <div className="history-list">
                  {chatHistory.map(entry => (
                    <div key={entry.id} className="history-item">
                      <div className="history-question">
                        <strong>Q:</strong> {entry.question}
                        <span className="timestamp">{entry.timestamp}</span>
                      </div>
                      <div className="history-answer">
                        <strong>A:</strong> {entry.answer.substring(0, 200)}...
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          <Home />
        )}
      </main>
    </div>
  );
}

export default App;
