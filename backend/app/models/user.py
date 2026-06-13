from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    skills = Column(Text, default="")          # comma-separated
    interests = Column(Text, default="")       # comma-separated
    preferences = Column(Text, default="")     # free-form notes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    goals = relationship("Goal", back_populates="user", cascade="all, delete")
    projects = relationship("Project", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="user", cascade="all, delete")
    memories = relationship("UserMemory", back_populates="user", cascade="all, delete")
