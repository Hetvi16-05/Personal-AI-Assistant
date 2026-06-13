from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base


class UserMemory(Base):
    __tablename__ = "user_memory"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)       # the memory text
    tags = Column(String(300), default="")       # comma-separated tags
    source = Column(String(100), default="chat") # chat | manual | system
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="memories")
