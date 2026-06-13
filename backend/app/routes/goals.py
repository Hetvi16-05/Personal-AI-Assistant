from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import Goal
from app.schemas.goal import GoalCreate, GoalUpdate, GoalOut
from app.config import settings
from datetime import datetime
from typing import List

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    goal = Goal(user_id=settings.DEFAULT_USER_ID, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("", response_model=List[GoalOut])
def list_goals(db: Session = Depends(get_db)):
    return db.query(Goal).filter(Goal.user_id == settings.DEFAULT_USER_ID).all()


@router.get("/{goal_id}", response_model=GoalOut)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == settings.DEFAULT_USER_ID).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return goal


@router.patch("/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: int, payload: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == settings.DEFAULT_USER_ID).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(goal, field, value)
    goal.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == settings.DEFAULT_USER_ID).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found.")
    db.delete(goal)
    db.commit()
