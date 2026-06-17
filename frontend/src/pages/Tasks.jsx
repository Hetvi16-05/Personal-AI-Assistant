import React, { useState, useEffect } from 'react';
import { apiGet, apiPost, apiPatch, apiDelete } from '../utils/api';
import { Plus, Check, Trash2, Calendar, Target, ListTodo } from 'lucide-react';

export default function Tasks() {
  const [tasks, setTasks] = useState([]);
  const [goals, setGoals] = useState([]);
  const [activeSubTab, setActiveSubTab] = useState('view');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [goalId, setGoalId] = useState('');
  const [deadline, setDeadline] = useState('');
  const [impact, setImpact] = useState(5);
  const [urgency, setUrgency] = useState(5);
  const [effort, setEffort] = useState(5);
  const [alignment, setAlignment] = useState(5);

  useEffect(() => {
    fetchGoals();
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [filterStatus]);

  const fetchGoals = async () => {
    try {
      const data = await apiGet('/goals') || [];
      setGoals(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const path = filterStatus !== 'all' ? `/tasks?status=${filterStatus}` : '/tasks';
      const data = await apiGet(path) || [];
      setTasks(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    if (!title) return;
    try {
      const payload = {
        title,
        description,
        goal_id: goalId ? parseInt(goalId) : null,
        deadline: deadline ? `${deadline}T00:00:00` : null,
        impact_score: parseFloat(impact),
        urgency_score: parseFloat(urgency),
        effort_score: parseFloat(effort),
        alignment_score: parseFloat(alignment),
      };
      const result = await apiPost('/tasks', payload);
      if (result) {
        setTitle('');
        setDescription('');
        setGoalId('');
        setDeadline('');
        setImpact(5);
        setUrgency(5);
        setEffort(5);
        setAlignment(5);
        setActiveSubTab('view');
        fetchTasks();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCompleteTask = async (taskId) => {
    try {
      const result = await apiPatch(`/tasks/${taskId}`, { status: 'completed' });
      if (result) {
        fetchTasks();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      const result = await apiDelete(`/tasks/${taskId}`);
      if (result) {
        fetchTasks();
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
      <h1 className="mb-6" style={{ fontSize: '2.2rem', fontWeight: 800 }}>📋 Task Backlog</h1>

      <div className="auth-tabs" style={{ marginBottom: '1.5rem' }}>
        <button
          className={`auth-tab ${activeSubTab === 'view' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('view')}
        >
          View Tasks
        </button>
        <button
          className={`auth-tab ${activeSubTab === 'add' ? 'active' : ''}`}
          onClick={() => setActiveSubTab('add')}
        >
          Add Task
        </button>
      </div>

      {activeSubTab === 'view' ? (
        <div>
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-3">
              <span className="text-muted" style={{ fontSize: '0.9rem', fontWeight: 600, textTransform: 'uppercase' }}>Filter status:</span>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                style={{ width: '180px', padding: '0.5rem 0.75rem' }}
              >
                <option value="all">All Tasks</option>
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="text-muted text-center p-6">Loading tasks backlog...</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {tasks.map((t) => (
                <div key={t.id} className="glass-card" style={{ padding: '1.5rem' }}>
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-bold text-lg mb-1">{t.title}</h3>
                      <div className="flex items-center gap-4 text-muted" style={{ fontSize: '0.82rem' }}>
                        <span className="flex items-center gap-1">
                          <Target size={12} />
                          {getGoalTitle(t.goal_id)}
                        </span>
                        {t.deadline && (
                          <span className="flex items-center gap-1">
                            <Calendar size={12} />
                            Due: {t.deadline.substring(0, 10)}
                          </span>
                        )}
                        <span className={`badge ${t.status === 'completed' ? 'badge-completed' : 'badge-pending'}`}>
                          {t.status}
                        </span>
                      </div>
                    </div>

                    <div className="flex gap-2">
                      {t.status !== 'completed' && (
                        <button
                          className="btn"
                          onClick={() => handleCompleteTask(t.id)}
                          style={{ padding: '0.4rem 0.6rem', background: '#2ecc71', borderColor: '#27ae60' }}
                          title="Mark Complete"
                        >
                          <Check size={14} />
                        </button>
                      )}
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDeleteTask(t.id)}
                        style={{ padding: '0.4rem 0.6rem' }}
                        title="Delete Task"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  {t.description && (
                    <p className="text-muted mb-4" style={{ fontSize: '0.9rem' }}>
                      {t.description}
                    </p>
                  )}

                  <div className="grid-4" style={{ background: 'rgba(255, 255, 255, 0.01)', borderRadius: '10px', padding: '1rem', border: '1px solid rgba(255,255,255,0.03)' }}>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>Impact</span>
                      <strong style={{ fontSize: '1.1rem', color: 'var(--primary-blue)' }}>{t.impact_score}/10</strong>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>Urgency</span>
                      <strong style={{ fontSize: '1.1rem', color: '#f1c40f' }}>{t.urgency_score}/10</strong>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>Effort</span>
                      <strong style={{ fontSize: '1.1rem', color: 'var(--primary-pink)' }}>{t.effort_score}/10</strong>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.75rem', textTransform: 'uppercase', display: 'block', marginBottom: '0.25rem' }}>Alignment</span>
                      <strong style={{ fontSize: '1.1rem', color: '#2ecc71' }}>{t.alignment_score}/10</strong>
                    </div>
                  </div>
                </div>
              ))}

              {tasks.length === 0 && (
                <div className="glass-card text-center text-muted p-8">
                  <ListTodo size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
                  <p>No tasks found for the selected status.</p>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="glass-card">
          <h3 className="font-bold text-lg mb-4">➕ Add New Task</h3>
          <form onSubmit={handleCreateTask}>
            <div className="form-group">
              <label>Task Title *</label>
              <input
                type="text"
                placeholder="e.g. Solve GATE mock test, Setup database models"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Description</label>
              <textarea
                placeholder="Describe what needs to be done..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label>Associated Goal</label>
                <select value={goalId} onChange={(e) => setGoalId(e.target.value)}>
                  <option value="">None</option>
                  {goals.map(g => (
                    <option key={g.id} value={g.id}>{g.title}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Deadline</label>
                <input
                  type="date"
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                />
              </div>
            </div>

            <div className="divider" style={{ margin: '1rem 0' }} />
            <h4 className="font-semibold mb-4" style={{ fontSize: '0.95rem', color: 'var(--primary-blue)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Priority Sliders (NBA weights)
            </h4>

            <div className="grid-2">
              <div className="form-group">
                <div className="flex justify-between mb-1">
                  <label style={{ margin: 0 }}>Impact Score: {impact}/10</label>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={impact}
                  onChange={(e) => setImpact(parseInt(e.target.value))}
                />
              </div>
              <div className="form-group">
                <div className="flex justify-between mb-1">
                  <label style={{ margin: 0 }}>Urgency Score: {urgency}/10</label>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={urgency}
                  onChange={(e) => setUrgency(parseInt(e.target.value))}
                />
              </div>
              <div className="form-group">
                <div className="flex justify-between mb-1">
                  <label style={{ margin: 0 }}>Effort Score: {effort}/10</label>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={effort}
                  onChange={(e) => setEffort(parseInt(e.target.value))}
                />
              </div>
              <div className="form-group">
                <div className="flex justify-between mb-1">
                  <label style={{ margin: 0 }}>Alignment Score: {alignment}/10</label>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={alignment}
                  onChange={(e) => setAlignment(parseInt(e.target.value))}
                />
              </div>
            </div>

            <button type="submit" className="btn mt-4">
              Create Task
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
