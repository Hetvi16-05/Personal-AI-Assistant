from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MemoryCreate(BaseModel):
    content: str
    tags: Optional[str] = ""
    source: Optional[str] = "chat"


class MemoryOut(BaseModel):
    id: int
    user_id: int
    content: str
    tags: str
    source: str
    created_at: datetime

    class Config:
        from_attributes = True
