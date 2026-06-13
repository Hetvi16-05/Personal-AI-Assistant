from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    goal_id: Optional[int] = None
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    deadline: Optional[datetime] = None


class ProjectOut(BaseModel):
    id: int
    user_id: int
    goal_id: Optional[int]
    title: str
    description: str
    status: ProjectStatus
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
