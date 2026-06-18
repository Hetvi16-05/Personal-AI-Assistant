from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import DailyHabit, DailyHabitLog
from app.models.user import User
from app.auth.dependencies import get_current_user
from app.schemas.habit import (
    HabitCreate, HabitUpdate, HabitOut,
    HabitLogCreate, HabitLogOut, HabitAnalytics, HabitsSummaryAnalytics
)
from datetime import date, datetime, timedelta
from typing import List, Optional

router = APIRouter(prefix="/habits", tags=["Habits"])


def compute_analytics(habit: DailyHabit, db: Session) -> HabitAnalytics:
    logs = db.query(DailyHabitLog).filter(DailyHabitLog.habit_id == habit.id).all()
    completed_dates = {log.date for log in logs if log.completed}
    
    # Streaks calculation
    longest_streak = 0
    current_run = 0
    sorted_dates = sorted(list(completed_dates))
    if sorted_dates:
        longest_streak = 1
        current_run = 1
        for i in range(1, len(sorted_dates)):
            if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
                current_run += 1
            else:
                longest_streak = max(longest_streak, current_run)
                current_run = 1
        longest_streak = max(longest_streak, current_run)

    current_streak = 0
    check_date = date.today()
    if check_date in completed_dates:
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    else:
        # Check starting from yesterday if today isn't completed yet
        check_date = date.today() - timedelta(days=1)
        while check_date in completed_dates:
            current_streak += 1
            check_date -= timedelta(days=1)

    completed_days_count = len(completed_dates)
    completion_rate = round((completed_days_count / habit.duration_days) * 100, 2)

    # Explicitly serialize logs so Pydantic doesn't need to resolve @property from ORM
    from app.schemas.habit import HabitLogOut as _HabitLogOut
    logs_out = [
        _HabitLogOut(
            id=log.id,
            habit_id=log.habit_id,
            date=log.date,
            completed=log.completed,
            completed_subtasks=log.completed_subtasks,  # calls @property explicitly
            created_at=log.created_at
        )
        for log in logs
    ]

    # Explicitly call habit.subtasks @property to get the Python list
    subtasks_list = list(habit.subtasks)

    return HabitAnalytics(
        habit_id=habit.id,
        title=habit.title,
        duration_days=habit.duration_days,
        start_date=habit.start_date,
        status=habit.status,
        completed_days_count=completed_days_count,
        completion_rate=completion_rate,
        current_streak=current_streak,
        longest_streak=longest_streak,
        history=sorted_dates,
        subtasks=subtasks_list,
        logs=logs_out
    )


@router.post("", response_model=HabitOut, status_code=201)
def create_habit(
    payload: HabitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    start_dt = payload.start_date or date.today()
    habit = DailyHabit(
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        duration_days=payload.duration_days,
        start_date=start_dt,
        subtasks=payload.subtasks or []
    )
    db.add(habit)
    db.commit()
    db.refresh(habit)
    return habit


@router.get("", response_model=List[HabitOut])
def list_habits(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DailyHabit).filter(DailyHabit.user_id == current_user.id)
    if status:
        query = query.filter(DailyHabit.status == status)
    return query.all()


@router.get("/analytics/summary", response_model=HabitsSummaryAnalytics)
def habits_summary_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habits = db.query(DailyHabit).filter(DailyHabit.user_id == current_user.id).all()
    
    total = len(habits)
    active = len([h for h in habits if h.status == "active"])
    completed = len([h for h in habits if h.status == "completed"])

    analytics_list = []
    total_rate = 0.0
    for h in habits:
        analytics = compute_analytics(h, db)
        analytics_list.append(analytics)
        total_rate += analytics.completion_rate

    avg_rate = round(total_rate / total, 2) if total > 0 else 0.0

    return HabitsSummaryAnalytics(
        total_habits=total,
        active_habits=active,
        completed_habits=completed,
        avg_completion_rate=avg_rate,
        habits=analytics_list
    )


@router.get("/{habit_id}", response_model=HabitOut)
def get_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(DailyHabit).filter(DailyHabit.id == habit_id, DailyHabit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Daily Habit not found.")
    return habit


@router.patch("/{habit_id}", response_model=HabitOut)
def update_habit(
    habit_id: int,
    payload: HabitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(DailyHabit).filter(DailyHabit.id == habit_id, DailyHabit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Daily Habit not found.")
    
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(habit, field, value)
    
    db.commit()
    db.refresh(habit)
    return habit


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(DailyHabit).filter(DailyHabit.id == habit_id, DailyHabit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Daily Habit not found.")
    db.delete(habit)
    db.commit()
    return


@router.post("/{habit_id}/log", response_model=HabitLogOut)
def log_habit_completion(
    habit_id: int,
    payload: HabitLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    habit = db.query(DailyHabit).filter(DailyHabit.id == habit_id, DailyHabit.user_id == current_user.id).first()
    if not habit:
        raise HTTPException(status_code=404, detail="Daily Habit not found.")

    # Validate that the date is within the habit duration
    delta_days = (payload.date - habit.start_date).days
    if delta_days < 0 or delta_days >= habit.duration_days:
        raise HTTPException(
            status_code=400,
            detail=f"Logging date {payload.date} is outside the challenge period: "
                   f"{habit.start_date} to {habit.start_date + timedelta(days=habit.duration_days - 1)}"
        )

    # Check if a log entry already exists for this date
    existing_log = db.query(DailyHabitLog).filter(
        DailyHabitLog.habit_id == habit_id,
        DailyHabitLog.date == payload.date
    ).first()

    # Determine completion state
    is_completed = payload.completed
    if habit.subtasks:
        if payload.completed_subtasks is not None:
            is_completed = len(payload.completed_subtasks) >= len(habit.subtasks)
        else:
            is_completed = False

    # Determine whether we keep/save the log or delete it
    should_delete = False
    if not habit.subtasks:
        should_delete = not payload.completed
    else:
        # Only delete if completed_subtasks is explicitly None (not just empty list)
        should_delete = payload.completed_subtasks is None

    if should_delete:
        if existing_log:
            db.delete(existing_log)
            db.commit()
            return HabitLogOut(
                id=existing_log.id,
                habit_id=habit_id,
                date=payload.date,
                completed=False,
                completed_subtasks=[],
                created_at=existing_log.created_at
            )
        else:
            return HabitLogOut(
                id=0,
                habit_id=habit_id,
                date=payload.date,
                completed=False,
                completed_subtasks=[],
                created_at=datetime.utcnow()
            )
    else:
        if existing_log:
            existing_log.completed = is_completed
            if habit.subtasks and payload.completed_subtasks is not None:
                existing_log.completed_subtasks = payload.completed_subtasks
            db.commit()
            db.refresh(existing_log)
            return existing_log
        else:
            log = DailyHabitLog(
                habit_id=habit_id,
                date=payload.date,
                completed=is_completed,
                completed_subtasks=payload.completed_subtasks or []
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
