from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.services.memory_service import MemoryService
from app.services.recommendation_service import RecommendationService


SYSTEM_HINT = """You are a personal AI mentor and daily coach.
Generate a warm, motivating, and highly personalized daily briefing.
Keep it concise, actionable, and specific to the user's actual goals and tasks."""


class DailyCoachService:

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_briefing(self) -> dict:
        mem_service = MemoryService(self.db, self.user_id)
        rec_service = RecommendationService(self.db, self.user_id)

        context = mem_service.build_context()
        top_tasks = rec_service.get_ranked_tasks()[:3]

        task_list = "\n".join(
            f"{i+1}. {t.title} (score: {s:.1f})"
            for i, (t, s) in enumerate(top_tasks)
        ) if top_tasks else "No tasks yet."

        prompt = f"""
{context}

## Today's Top Tasks (ranked by AI engine):
{task_list}

Generate a personalized daily briefing with:
1. A warm, motivating greeting using the user's name
2. Today's Focus (the top 3 tasks with brief reasons)
3. One motivational insight tied to their main goal
4. A closing encouragement

Keep the entire response under 200 words. Be personal, specific, and energetic.
"""

        briefing_text = ask_llm(prompt, SYSTEM_HINT)

        return {
            "briefing": briefing_text,
            "top_tasks": [
                {"task_id": t.id, "title": t.title, "score": round(s, 2)}
                for t, s in top_tasks
            ]
        }
