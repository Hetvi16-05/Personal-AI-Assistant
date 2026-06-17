import React, { useState, useEffect, useRef } from 'react';
import { apiGet, apiPost } from '../utils/api';
import { Plus, Send, MessageSquare } from 'lucide-react';

export default function Chat() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      const data = await apiGet('/chat/sessions') || [];
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        // Default to first session
        setActiveSession(data[0].id);
      }
    } catch (err) {
      console.error('Error fetching chat sessions:', err);
    }
  };

  const fetchMessages = async (sessionId) => {
    setLoadingMessages(true);
    try {
      const data = await apiGet(`/chat/sessions/${sessionId}/messages`) || [];
      setMessages(data);
    } catch (err) {
      console.error('Error fetching messages:', err);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleNewSession = async () => {
    try {
      const result = await apiPost('/chat/sessions', { title: 'New Conversation' });
      if (result) {
        setSessions(prev => [result, ...prev]);
        setActiveSession(result.id);
      }
    } catch (err) {
      console.error('Error creating new session:', err);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || !activeSession || sending) return;

    const userMessageContent = input.trim();
    setInput('');
    setSending(true);

    // Optimistically add user message to list
    const optimisticMessage = {
      id: Date.now(),
      role: 'user',
      content: userMessageContent,
    };
    setMessages(prev => [...prev, optimisticMessage]);

    try {
      const result = await apiPost(`/chat/sessions/${activeSession}/messages`, {
        content: userMessageContent,
      });
      if (result) {
        // Fetch all messages to make sure we get vector database context and ID updates correctly
        await fetchMessages(activeSession);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      // Remove optimistic message on error or show alert
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fade-in-section">
      <h1 className="mb-6" style={{ fontSize: '2.2rem', fontWeight: 800 }}>
        💬 AI Mentor Chat
      </h1>

      <div className="chat-container">
        {/* Sessions Sidebar */}
        <div className="chat-sidebar">
          <button className="btn btn-block" onClick={handleNewSession}>
            <Plus size={16} />
            New Session
          </button>
          
          <div className="divider" style={{ margin: '0.5rem 0' }} />
          
          <div className="chat-sessions-list">
            {sessions.map((session) => (
              <button
                key={session.id}
                className={`chat-session-btn ${activeSession === session.id ? 'active' : ''}`}
                onClick={() => setActiveSession(session.id)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <MessageSquare size={14} />
                  <span>{session.title}</span>
                </div>
              </button>
            ))}
            {sessions.length === 0 && (
              <div className="text-muted text-center" style={{ fontSize: '0.85rem', padding: '1rem 0' }}>
                No active conversations.
              </div>
            )}
          </div>
        </div>

        {/* Messages Log Panel */}
        <div className="chat-area">
          {activeSession ? (
            <>
              <div className="chat-messages">
                {loadingMessages && messages.length === 0 ? (
                  <div className="text-muted text-center p-6">Recalling conversation logs...</div>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`chat-message-bubble ${msg.role}`}
                      style={{ whiteSpace: 'pre-wrap' }}
                    >
                      {msg.content}
                    </div>
                  ))
                )}
                {sending && (
                  <div className="chat-message-bubble assistant">
                    <span className="text-muted">AI Mentor is thinking...</span>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              <form className="chat-input-wrapper" onSubmit={handleSendMessage}>
                <input
                  type="text"
                  placeholder="Ask your AI mentor anything..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={sending}
                />
                <button type="submit" className="btn" style={{ padding: '0.75rem' }} disabled={sending || !input.trim()}>
                  <Send size={16} />
                </button>
              </form>
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flexGrow: 1, padding: '2rem' }} className="text-muted">
              <MessageSquare size={48} className="mb-4" style={{ color: 'var(--primary-purple)', opacity: 0.5 }} />
              <p>Select a session or create a new one to chat with your AI mentor.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
