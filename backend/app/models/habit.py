from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.database.db import Base


class HabitStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    archived = "archived"


class DailyHabit(Base):
    __tablename__ = "daily_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(300), nullable=False)
    description = Column(Text, default="")
    duration_days = Column(Integer, default=30, nullable=False)
    start_date = Column(Date, default=date.today, nullable=False)
    status = Column(Enum(HabitStatus), default=HabitStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="habits")
    logs = relationship("DailyHabitLog", back_populates="habit", cascade="all, delete-orphan")


class DailyHabitLog(Base):
    __tablename__ = "daily_habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("daily_habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    habit = relationship("DailyHabit", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )
