"""
Project Model
Represents projects within an organization
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel
from .user import user_projects


class Project(BaseModel):
    """Project entity representing a workspace or initiative"""
    __tablename__ = "projects"
    __table_args__ = (
        Index('ix_projects_organization_id', 'organization_id'),
        Index('ix_projects_created_by', 'created_by'),
        Index('ix_projects_is_active', 'is_active'),
        {"comment": "Projects/workspaces within organizations"}
    )
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    icon_url = Column(String(500), nullable=True)
    
    # Organization and creator
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False
    )
    created_by = Column(
        String(36),
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=False
    )
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_archived = Column(Boolean, default=False)
    
    # Configuration
    settings = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Project-specific configuration"
    )
    proj_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional metadata"
    )
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="projects",
        foreign_keys=[organization_id]
    )
    creator = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by]
    )
    members = relationship(
        "User",
        secondary=user_projects,
        back_populates="projects"
    )
    conversations = relationship(
        "Conversation",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.project_id"
    )
    agent_configs = relationship(
        "AgentConfig",
        back_populates="project",
        cascade="all, delete-orphan",
        foreign_keys="AgentConfig.project_id"
    )
