import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.database.db import init_db
from app.routes import users, goals, projects, tasks, ai
from app.routes import auth, chat, insights, habits

# ── Logging ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personal AI Assistant API",
    description="Production-ready AI mentor with memory, goal planning, and Next Best Action engine.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ── CORS ─────────────────────────────────────────────────
# Set ALLOWED_ORIGINS env var in production (comma-separated Vercel URLs)
# e.g. "https://saarthi-ai.vercel.app,https://saarthi-ai-git-main.vercel.app"
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allow_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global Error Handler ──────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again."}
    )


# ── Startup ──────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    logger.info("Starting Personal AI Assistant API v2.0")
    init_db()
    logger.info("Database initialized")


# ── Health ───────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "running", "version": "2.0.0", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "2.0.0"}


# ── Routers ──────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(chat.router)
app.include_router(insights.router)
app.include_router(habits.router)
