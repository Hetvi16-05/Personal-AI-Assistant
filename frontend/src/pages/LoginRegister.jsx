import React, { useState } from 'react';
import { apiPost } from '../utils/api';

export default function LoginRegister({ onAuthSuccess }) {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Login inputs
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register inputs
  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regSkills, setRegSkills] = useState('');
  const [regInterests, setRegInterests] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginEmail || !loginPassword) {
      setError('Please enter email and password');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const result = await apiPost('/auth/login', {
        email: loginEmail,
        password: loginPassword,
      });
      if (result && result.access_token) {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        onAuthSuccess(result.access_token, result.user);
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!regName || !regEmail || !regPassword) {
      setError('Please fill in all required fields (Name, Email, Password)');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const result = await apiPost('/auth/register', {
        name: regName,
        email: regEmail,
        password: regPassword,
        skills: regSkills || '',
        interests: regInterests || '',
      });
      if (result && result.access_token) {
        localStorage.setItem('token', result.access_token);
        localStorage.setItem('user', JSON.stringify(result.user));
        onAuthSuccess(result.access_token, result.user);
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Email might already exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="text-center mb-6">
          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 0.25rem 0' }}>🧠 Saarthi AI</h2>
          <p className="text-muted">Your AI-powered personal mentor & goal planner</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => { setActiveTab('login'); setError(''); }}
          >
            Login
          </button>
          <button
            className={`auth-tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => { setActiveTab('register'); setError(''); }}
          >
            Register
          </button>
        </div>

        {error && (
          <div style={{
            background: 'rgba(231, 76, 60, 0.15)',
            border: '1px solid #e74c3c',
            borderRadius: '10px',
            padding: '0.75rem 1rem',
            marginBottom: '1.5rem',
            color: '#e74c3c',
            fontSize: '0.9rem',
            fontWeight: 500
          }}>
            ⚠️ {error}
          </div>
        )}

        {activeTab === 'login' ? (
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Email Address</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                placeholder="••••••••"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit" className="btn btn-block mt-4" disabled={loading}>
              {loading ? 'Logging in...' : 'Sign In'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister}>
            <div className="form-group">
              <label>Full Name *</label>
              <input
                type="text"
                placeholder="John Doe"
                value={regName}
                onChange={(e) => setRegName(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Email Address *</label>
              <input
                type="email"
                placeholder="you@example.com"
                value={regEmail}
                onChange={(e) => setRegEmail(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                placeholder="••••••••"
                value={regPassword}
                onChange={(e) => setRegPassword(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Skills (comma separated, optional)</label>
              <input
                type="text"
                placeholder="Python, Public Speaking, Stats"
                value={regSkills}
                onChange={(e) => setRegSkills(e.target.value)}
              />
            </div>
            <div className="form-group">
              <label>Interests (comma separated, optional)</label>
              <input
                type="text"
                placeholder="Machine Learning, GATE prep, Writing"
                value={regInterests}
                onChange={(e) => setRegInterests(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-block mt-4" disabled={loading}>
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
