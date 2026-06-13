from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base


class GoalStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    deadline = Column(DateTime, nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="goals")
    tasks = relationship("Task", back_populates="goal", cascade="all, delete")
    projects = relationship("Project", back_populates="goal", cascade="all, delete")
    roadmaps = relationship("Roadmap", back_populates="goal", cascade="all, delete")
