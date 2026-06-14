from sqlalchemy.orm import Session
from app.services.memory_service import MemoryService
from app.services.vector_memory_service import retrieve_relevant


class MemoryAgent:
    """
    Builds the full enriched context for LLM prompts.
    Combines:
      1. Structured context (goals, tasks, projects, profile)
      2. Top-5 semantically relevant memories via pgvector
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        self._mem_service = MemoryService(db, user_id)

    def build_full_context(self, query: str = "") -> str:
        # 1. Structured context
        structured = self._mem_service.build_context()

        # 2. Vector-retrieved relevant memories
        relevant = []
        if query:
            relevant = retrieve_relevant(self.db, self.user_id, query, top_k=5)

        if relevant:
            relevant_block = "\n## Relevant Long-Term Memories\n" + \
                             "\n".join(f"- {m}" for m in relevant)
        else:
            relevant_block = ""

        return structured + relevant_block
