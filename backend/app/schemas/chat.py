from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.chat import MessageRole


class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"


class SessionOut(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: int
    session_id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    user_message: MessageOut
    assistant_message: MessageOut
