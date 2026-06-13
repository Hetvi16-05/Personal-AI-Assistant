from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.services.memory_service import MemoryService
from app.models import Task, WeeklyReport
from app.models.task import TaskStatus


SYSTEM_HINT = """You are a personal AI performance coach.
Generate a structured, honest, and motivating weekly review.
Include specific observations tied to the user's actual data."""


class WeeklyReviewService:

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def generate_review(self) -> dict:
        now = datetime.utcnow()
        week_start = now - timedelta(days=7)

        # Tasks completed this week
        completed = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status == TaskStatus.completed,
            Task.completed_at >= week_start
        ).all()

        # Total tasks created (active + completed)
        total = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.created_at >= week_start
        ).count()

        completion_pct = round(len(completed) / total * 100, 1) if total > 0 else 0.0

        # Most active goal
        goal_counts = Counter(t.goal_id for t in completed if t.goal_id)
        most_active_goal = ""
        if goal_counts:
            top_goal_id = goal_counts.most_common(1)[0][0]
            from app.models import Goal
            goal = self.db.query(Goal).filter(Goal.id == top_goal_id).first()
            if goal:
                most_active_goal = goal.title

        context = MemoryService(self.db, self.user_id).build_context()

        completed_titles = "\n".join(f"- {t.title}" for t in completed) or "None"

        prompt = f"""
{context}

## This Week's Stats
Tasks completed: {len(completed)}
Total tasks: {total}
Completion rate: {completion_pct}%
Most active goal: {most_active_goal or 'N/A'}

Completed tasks:
{completed_titles}

Generate a weekly review with:
1. Summary of what was accomplished
2. Honest assessment of completion rate
3. Highlight of the most impactful work
4. 3 specific recommendations for next week
5. One motivating closing statement

Keep it under 250 words. Be honest, specific, and forward-looking.
"""

        ai_summary = ask_llm(prompt, SYSTEM_HINT)

        # Store report
        report = WeeklyReport(
            user_id=self.user_id,
            week_start=week_start,
            week_end=now,
            tasks_completed=len(completed),
            completion_percentage=completion_pct,
            most_active_goal=most_active_goal,
            ai_summary=ai_summary
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return {
            "report_id": report.id,
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": now.strftime("%Y-%m-%d"),
            "tasks_completed": len(completed),
            "total_tasks": total,
            "completion_percentage": completion_pct,
            "most_active_goal": most_active_goal,
            "ai_summary": ai_summary
        }
