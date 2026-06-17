import React, { useState, useEffect } from 'react';
import { apiGet, apiPost } from '../utils/api';
import { FolderPlus, Calendar, Target, Briefcase } from 'lucide-react';

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [goals, setGoals] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [goalId, setGoalId] = useState('');
  const [deadline, setDeadline] = useState('');

  useEffect(() => {
    fetchGoals();
    fetchProjects();
  }, []);

  const fetchGoals = async () => {
    try {
      const data = await apiGet('/goals') || [];
      setGoals(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/projects') || [];
      setProjects(data);
    } catch (err) {
      console.error(err);
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
        goal_id: goalId ? parseInt(goalId) : null,
        deadline: deadline ? `${deadline}T00:00:00` : null,
      };
      const result = await apiPost('/projects', payload);
      if (result) {
        setTitle('');
        setDescription('');
        setGoalId('');
        setDeadline('');
        setShowForm(false);
        fetchProjects();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const getGoalTitle = (id) => {
    const goal = goals.find(g => g.id === id);
    return goal ? goal.title : 'No Goal';
  };

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>📁 Project Folders</h1>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          <FolderPlus size={16} />
          {showForm ? 'Close' : 'Add Project'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card mb-6">
          <h3 className="font-bold text-lg mb-4">➕ Start New Project</h3>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Project Title *</label>
              <input
                type="text"
                placeholder="e.g. Portfolio Website, Deep Learning Model"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                placeholder="Outline what this project encompasses..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>
            <div className="grid-2">
              <div className="form-group">
                <label>Link to Core Goal</label>
                <select value={goalId} onChange={(e) => setGoalId(e.target.value)}>
                  <option value="">None</option>
                  {goals.map(g => (
                    <option key={g.id} value={g.id}>{g.title}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Target Deadline</label>
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                />
              </div>
            </div>
            <button type="submit" className="btn mt-2">
              Create Project
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-muted text-center p-6">Loading projects...</div>
      ) : (
        <div className="grid-2">
          {projects.map((p) => (
            <div key={p.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', minHeight: '200px' }}>
              <div>
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-bold text-lg">{p.title}</h3>
                  <span className="badge badge-active">{p.status || 'active'}</span>
                </div>
                
                <div className="flex items-center gap-3 text-muted mb-4" style={{ fontSize: '0.8rem' }}>
                  <span className="flex items-center gap-1">
                    <Target size={12} />
                    {getGoalTitle(p.goal_id)}
                  </span>
                  {p.deadline && (
                    <span className="flex items-center gap-1">
                      <Calendar size={12} />
                      Due: {p.deadline.substring(0, 10)}
                    </span>
                  )}
                </div>

                {p.description && (
                  <p className="text-muted" style={{ fontSize: '0.9rem', lineHeight: '1.5' }}>
                    {p.description}
                  </p>
                )}
              </div>
            </div>
          ))}

          {projects.length === 0 && (
            <div className="glass-card text-center text-muted p-8 w-full" style={{ gridColumn: 'span 2' }}>
              <Briefcase size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
              <p>No active projects. Group your tasks together by creating a project folder.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
