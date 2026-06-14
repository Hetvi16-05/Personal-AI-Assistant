from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database.db import get_db
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.agents.planner_agent import PlannerAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.memory_agent import MemoryAgent
from app.services.daily_coach import DailyCoachService
from app.services.weekly_review import WeeklyReviewService
from app.services.vector_memory_service import store_memory
from app.ai.llm import ask_llm

router = APIRouter(prefix="/ai", tags=["AI"])


class RoadmapRequest(BaseModel):
    goal_id: int


class ChatRequest(BaseModel):
    message: str


@router.post("/generate-roadmap")
def generate_roadmap(
    payload: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        agent = PlannerAgent(db, current_user.id)
        return agent.generate_roadmap(payload.goal_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roadmap generation failed: {str(e)}")


@router.get("/next-action")
def next_action(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    agent = RecommendationAgent(db, current_user.id)
    return agent.next_action()


@router.get("/daily-coach")
def daily_coach(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = DailyCoachService(db, current_user.id)
    return service.get_briefing()


@router.get("/weekly-review")
def weekly_review(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = WeeklyReviewService(db, current_user.id)
    return service.generate_review()


@router.post("/chat")
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Quick AI chat (stateless). Use /chat/sessions for persistent conversations."""
    agent = MemoryAgent(db, current_user.id)
    context = agent.build_full_context(query=payload.message)

    system = """You are a personal AI assistant and mentor.
Answer helpfully and specifically using the user's actual goals and data."""

    prompt = f"{context}\n\n## User Message\n{payload.message}"

    response = ask_llm(prompt, system)
    store_memory(db, current_user.id, payload.message, tags="chat")

    return {"response": response, "context_used": True}
