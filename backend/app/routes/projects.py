from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.config import settings
from typing import List

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(user_id=settings.DEFAULT_USER_ID, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).filter(Project.user_id == settings.DEFAULT_USER_ID).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == settings.DEFAULT_USER_ID
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(
        Project.id == project_id, Project.user_id == settings.DEFAULT_USER_ID
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project
