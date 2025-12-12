"""
Conversation and Message Models
Represents conversations with AI agents
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Index, Integer
from sqlalchemy.orm import relationship
from .base import BaseModel


class Conversation(BaseModel):
    """Conversation entity representing a chat with an agent"""
    __tablename__ = "conversations"
    __table_args__ = (
        Index('ix_conversations_user_id', 'user_id'),
        Index('ix_conversations_project_id', 'project_id'),
        Index('ix_conversations_agent_config_id', 'agent_config_id'),
        {"comment": "Conversations with AI agents"}
    )
    
    # References
    user_id = Column(
        String(36),
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )
    project_id = Column(
        String(36),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=True
    )
    agent_config_id = Column(
        String(36),
        ForeignKey('agent_configs.id', ondelete='SET NULL'),
        nullable=True
    )
    
    # Basic info
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_archived = Column(Boolean, default=False)
    
    # Metadata
    message_count = Column(Integer, default=0)
    context = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Conversation context and settings"
    )
    conv_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional metadata"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="conversations",
        foreign_keys=[user_id]
    )
    project = relationship(
        "Project",
        back_populates="conversations",
        foreign_keys=[project_id]
    )
    agent = relationship(
        "AgentConfig",
        back_populates="conversations",
        foreign_keys=[agent_config_id]
    )
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        foreign_keys="Message.conversation_id",
        lazy="selectin"
    )


class Message(BaseModel):
    """Message entity representing individual messages in a conversation"""
    __tablename__ = "messages"
    __table_args__ = (
        Index('ix_messages_conversation_id', 'conversation_id'),
        Index('ix_messages_role', 'role'),
        {"comment": "Messages in conversations"}
    )
    
    # References
    conversation_id = Column(
        String(36),
        ForeignKey('conversations.id', ondelete='CASCADE'),
        nullable=False
    )
    
    # Message content
    role = Column(
        String(20),
        nullable=False,
        comment="user, assistant, system"
    )
    content = Column(Text, nullable=False)
    
    # Metadata
    tokens_used = Column(Integer, default=0)
    processing_time_ms = Column(Integer, nullable=True)
    
    msg_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Message metadata (model, finish_reason, etc.)"
    )
    
    # Relationships
    conversation = relationship(
        "Conversation",
        back_populates="messages",
        foreign_keys=[conversation_id]
    )
