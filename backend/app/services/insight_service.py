from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.agents.memory_agent import MemoryAgent
from app.models import Task, Goal, AIInsight
from app.models.task import TaskStatus
from app.models.insight import InsightType

SYSTEM_HINT = """You are a data-driven AI analyst for a personal productivity assistant.
Generate specific, data-backed insights. Be concise (1-2 sentences each).
Reference actual numbers and patterns from the user's data."""


class InsightService:

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def _tasks_last_n_days(self, days: int, status=None):
        since = datetime.utcnow() - timedelta(days=days)
        q = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.created_at >= since
        )
        if status:
            q = q.filter(Task.status == status)
        return q.all()

    def generate_insights(self) -> list[dict]:
        context = MemoryAgent(self.db, self.user_id).build_full_context()

        # ── Data gathering ──────────────────────────────
        completed_7d = self._tasks_last_n_days(7, TaskStatus.completed)
        completed_30d = self._tasks_last_n_days(30, TaskStatus.completed)
        all_pending = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status.in_([TaskStatus.pending, TaskStatus.in_progress])
        ).all()
        active_goals = self.db.query(Goal).filter(
            Goal.user_id == self.user_id,
            Goal.status == "active"
        ).all()

        completion_rate = round(len(completed_7d) / max(len(all_pending) + len(completed_7d), 1) * 100, 1)

        # Goal alignment (which goal has most completed tasks)
        goal_task_counts = Counter(t.goal_id for t in completed_30d if t.goal_id)
        top_goal_name = "N/A"
        if goal_task_counts:
            top_id = goal_task_counts.most_common(1)[0][0]
            g = next((g for g in active_goals if g.id == top_id), None)
            if g:
                top_goal_name = g.title

        prompt = f"""
{context}

## Analytics Data
- Tasks completed this week: {len(completed_7d)}
- Tasks completed this month: {len(completed_30d)}
- Current completion rate: {completion_rate}%
- Active goals: {len(active_goals)}
- Most active goal: {top_goal_name}
- Pending tasks: {len(all_pending)}

Generate exactly 4 insights, one for each type.
Return as JSON array with this exact format:
[
  {{"type": "productivity", "content": "..."}},
  {{"type": "learning", "content": "..."}},
  {{"type": "goal_progress", "content": "..."}},
  {{"type": "recommendation", "content": "..."}}
]
Return ONLY valid JSON. No markdown. No extra text.
Use specific numbers from the data above.
"""

        import json
        raw = ask_llm(prompt, SYSTEM_HINT).strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```")

        data = json.loads(raw)

        # Store in DB
        saved = []
        for item in data:
            insight = AIInsight(
                user_id=self.user_id,
                insight_type=item["type"],
                content=item["content"]
            )
            self.db.add(insight)
            saved.append(item)

        self.db.commit()
        return saved

    def get_history(self, limit: int = 20) -> list[AIInsight]:
        return self.db.query(AIInsight).filter(
            AIInsight.user_id == self.user_id
        ).order_by(AIInsight.generated_at.desc()).limit(limit).all()
