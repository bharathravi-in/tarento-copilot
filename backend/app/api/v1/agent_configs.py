"""
Agent Configuration CRUD Endpoints
Provides complete CRUD operations for agent configurations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import AgentConfig, User, Conversation
from app.schemas.agent import AgentConfigCreate, AgentConfigUpdate, AgentConfigResponse
from app.schemas.common import ListResponse
from app.utils.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/agent-configs", tags=["Agent Configs"])


@router.get("/", response_model=ListResponse[AgentConfigResponse])
async def list_agent_configs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    agent_type: Optional[str] = None,
    project_id: Optional[str] = None
):
    """
    List agent configs in user's organization
    
    Users see only agent configs in their organization
    Superusers see all agent configs
    """
    query = db.query(AgentConfig)
    
    # Filter by organization if not superuser
    if not current_user.is_superuser:
        query = query.filter(AgentConfig.organization_id == current_user.organization_id)
    
    # Search by name or description
    if search:
        query = query.filter(
            (AgentConfig.name.ilike(f"%{search}%")) |
            (AgentConfig.description.ilike(f"%{search}%"))
        )
    
    # Filter by agent type
    if agent_type:
        query = query.filter(AgentConfig.agent_type == agent_type)
    
    # Filter by project
    if project_id:
        query = query.filter(AgentConfig.project_id == project_id)
    
    total = query.count()
    agent_configs = query.order_by(AgentConfig.created_at.desc()).offset(skip).limit(limit).all()
    
    return ListResponse(
        data=agent_configs,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{agent_config_id}", response_model=AgentConfigResponse)
async def get_agent_config(
    agent_config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get agent config by ID
    
    Users can only access agent configs in their organization
    """
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.id == agent_config_id
    ).first()
    
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent config not found")
    
    # Check organization access
    if not current_user.is_superuser and agent_config.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return agent_config


@router.post("/", response_model=AgentConfigResponse)
async def create_agent_config(
    config: AgentConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new agent config
    
    Requires admin role or superuser
    """
    # Check authorization
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create agent configs")
    
    # Verify project exists if project_id provided
    if config.project_id:
        from app.models import Project
        project = db.query(Project).filter(Project.id == config.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.organization_id != current_user.organization_id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Project not in your organization")
    
    # Create agent config
    agent_config = AgentConfig(
        id=str(uuid.uuid4()),
        name=config.name,
        description=config.description,
        agent_type=config.agent_type,
        organization_id=current_user.organization_id,
        project_id=config.project_id,
        llm_model=config.llm_model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        system_prompt=config.system_prompt,
        tools=config.tools,
        knowledge_bases=config.knowledge_bases,
        parameters=config.parameters,
        is_active=True,
        is_default=False,
        agent_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(agent_config)
    db.commit()
    db.refresh(agent_config)
    
    return agent_config


@router.put("/{agent_config_id}", response_model=AgentConfigResponse)
async def update_agent_config(
    agent_config_id: str,
    config_update: AgentConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update agent config
    
    Requires admin role or superuser
    """
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.id == agent_config_id
    ).first()
    
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent config not found")
    
    # Check organization access
    if not current_user.is_superuser and agent_config.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check authorization
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update agent configs")
    
    # Update fields
    if config_update.name is not None:
        agent_config.name = config_update.name
    if config_update.description is not None:
        agent_config.description = config_update.description
    if config_update.llm_model is not None:
        agent_config.llm_model = config_update.llm_model
    if config_update.temperature is not None:
        agent_config.temperature = config_update.temperature
    if config_update.max_tokens is not None:
        agent_config.max_tokens = config_update.max_tokens
    if config_update.system_prompt is not None:
        agent_config.system_prompt = config_update.system_prompt
    if config_update.tools is not None:
        agent_config.tools = config_update.tools
    if config_update.knowledge_bases is not None:
        agent_config.knowledge_bases = config_update.knowledge_bases
    if config_update.parameters is not None:
        agent_config.parameters = config_update.parameters
    if config_update.is_active is not None:
        agent_config.is_active = config_update.is_active
    
    agent_config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(agent_config)
    
    return agent_config


@router.delete("/{agent_config_id}")
async def delete_agent_config(
    agent_config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete agent config (soft delete)
    
    Requires admin role or superuser
    """
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.id == agent_config_id
    ).first()
    
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent config not found")
    
    # Check organization access
    if not current_user.is_superuser and agent_config.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check authorization
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete agent configs")
    
    # Soft delete
    agent_config.is_active = False
    agent_config.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Agent config deleted successfully"}


@router.post("/{agent_config_id}/activate")
async def activate_agent_config(
    agent_config_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reactivate a deactivated agent config
    
    Requires admin role or superuser
    """
    agent_config = db.query(AgentConfig).filter(
        AgentConfig.id == agent_config_id
    ).first()
    
    if not agent_config:
        raise HTTPException(status_code=404, detail="Agent config not found")
    
    # Check organization access
    if not current_user.is_superuser and agent_config.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check authorization
    is_admin = current_user.is_superuser or (current_user.role and current_user.role.name.lower() == 'admin')
    if not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can activate agent configs")
    
    agent_config.is_active = True
    agent_config.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(agent_config)
    
    return agent_config
