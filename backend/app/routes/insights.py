from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database.db import get_db
from app.models.user import User
from app.models.insight import AIInsight
from app.services.insight_service import InsightService
from app.auth.dependencies import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/insights", tags=["AI Insights"])


class InsightOut(BaseModel):
    id: int
    insight_type: str
    content: str
    generated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[dict])
def generate_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate fresh AI insights based on user's current data."""
    service = InsightService(db, current_user.id)
    return service.generate_insights()


@router.get("/history", response_model=List[InsightOut])
def get_insight_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return past generated insights."""
    service = InsightService(db, current_user.id)
    return service.get_history()
