"""
Conversation and Message Schemas
Request and response models for chat functionality
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class MessageCreate(BaseModel):
    """Schema for creating a new message"""
    content: str = Field(..., min_length=1, max_length=5000)
    role: str = Field(..., description="user or assistant")
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: str
    conversation_id: str
    role: str
    content: str
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation"""
    title: Optional[str] = None
    description: Optional[str] = None
    agent_config_id: Optional[str] = None
    project_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ConversationUpdate(BaseModel):
    """Schema for updating conversation"""
    title: Optional[str] = None
    description: Optional[str] = None
    is_archived: Optional[bool] = None
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: str
    user_id: str
    project_id: Optional[str]
    agent_config_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    is_active: bool
    is_archived: bool
    message_count: int
    context: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Conversation response with messages"""
    messages: list[MessageResponse] = []
