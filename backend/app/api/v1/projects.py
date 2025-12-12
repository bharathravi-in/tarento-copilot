"""
Project Management API Endpoints
Provides CRUD operations for projects
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Project, User
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schemas.common import ListResponse
from app.utils.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=ListResponse[ProjectResponse])
async def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    organization_id: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List projects in organization
    
    Users see only projects in their organization
    Can filter by organization and search
    """
    query = db.query(Project)
    
    # Filter by organization
    org_id = organization_id or current_user.organization_id
    query = query.filter(Project.organization_id == org_id)
    
    # Search
    if search:
        query = query.filter(
            (Project.name.ilike(f"%{search}%")) |
            (Project.description.ilike(f"%{search}%"))
        )
    
    total = query.count()
    projects = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=projects,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get project details"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new project
    
    Any authenticated user can create projects in their organization
    """
    # Check if project name already exists in org
    existing = db.query(Project).filter(
        (Project.name == project_data.name) &
        (Project.organization_id == current_user.organization_id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Project with this name already exists"
        )
    
    new_project = Project(
        id=str(uuid.uuid4()),
        name=project_data.name,
        description=project_data.description,
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a project
    
    Only the project creator or org admins can update
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only creators can update projects")
    
    # Update fields
    if project_data.name:
        project.name = project_data.name
    if project_data.description is not None:
        project.description = project_data.description
    if project_data.is_active is not None:
        project.is_active = project_data.is_active
    
    project.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a project (soft delete)
    
    Only the creator or org admins can delete
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only creators can delete projects")
    
    project.is_active = False
    db.commit()


@router.post("/{project_id}/members/{user_id}", status_code=200)
async def add_project_member(
    project_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a user to a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only creators can add members")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    if user in project.members:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    project.members.append(user)
    db.commit()
    
    return {"message": f"User {user.username} added to project"}


@router.delete("/{project_id}/members/{user_id}", status_code=204)
async def remove_project_member(
    project_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a user from a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check authorization
    if project.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if project.created_by != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only creators can remove members")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user not in project.members:
        raise HTTPException(status_code=400, detail="User is not a member")
    
    project.members.remove(user)
    db.commit()
