# app/api/endpoints/projects.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import ProjectCreate, ProjectOut, ProjectOut as ProjectWithTasks  # ProjectWithTasks not separate here
from app.models.project import Project
from app.core.auth_helpers import get_current_user_or_401

router = APIRouter()

@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    proj = Project(name=payload.name, description=payload.description, owner_id=current_user.id)
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return proj

@router.get("/", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    return projects

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    proj = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    proj = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    proj.name = payload.name
    proj.description = payload.description
    db.commit()
    db.refresh(proj)
    return proj

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user_or_401)):
    proj = db.query(Project).filter(Project.id == project_id, Project.owner_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(proj)
    db.commit()
    return None
