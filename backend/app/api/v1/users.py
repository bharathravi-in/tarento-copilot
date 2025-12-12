"""
User Management API Endpoints
Provides CRUD operations for user management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, Organization
from app.schemas.auth import UserResponse, UserCreate, UserBase
from app.schemas.common import PaginationParams, ListResponse
from app.utils.security import get_current_user
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=ListResponse[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    organization_id: Optional[str] = None,
    search: Optional[str] = None
):
    """
    List all users in current organization
    
    Supports:
    - Pagination (skip, limit)
    - Filtering by organization
    - Search by username/email
    """
    query = db.query(User)
    
    # Filter by organization
    org_id = organization_id or current_user.organization_id
    query = query.filter(User.organization_id == org_id)
    
    # Search filter
    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    
    # Count total
    total = query.count()
    
    # Pagination
    users = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check authorization - only same org members can view
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user in the organization
    
    Only admins can create users
    """
    # Check if user is admin
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create users"
        )
    
    # Check if user already exists
    existing = db.query(User).filter(
        (User.email == user_data.email) | 
        (User.username == user_data.username)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )
    
    # Create new user
    auth_service = AuthService()
    try:
        new_user = auth_service.register_user(
            db=db,
            email=user_data.email,
            username=user_data.username,
            password=user_data.password,
            organization_id=current_user.organization_id,
            full_name=user_data.full_name
        )
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update user information
    
    Users can update their own profile
    Admins can update any user in their organization
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check authorization
    if user.id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check organization
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.avatar_url is not None:
        user.avatar_url = user_data.avatar_url
    if user_data.bio is not None:
        user.bio = user_data.bio
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Soft delete a user (mark as inactive)
    
    Only admins can delete users
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check organization
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Soft delete
    user.is_active = False
    db.commit()


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reactivate an inactive user"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can activate users"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user's role
    
    Only admins can change user roles
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only administrators can change user roles"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Verify role exists in same organization
    from app.models import Role
    role = db.query(Role).filter(
        (Role.id == role_id) &
        (Role.organization_id == current_user.organization_id)
    ).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    user.role_id = role_id
    db.commit()
    db.refresh(user)
    
    return user
