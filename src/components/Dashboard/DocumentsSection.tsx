import React, { useState, useRef, useEffect } from 'react';

interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'text' | 'document' | 'suggestion';
}

interface Document {
  id: string;
  title: string;
  subject: string;
  type: 'pdf' | 'doc' | 'ppt' | 'video' | 'link';
  size?: string;
  uploadDate: string;
  description: string;
  tags: string[];
}

const DocumentsSection: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      content: 'Hello! I\'m your class assistant. I can help you find documents, answer questions about your coursework, and provide study guidance. What would you like to know?',
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Mock documents data
  const documents: Document[] = [
    {
      id: '1',
      title: 'Calculus Integration Formulas',
      subject: 'Mathematics',
      type: 'pdf',
      size: '2.3 MB',
      uploadDate: '2025-09-10',
      description: 'Comprehensive guide to integration techniques and formulas',
      tags: ['calculus', 'integration', 'formulas', 'reference']
    },
    {
      id: '2',
      title: 'Electromagnetic Waves Lecture',
      subject: 'Physics',
      type: 'video',
      size: '45.2 MB',
      uploadDate: '2025-09-08',
      description: 'Video lecture on electromagnetic wave properties and applications',
      tags: ['waves', 'electromagnetic', 'physics', 'lecture']
    },
    {
      id: '3',
      title: 'Organic Chemistry Reactions',
      subject: 'Chemistry',
      type: 'ppt',
      size: '8.7 MB',
      uploadDate: '2025-09-06',
      description: 'PowerPoint presentation covering major organic reaction mechanisms',
      tags: ['organic', 'reactions', 'mechanisms', 'chemistry']
    },
    {
      id: '4',
      title: 'Cell Division Study Guide',
      subject: 'Biology',
      type: 'doc',
      size: '1.8 MB',
      uploadDate: '2025-09-04',
      description: 'Detailed study guide on mitosis and meiosis processes',
      tags: ['cell division', 'mitosis', 'meiosis', 'biology']
    },
    {
      id: '5',
      title: 'Shakespeare Analysis Resources',
      subject: 'English',
      type: 'link',
      uploadDate: '2025-09-02',
      description: 'Collection of online resources for analyzing Shakespeare\'s works',
      tags: ['shakespeare', 'literature', 'analysis', 'english']
    }
  ];

  const subjects = ['all', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'English'];

  const filteredDocuments = documents.filter(doc => {
    const matchesCategory = selectedCategory === 'all' || doc.subject === selectedCategory;
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const getFileIcon = (type: string) => {
    switch (type) {
      case 'pdf': return '📄';
      case 'doc': return '📝';
      case 'ppt': return '📊';
      case 'video': return '🎥';
      case 'link': return '🔗';
      default: return '📁';
    }
  };

  const mockChatResponses = [
    "I can help you with that! Let me search through your class materials...",
    "Based on your recent coursework, here are some relevant documents:",
    "That's a great question! Here's what I found in your study materials:",
    "I notice you've been working on this topic. These resources might help:",
    "Let me suggest some documents that other students found helpful for this topic:"
  ];

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: currentMessage,
      sender: 'user',
      timestamp: new Date(),
      type: 'text'
    };

    setChatMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);

    // Simulate bot response
    setTimeout(() => {
      const botResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: mockChatResponses[Math.floor(Math.random() * mockChatResponses.length)],
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      };

      setChatMessages(prev => [...prev, botResponse]);

      // Add document suggestions if relevant
      if (currentMessage.toLowerCase().includes('math') || currentMessage.toLowerCase().includes('calculus')) {
        setTimeout(() => {
          const docSuggestion: ChatMessage = {
            id: (Date.now() + 2).toString(),
            content: 'Calculus Integration Formulas',
            sender: 'bot',
            timestamp: new Date(),
            type: 'document'
          };
          setChatMessages(prev => [...prev, docSuggestion]);
        }, 1000);
      }

      setIsTyping(false);
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const quickActions = [
    { icon: '📚', text: 'Find study materials', action: () => setCurrentMessage('Can you help me find study materials for my upcoming exam?') },
    { icon: '❓', text: 'Explain concepts', action: () => setCurrentMessage('Can you explain this concept from my recent classes?') },
    { icon: '📝', text: 'Assignment help', action: () => setCurrentMessage('I need help with my assignment. Can you suggest relevant resources?') },
    { icon: '🎯', text: 'Study schedule', action: () => setCurrentMessage('Can you help me create a study schedule based on my upcoming deadlines?') }
  ];

  return (
    <div className="documents-section">
      <div className="documents-layout">
        
        {/* Documents Library */}
        <div className="documents-library">
          <div className="library-header">
            <h3>Class Documents</h3>
            <div className="library-controls">
              <div className="search-box">
                <input
                  type="text"
                  placeholder="Search documents..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="search-input"
                />
                <span className="search-icon">🔍</span>
              </div>
              <select 
                value={selectedCategory} 
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="category-filter"
                title="Filter by subject"
              >
                {subjects.map(subject => (
                  <option key={subject} value={subject}>
                    {subject === 'all' ? 'All Subjects' : subject}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="documents-grid">
            {filteredDocuments.map(doc => (
              <div key={doc.id} className="document-card">
                <div className="document-header">
                  <div className="file-icon">{getFileIcon(doc.type)}</div>
                  <div className="document-actions">
                    <button className="action-btn" title="Download">📥</button>
                    <button className="action-btn" title="Share">📤</button>
                    <button className="action-btn" title="More">⋮</button>
                  </div>
                </div>
                <div className="document-content">
                  <h4 className="document-title">{doc.title}</h4>
                  <div className="document-meta">
                    <span className="document-subject">{doc.subject}</span>
                    {doc.size && <span className="document-size">{doc.size}</span>}
                  </div>
                  <p className="document-description">{doc.description}</p>
                  <div className="document-tags">
                    {doc.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="tag">#{tag}</span>
                    ))}
                  </div>
                  <div className="document-date">Uploaded: {doc.uploadDate}</div>
                </div>
                <div className="document-footer">
                  <button className="open-btn">Open</button>
                  <button 
                    className="ask-btn"
                    onClick={() => setCurrentMessage(`Can you help me understand the content in "${doc.title}"?`)}
                  >
                    Ask AI
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredDocuments.length === 0 && (
            <div className="no-documents">
              <div className="no-docs-icon">📭</div>
              <h3>No documents found</h3>
              <p>Try adjusting your search or filter criteria</p>
            </div>
          )}
        </div>

        {/* AI Chatbot */}
        <div className="ai-chatbot">
          <div className="chatbot-header">
            <div className="bot-avatar">🤖</div>
            <div className="bot-info">
              <h3>Class Assistant</h3>
              <div className="bot-status online">● Online</div>
            </div>
          </div>

          <div className="chat-messages">
            {chatMessages.map(message => (
              <div 
                key={message.id} 
                className={`message ${message.sender} ${message.type}`}
              >
                <div className="message-content">
                  {message.type === 'document' ? (
                    <div className="document-suggestion">
                      <div className="suggestion-icon">📄</div>
                      <div className="suggestion-content">
                        <div className="suggestion-title">{message.content}</div>
                        <button className="view-document-btn">View Document</button>
                      </div>
                    </div>
                  ) : (
                    <p>{message.content}</p>
                  )}
                </div>
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message bot typing">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={chatEndRef} />
          </div>

          <div className="quick-actions">
            <div className="quick-actions-label">Quick actions:</div>
            <div className="actions-grid">
              {quickActions.map((action, index) => (
                <button 
                  key={index}
                  className="quick-action-btn"
                  onClick={action.action}
                  title={action.text}
                >
                  <span className="action-icon">{action.icon}</span>
                  <span className="action-text">{action.text}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="chat-input">
            <div className="input-container">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your coursework..."
                className="message-input"
                rows={2}
              />
              <button 
                onClick={handleSendMessage}
                className="send-btn"
                disabled={!currentMessage.trim()}
              >
                📤
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Document Stats */}
      <div className="document-stats">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <div className="stat-number">{documents.length}</div>
            <div className="stat-label">Total Documents</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📥</div>
          <div className="stat-content">
            <div className="stat-number">12</div>
            <div className="stat-label">Downloads This Week</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">🤖</div>
          <div className="stat-content">
            <div className="stat-number">{chatMessages.length - 1}</div>
            <div className="stat-label">AI Interactions</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">📈</div>
          <div className="stat-content">
            <div className="stat-number">87%</div>
            <div className="stat-label">Helpful Responses</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocumentsSection;