from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    summary = Column(Text, default="")          # full LLM-generated roadmap text
    created_at = Column(DateTime, default=datetime.utcnow)

    goal = relationship("Goal", back_populates="roadmaps")
    milestones = relationship("Milestone", back_populates="roadmap", cascade="all, delete")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    roadmap_id = Column(Integer, ForeignKey("roadmaps.id"), nullable=False)
    period = Column(String(100), nullable=False)   # e.g. "Month 1", "Week 2"
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    roadmap = relationship("Roadmap", back_populates="milestones")
