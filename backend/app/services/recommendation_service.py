from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.agents.memory_agent import MemoryAgent
from app.models import Task
from app.models.task import TaskStatus


SYSTEM_HINT = """You are a personal AI productivity coach.
Identify the single most impactful action for the user right now.
Be specific, motivating, and data-driven."""


class RecommendationService:
    """
    Next Best Action Engine V2 — Dynamic scoring using:
    - Impact, urgency, goal alignment, effort (existing)
    - productivity_score: based on 7-day completion rate
    - focus_score: % of pending tasks in same goal
    - consistency_score: consecutive days with task completions
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    # ── Dynamic score components ──────────────────────────

    def _productivity_score(self) -> float:
        """7-day task completion rate (0–10)."""
        week_ago = datetime.utcnow() - timedelta(days=7)
        total = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.created_at >= week_ago
        ).count()
        completed = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status == TaskStatus.completed,
            Task.completed_at >= week_ago
        ).count()
        return round((completed / max(total, 1)) * 10, 2)

    def _focus_score(self, task: Task, all_pending: list) -> float:
        """How focused is the user on this task's goal? (0–10)"""
        if not task.goal_id:
            return 5.0
        same_goal = sum(1 for t in all_pending if t.goal_id == task.goal_id)
        return min(same_goal * 2.0, 10.0)

    def _consistency_score(self) -> float:
        """Consecutive days with at least one completed task (0–10)."""
        streak = 0
        for i in range(10):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0)
            day_end = day.replace(hour=23, minute=59, second=59)
            count = self.db.query(Task).filter(
                Task.user_id == self.user_id,
                Task.status == TaskStatus.completed,
                Task.completed_at >= day_start,
                Task.completed_at <= day_end
            ).count()
            if count > 0:
                streak += 1
            else:
                break
        return min(streak * 1.5, 10.0)

    def score_task(self, task: Task, all_pending: list,
                   productivity: float, consistency: float) -> float:
        """
        V2 scoring formula:
        score = impact*0.35 + urgency*0.25 + alignment*0.20
              + effort_match*0.10 + productivity*0.05 + consistency*0.05
        """
        effort_match = 10.0 - task.effort_score
        focus = self._focus_score(task, all_pending)

        return (
            task.impact_score * 0.35
            + task.urgency_score * 0.25
            + task.alignment_score * 0.20
            + effort_match * 0.10
            + focus * 0.05
            + consistency * 0.05
        )

    def get_ranked_tasks(self) -> list[tuple[Task, float]]:
        pending = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status.in_([TaskStatus.pending, TaskStatus.in_progress])
        ).all()

        if not pending:
            return []

        productivity = self._productivity_score()
        consistency = self._consistency_score()

        ranked = [
            (t, self.score_task(t, pending, productivity, consistency))
            for t in pending
        ]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def next_action(self) -> dict:
        ranked = self.get_ranked_tasks()

        if not ranked:
            return {
                "recommended_action": None,
                "reason": "No pending tasks. Add some tasks to get started!",
                "score": 0,
                "why_it_matters": None,
                "estimated_impact": None,
                "all_ranked": []
            }

        top_task, top_score = ranked[0]
        productivity = self._productivity_score()
        consistency = self._consistency_score()

        context = MemoryAgent(self.db, self.user_id).build_full_context(
            query=top_task.title
        )

        prompt = f"""
{context}

## Next Best Action Analysis (V2)

Top-ranked task (score: {top_score:.2f}/10):
Title: "{top_task.title}"
Description: {top_task.description or 'No description'}
Impact: {top_task.impact_score}/10 | Urgency: {top_task.urgency_score}/10
Alignment: {top_task.alignment_score}/10 | Effort: {top_task.effort_score}/10

User productivity score this week: {productivity}/10
User consistency streak score: {consistency}/10

Provide 3 things:
1. REASON (2 sentences): Why this is the most important task right now
2. WHY_IT_MATTERS (1 sentence): Long-term impact on user's main goal
3. ESTIMATED_IMPACT (very short): e.g. "High — completes Month 2 milestone"

Format as JSON:
{{"reason": "...", "why_it_matters": "...", "estimated_impact": "..."}}
Return ONLY valid JSON.
"""

        import json
        try:
            raw = ask_llm(prompt, SYSTEM_HINT).strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip().rstrip("```")
            ai_data = json.loads(raw)
        except Exception:
            ai_data = {
                "reason": "This task has the highest combined impact and urgency score.",
                "why_it_matters": "Completing it moves you closer to your primary goal.",
                "estimated_impact": "High"
            }

        return {
            "recommended_action": top_task.title,
            "task_id": top_task.id,
            "score": round(top_score, 2),
            "productivity_score": productivity,
            "consistency_score": consistency,
            "reason": ai_data.get("reason"),
            "why_it_matters": ai_data.get("why_it_matters"),
            "estimated_impact": ai_data.get("estimated_impact"),
            "all_ranked": [
                {"task_id": t.id, "title": t.title, "score": round(s, 2)}
                for t, s in ranked[:5]
            ]
        }
