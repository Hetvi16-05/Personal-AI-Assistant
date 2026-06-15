import logging
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock to specific origins in production
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
