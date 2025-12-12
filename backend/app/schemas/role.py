"""
Pydantic schemas for roles and permissions
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Permission schemas
class PermissionBase(BaseModel):
    """Base permission schema"""
    name: str = Field(..., min_length=1, max_length=100)
    resource: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Permission response schema"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    """Base role schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Role creation schema"""
    organization_id: str
    permission_ids: Optional[List[str]] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Role update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """Role response schema"""
    id: str
    organization_id: str
    is_system: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleDetailResponse(RoleResponse):
    """Role detail response with permissions"""
    permissions: List[PermissionResponse] = Field(default_factory=list)


# Bulk operations
class BulkPermissionAssign(BaseModel):
    """Bulk permission assignment to role"""
    permission_ids: List[str]


class BulkPermissionRevoke(BaseModel):
    """Bulk permission revocation from role"""
    permission_ids: List[str]
