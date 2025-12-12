"""
Organization Management API Endpoints
Provides CRUD operations for organizations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Organization, User
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.schemas.common import ListResponse
from app.utils.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get("/", response_model=ListResponse[OrganizationResponse])
async def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None
):
    """
    List organizations
    
    Users see only their own organization
    Superusers can see all organizations
    """
    query = db.query(Organization)
    
    # Regular users only see their org
    if not current_user.is_superuser:
        query = query.filter(Organization.id == current_user.organization_id)
    
    # Search
    if search:
        query = query.filter(
            (Organization.name.ilike(f"%{search}%")) |
            (Organization.domain.ilike(f"%{search}%"))
        )
    
    total = query.count()
    orgs = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=orgs,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get organization details"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check authorization
    if org.id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return org


@router.post("/", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    org_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new organization
    
    Only superusers can create organizations
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only superusers can create organizations"
        )
    
    # Check if domain already exists
    existing = db.query(Organization).filter(
        Organization.domain == org_data.domain
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Domain already registered"
        )
    
    new_org = Organization(
        id=str(uuid.uuid4()),
        name=org_data.name,
        domain=org_data.domain,
        description=org_data.description,
        logo_url=org_data.logo_url,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    
    return new_org


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: str,
    org_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update organization
    
    Only admins of that organization can update it
    """
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check authorization
    if org.id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update organization"
        )
    
    # Update fields
    if org_data.name:
        org.name = org_data.name
    if org_data.description is not None:
        org.description = org_data.description
    if org_data.logo_url is not None:
        org.logo_url = org_data.logo_url
    
    org.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(org)
    
    return org


@router.get("/{org_id}/members", response_model=ListResponse)
async def get_organization_members(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """Get all members of an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check authorization
    if org.id != current_user.organization_id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get members
    from app.schemas.auth import UserResponse
    query = db.query(User).filter(User.organization_id == org_id)
    total = query.count()
    members = query.offset(skip).limit(limit).all()
    
    return ListResponse(
        data=members,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/{org_id}/members/{user_id}", status_code=200)
async def add_member_to_organization(
    org_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add an existing user to an organization"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check authorization
    if org.id != current_user.organization_id or not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    if user.organization_id == org_id:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    user.organization_id = org_id
    db.commit()
    
    return {"message": f"User {user.username} added to organization"}
