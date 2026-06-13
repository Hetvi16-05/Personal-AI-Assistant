import json
from sqlalchemy.orm import Session
from app.ai.llm import ask_llm
from app.services.memory_service import MemoryService
from app.models import Goal, Roadmap, Milestone


SYSTEM_HINT = """You are an expert AI career and study planner.
Generate structured, actionable roadmaps based on the user's profile and goals.
Always return valid JSON in the exact format requested."""


class GoalPlannerService:

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def generate_roadmap(self, goal_id: int) -> dict:
        goal: Goal | None = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == self.user_id
        ).first()

        if not goal:
            raise ValueError(f"Goal {goal_id} not found")

        context = MemoryService(self.db, self.user_id).build_context()

        deadline_str = goal.deadline.strftime("%Y-%m-%d") if goal.deadline else "6 months from now"

        prompt = f"""
{context}

## Task
The user wants to achieve: "{goal.title}"
Deadline: {deadline_str}

Generate a detailed roadmap as JSON with this exact structure:
{{
  "summary": "2-3 sentence overview of the plan",
  "milestones": [
    {{
      "period": "Month 1",
      "title": "Foundation",
      "description": "What to focus on and why",
      "order": 1
    }},
    ...
  ]
}}

Return ONLY valid JSON. No markdown code fences. No extra text.
"""

        raw = ask_llm(prompt, SYSTEM_HINT)

        # Strip markdown fences if model adds them
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```")

        data = json.loads(raw)

        # Persist to DB
        roadmap = Roadmap(goal_id=goal_id, summary=data.get("summary", ""))
        self.db.add(roadmap)
        self.db.flush()

        for m in data.get("milestones", []):
            milestone = Milestone(
                roadmap_id=roadmap.id,
                period=m.get("period", ""),
                title=m.get("title", ""),
                description=m.get("description", ""),
                order=m.get("order", 0)
            )
            self.db.add(milestone)

        self.db.commit()
        self.db.refresh(roadmap)

        return {
            "roadmap_id": roadmap.id,
            "goal": goal.title,
            "summary": roadmap.summary,
            "milestones": [
                {
                    "period": ms.period,
                    "title": ms.title,
                    "description": ms.description,
                    "order": ms.order
                }
                for ms in sorted(roadmap.milestones, key=lambda x: x.order)
            ]
        }
