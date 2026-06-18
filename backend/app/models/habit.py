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
    subtasks_db = Column("subtasks", Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def subtasks(self) -> list:
        try:
            import json
            return json.loads(self.subtasks_db or "[]")
        except:
            return []

    @subtasks.setter
    def subtasks(self, val: list):
        import json
        self.subtasks_db = json.dumps(val or [])

    user = relationship("User", back_populates="habits")
    logs = relationship("DailyHabitLog", back_populates="habit", cascade="all, delete-orphan")


class DailyHabitLog(Base):
    __tablename__ = "daily_habit_logs"

    id = Column(Integer, primary_key=True, index=True)
    habit_id = Column(Integer, ForeignKey("daily_habits.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=True, nullable=False)
    completed_subtasks_db = Column("completed_subtasks", Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def completed_subtasks(self) -> list:
        try:
            import json
            return json.loads(self.completed_subtasks_db or "[]")
        except:
            return []

    @completed_subtasks.setter
    def completed_subtasks(self, val: list):
        import json
        self.completed_subtasks_db = json.dumps(val or [])

    habit = relationship("DailyHabit", back_populates="logs")

    __table_args__ = (
        UniqueConstraint("habit_id", "date", name="uq_habit_date"),
    )
