import React, { useState, useEffect } from 'react';
import { apiGet, apiPost, apiPatch, apiDelete } from '../utils/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Calendar, Flame, Trophy, Trash2, CheckCircle2, ChevronDown, ChevronUp, Lock, Plus } from 'lucide-react';

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
  const [subtasks, setSubtasks] = useState([]);
  const [newSubtask, setNewSubtask] = useState('');
  const [selectedDates, setSelectedDates] = useState({});

  const [localLogs, setLocalLogs] = useState({});
  const [savingKeys, setSavingKeys] = useState({}); // tracks which subtask rows are saving
  const [showManageHabits, setShowManageHabits] = useState(false);
  const [reminderEnabled, setReminderEnabled] = useState(
    localStorage.getItem('hourly_reminder') === 'true'
  );

  useEffect(() => {
    fetchSummary();
  }, []);

  useEffect(() => {
    if (summary && summary.habits) {
      const newLocalLogs = {};
      summary.habits.forEach(h => {
        h.logs?.forEach(log => {
          const key = `${h.habit_id}_${log.date}`;
          newLocalLogs[key] = log.completed_subtasks || [];
        });
      });
      // Merge: server data is the base (fresh after save), user's unsaved edits on
      // OTHER keys are preserved by only keeping prev entries not returned by server.
      setLocalLogs(prev => {
        const merged = { ...newLocalLogs };
        Object.keys(prev).forEach(k => {
          if (!(k in newLocalLogs)) {
            merged[k] = prev[k]; // keep unsaved in-progress edits for new days
          }
        });
        return merged;
      });
    }
  }, [summary]);

  const toggleReminder = () => {
    const nextVal = !reminderEnabled;
    setReminderEnabled(nextVal);
    localStorage.setItem('hourly_reminder', nextVal ? 'true' : 'false');
    
    if (nextVal) {
      if (Notification.permission === 'default' || Notification.permission === 'denied') {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            new Notification("🧠 Daily Challenges Reminder Enabled!", {
              body: "You will be reminded every hour if there are pending daily challenges."
            });
            checkAndNotify(summary?.habits);
          }
        });
      } else if (Notification.permission === 'granted') {
        new Notification("🧠 Daily Challenges Reminder Enabled!", {
          body: "You will be reminded every hour if there are pending daily challenges."
        });
        checkAndNotify(summary?.habits);
      }
    }
  };

  const checkAndNotify = (habitsList) => {
    const todayStr = new Date().toISOString().substring(0, 10);
    const pendingHabits = [];

    habitsList?.forEach(h => {
      if (h.status === 'active') {
        const todayLog = h.logs?.find(log => log.date === todayStr);
        if (!todayLog || !todayLog.completed) {
          pendingHabits.push(h.title);
        }
      }
    });

    if (pendingHabits.length > 0) {
      if (Notification.permission === 'granted') {
        new Notification("🧠 Daily Challenges Reminder", {
          body: `You still have pending challenges today: ${pendingHabits.join(', ')}. Click to check them off!`,
        });
      }
    }
  };

  useEffect(() => {
    let intervalId;
    if (reminderEnabled && summary?.habits) {
      // Check every 1 hour (3600000 ms)
      intervalId = setInterval(() => {
        checkAndNotify(summary.habits);
      }, 3600000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [reminderEnabled, summary]);

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

  const getSelectedDate = (habitId) => {
    return selectedDates[habitId] || new Date().toISOString().substring(0, 10);
  };

  const handleDayClick = (h, dateStr, currentChecked) => {
    if (h.subtasks && h.subtasks.length > 0) {
      setSelectedDates({
        ...selectedDates,
        [h.habit_id]: dateStr
      });
    } else {
      handleToggleLog(h.habit_id, dateStr, currentChecked);
    }
  };

  const handleToggleSubtask = async (h, dateStr, subtaskTitle) => {
    const key = `${h.habit_id}_${dateStr}`;
    const current = localLogs[key] || [];
    const next = current.includes(subtaskTitle)
      ? current.filter(t => t !== subtaskTitle)
      : [...current, subtaskTitle];

    // Optimistic UI update
    setLocalLogs(prev => ({ ...prev, [key]: next }));

    // Mark this specific subtask as saving
    const saveKey = `${key}_${subtaskTitle}`;
    setSavingKeys(prev => ({ ...prev, [saveKey]: true }));

    try {
      const payload = {
        date: dateStr,
        completed: next.length >= h.subtasks.length,
        completed_subtasks: next
      };
      await apiPost(`/habits/${h.habit_id}/log`, payload);
      fetchSummary();
    } catch (err) {
      console.error(err);
      // Revert optimistic update on error
      setLocalLogs(prev => ({ ...prev, [key]: current }));
    } finally {
      setSavingKeys(prev => {
        const copy = { ...prev };
        delete copy[saveKey];
        return copy;
      });
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
        subtasks,
      };
      const result = await apiPost('/habits', payload);
      if (result) {
        setTitle('');
        setDescription('');
        setSubtasks([]);
        setNewSubtask('');
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

  // Get all active tasks for today
  const getTodayTasks = () => {
    if (!summary || !summary.habits) return [];
    
    const todayStr = new Date().toISOString().substring(0, 10);
    const tasksList = [];
    
    summary.habits.forEach(h => {
      if (h.status !== 'active') return;
      
      const hasSubtasks = h.subtasks && h.subtasks.length > 0;
      if (hasSubtasks) {
        h.subtasks.forEach(st => {
          const logKey = `${h.habit_id}_${todayStr}`;
          const completedSubtasks = localLogs[logKey] || [];
          const isChecked = completedSubtasks.includes(st);
          
          tasksList.push({
            type: 'subtask',
            id: `subtask_${h.habit_id}_${st}`,
            title: st,
            category: h.title,
            habit: h,
            checked: isChecked,
            isSaving: savingKeys[`${logKey}_${st}`],
            onToggle: () => handleToggleSubtask(h, todayStr, st)
          });
        });
      } else {
        const isChecked = h.logs?.find(log => log.date === todayStr)?.completed || false;
        
        tasksList.push({
          type: 'habit',
          id: `habit_${h.habit_id}`,
          title: h.title,
          category: 'General',
          habit: h,
          checked: isChecked,
          isSaving: false,
          onToggle: () => handleToggleLog(h.habit_id, todayStr, isChecked)
        });
      }
    });
    
    return tasksList;
  };

  const todayStr = new Date().toISOString().substring(0, 10);
  const todayTasks = getTodayTasks();
  const totalTasksCount = todayTasks.length;
  const completedTasksCount = todayTasks.filter(t => t.checked).length;
  const progressPercent = totalTasksCount > 0 ? Math.round((completedTasksCount / totalTasksCount) * 100) : 0;

  const todayFormatted = new Date(todayStr + 'T00:00:00').toLocaleDateString('en-US', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  });

  return (
    <div className="fade-in-section">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>📅 Daily Tasks</h1>
          <p className="text-muted">Form habits by tracking daily tasks. Maintain streaks and build consistency.</p>
        </div>
        <div className="flex gap-3 items-center">
          <button 
            type="button"
            className={`btn ${reminderEnabled ? '' : 'btn-secondary'}`}
            onClick={toggleReminder}
            style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
            title={reminderEnabled ? "Hourly reminders are active" : "Enable hourly reminders"}
          >
            ⏰ {reminderEnabled ? 'Hourly Reminder Active' : 'Enable Hourly Reminder'}
          </button>
          <button className="btn" onClick={() => setShowForm(!showForm)}>
            <Plus size={16} />
            {showForm ? 'Close' : 'Add Tasks/Category'}
          </button>
        </div>
      </div>

      {showForm && (
        <div className="glass-card mb-6">
          <h3 className="font-bold text-lg mb-4">🏁 Add Daily Habit Category & Tasks</h3>
          <form onSubmit={handleStartChallenge}>
            <div className="form-group">
              <label>Category Title *</label>
              <input
                type="text"
                placeholder="e.g. Medicine, Study, Fitness"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label>Description / Motivation</label>
              <textarea
                placeholder="Why is this category important? Keep your motivation visible..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={2}
              />
            </div>
            
            <div className="form-group">
              <label>Daily Sub-tasks (Checklist Items)</label>
              <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '-0.25rem', marginBottom: '0.5rem' }}>
                Add individual items you want to tick off daily (e.g. "Take medicine 1", "LeetCode", "GATE for 2 hours").
              </p>
              
              {subtasks.length > 0 && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  {subtasks.map((st, idx) => (
                    <div key={idx} className="flex justify-between items-center" style={{ background: 'rgba(255,255,255,0.02)', padding: '0.4rem 0.75rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.05)' }}>
                      <span style={{ fontSize: '0.9rem' }}>{st}</span>
                      <button
                        type="button"
                        onClick={() => setSubtasks(subtasks.filter((_, i) => i !== idx))}
                        style={{ background: 'none', border: 'none', color: '#ff4d4d', cursor: 'pointer', display: 'flex', alignItems: 'center' }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Type a subtask and press Enter or Add button"
                  value={newSubtask}
                  onChange={(e) => setNewSubtask(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      if (newSubtask.trim()) {
                        setSubtasks([...subtasks, newSubtask.trim()]);
                        setNewSubtask('');
                      }
                    }
                  }}
                />
                <button
                  type="button"
                  className="btn"
                  onClick={() => {
                    if (newSubtask.trim()) {
                      setSubtasks([...subtasks, newSubtask.trim()]);
                      setNewSubtask('');
                    }
                  }}
                  style={{ padding: '0.5rem 1.25rem' }}
                >
                  Add
                </button>
              </div>
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
          {/* Unified Daily Tasks Checklist Card */}
          <div className="glass-card" style={{ padding: '2rem' }}>
            <div className="flex justify-between items-center mb-4">
              <div>
                <h3 className="font-bold text-xl mb-1">📝 Today's Tasks</h3>
                <p className="text-muted" style={{ fontSize: '0.88rem' }}>
                  {todayFormatted}
                </p>
              </div>
              <div>
                <span style={{
                  fontSize: '0.85rem', fontWeight: 700, padding: '0.3rem 0.8rem',
                  borderRadius: '999px',
                  background: totalTasksCount > 0 && completedTasksCount === totalTasksCount
                    ? 'rgba(46,204,113,0.15)' : 'rgba(255,255,255,0.06)',
                  color: totalTasksCount > 0 && completedTasksCount === totalTasksCount
                    ? '#2ecc71' : 'var(--text-muted)',
                  border: totalTasksCount > 0 && completedTasksCount === totalTasksCount
                    ? '1px solid rgba(46,204,113,0.3)' : '1px solid rgba(255,255,255,0.08)'
                }}>
                  {totalTasksCount === 0 ? 'No tasks' : completedTasksCount === totalTasksCount ? '✅ All Done!' : `${completedTasksCount} / ${totalTasksCount}`}
                </span>
              </div>
            </div>

            {totalTasksCount > 0 && (
              <div style={{ height: '8px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px', marginBottom: '1.5rem', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${progressPercent}%`, background: 'linear-gradient(90deg, var(--primary-blue), var(--primary-purple))', transition: 'width 0.3s ease' }} />
              </div>
            )}

            {todayTasks.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {todayTasks.map((t) => (
                  <label
                    key={t.id}
                    onClick={() => !t.isSaving && t.onToggle()}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.75rem',
                      cursor: t.isSaving ? 'wait' : 'pointer',
                      margin: 0,
                      userSelect: 'none',
                      padding: '0.8rem 1.1rem',
                      borderRadius: '10px',
                      border: t.checked ? '1px solid rgba(46,204,113,0.35)' : '1px solid rgba(255,255,255,0.06)',
                      background: t.checked ? 'rgba(46,204,113,0.08)' : 'rgba(255,255,255,0.02)',
                      transition: 'all 0.2s',
                      opacity: t.isSaving ? 0.7 : 1
                    }}
                  >
                    {/* Custom styled checkbox */}
                    <div style={{
                      width: '22px',
                      height: '22px',
                      borderRadius: '7px',
                      flexShrink: 0,
                      border: t.checked ? '2px solid #2ecc71' : '2px solid rgba(255,255,255,0.25)',
                      background: t.checked ? '#2ecc71' : 'transparent',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.2s'
                    }}>
                      {t.isSaving ? (
                        <span style={{ fontSize: '10px', animation: 'spin 1s linear infinite', display: 'inline-block' }}>⟳</span>
                      ) : t.checked ? (
                        <span style={{ color: '#fff', fontSize: '12px', fontWeight: 900 }}>✓</span>
                      ) : null}
                    </div>
                    
                    <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                      <span style={{
                        fontSize: '0.95rem',
                        fontWeight: 500,
                        textDecoration: t.checked ? 'line-through' : 'none',
                        color: t.checked ? 'rgba(255,255,255,0.4)' : '#e2e8f0',
                        transition: 'all 0.2s'
                      }}>
                        {t.title}
                      </span>
                      <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.15rem' }}>
                        Category: {t.category}
                      </span>
                    </div>
                    
                    {t.checked && !t.isSaving && (
                      <span style={{ fontSize: '0.75rem', color: '#2ecc71', fontWeight: 600 }}>Saved ✓</span>
                    )}
                    {t.isSaving && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>Saving...</span>
                    )}
                  </label>
                ))}
              </div>
            ) : (
              <div className="text-center text-muted p-8">
                <Calendar size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
                <p>No active daily tasks found. Create a Category and add some tasks to see them here.</p>
              </div>
            )}
          </div>

          {/* Manage Categories Bottom Panel */}
          {summary.habits?.length > 0 && (
            <div className="glass-card mt-6" style={{ padding: '1.5rem' }}>
              <button
                type="button"
                className="flex justify-between items-center w-full"
                style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', textAlign: 'left' }}
                onClick={() => setShowManageHabits(!showManageHabits)}
              >
                <h3 className="font-bold text-lg flex items-center gap-2 m-0" style={{ color: '#fff' }}>
                  ⚙️ Manage Habit Categories ({summary.habits?.length || 0})
                </h3>
                {showManageHabits ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
              </button>
              
              {showManageHabits && (
                <div className="mt-4" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                    Here you can view, archive, or delete your daily categories. Deleting a category will remove its tasks from your checklist.
                  </p>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {summary.habits.map((h) => {
                      const endDate = new Date(new Date(h.start_date).getTime() + (h.duration_days - 1) * 24 * 60 * 60 * 1000);
                      const isPastEnd = new Date() > endDate;
                      
                      return (
                        <div key={h.habit_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                          <div>
                            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>{h.title}</h4>
                            <p className="text-muted" style={{ fontSize: '0.78rem', marginTop: '0.2rem' }}>
                              {h.duration_days} Days ({h.start_date} to {endDate.toISOString().substring(0, 10)}) • Streak: {h.current_streak} days • Rate: {h.completion_rate}%
                            </p>
                          </div>
                          
                          <div className="flex gap-2">
                            {h.status === 'active' && isPastEnd && (
                              <button
                                className="btn"
                                style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem' }}
                                onClick={() => handleMarkComplete(h.habit_id)}
                              >
                                Finish
                              </button>
                            )}
                            {h.status === 'completed' && (
                              <button
                                className="btn btn-secondary"
                                style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem' }}
                                onClick={() => handleArchiveChallenge(h.habit_id)}
                              >
                                Archive
                              </button>
                            )}
                            <button
                              className="btn btn-danger"
                              style={{ padding: '0.35rem 0.6rem', fontSize: '0.78rem' }}
                              onClick={() => handleDeleteChallenge(h.habit_id)}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-6 text-muted">No habit logs available. Start by adding a challenge.</div>
      )}
    </div>
  );
}
