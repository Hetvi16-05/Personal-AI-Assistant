from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.config import settings
from datetime import datetime

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.id == settings.DEFAULT_USER_ID).first()
    if existing:
        raise HTTPException(status_code=409, detail="User profile already exists. Use PATCH /users/me to update.")
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
def get_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == settings.DEFAULT_USER_ID).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found. POST /users first.")
    return user


@router.patch("/me", response_model=UserOut)
def update_user(payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == settings.DEFAULT_USER_ID).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
