import React, { useState, useEffect } from 'react';
import { apiGet } from '../utils/api';
import { Lightbulb, Sparkles, History, Loader2 } from 'lucide-react';

export default function Insights() {
  const [freshInsights, setFreshInsights] = useState([]);
  const [history, setHistory] = useState([]);
  const [generating, setGenerating] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const data = await apiGet('/insights/history') || [];
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleGenerateInsights = async () => {
    setGenerating(true);
    try {
      const data = await apiGet('/insights');
      if (data) {
        setFreshInsights(data);
        // Refresh history
        fetchHistory();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setGenerating(false);
    }
  };

  const typeIcons = {
    productivity: '⚡',
    learning: '📚',
    goal_progress: '🎯',
    recommendation: '💡',
  };

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>💡 AI Insights</h1>
          <p className="text-muted">Personalized analysis and productivity tips compiled by Gemini.</p>
        </div>
        <button className="btn" onClick={handleGenerateInsights} disabled={generating}>
          {generating ? (
            <Loader2 size={16} className="spin-anim" />
          ) : (
            <Sparkles size={16} />
          )}
          {generating ? 'Analyzing...' : 'Generate Insights'}
        </button>
      </div>

      {freshInsights.length > 0 && (
        <div className="mb-6">
          <h3 className="font-bold text-lg mb-3" style={{ color: 'var(--primary-blue)' }}>🔮 Newly Formulated Insights</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {freshInsights.map((ins, idx) => (
              <div key={idx} className="insight-card">
                <span className="type-badge">
                  {typeIcons[ins.type] || '🔹'} {ins.type?.replace('_', ' ')}
                </span>
                <p style={{ lineHeight: '1.6', fontSize: '0.95rem' }}>{ins.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="divider" />

      <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
        <History size={18} />
        Past Insights History
      </h3>

      {loadingHistory ? (
        <div className="text-muted text-center p-6">Recalling insights archive...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {history.map((ins) => (
            <div key={ins.id} className="insight-card">
              <div className="flex justify-between items-start mb-2">
                <span className="type-badge">
                  {typeIcons[ins.insight_type] || '🔹'} {ins.insight_type?.replace('_', ' ')}
                </span>
                <span className="text-muted" style={{ fontSize: '0.75rem' }}>
                  {ins.generated_at?.substring(0, 10)}
                </span>
              </div>
              <p style={{ lineHeight: '1.6', fontSize: '0.92rem' }}>{ins.content}</p>
            </div>
          ))}

          {history.length === 0 && freshInsights.length === 0 && (
            <div className="glass-card text-center text-muted p-8">
              <Lightbulb size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
              <p>No insights generated yet. Click 'Generate Insights' above to run AI diagnostic engine.</p>
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
