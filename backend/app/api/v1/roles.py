"""
Role and Permission Management API Endpoints
Provides CRUD operations for roles and permissions
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Role, Permission, User
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate, PermissionResponse
from app.schemas.common import ListResponse
from app.utils.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=ListResponse[RoleResponse])
async def list_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    """
    List roles in organization
    
    Users see only roles in their organization
    """
    query = db.query(Role).filter(Role.organization_id == current_user.organization_id)
    
    # Search
    if search:
        query = query.filter(Role.name.ilike(f"%{search}%"))
    
    total = query.count()
    roles = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=roles,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get role details"""
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check authorization
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return role


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role(
    role_data: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new role
    
    Only admins can create roles
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create roles"
        )
    
    # Check if role name already exists in org
    existing = db.query(Role).filter(
        (Role.name == role_data.name) &
        (Role.organization_id == current_user.organization_id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Role with this name already exists"
        )
    
    new_role = Role(
        id=str(uuid.uuid4()),
        name=role_data.name,
        description=role_data.description,
        organization_id=current_user.organization_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    return new_role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    role_data: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a role
    
    Only admins can update roles
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Check authorization
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can update roles")
    
    # Update fields
    if role_data.name:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    
    role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(role)
    
    return role


@router.delete("/{role_id}", status_code=204)
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a role
    
    Only admins can delete roles
    Cannot delete if users have this role
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can delete roles")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if role is in use
    users_with_role = db.query(User).filter(User.role_id == role_id).count()
    if users_with_role > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete role: {users_with_role} users have this role"
        )
    
    db.delete(role)
    db.commit()


@router.post("/{role_id}/permissions/{permission_id}", status_code=200)
async def add_permission_to_role(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a permission to a role"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can manage permissions")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Check if already assigned
    if permission in role.permissions:
        raise HTTPException(status_code=400, detail="Permission already assigned")
    
    role.permissions.append(permission)
    db.commit()
    
    return {"message": f"Permission {permission.name} added to role {role.name}"}


@router.delete("/{role_id}/permissions/{permission_id}", status_code=204)
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a permission from a role"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Only admins can manage permissions")
    
    role = db.query(Role).filter(Role.id == role_id).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    if permission not in role.permissions:
        raise HTTPException(status_code=400, detail="Permission not assigned")
    
    role.permissions.remove(permission)
    db.commit()


# Permissions endpoints
@router.get("/permissions/", response_model=ListResponse[PermissionResponse])
async def list_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    List all system permissions
    
    Permissions are system-wide, not organization-specific
    """
    query = db.query(Permission)
    total = query.count()
    permissions = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=permissions,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permission details"""
    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    return permission
