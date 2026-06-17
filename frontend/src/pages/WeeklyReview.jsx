import React, { useState } from 'react';
import { apiGet } from '../utils/api';
import { RefreshCw, BarChart, Percent, Award, Sparkles, Loader2 } from 'lucide-react';

export default function WeeklyReview() {
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateReview = async () => {
    setLoading(true);
    try {
      const result = await apiGet('/ai/weekly-review');
      if (result) {
        setReview(result);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>📊 Weekly Performance Review</h1>
          <p className="text-muted">Analyze your goals, tasks, and streaks over the last 7 days with Gemini diagnostics.</p>
        </div>
        <button className="btn" onClick={handleGenerateReview} disabled={loading}>
          {loading ? (
            <Loader2 size={16} className="spin-anim" />
          ) : (
            <RefreshCw size={16} />
          )}
          {loading ? 'Analyzing Week...' : "Generate Weekly Review"}
        </button>
      </div>

      {loading ? (
        <div className="text-muted text-center p-6">Running weekly diagnostic engines...</div>
      ) : review ? (
        <div>
          {/* Metrics Row */}
          <div className="grid-3 mb-6">
            <div className="metric-card">
              <div className="flex items-center gap-3">
                <BarChart size={24} style={{ color: 'var(--primary-blue)' }} />
                <div>
                  <h4>Tasks Completed</h4>
                  <p>{review.tasks_completed}</p>
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="flex items-center gap-3">
                <Percent size={24} style={{ color: 'var(--primary-pink)' }} />
                <div>
                  <h4>Completion Rate</h4>
                  <p>{review.completion_percentage}%</p>
                </div>
              </div>
            </div>

            <div className="metric-card">
              <div className="flex items-center gap-3">
                <Award size={24} style={{ color: '#f1c40f' }} />
                <div>
                  <h4>Most Active Goal</h4>
                  <p style={{ fontSize: '1.25rem', fontWeight: 700, margin: '0.25rem 0 0 0', textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden', maxWidth: '200px' }}>
                    {review.most_active_goal || 'None'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="divider" />

          {/* AI Coach Box */}
          <div className="glass-card">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2" style={{ color: 'var(--primary-blue)' }}>
              <Sparkles size={18} />
              AI Performance Summary
            </h3>
            <div className="coach-box" style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
              {review.ai_summary}
            </div>
          </div>
        </div>
      ) : (
        <div className="glass-card text-center text-muted p-8">
          <Sparkles size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto', color: 'var(--primary-purple)' }} />
          <p>Click 'Generate Weekly Review' above to prompt your AI mentor to analyze your progress and compile a detailed weekly feedback report.</p>
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
