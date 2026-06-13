from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(DateTime, nullable=False)
    week_end = Column(DateTime, nullable=False)
    tasks_completed = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    most_active_goal = Column(String(300), default="")
    ai_summary = Column(Text, default="")
    recommendations = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
