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
from app.auth.password import hash_password
from app.services.vector_memory_service import store_memory

init_db()
db = SessionLocal()

# ── Clear existing data ──────────────────────────────────
print("Clearing existing database tables...")
db.query(UserMemory).delete()
db.query(Task).delete()
db.query(Project).delete()
db.query(Goal).delete()
db.query(User).delete()
db.commit()

# ── User ─────────────────────────────────────────────────
print("Creating user 'Hetvi'...")
password_raw = "password123"
user = User(
    id=1,
    name="Hetvi",
    email="hetvi@example.com",
    password_hash=hash_password(password_raw),
    skills="Python, Statistics, SQL",
    interests="AI, Machine Learning, Data Science, GATE DA",
    preferences="Morning study sessions, visual learning, project-based practice"
)
db.add(user)
db.flush()

# ── Goals ─────────────────────────────────────────────────
print("Creating goals...")
goal1 = Goal(
    user_id=user.id,
    title="Crack GATE DA 2025",
    description="Score 700+ in GATE Data Science and AI exam",
    deadline=datetime(2025, 2, 1),
    status="active"
)
goal2 = Goal(
    user_id=user.id,
    title="Become a Data Scientist in 6 months",
    description="Land a DS internship or full-time job by end of year",
    deadline=datetime.utcnow() + timedelta(days=180),
    status="active"
)
db.add_all([goal1, goal2])
db.flush()

# ── Projects ──────────────────────────────────────────────
print("Creating projects...")
proj1 = Project(
    user_id=user.id,
    goal_id=goal2.id,
    title="ML Portfolio Project",
    description="End-to-end ML project with EDA, modeling, and dashboard deployment",
    status="active",
    deadline=datetime.utcnow() + timedelta(days=45)
)
proj2 = Project(
    user_id=user.id,
    goal_id=goal1.id,
    title="GATE DA Practice Series",
    description="Daily revision and solving of previous years' GATE DA papers",
    status="active"
)
db.add_all([proj1, proj2])
db.flush()

# ── Tasks ─────────────────────────────────────────────────
print("Creating tasks...")
tasks = [
    Task(
        user_id=user.id, goal_id=goal2.id, project_id=proj1.id,
        title="Complete XGBoost tutorial",
        description="Study XGBoost hyperparameter tuning, implement on Titanic dataset",
        deadline=datetime.utcnow() + timedelta(days=3),
        status="pending",
        impact_score=9.0, effort_score=4.0, urgency_score=8.0, alignment_score=9.0
    ),
    Task(
        user_id=user.id, goal_id=goal2.id,
        title="Finish EDA on ML portfolio project",
        description="Complete exploratory data analysis, correlation checks and visualizations",
        deadline=datetime.utcnow() + timedelta(days=7),
        status="in_progress",
        impact_score=8.0, effort_score=5.0, urgency_score=7.0, alignment_score=8.0
    ),
    Task(
        user_id=user.id, goal_id=goal1.id, project_id=proj2.id,
        title="Revise Statistics — Probability & Distributions",
        description="Cover probability theory, discrete and continuous distributions, hypothesis testing",
        deadline=datetime.utcnow() + timedelta(days=5),
        status="pending",
        impact_score=9.0, effort_score=6.0, urgency_score=9.0, alignment_score=10.0
    ),
    Task(
        user_id=user.id, goal_id=goal2.id,
        title="Build a Streamlit dashboard for ML project",
        description="Interactive dashboard to showcase ML model results and metrics",
        deadline=datetime.utcnow() + timedelta(days=14),
        status="pending",
        impact_score=7.0, effort_score=6.0, urgency_score=5.0, alignment_score=7.0
    ),
    Task(
        user_id=user.id, goal_id=goal1.id,
        title="Solve 50 GATE DA previous year questions",
        description="Focus on Linear Algebra, Calculus, and Data Structures questions",
        deadline=datetime.utcnow() + timedelta(days=10),
        status="pending",
        impact_score=10.0, effort_score=7.0, urgency_score=9.0, alignment_score=10.0
    ),
]
db.add_all(tasks)
db.commit()

# ── Memory ────────────────────────────────────────────────
print("Creating memory records...")
memories = [
    UserMemory(user_id=user.id, content="I am preparing for GATE DA 2025", tags="gate,goals", source="manual"),
    UserMemory(user_id=user.id, content="I am interested in AI and Machine Learning", tags="interests", source="manual"),
    UserMemory(user_id=user.id, content="I prefer studying in the morning", tags="preferences", source="manual"),
    UserMemory(user_id=user.id, content="I want to become a Data Scientist", tags="goals", source="manual"),
]
db.add_all(memories)
db.commit()

# ── Vector Embeddings ─────────────────────────────────────
print("Generating and saving vector memory embeddings via Gemini model...")
vector_memories = [
    ("I am preparing for the GATE Data Science and AI (DA) exam in 2025", "gate,exams"),
    ("My favorite programming language is Python", "programming,skills"),
    ("I prefer morning study sessions and visual learning guides", "preferences"),
    ("I want to become a professional Data Scientist or Machine Learning Engineer", "career,goals"),
]

for content, tags in vector_memories:
    try:
        store_memory(db, user.id, content, tags)
    except Exception as e:
        print(f"Skipped vector memory embedding generation: {e}")

print("\n✅ Database seeded successfully!")
print(f"   User Login Email : {user.email}")
print(f"   User Password    : {password_raw}")
print(f"   Goals count      : {db.query(Goal).filter(Goal.user_id == user.id).count()}")
print(f"   Projects count   : {db.query(Project).filter(Project.user_id == user.id).count()}")
print(f"   Tasks count      : {db.query(Task).filter(Task.user_id == user.id).count()}")
print(f"   Memories count   : {db.query(UserMemory).filter(UserMemory.user_id == user.id).count()}")
db.close()
