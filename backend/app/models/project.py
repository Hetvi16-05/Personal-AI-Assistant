from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database.db import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    on_hold = "on_hold"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="projects")
    goal = relationship("Goal", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete")
