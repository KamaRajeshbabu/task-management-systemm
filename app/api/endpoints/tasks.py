# app/api/endpoints/tasks.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas import TaskCreate, TaskOut, TaskUpdate
from app.models.task import Task
from app.models.project import Project
from app.core.auth_helpers import get_current_user_or_401

router = APIRouter()

@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    proj = db.query(Project).filter(Project.id == payload.project_id, Project.owner_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found for the current user")
    task = Task(
        title=payload.title,
        description=payload.description,
        project_id=payload.project_id,
        assignee_id=payload.assignee_id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.get("/", response_model=List[TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_or_401)
):
    q = db.query(Task).join(Project).filter(Project.owner_id == current_user.id)
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == priority)
    if project_id:
        q = q.filter(Task.project_id == project_id)
    items = q.offset(skip).limit(limit).all()
    return items

@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    task = db.query(Task).join(Project).filter(Task.id == task_id, Project.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None
