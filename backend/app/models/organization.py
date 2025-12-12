"""
Organization Model
Represents a tenant in the multi-tenant SaaS application
"""

from sqlalchemy import Column, String, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from .base import BaseModel


class Organization(BaseModel):
    """Organization entity for multi-tenancy"""
    __tablename__ = "organizations"
    __table_args__ = {"comment": "Multi-tenant organizations"}
    
    # Basic info
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    
    # Subscription and status
    subscription_plan = Column(
        String(50),
        default="starter",
        nullable=False,
        comment="starter, professional, enterprise"
    )
    is_active = Column(Boolean, default=True, index=True)
    
    # Configuration
    settings = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Organization-level configuration (theme, locale, etc.)"
    )
    org_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional metadata"
    )
    
    # Relationships
    users = relationship(
        "User",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="User.organization_id"
    )
    projects = relationship(
        "Project",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="Project.organization_id"
    )
    roles = relationship(
        "Role",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="Role.organization_id"
    )
    permissions = relationship(
        "Permission",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="Permission.organization_id"
    )
    agent_configs = relationship(
        "AgentConfig",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="AgentConfig.organization_id"
    )
    documents = relationship(
        "Document",
        back_populates="organization",
        cascade="all, delete-orphan",
        foreign_keys="Document.organization_id"
    )
