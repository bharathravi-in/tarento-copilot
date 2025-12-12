"""
Permission Model
Represents granular permissions in the system
"""

from sqlalchemy import Column, String, Text, ForeignKey, JSON, Index, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
from .role import role_permissions


class Permission(BaseModel):
    """Permission entity for fine-grained access control"""
    __tablename__ = "permissions"
    __table_args__ = (
        Index('ix_permissions_organization_id', 'organization_id'),
        Index('ix_permissions_name', 'name'),
        {"comment": "Granular permissions for authorization"}
    )
    
    # Basic info
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Permission category
    resource = Column(
        String(100),
        nullable=False,
        comment="Resource this permission applies to (users, projects, agents, etc.)"
    )
    action = Column(
        String(100),
        nullable=False,
        comment="Action on resource (create, read, update, delete)"
    )
    
    # Organization scope
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=True,
        comment="NULL means global/system permission"
    )
    
    # Metadata
    is_system_permission = Column(
        Boolean,
        default=False,
        comment="Cannot be deleted if True"
    )
    perm_metadata = Column(JSON, default=dict, nullable=False)
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="permissions",
        foreign_keys=[organization_id]
    )
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
