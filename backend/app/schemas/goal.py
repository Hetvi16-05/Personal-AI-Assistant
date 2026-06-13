from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.goal import GoalStatus


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[GoalStatus] = None


class GoalOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    deadline: Optional[datetime]
    status: GoalStatus
    created_at: datetime

    class Config:
        from_attributes = True
