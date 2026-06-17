import React, { useState, useEffect } from 'react';
import LoginRegister from './pages/LoginRegister';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Goals from './pages/Goals';
import Tasks from './pages/Tasks';
import Projects from './pages/Projects';
import DailyChallenges from './pages/DailyChallenges';
import Insights from './pages/Insights';
import Analytics from './pages/Analytics';
import WeeklyReview from './pages/WeeklyReview';

import { 
  Brain, 
  Home, 
  MessageSquare, 
  Target, 
  ListTodo, 
  Briefcase, 
  Calendar, 
  Lightbulb, 
  BarChart2, 
  Sparkles, 
  LogOut 
} from 'lucide-react';

export default function App() {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for stored credentials
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const handleAuthSuccess = (newToken, newUser) => {
    setToken(newToken);
    setUser(newUser);
    setActiveTab('dashboard');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0a0712' }}>
        <div className="text-muted">Initializing Saarthi AI...</div>
      </div>
    );
  }

  if (!token) {
    return <LoginRegister onAuthSuccess={handleAuthSuccess} />;
  }

  // Active page router logic
  const renderActivePage = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard user={user} />;
      case 'chat':
        return <Chat />;
      case 'goals':
        return <Goals />;
      case 'tasks':
        return <Tasks />;
      case 'projects':
        return <Projects />;
      case 'habits':
        return <DailyChallenges />;
      case 'insights':
        return <Insights />;
      case 'analytics':
        return <Analytics />;
      case 'weekly':
        return <WeeklyReview />;
      default:
        return <Dashboard user={user} />;
    }
  };

  return (
    <div className="app-container">
      {/* Sidebar navigation */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <Brain size={24} style={{ color: 'var(--primary-blue)' }} />
          <span>Saarthi AI</span>
        </div>

        {user && (
          <div className="sidebar-user">
            <div className="sidebar-user-name">👤 {user.name}</div>
            {user.skills && (
              <div className="sidebar-user-skills" title={user.skills}>
                🛠 {user.skills}
              </div>
            )}
          </div>
        )}

        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <Home size={16} />
            <span>Dashboard</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'chat' ? 'active' : ''}`}
            onClick={() => setActiveTab('chat')}
          >
            <MessageSquare size={16} />
            <span>AI Chat</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'goals' ? 'active' : ''}`}
            onClick={() => setActiveTab('goals')}
          >
            <Target size={16} />
            <span>Goals</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveTab('tasks')}
          >
            <ListTodo size={16} />
            <span>Tasks</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            <Briefcase size={16} />
            <span>Projects</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'habits' ? 'active' : ''}`}
            onClick={() => setActiveTab('habits')}
          >
            <Calendar size={16} />
            <span>Daily Challenges</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <Lightbulb size={16} />
            <span>AI Insights</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            <BarChart2 size={16} />
            <span>Analytics</span>
          </button>

          <button 
            className={`nav-item ${activeTab === 'weekly' ? 'active' : ''}`}
            onClick={() => setActiveTab('weekly')}
          >
            <Sparkles size={16} />
            <span>Weekly Review</span>
          </button>
        </nav>

        <div className="sidebar-logout">
          <button className="nav-item" onClick={handleLogout} style={{ color: 'var(--primary-pink)' }}>
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content viewport */}
      <main className="main-content">
        {renderActivePage()}
      </main>
    </div>
  );
}
