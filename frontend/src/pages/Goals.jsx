import React, { useState, useEffect } from 'react';
import { apiGet, apiPost } from '../utils/api';
import { Target, Calendar, Plus, Map, CheckCircle2, PauseCircle, HelpCircle, Loader2 } from 'lucide-react';

export default function Goals() {
  const [goals, setGoals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [deadline, setDeadline] = useState('');
  const [roadmaps, setRoadmaps] = useState({}); // goal_id -> roadmap data
  const [generatingRoadmap, setGeneratingRoadmap] = useState({}); // goal_id -> boolean
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/goals') || [];
      setGoals(data);
    } catch (err) {
      console.error('Error fetching goals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title) return;
    try {
      const payload = {
        title,
        description,
        deadline: deadline ? `${deadline}T00:00:00` : null,
      };
      const result = await apiPost('/goals', payload);
      if (result) {
        setTitle('');
        setDescription('');
        setDeadline('');
        setShowForm(false);
        fetchGoals();
      }
    } catch (err) {
      console.error('Error creating goal:', err);
    }
  };

  const handleGenerateRoadmap = async (goalId) => {
    setGeneratingRoadmap(prev => ({ ...prev, [goalId]: true }));
    try {
      const result = await apiPost('/ai/generate-roadmap', { goal_id: goalId });
      if (result) {
        setRoadmaps(prev => ({ ...prev, [goalId]: result }));
      }
    } catch (err) {
      console.error('Error generating roadmap:', err);
    } finally {
      setGeneratingRoadmap(prev => ({ ...prev, [goalId]: false }));
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'active':
        return <span className="badge badge-active">🟢 Active</span>;
      case 'completed':
        return <span className="badge badge-completed">✅ Completed</span>;
      case 'paused':
        return <span className="badge badge-pending">⏸️ Paused</span>;
      default:
        return <span className="badge badge-pending">⚪ {status}</span>;
    }
  };

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>🎯 Goals Tracker</h1>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} />
          {showForm ? 'Close' : 'Add New Goal'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card mb-6">
          <h3 className="font-bold text-lg mb-4">➕ Create New Goal</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Goal Title *</label>
              <input
                type="text"
                placeholder="e.g. Crack GATE exam, Learn React Native"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                placeholder="Describe your target, motivations, and overall outcome..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
            <div className="form-group">
              <label>Target Deadline</label>
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
            </div>
            <button type="submit" className="btn mt-2">
              Create Goal
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-muted text-center p-6">Loading goals list...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {goals.map((g) => (
            <div key={g.id} className="glass-card" style={{ padding: '2rem' }}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>{g.title}</h2>
                    {getStatusBadge(g.status)}
                  </div>
                  {g.deadline && (
                    <div className="flex items-center gap-1.5 text-muted" style={{ fontSize: '0.85rem' }}>
                      <Calendar size={14} />
                      <span>Deadline: {g.deadline.substring(0, 10)}</span>
                    </div>
                  )}
                </div>
                <button
                  className="btn btn-secondary"
                  onClick={() => handleGenerateRoadmap(g.id)}
                  disabled={generatingRoadmap[g.id]}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  {generatingRoadmap[g.id] ? (
                    <Loader2 size={16} className="spin-anim" />
                  ) : (
                    <Map size={16} />
                  )}
                  {roadmaps[g.id] ? 'Regenerate Roadmap' : 'Generate AI Roadmap'}
                </button>
              </div>

              {g.description && (
                <p className="text-muted mb-4" style={{ fontSize: '0.95rem', lineHeight: '1.6' }}>
                  {g.description}
                </p>
              )}

              {/* Roadmap timeline display */}
              {roadmaps[g.id] && (
                <div style={{
                  marginTop: '1.5rem',
                  padding: '1.5rem',
                  background: 'rgba(255, 255, 255, 0.01)',
                  borderRadius: '12px',
                  border: '1px dashed rgba(123, 44, 191, 0.25)'
                }}>
                  <h4 className="font-bold mb-3" style={{ color: 'var(--primary-blue)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Map size={18} />
                    AI-Generated Milestone Roadmap:
                  </h4>
                  <p className="mb-4" style={{ fontStyle: 'italic', fontSize: '0.9rem', color: '#c0c0ff' }}>
                    "{roadmaps[g.id].summary}"
                  </p>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', position: 'relative', paddingLeft: '1rem', borderLeft: '2px solid rgba(123, 44, 191, 0.2)' }}>
                    {roadmaps[g.id].milestones?.map((milestone, idx) => (
                      <div key={idx} style={{ position: 'relative' }}>
                        {/* Timeline dot */}
                        <div style={{
                          position: 'absolute',
                          left: '-21px',
                          top: '4px',
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          background: 'var(--primary-pink)',
                          border: '2px solid var(--bg-dark)'
                        }} />
                        <h5 className="font-semibold" style={{ fontSize: '0.95rem', color: '#fff' }}>
                          <span style={{ color: 'var(--primary-blue)' }}>{milestone.period}</span> — {milestone.title}
                        </h5>
                        <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '0.2rem' }}>
                          {milestone.description}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {goals.length === 0 && (
            <div className="glass-card text-center text-muted p-8">
              <Target size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
              <p>No goals logged yet. Define a core study target or personal goal using the 'Add New Goal' button.</p>
            </div>
          )}
        </div>
      )}
      
      {/* Spin animation CSS */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin-anim {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
}
