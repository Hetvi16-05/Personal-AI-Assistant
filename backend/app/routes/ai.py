from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.services.goal_planner import GoalPlannerService
from app.services.recommendation_service import RecommendationService
from app.services.daily_coach import DailyCoachService
from app.services.weekly_review import WeeklyReviewService
from app.services.memory_service import MemoryService
from app.ai.llm import ask_llm
from app.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])


class RoadmapRequest(BaseModel):
    goal_id: int


class ChatRequest(BaseModel):
    message: str


@router.post("/generate-roadmap")
def generate_roadmap(payload: RoadmapRequest, db: Session = Depends(get_db)):
    try:
        service = GoalPlannerService(db, settings.DEFAULT_USER_ID)
        return service.generate_roadmap(payload.goal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


@router.get("/next-action")
def next_action(db: Session = Depends(get_db)):
    service = RecommendationService(db, settings.DEFAULT_USER_ID)
    return service.next_action()


@router.get("/daily-coach")
def daily_coach(db: Session = Depends(get_db)):
    service = DailyCoachService(db, settings.DEFAULT_USER_ID)
    return service.get_briefing()


@router.get("/weekly-review")
def weekly_review(db: Session = Depends(get_db)):
    service = WeeklyReviewService(db, settings.DEFAULT_USER_ID)
    return service.generate_review()


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    """Free-form AI chat enriched with full user memory context."""
    mem_service = MemoryService(db, settings.DEFAULT_USER_ID)
    context = mem_service.build_context()

    system = """You are a personal AI assistant and mentor.
You have deep knowledge of the user's goals, projects, tasks, and memory.
Answer helpfully, specifically, and personally. Reference their actual data when relevant."""

    prompt = f"""
{context}

## User's Message
{payload.message}
"""

    response = ask_llm(prompt, system)

    # Store the exchange in memory
    mem_service.add_memory(
        content=f"User asked: {payload.message}",
        tags="chat",
        source="chat"
    )

    return {"response": response, "context_used": True}
