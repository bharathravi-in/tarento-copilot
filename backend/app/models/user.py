"""
User Model
Represents users in the multi-tenant system
"""

from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Index, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

# Association table for user-project membership
user_projects = Table(
    'user_projects',
    BaseModel.metadata,
    Column('user_id', String(36), ForeignKey('users.id', ondelete='CASCADE')),
    Column('project_id', String(36), ForeignKey('projects.id', ondelete='CASCADE')),
    Index('ix_user_projects_user_id', 'user_id'),
    Index('ix_user_projects_project_id', 'project_id')
)


class User(BaseModel):
    """User entity for the multi-tenant system"""
    __tablename__ = "users"
    __table_args__ = (
        Index('ix_users_email', 'email'),
        Index('ix_users_username', 'username'),
        Index('ix_users_organization_id', 'organization_id'),
        Index('ix_users_is_active', 'is_active'),
        {"comment": "User accounts with authentication"}
    )
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(512), nullable=False)
    
    # Profile
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Organization and role
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False
    )
    role_id = Column(
        String(36),
        ForeignKey('roles.id', ondelete='SET NULL'),
        nullable=False
    )
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    
    # Tracking
    last_login = Column(DateTime, nullable=True)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id]
    )
    role = relationship(
        "Role",
        back_populates="users",
        foreign_keys=[role_id]
    )
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.user_id"
    )
    projects = relationship(
        "Project",
        secondary=user_projects,
        back_populates="members"
    )
    created_projects = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by",
        cascade="all, delete-orphan"
    )
