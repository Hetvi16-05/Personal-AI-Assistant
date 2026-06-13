"""
Seed the database with a sample user, goals, projects, and tasks.
Run from the backend/ directory:
    python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from app.database.db import SessionLocal, init_db
from app.models import User, Goal, Project, Task, UserMemory

init_db()
db = SessionLocal()

# ── Clear existing data ──────────────────────────────────
db.query(UserMemory).delete()
db.query(Task).delete()
db.query(Project).delete()
db.query(Goal).delete()
db.query(User).delete()
db.commit()

# ── User ─────────────────────────────────────────────────
user = User(
    id=1,
    name="Hetvi",
    email="hetvi@example.com",
    skills="Python, Statistics, SQL",
    interests="AI, Machine Learning, Data Science, GATE DA",
    preferences="Morning study sessions, visual learning, project-based practice"
)
db.add(user)
db.flush()

# ── Goals ─────────────────────────────────────────────────
goal1 = Goal(
    user_id=1,
    title="Crack GATE DA 2025",
    description="Score 700+ in GATE Data Science and AI",
    deadline=datetime(2025, 2, 1),
    status="active"
)
goal2 = Goal(
    user_id=1,
    title="Become a Data Scientist in 6 months",
    description="Land a DS internship or job by end of year",
    deadline=datetime.utcnow() + timedelta(days=180),
    status="active"
)
db.add_all([goal1, goal2])
db.flush()

# ── Projects ──────────────────────────────────────────────
proj1 = Project(
    user_id=1,
    goal_id=goal2.id,
    title="ML Portfolio Project",
    description="End-to-end ML project with EDA, modeling, and deployment",
    status="active",
    deadline=datetime.utcnow() + timedelta(days=45)
)
proj2 = Project(
    user_id=1,
    goal_id=goal1.id,
    title="GATE DA Practice",
    description="Daily practice of GATE DA previous year questions",
    status="active"
)
db.add_all([proj1, proj2])
db.flush()

# ── Tasks ─────────────────────────────────────────────────
tasks = [
    Task(
        user_id=1, goal_id=goal2.id, project_id=proj1.id,
        title="Complete XGBoost tutorial",
        description="Study XGBoost, implement on Titanic dataset",
        deadline=datetime.utcnow() + timedelta(days=3),
        status="pending",
        impact_score=9.0, effort_score=4.0, urgency_score=8.0, alignment_score=9.0
    ),
    Task(
        user_id=1, goal_id=goal2.id,
        title="Finish EDA on ML portfolio project",
        description="Complete exploratory data analysis and visualizations",
        deadline=datetime.utcnow() + timedelta(days=7),
        status="in_progress",
        impact_score=8.0, effort_score=5.0, urgency_score=7.0, alignment_score=8.0
    ),
    Task(
        user_id=1, goal_id=goal1.id, project_id=proj2.id,
        title="Revise Statistics — Probability & Distributions",
        description="Cover probability theory, distributions, hypothesis testing",
        deadline=datetime.utcnow() + timedelta(days=5),
        status="pending",
        impact_score=9.0, effort_score=6.0, urgency_score=9.0, alignment_score=10.0
    ),
    Task(
        user_id=1, goal_id=goal2.id,
        title="Build a Streamlit dashboard for ML project",
        description="Interactive dashboard to showcase ML model results",
        deadline=datetime.utcnow() + timedelta(days=14),
        status="pending",
        impact_score=7.0, effort_score=6.0, urgency_score=5.0, alignment_score=7.0
    ),
    Task(
        user_id=1, goal_id=goal1.id,
        title="Solve 50 GATE DA previous year questions",
        deadline=datetime.utcnow() + timedelta(days=10),
        status="pending",
        impact_score=10.0, effort_score=7.0, urgency_score=9.0, alignment_score=10.0
    ),
]
db.add_all(tasks)

# ── Memory ────────────────────────────────────────────────
memories = [
    UserMemory(user_id=1, content="I am preparing for GATE DA 2025", tags="gate,goals", source="manual"),
    UserMemory(user_id=1, content="I am interested in AI and Machine Learning", tags="interests", source="manual"),
    UserMemory(user_id=1, content="I prefer studying in the morning", tags="preferences", source="manual"),
    UserMemory(user_id=1, content="I want to become a Data Scientist", tags="goals", source="manual"),
]
db.add_all(memories)
db.commit()

print("✅ Database seeded successfully!")
print(f"   User: {user.name}")
print(f"   Goals: {db.query(Goal).count()}")
print(f"   Projects: {db.query(Project).count()}")
print(f"   Tasks: {db.query(Task).count()}")
print(f"   Memories: {db.query(UserMemory).count()}")
db.close()
