from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.services.memory_service import MemoryService
from app.models import Task
from app.models.task import TaskStatus


SYSTEM_HINT = """You are a personal AI productivity coach.
Your job is to identify the single most impactful action for the user right now.
Be specific, motivating, and data-driven."""


class RecommendationService:
    """
    Next Best Action Engine.
    Scores all pending tasks and returns the top recommendation
    with an AI-generated reason.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def score_task(self, task: Task) -> float:
        """
        score = impact*0.4 + urgency*0.3 + alignment*0.2 + effort_match*0.1
        effort_match is inverted: low effort = high score (quick wins)
        """
        effort_match = 10.0 - task.effort_score  # prefer lower effort tasks
        return (
            task.impact_score * 0.4
            + task.urgency_score * 0.3
            + task.alignment_score * 0.2
            + effort_match * 0.1
        )

    def get_ranked_tasks(self) -> list[tuple[Task, float]]:
        tasks = self.db.query(Task).filter(
            Task.user_id == self.user_id,
            Task.status.in_([TaskStatus.pending, TaskStatus.in_progress])
        ).all()

        ranked = [(t, self.score_task(t)) for t in tasks]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def next_action(self) -> dict:
        ranked = self.get_ranked_tasks()

        if not ranked:
            return {
                "recommended_action": None,
                "reason": "No pending tasks found. Add some tasks first!",
                "score": 0,
                "all_ranked": []
            }

        top_task, top_score = ranked[0]
        context = MemoryService(self.db, self.user_id).build_context()

        prompt = f"""
{context}

## Next Best Action Analysis

The scoring engine ranked this task #1 (score: {top_score:.2f}/10):
Task: "{top_task.title}"
Description: {top_task.description or 'No description'}
Impact: {top_task.impact_score}/10
Urgency: {top_task.urgency_score}/10
Goal alignment: {top_task.alignment_score}/10

In 2-3 sentences, explain WHY this is the most important task to work on right now.
Be specific to the user's goals and context. Be motivating but concise.
"""

        reason = ask_llm(prompt, SYSTEM_HINT)

        return {
            "recommended_action": top_task.title,
            "task_id": top_task.id,
            "score": round(top_score, 2),
            "reason": reason,
            "all_ranked": [
                {
                    "task_id": t.id,
                    "title": t.title,
                    "score": round(s, 2)
                }
                for t, s in ranked[:5]
            ]
        }
