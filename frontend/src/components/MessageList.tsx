import React from 'react';
import { Message } from '../types';
import { formatTimestamp } from '../utils';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">💬</div>
        <h3 className="empty-state-title">¡Bienvenido al Chatbot UGR!</h3>
        <p className="empty-state-description">
          Selecciona una asignatura y comienza a hacer preguntas. 
          Estoy aquí para ayudarte con el contenido académico.
        </p>
      </div>
    );
  }

  return (
    <div className="messages-container">
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.role}`}>
          <div className="message-avatar">
            {message.role === 'user' ? 'T' : '🤖'}
          </div>
          <div className="message-content">
            <div className="message-bubble">
              <div className="message-text">{message.content}</div>
              {message.role === 'assistant' && message.sources && message.sources.length > 0 && (
                <div className="message-sources">
                  <details className="sources-details">
                    <summary className="sources-summary">
                      📚 Fuentes consultadas ({message.sources.length})
                    </summary>
                    <div className="sources-list">
                      {message.sources.map((source, index) => (
                        <div key={index} className="source-item">
                          <span className="source-number">{index + 1}.</span>
                          <span className="source-text">{source}</span>
                        </div>
                      ))}
                    </div>
                  </details>
                </div>
              )}
              {message.role === 'assistant' && message.modelUsed && (
                <div className="message-meta">
                  <span className="model-info">🤖 {message.modelUsed}</span>
                </div>
              )}
            </div>
            <div className="message-timestamp">
              {formatTimestamp(message.timestamp)}
            </div>
          </div>
        </div>
      ))}
      
      {isLoading && (
        <div className="message assistant">
          <div className="message-avatar">🤖</div>
          <div className="message-content">
            <div className="message-bubble">
              <div className="loading-message">
                <span>Pensando</span>
                <div className="loading-dots">
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                  <div className="loading-dot"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
