"""
Agent Configuration Model
Represents AI agent configurations
"""

from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Index, Integer, Float
from sqlalchemy.orm import relationship
from .base import BaseModel


class AgentConfig(BaseModel):
    """Agent configuration for each specialized agent"""
    __tablename__ = "agent_configs"
    __table_args__ = (
        Index('ix_agent_configs_organization_id', 'organization_id'),
        Index('ix_agent_configs_project_id', 'project_id'),
        Index('ix_agent_configs_agent_type', 'agent_type'),
        Index('ix_agent_configs_is_active', 'is_active'),
        {"comment": "AI Agent configurations"}
    )
    
    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Agent type
    agent_type = Column(
        String(50),
        nullable=False,
        comment="rfp, jira, documentation, hr, finance"
    )
    
    # Organization and project scope
    organization_id = Column(
        String(36),
        ForeignKey('organizations.id', ondelete='CASCADE'),
        nullable=False
    )
    project_id = Column(
        String(36),
        ForeignKey('projects.id', ondelete='CASCADE'),
        nullable=True,
        comment="NULL means organization-level agent"
    )
    
    # LLM Configuration
    llm_model = Column(
        String(100),
        default="gemini-2.5-pro",
        nullable=False
    )
    system_prompt = Column(
        Text,
        nullable=True,
        comment="System prompt for agent behavior"
    )
    max_tokens = Column(
        Integer,
        default=4096,
        comment="Maximum output tokens"
    )
    temperature = Column(
        Float,
        default=0.7,
        comment="Creativity level (0-1)"
    )
    
    # Tools and knowledge
    tools = Column(
        JSON,
        default=list,
        nullable=False,
        comment="List of tools agent can use"
    )
    knowledge_bases = Column(
        JSON,
        default=list,
        nullable=False,
        comment="Knowledge bases for RAG"
    )
    parameters = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional agent parameters"
    )
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    agent_metadata = Column(
        JSON,
        default=dict,
        nullable=False,
        comment="Additional configuration metadata"
    )
    
    # Relationships
    organization = relationship(
        "Organization",
        back_populates="agent_configs",
        foreign_keys=[organization_id]
    )
    project = relationship(
        "Project",
        back_populates="agent_configs",
        foreign_keys=[project_id]
    )
    conversations = relationship(
        "Conversation",
        back_populates="agent",
        cascade="all, delete-orphan",
        foreign_keys="Conversation.agent_config_id"
    )
