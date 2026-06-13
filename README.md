# Personal AI Assistant

An AI-powered personal mentor with persistent memory, goal planning, Next Best Action engine, and a Streamlit UI — built with **FastAPI + SQLite + Google Gemini**.

---

## Architecture

```
Personal-AI-Assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI entry point
│   │   ├── config.py            ← Settings (env vars)
│   │   ├── database/db.py       ← SQLAlchemy engine
│   │   ├── models/              ← ORM models (8 tables)
│   │   ├── schemas/             ← Pydantic schemas
│   │   ├── routes/              ← API routers
│   │   ├── services/            ← Business logic + AI services
│   │   └── ai/llm.py            ← Gemini LLM wrapper
│   ├── seed.py                  ← Sample data
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── app.py                   ← Streamlit UI
    └── requirements.txt
```

---

## Quick Start

### 1. Set up environment

```bash
cd Personal-AI-Assistant
python -m venv venv
source venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r backend/requirements.txt
```

### 3. Configure environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — add your GEMINI_API_KEY
```

Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### 4. Seed the database

```bash
cd backend
python seed.py
```

### 5. Start the API server

```bash
cd backend
uvicorn app.main:app --reload
```

API runs at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### 6. Start the Streamlit frontend

In a new terminal:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Frontend runs at: http://localhost:8501

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /users | Create user profile |
| GET | /users/me | Get profile |
| PATCH | /users/me | Update profile |
| POST | /goals | Create goal |
| GET | /goals | List goals |
| GET | /goals/{id} | Get goal |
| DELETE | /goals/{id} | Delete goal |
| POST | /projects | Create project |
| GET | /projects | List projects |
| POST | /tasks | Create task |
| GET | /tasks | List tasks |
| PATCH | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| POST | /ai/generate-roadmap | AI roadmap generator |
| GET | /ai/next-action | Next Best Action engine |
| GET | /ai/daily-coach | Daily AI briefing |
| GET | /ai/weekly-review | Weekly review + report |
| POST | /ai/chat | Free-form AI chat |

---

## Next Best Action Formula

```python
score = (
    impact * 0.4 +
    urgency * 0.3 +
    alignment * 0.2 +
    effort_match * 0.1
)
```

---

## Status

In Development 🚀

| Feature | Status |
|---------|--------|
| FastAPI Backend | ✅ |
| SQLite Database | ✅ |
| Memory System | ✅ |
| Goal Planner (AI) | ✅ |
| Task Manager | ✅ |
| Next Best Action Engine | ✅ |
| Daily AI Coach | ✅ |
| Weekly Review | ✅ |
| Streamlit Frontend | ✅ |
