import React, { useState, useEffect } from 'react';
import { apiGet } from '../utils/api';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ScatterChart, Scatter, ZAxis, LabelList, Legend } from 'recharts';
import { BarChart2, PieChart as PieIcon, Activity } from 'lucide-react';

export default function Analytics() {
  const [goals, setGoals] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const gData = await apiGet('/goals') || [];
      const tData = await apiGet('/tasks') || [];
      setGoals(gData);
      setTasks(tData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-muted text-center p-6">Computing analytics metrics...</div>;
  }

  if (tasks.length === 0 && goals.length === 0) {
    return (
      <div className="glass-card text-center text-muted p-8">
        <BarChart2 size={48} className="mb-2" style={{ opacity: 0.3, margin: '0 auto' }} />
        <p>Add some goals and tasks to unlock your performance analytics dashboard.</p>
      </div>
    );
  }

  // Quick stats calculation
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'completed').length;
  const inProgressTasks = tasks.filter(t => t.status === 'in_progress').length;
  const pendingTasks = tasks.filter(t => t.status === 'pending').length;
  const activeGoals = goals.filter(g => g.status === 'active').length;

  // Task Status Donut Data
  const statusData = [
    { name: 'Completed', value: completedTasks, color: '#2ecc71' },
    { name: 'In Progress', value: inProgressTasks, color: '#f1c40f' },
    { name: 'Pending', value: pendingTasks, color: '#444466' }
  ].filter(d => d.value > 0);

  // Goal Progress Calculation
  const goalMap = {};
  goals.forEach(g => {
    goalMap[g.id] = g.title;
  });

  const goalTotal = {};
  const goalDone = {};
  tasks.forEach(t => {
    const gid = t.goal_id;
    if (gid) {
      goalTotal[gid] = (goalTotal[gid] || 0) + 1;
      if (t.status === 'completed') {
        goalDone[gid] = (goalDone[gid] || 0) + 1;
      }
    }
  });

  const goalProgressData = Object.keys(goalTotal).map(gid => {
    const total = goalTotal[gid];
    const done = goalDone[gid] || 0;
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    return {
      name: goalMap[gid] ? (goalMap[gid].substring(0, 20) + (goalMap[gid].length > 20 ? '...' : '')) : `Goal ${gid}`,
      'Completion %': pct
    };
  });

  // Task Priority Matrix (Scatter Data)
  const scatterData = tasks.map(t => ({
    name: t.title.substring(0, 15) + (t.title.length > 15 ? '...' : ''),
    Urgency: t.urgency_score,
    Impact: t.impact_score
  }));

  return (
    <div className="fade-in-section">
      <h1 className="mb-6" style={{ fontSize: '2.2rem', fontWeight: 800 }}>📈 Performance Analytics</h1>

      {/* Metrics Row */}
      <div className="grid-4 mb-6">
        <div className="metric-card">
          <h4>Total Tasks</h4>
          <p>{totalTasks}</p>
        </div>
        <div className="metric-card">
          <h4>Completed</h4>
          <p>{completedTasks}</p>
        </div>
        <div className="metric-card">
          <h4>In Progress</h4>
          <p>{inProgressTasks}</p>
        </div>
        <div className="metric-card">
          <h4>Active Goals</h4>
          <p>{activeGoals}</p>
        </div>
      </div>

      <div className="divider" />

      {/* Charts Row */}
      <div className="grid-2 mb-6">
        {/* Donut Chart */}
        <div className="glass-card" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <PieIcon size={18} style={{ color: 'var(--primary-purple)' }} />
            Task Status Breakdown
          </h3>
          <div style={{ flexGrow: 1, minHeight: '220px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            {statusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={90}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ background: '#150f27', borderColor: 'var(--primary-purple)' }} />
                  <Legend iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <span className="text-muted">No task logs logged yet.</span>
            )}
          </div>
        </div>

        {/* Goal Progress Bars */}
        <div className="glass-card" style={{ height: '380px', display: 'flex', flexDirection: 'column' }}>
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <BarChart2 size={18} style={{ color: 'var(--primary-blue)' }} />
            Goal Progress (%)
          </h3>
          <div style={{ flexGrow: 1, minHeight: '220px' }}>
            {goalProgressData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={goalProgressData} layout="vertical" margin={{ left: 10, right: 30 }}>
                  <XAxis type="number" domain={[0, 100]} stroke="#a0a0cc" />
                  <YAxis dataKey="name" type="category" stroke="#a0a0cc" width={110} style={{ fontSize: '0.75rem' }} />
                  <Tooltip contentStyle={{ background: '#150f27', borderColor: 'var(--primary-purple)' }} />
                  <Bar dataKey="Completion %" fill="var(--primary-purple)" radius={[0, 4, 4, 0]}>
                    <LabelList dataKey="Completion %" position="right" fill="#fff" style={{ fontSize: '0.8rem' }} formatter={v => `${v}%`} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-muted text-center p-6">Connect tasks to goals to track their progress.</div>
            )}
          </div>
        </div>
      </div>

      <div className="divider" />

      {/* Task Priority Matrix (Scatter Chart) */}
      <div className="glass-card" style={{ height: '450px', display: 'flex', flexDirection: 'column' }}>
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <Activity size={18} style={{ color: 'var(--primary-pink)' }} />
          Task Priority Matrix (Urgency vs Impact)
        </h3>
        <div style={{ flexGrow: 1, minHeight: '300px' }}>
          {scatterData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
                <XAxis type="number" dataKey="Urgency" name="Urgency" domain={[0, 10]} stroke="#a0a0cc" label={{ value: 'Urgency', position: 'bottom', fill: '#a0a0cc' }} />
                <YAxis type="number" dataKey="Impact" name="Impact" domain={[0, 10]} stroke="#a0a0cc" label={{ value: 'Impact', angle: -90, position: 'insideLeft', fill: '#a0a0cc' }} />
                <ZAxis type="category" dataKey="name" name="Task" />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ background: '#150f27', borderColor: 'var(--primary-purple)' }} />
                <Scatter name="Tasks" data={scatterData} fill="var(--primary-blue)">
                  <LabelList dataKey="name" position="top" style={{ fill: '#c0c0ff', fontSize: '0.75rem' }} />
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-muted text-center p-6">Add tasks with impact and urgency scores to see matrix.</div>
          )}
        </div>
      </div>
    </div>
  );
}
