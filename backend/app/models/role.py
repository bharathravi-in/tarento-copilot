"""
Role Model
Represents user roles in the system
"""

from sqlalchemy import Column, String, Text, ForeignKey, JSON, Table, Index, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel

# Association table for role-permission mapping
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', String(36), ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', String(36), ForeignKey('permissions.id', ondelete='CASCADE')),
    Index('ix_role_permissions_role_id', 'role_id'),
    Index('ix_role_permissions_permission_id', 'permission_id')
)


class Role(BaseModel):
    """Role entity for RBAC"""
    __tablename__ = "roles"
    __table_args__ = (
        Index('ix_roles_organization_id', 'organization_id'),
        Index('ix_roles_name', 'name'),
        {"comment": "User roles for RBAC"}
    )
    
    # Basic info
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Organization scope
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=True,
        comment="NULL means global/system role"
    )
    
    # Metadata
    is_system_role = Column(
        Boolean,
        default=False,
        comment="Cannot be deleted if True"
    )
    role_metadata = Column(JSON, default=dict, nullable=False)
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="roles",
        foreign_keys=[organization_id]
    )
    users = relationship(
        "User",
        back_populates="role",
        foreign_keys="User.role_id"
    )
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )
