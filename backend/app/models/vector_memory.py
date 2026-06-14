from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

try:
    from pgvector.sqlalchemy import Vector
    VECTOR_AVAILABLE = True
except ImportError:
    VECTOR_AVAILABLE = False


class MemoryEmbedding(Base):
    __tablename__ = "memory_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    memory_text = Column(Text, nullable=False)
    # 768 dims for Gemini text-embedding-004
    embedding = Column(Vector(768) if VECTOR_AVAILABLE else Text, nullable=True)
    tags = Column(String(300), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memory_embeddings")
