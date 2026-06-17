import React, { useState, useEffect } from 'react';
import { apiGet, apiPost, apiPatch, apiDelete } from '../utils/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Calendar, Flame, Trophy, Trash2, CheckCircle2, ChevronDown, ChevronUp, Lock } from 'lucide-react';

export default function DailyChallenges() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [durationPreset, setDurationPreset] = useState('30');
  const [customDays, setCustomDays] = useState(30);
  const [startDate, setStartDate] = useState(new Date().toISOString().substring(0, 10));

  useEffect(() => {
    fetchSummary();
  }, []);

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const data = await apiGet('/habits/analytics/summary');
      if (data) {
        setSummary(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartChallenge = async (e) => {
    e.preventDefault();
    if (!title) return;

    let durationDays = parseInt(durationPreset);
    if (durationPreset === 'custom') {
      durationDays = customDays;
    } else if (durationPreset === 'month') {
      const start = new Date(startDate);
      // Days in month
      durationDays = new Date(start.getFullYear(), start.getMonth() + 1, 0).getDate();
    }

    try {
      const payload = {
        title,
        description,
        duration_days: durationDays,
        start_date: startDate,
      };
      const result = await apiPost('/habits', payload);
      if (result) {
        setTitle('');
        setDescription('');
        setDurationPreset('30');
        setShowForm(false);
        fetchSummary();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleToggleLog = async (habitId, dateStr, currentChecked) => {
    try {
      const result = await apiPost(`/habits/${habitId}/log`, {
        date: dateStr,
        completed: !currentChecked,
      });
      if (result) {
        fetchSummary();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteChallenge = async (habitId) => {
    if (!window.confirm('Are you sure you want to delete this challenge?')) return;
    try {
      const res = await fetch(`/api/habits/${habitId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (res.ok) {
        fetchSummary();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkComplete = async (habitId) => {
    try {
      const result = await apiPatch(`/habits/${habitId}`, { status: 'completed' });
      if (result) {
        fetchSummary();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleArchiveChallenge = async (habitId) => {
    try {
      const result = await apiPatch(`/habits/${habitId}`, { status: 'archived' });
      if (result) {
        fetchSummary();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Generate date array for checkboxes
  const getChallengeDates = (startStr, durationDays) => {
    const dates = [];
    const start = new Date(startStr);
    for (let i = 0; i < durationDays; i++) {
      const current = new Date(start);
      current.setDate(start.getDate() + i);
      dates.push(current);
    }
    return dates;
  };

  // Check if a date is in the future
  const isFutureDate = (d) => {
    const today = new Date();
    today.setHours(0,0,0,0);
    const dateToCheck = new Date(d);
    dateToCheck.setHours(0,0,0,0);
    return dateToCheck > today;
  };

  const formatDateLabel = (d) => {
    return d.toLocaleDateString('en-US', { day: 'numeric', month: 'short' });
  };

  const getChartData = () => {
    if (!summary || !summary.habits) return [];
    return summary.habits.map(h => ({
      name: h.title.substring(0, 15) + (h.title.length > 15 ? '...' : ''),
      'Completion Rate': h.completion_rate,
      'Current Streak': h.current_streak,
      'Longest Streak': h.longest_streak,
    }));
  };

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>📅 Daily Challenges</h1>
          <p className="text-muted">Form habits by tracking daily tasks. Maintain streaks and build consistency.</p>
        </div>
        <button className="btn" onClick={() => setShowForm(!showForm)}>
          <Plus size={16} />
          {showForm ? 'Close' : 'Start Challenge'}
        </button>
      </div>

      {showForm && (
        <div className="glass-card mb-6">
          <h3 className="font-bold text-lg mb-4">🏁 Start 30-Day (or custom) Challenge</h3>
          <form onSubmit={handleStartChallenge}>
            <div className="form-group">
              <label>Challenge Title *</label>
              <input
                type="text"
                placeholder="e.g. 30 Days of Code, Daily Math Prep, Workout"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Description / Motivation</label>
              <textarea
                placeholder="Why is this important? Keep your motivation visible..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>
            
            <div className="grid-3">
              <div className="form-group">
                <label>Duration Preset</label>
                <select value={durationPreset} onChange={(e) => setDurationPreset(e.target.value)}>
                  <option value="30">30 Days (Standard)</option>
                  <option value="7">7 Days</option>
                  <option value="14">14 Days</option>
                  <option value="21">21 Days</option>
                  <option value="month">Current Month</option>
                  <option value="custom">Custom Days</option>
                </select>
              </div>
              
              {durationPreset === 'custom' && (
                <div className="form-group">
                  <label>Custom Days (1-31)</label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={customDays}
                    onChange={(e) => setCustomDays(parseInt(e.target.value))}
                  />
                </div>
              )}

              <div className="form-group">
                <label>Start Date</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
            </div>

            <button type="submit" className="btn mt-2">
              Start Challenge
            </button>
          </form>
        </div>
      )}

      {loading ? (
        <div className="text-muted text-center p-6">Recalling habit sheets...</div>
      ) : summary ? (
        <div>
          {/* Summary Row */}
          <div className="grid-4 mb-6">
            <div className="metric-card">
              <h4>Total Logged</h4>
              <p>{summary.total_habits}</p>
            </div>
            <div className="metric-card">
              <h4>Active Challenges</h4>
              <p>{summary.active_habits}</p>
            </div>
            <div className="metric-card">
              <h4>Completed</h4>
              <p>{summary.completed_habits}</p>
            </div>
            <div className="metric-card">
              <h4>Avg Completion Rate</h4>
              <p>{summary.avg_completion_rate}%</p>
            </div>
          </div>

          <div className="divider" />

          {/* List of Challenges */}
          <h3 className="font-bold text-lg mb-4">🎯 Active Challenges</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {summary.habits?.map((h) => {
              const habitId = h.habit_id;
              const dates = getChallengeDates(h.start_date, h.duration_days);
              const historySet = new Set(h.history);
              const endDate = new Date(new Date(h.start_date).getTime() + (h.duration_days - 1) * 24 * 60 * 60 * 1000);
              const isPastEnd = new Date() > endDate;

              return (
                <div key={habitId} className="glass-card" style={{ padding: '2rem' }}>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-xl mb-1">{h.title}</h3>
                      <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                        📅 {h.start_date} to {endDate.toISOString().substring(0, 10)} ({h.duration_days} Days) •{' '}
                        <span className={`badge ${h.status === 'active' ? 'badge-active' : 'badge-completed'}`}>
                          {h.status}
                        </span>
                      </p>
                    </div>

                    <div className="flex gap-2">
                      {h.status === 'active' && isPastEnd && (
                        <button
                          className="btn"
                          style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem' }}
                          onClick={() => handleMarkComplete(habitId)}
                        >
                          <CheckCircle2 size={14} /> Finish
                        </button>
                      )}
                      {h.status === 'completed' && (
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '0.4rem 0.6rem', fontSize: '0.85rem' }}
                          onClick={() => handleArchiveChallenge(habitId)}
                        >
                          Archive
                        </button>
                      )}
                      <button
                        className="btn btn-danger"
                        style={{ padding: '0.4rem 0.6rem' }}
                        onClick={() => handleDeleteChallenge(habitId)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>

                  {h.description && (
                    <p className="text-muted mb-4" style={{ fontSize: '0.9rem' }}>
                      {h.description}
                    </p>
                  )}

                  {/* Highlights row */}
                  <div className="grid-4 mb-4" style={{ background: 'rgba(255,255,255,0.01)', borderRadius: '10px', padding: '0.75rem', border: '1px solid rgba(255,255,255,0.03)' }}>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>Streak</span>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        <Flame size={16} style={{ color: 'var(--primary-pink)' }} />
                        <strong style={{ fontSize: '1rem' }}>{h.current_streak} Days</strong>
                      </div>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>Max Streak</span>
                      <div className="flex items-center justify-center gap-1 mt-1">
                        <Trophy size={16} style={{ color: '#f1c40f' }} />
                        <strong style={{ fontSize: '1rem' }}>{h.longest_streak} Days</strong>
                      </div>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>Completion</span>
                      <strong style={{ fontSize: '1rem', display: 'block', marginTop: '0.2rem', color: 'var(--primary-blue)' }}>{h.completion_rate}%</strong>
                    </div>
                    <div className="text-center">
                      <span className="text-muted" style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>Checked In</span>
                      <strong style={{ fontSize: '1rem', display: 'block', marginTop: '0.2rem', color: '#2ecc71' }}>{h.completed_days_count} / {h.duration_days}</strong>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div style={{ height: '6px', background: 'rgba(255,255,255,0.05)', borderRadius: '3px', marginBottom: '1.5rem', overflow: 'hidden' }}>
                    <div style={{ height: '100%', width: `${Math.min(h.completion_rate, 100)}%`, background: 'linear-gradient(90deg, var(--primary-blue), var(--primary-purple))', transition: 'width 0.3s ease' }} />
                  </div>

                  {/* Habit Calendar Checkbox Grid */}
                  <h4 className="font-semibold mb-2" style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Completion Grid:</h4>
                  <div className="challenge-grid">
                    {dates.map((dateObj, idx) => {
                      const dateStr = dateObj.toISOString().substring(0, 10);
                      const isFuture = isFutureDate(dateObj);
                      const checked = historySet.has(dateStr);

                      return (
                        <div
                          key={idx}
                          className={`challenge-day-card ${checked ? 'checked' : ''} ${isFuture ? 'future' : ''}`}
                          onClick={() => !isFuture && handleToggleLog(habitId, dateStr, checked)}
                        >
                          <span className="day-number">Day {idx + 1}</span>
                          {isFuture ? (
                            <Lock size={12} className="text-muted" />
                          ) : checked ? (
                            <CheckCircle2 size={12} className="day-check-icon" />
                          ) : (
                            <span style={{ width: 12, height: 12, borderRadius: '50%', border: '1px solid rgba(255,255,255,0.3)' }} />
                          )}
                          <span className="day-date">{formatDateLabel(dateObj)}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}

            {summary.habits?.length === 0 && (
              <div className="glass-card text-center text-muted p-8">
                <Calendar size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
                <p>No logged challenges. Click 'Start Challenge' above to setup a daily habit logs sheet.</p>
              </div>
            )}
          </div>

          <div className="divider" />

          {/* Recharts Analytics graphs */}
          {summary.habits?.length > 0 && (
            <div>
              <h3 className="font-bold text-lg mb-4">📈 Habit Analytics</h3>
              <div className="grid-2">
                {/* Graph 1: Completion rates */}
                <div className="glass-card" style={{ height: '350px' }}>
                  <h4 className="font-semibold text-center mb-4" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Completion Rates (%)</h4>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={getChartData()} layout="vertical">
                      <XAxis type="number" domain={[0, 100]} stroke="#a0a0cc" />
                      <YAxis dataKey="name" type="category" width={100} stroke="#a0a0cc" style={{ fontSize: '0.8rem' }} />
                      <Tooltip contentStyle={{ background: '#150f27', borderColor: 'var(--primary-purple)' }} />
                      <Bar dataKey="Completion Rate" fill="var(--primary-blue)" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Graph 2: Streaks comparison */}
                <div className="glass-card" style={{ height: '350px' }}>
                  <h4 className="font-semibold text-center mb-4" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Streaks Comparison (Days)</h4>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={getChartData()}>
                      <XAxis dataKey="name" stroke="#a0a0cc" style={{ fontSize: '0.8rem' }} />
                      <YAxis stroke="#a0a0cc" />
                      <Tooltip contentStyle={{ background: '#150f27', borderColor: 'var(--primary-purple)' }} />
                      <Legend />
                      <Bar dataKey="Current Streak" fill="var(--primary-pink)" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Longest Streak" fill="var(--primary-purple)" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-6 text-muted">No habit logs available. Start by adding a challenge.</div>
      )}
    </div>
  );
}
