import React, { useState, useEffect } from 'react';
import { apiGet } from '../utils/api';
import { RefreshCw, Play, ShieldAlert, Target, CheckCircle2, ListTodo, Percent } from 'lucide-react';

export default function Dashboard({ user }) {
  const [briefing, setBriefing] = useState(null);
  const [nextAction, setNextAction] = useState(null);
  const [stats, setStats] = useState({
    activeGoals: 0,
    pendingTasks: 0,
    completedTasks: 0,
    completionPercentage: 0,
  });
  const [loadingBriefing, setLoadingBriefing] = useState(false);
  const [loadingAction, setLoadingAction] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const goals = await apiGet('/goals') || [];
      const tasks = await apiGet('/tasks') || [];
      
      const activeGoals = goals.filter(g => g.status === 'active').length;
      const pendingTasks = tasks.filter(t => t.status === 'pending' || t.status === 'in_progress').length;
      const completedTasks = tasks.filter(t => t.status === 'completed').length;
      const totalTasks = tasks.length;
      const completionPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

      setStats({
        activeGoals,
        pendingTasks,
        completedTasks,
        completionPercentage
      });
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    }
  };

  const handleGenerateBriefing = async () => {
    setLoadingBriefing(true);
    try {
      const result = await apiGet('/ai/daily-coach');
      if (result) {
        setBriefing(result);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingBriefing(false);
    }
  };

  const handleNextAction = async () => {
    setLoadingAction(true);
    try {
      const result = await apiGet('/ai/next-action');
      if (result) {
        setNextAction(result);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingAction(false);
    }
  };

  return (
    <div className="fade-in-section">
      <h1 className="mb-6" style={{ fontSize: '2.2rem', fontWeight: 800 }}>
        🏠 Good day, {user?.name || 'User'}!
      </h1>

      <div className="grid-2 mb-6">
        {/* Daily Briefing Card */}
        <div className="glass-card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-lg">🤖 Daily Briefing</h3>
            <button 
              className="btn btn-secondary" 
              onClick={handleGenerateBriefing} 
              disabled={loadingBriefing}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            >
              <RefreshCw size={14} className={loadingBriefing ? 'spin-anim' : ''} />
              {briefing ? 'Regenerate' : 'Generate'}
            </button>
          </div>

          {loadingBriefing ? (
            <div className="text-muted p-4 text-center">Formulating study schedule and coach briefing...</div>
          ) : briefing ? (
            <div>
              <div className="coach-box" style={{ whiteSpace: 'pre-wrap' }}>
                {briefing.briefing}
              </div>
              {briefing.top_tasks && briefing.top_tasks.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-semibold mb-2" style={{ color: 'var(--primary-blue)', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    📌 Today's Target Tasks:
                  </h4>
                  <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
                    {briefing.top_tasks.map((task, idx) => (
                      <li key={idx} style={{ padding: '0.5rem 0', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', display: 'flex', justifyContent: 'space-between' }}>
                        <span>• {task.title}</span>
                        <span className="text-muted" style={{ fontSize: '0.85rem' }}>Score: {task.score}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center p-6 text-muted">
              Click the button above to generate today's briefing based on your study habits and goal milestones.
            </div>
          )}
        </div>

        {/* Next Best Action Card */}
        <div className="glass-card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-bold text-lg">⚡ Next Best Action</h3>
            <button 
              className="btn" 
              onClick={handleNextAction} 
              disabled={loadingAction}
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}
            >
              <Play size={14} />
              Calculate NBA
            </button>
          </div>

          {loadingAction ? (
            <div className="text-muted p-4 text-center">Calculating task priority matrix...</div>
          ) : nextAction && nextAction.recommended_action ? (
            <div className="action-box">
              <div className="flex justify-between items-start mb-2">
                <span className="font-bold" style={{ color: '#fff', fontSize: '1.1rem' }}>
                  ✅ {nextAction.recommended_action}
                </span>
                <span className="badge badge-active" style={{ fontSize: '0.75rem' }}>
                  Score: {nextAction.score}
                </span>
              </div>
              <p style={{ margin: '0.5rem 0', fontSize: '0.95rem', color: '#d0d2ff' }}>
                {nextAction.reason}
              </p>
              {nextAction.why_it_matters && (
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontStyle: 'italic', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '0.5rem', marginTop: '0.5rem' }}>
                  💡 {nextAction.why_it_matters}
                </p>
              )}
            </div>
          ) : (
            <div className="text-center p-6 text-muted">
              Click the button above to determine your highest leverage next task based on the NBA priority scoring.
            </div>
          )}
        </div>
      </div>

      <div className="divider" />

      {/* Metrics Section */}
      <h3 className="mb-4 font-bold text-lg">📊 Activity Dashboard Overview</h3>
      <div className="grid-4">
        <div className="metric-card">
          <div className="flex items-center gap-3">
            <Target size={24} style={{ color: 'var(--primary-blue)' }} />
            <div>
              <h4>Active Goals</h4>
              <p>{stats.activeGoals}</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center gap-3">
            <ListTodo size={24} style={{ color: '#f1c40f' }} />
            <div>
              <h4>Pending Tasks</h4>
              <p>{stats.pendingTasks}</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center gap-3">
            <CheckCircle2 size={24} style={{ color: '#2ecc71' }} />
            <div>
              <h4>Completed Tasks</h4>
              <p>{stats.completedTasks}</p>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center gap-3">
            <Percent size={24} style={{ color: 'var(--primary-pink)' }} />
            <div>
              <h4>Completion %</h4>
              <p>{stats.completionPercentage}%</p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Dynamic Spin CSS */}
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
