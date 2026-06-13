from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: Optional[str] = None
    skills: Optional[str] = ""
    interests: Optional[str] = ""
    preferences: Optional[str] = ""


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    preferences: Optional[str] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: Optional[str]
    skills: str
    interests: str
    preferences: str
    created_at: datetime

    class Config:
        from_attributes = True
