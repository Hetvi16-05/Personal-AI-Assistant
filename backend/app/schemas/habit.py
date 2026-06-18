from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.habit import HabitStatus


class HabitLogCreate(BaseModel):
    date: date
    completed: Optional[bool] = True
    completed_subtasks: Optional[List[str]] = []


class HabitLogOut(BaseModel):
    id: int
    habit_id: int
    date: date
    completed: bool
    completed_subtasks: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class HabitCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = ""
    duration_days: int = Field(default=30, ge=1, le=31)
    start_date: Optional[date] = None
    subtasks: Optional[List[str]] = []


class HabitUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    duration_days: Optional[int] = Field(None, ge=1, le=31)
    status: Optional[HabitStatus] = None
    subtasks: Optional[List[str]] = None


class HabitOut(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    duration_days: int
    start_date: date
    status: HabitStatus
    subtasks: List[str] = []
    created_at: datetime
    logs: List[HabitLogOut] = []

    class Config:
        from_attributes = True


class HabitAnalytics(BaseModel):
    habit_id: int
    title: str
    duration_days: int
    start_date: date
    status: HabitStatus
    completed_days_count: int
    completion_rate: float
    current_streak: int
    longest_streak: int
    history: List[date]
    subtasks: List[str] = []
    logs: List[HabitLogOut] = []

    class Config:
        from_attributes = True


class HabitsSummaryAnalytics(BaseModel):
    total_habits: int
    active_habits: int
    completed_habits: int
    avg_completion_rate: float
    habits: List[HabitAnalytics]
