from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.db import init_db
from app.routes import users, goals, projects, tasks, ai

app = FastAPI(
    title="Personal AI Assistant API",
    description="AI-powered personal mentor with memory, goal planning, and Next Best Action engine.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "running",
        "message": "Personal AI Assistant API",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}


app.include_router(users.router)
app.include_router(goals.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(ai.router)
