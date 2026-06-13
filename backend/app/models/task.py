from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)

    # Scoring fields for Next Best Action Engine
    impact_score = Column(Float, default=5.0)    # 1-10: how impactful is this task
    effort_score = Column(Float, default=5.0)    # 1-10: how much effort required
    urgency_score = Column(Float, default=5.0)   # 1-10: how time-sensitive
    alignment_score = Column(Float, default=5.0) # 1-10: how aligned with goal

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
