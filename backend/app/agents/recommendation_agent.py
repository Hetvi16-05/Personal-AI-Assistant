from sqlalchemy.orm import Session
from app.agents.memory_agent import MemoryAgent
from app.services.recommendation_service import RecommendationService


class RecommendationAgent:
    """
    Orchestrates Next Best Action with vector-enriched context.
    Route → RecommendationAgent → MemoryAgent + RecommendationService → Gemini
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def next_action(self) -> dict:
        service = RecommendationService(self.db, self.user_id)
        return service.next_action()

    def get_ranked_tasks(self):
        service = RecommendationService(self.db, self.user_id)
        return service.get_ranked_tasks()
