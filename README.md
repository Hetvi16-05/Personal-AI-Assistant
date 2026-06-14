# Personal AI Assistant v2.0

> Production-ready AI mentor with persistent memory, pgvector long-term memory, JWT auth, multi-user isolation, agent layer, analytics, and Docker deployment.

**Stack:** FastAPI · Supabase PostgreSQL · pgvector · Gemini 2.5 Flash · Streamlit · Docker · Railway

---

## Architecture

```
User (Browser)
     │
     ▼
Streamlit Frontend (Login, Chat, Goals, Analytics, Insights)
     │ JWT Bearer Token
     ▼
FastAPI Backend
     ├── Auth Layer (JWT + bcrypt)
     ├── Routes (goals / tasks / projects / chat / insights / ai)
     │
     ├── Agent Layer ──────────────────────────────────────────────┐
     │   ├── PlannerAgent           Roadmap generation             │
     │   ├── MemoryAgent            Structured + vector context    │
     │   └── RecommendationAgent    NBA Engine V2                  │
     │                                                              │
     ├── Services                                                   │
     │   ├── MemoryService          Structured context builder     │
     │   ├── VectorMemoryService    pgvector embed + retrieve      │
     │   ├── GoalPlannerService     AI roadmap + milestones        │
     │   ├── RecommendationService  Dynamic scoring engine         │
     │   ├── InsightService         4-type AI insight generation   │
     │   ├── DailyCoachService      Morning AI briefing            │
     │   └── WeeklyReviewService    Performance report             │
     │                                                              │
     └── Database (Supabase PostgreSQL + pgvector) ◄───────────────┘
          users, goals, projects, tasks, user_memory
          chat_sessions, chat_messages
          memory_embeddings (vector 768-dim)
          ai_insights, roadmaps, milestones, weekly_reports
```

---

## NBA Engine V2 Scoring

```python
score = (
    impact     * 0.35 +
    urgency    * 0.25 +
    alignment  * 0.20 +
    effort_match * 0.10 +
    focus_score  * 0.05 +
    consistency  * 0.05
)
```

Also returns: `why_it_matters`, `estimated_impact`, `productivity_score`, `consistency_score`

---

## Quick Start

### 1. Clone + virtual env

```bash
git clone https://github.com/Hetvi16-05/Personal-AI-Assistant
cd Personal-AI-Assistant
python -m venv venv && source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — add your real GEMINI_API_KEY and DATABASE_URL
```

### 4. Supabase Setup (one-time)

In Supabase SQL Editor, run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Then run migrations:
```bash
cd backend
alembic upgrade head
```

### 5. Start backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 6. Start frontend

```bash
cd frontend
streamlit run app.py
```

---

## Docker (local)

```bash
docker-compose up --build
```

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Frontend | http://localhost:8501 |

---

## Deploy to Production

| Component | Platform | Notes |
|-----------|----------|-------|
| Backend | Railway | Set all env vars from `.env` |
| Database | Supabase | Already configured |
| Frontend | Streamlit Cloud | Set `API_URL=https://your-railway-url` |
| LLM | Gemini 2.5 Flash | Free tier |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | /auth/register | ❌ | Create account |
| POST | /auth/login | ❌ | Get JWT token |
| GET | /auth/me | ✅ | Current user |
| GET | /goals | ✅ | List goals |
| POST | /goals | ✅ | Create goal |
| GET | /tasks | ✅ | List tasks |
| POST | /tasks | ✅ | Create task |
| GET | /projects | ✅ | List projects |
| POST | /chat/sessions | ✅ | New chat session |
| POST | /chat/sessions/{id}/messages | ✅ | Send message (stores + AI responds) |
| GET | /ai/next-action | ✅ | NBA Engine V2 |
| GET | /ai/daily-coach | ✅ | Morning briefing |
| GET | /ai/weekly-review | ✅ | Weekly report |
| POST | /ai/generate-roadmap | ✅ | Goal roadmap |
| GET | /insights | ✅ | Generate AI insights |
| GET | /health | ❌ | Health check |

---

## Status

| Feature | Status |
|---------|--------|
| FastAPI Backend | ✅ |
| Supabase PostgreSQL | ✅ |
| Alembic Migrations | ✅ |
| JWT Authentication | ✅ |
| Multi-User Isolation | ✅ |
| pgvector Long-Term Memory | ✅ |
| Agent Layer (3 agents) | ✅ |
| Chat Memory (Sessions) | ✅ |
| NBA Engine V2 | ✅ |
| AI Insights Engine | ✅ |
| Analytics Dashboard (Plotly) | ✅ |
| Daily Coach | ✅ |
| Weekly Review | ✅ |
| Docker | ✅ |
| Streamlit Frontend | ✅ |
