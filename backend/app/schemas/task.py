from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    deadline: Optional[datetime] = None
    goal_id: Optional[int] = None
    project_id: Optional[int] = None
    impact_score: Optional[float] = 5.0
    effort_score: Optional[float] = 5.0
    urgency_score: Optional[float] = 5.0
    alignment_score: Optional[float] = 5.0


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = None
    impact_score: Optional[float] = None
    effort_score: Optional[float] = None
    urgency_score: Optional[float] = None
    alignment_score: Optional[float] = None


class TaskOut(BaseModel):
    id: int
    user_id: int
    goal_id: Optional[int]
    project_id: Optional[int]
    title: str
    description: str
    deadline: Optional[datetime]
    status: TaskStatus
    impact_score: float
    effort_score: float
    urgency_score: float
    alignment_score: float
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
