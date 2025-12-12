"""
Pydantic schemas for organizations
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class OrganizationBase(BaseModel):
    """Base organization schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    subscription_plan: str = Field(default="starter")


class OrganizationCreate(OrganizationBase):
    """Organization creation schema"""
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OrganizationUpdate(BaseModel):
    """Organization update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    subscription_plan: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class OrganizationResponse(OrganizationBase):
    """Organization response schema"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrganizationDetailResponse(OrganizationResponse):
    """Organization detail response with additional info"""
    settings: Dict[str, Any]
    metadata: Dict[str, Any]
    user_count: Optional[int] = None
    project_count: Optional[int] = None
