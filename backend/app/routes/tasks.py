from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import Task
from app.models.task import TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from app.config import settings
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(user_id=settings.DEFAULT_USER_ID, **payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("", response_model=List[TaskOut])
def list_tasks(
    status: Optional[TaskStatus] = Query(None),
    goal_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Task).filter(Task.user_id == settings.DEFAULT_USER_ID)
    if status:
        q = q.filter(Task.status == status)
    if goal_id:
        q = q.filter(Task.goal_id == goal_id)
    return q.order_by(Task.created_at.desc()).all()


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == settings.DEFAULT_USER_ID).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(task, field, value)
    if payload.status == TaskStatus.completed and not task.completed_at:
        task.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == settings.DEFAULT_USER_ID).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task)
    db.commit()
