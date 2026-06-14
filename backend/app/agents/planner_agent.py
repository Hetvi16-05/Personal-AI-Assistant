from sqlalchemy.orm import Session
from app.agents.memory_agent import MemoryAgent
from app.services.goal_planner import GoalPlannerService


class PlannerAgent:
    """
    Orchestrates roadmap generation with full memory context.
    Route → PlannerAgent → MemoryAgent + GoalPlannerService → Gemini → DB
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def generate_roadmap(self, goal_id: int) -> dict:
        # MemoryAgent enriches context; GoalPlannerService uses it internally
        # via MemoryService — here we just call the service which handles it
        service = GoalPlannerService(self.db, self.user_id)
        return service.generate_roadmap(goal_id)
