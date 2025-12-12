"""
Agent Configuration Schemas
Request and response models for agent management
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentConfigCreate(BaseModel):
    """Schema for creating a new agent config"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    agent_type: str = Field(..., description="Agent type: rfp, jira, documentation, hr, finance")
    project_id: Optional[str] = None
    llm_model: str = Field(default="gemini-2.5-pro")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, ge=100, le=8000)
    system_prompt: Optional[str] = None
    tools: List[str] = Field(default=[])
    knowledge_bases: List[str] = Field(default=[])
    parameters: Dict[str, Any] = Field(default={})


class AgentConfigUpdate(BaseModel):
    """Schema for updating agent config"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    llm_model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    system_prompt: Optional[str] = None
    tools: Optional[List[str]] = None
    knowledge_bases: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AgentConfigResponse(BaseModel):
    """Schema for agent config response"""
    id: str
    name: str
    description: Optional[str]
    agent_type: str
    organization_id: str
    project_id: Optional[str]
    llm_model: str
    temperature: float
    max_tokens: int
    system_prompt: Optional[str]
    tools: List[str]
    knowledge_bases: List[str]
    parameters: Dict[str, Any]
    is_active: bool
    is_default: bool
    agent_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
