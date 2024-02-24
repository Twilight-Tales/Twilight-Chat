import React, { useState } from 'react';
import './App.css';

function App() {
  const [isInfoVisible, setInfoVisible] = useState(false);
  const [bookDetails, setBookDetails] = useState({
    book: 'Example Book Title',
    author: 'Author Name',
    pages: 300,
    currentChapter: 5,
    currentPage: 150,
    startDate: '01/01/2024',
    progress: 50
  });
  const toggleInfo = () => setInfoVisible(!isInfoVisible);

  return (
    <div className="App">
      {isInfoVisible && <InformationComponent {...bookDetails} />}
      <div className="chatbot">
        <ChatbotComponent />
        <button onClick={toggleInfo} className="info-toggle">
          i
        </button>
      </div>
    </div>
  );
}

function InformationComponent({ book, author, pages, currentChapter, currentPage, startDate, progress }) {
  return (
    <div className="information-panel">
      <h2>Information</h2>
      <div className="book-details">
        <p><strong>Book:</strong> {book}</p>
        <p><strong>Author:</strong> {author}</p>
        <p><strong>Pages:</strong> {pages}</p>
      </div>
      <div className="current-status">
        <p><strong>Current Status:</strong></p>
        <p>Chapter {currentChapter} Page {currentPage}</p>
        <progress value={progress} max="100">{progress}%</progress>
        <p>{progress}% finished</p>
      </div>
      <div className="start-date">
        <p><strong>Date Started:</strong> {startDate}</p>
      </div>
    </div>
  );
}

function ChatbotComponent() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState('');

  const handleSendMessage = () => {
    if (!userInput.trim()) return;
    setMessages([...messages, { sender: 'user', text: userInput }]);
    // Simulate a bot response
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'bot', text: `Echo: "${userInput}"` },
    ]);
    setUserInput('');
  };

  const handleInputChange = (event) => {
    setUserInput(event.target.value);
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chatbot-component">
      <div className="conversation">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.sender}`}>
            {message.text}
          </div>
        ))}
      </div>
      <div className="message-input">
        <input
          type="text"
          value={userInput}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          placeholder="Type here..."
        />
        <button onClick={handleSendMessage}>Send</button>
      </div>
    </div>
  );
}

export default App;
