"""
Google ADK Agent API Endpoints
Provides REST API for agent creation, execution, and management
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
import logging

from app.services.google_adk_service import (
    GoogleADKService,
    AgentContext,
    AgentMessage,
    google_adk_service
)
from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])


# Request/Response Models
class CreateAgentRequest(BaseModel):
    """Request to create a new agent"""
    name: str
    description: str
    system_prompt: str
    tools: Optional[List[str]] = None
    metadata: Optional[dict] = None


class CreateAgentResponse(BaseModel):
    """Response after agent creation"""
    success: bool
    agent_name: str
    agent_config: dict


class ExecuteAgentRequest(BaseModel):
    """Request to execute an agent"""
    agent_id: str
    project_id: str
    organization_id: str
    user_input: str
    system_prompt: Optional[str] = None


class ExecuteAgentResponse(BaseModel):
    """Response from agent execution"""
    success: bool
    agent_id: str
    response: dict
    message_count: Optional[int] = None


class AgenticLoopRequest(BaseModel):
    """Request for agentic loop execution"""
    agent_id: str
    project_id: str
    organization_id: str
    user_input: str
    max_iterations: int = 5
    system_prompt: Optional[str] = None


class BatchExecuteRequest(BaseModel):
    """Request for batch agent execution"""
    agent_id: str
    project_id: str
    organization_id: str
    inputs: List[str]
    system_prompt: Optional[str] = None


@router.post("/create", response_model=CreateAgentResponse)
async def create_agent(request: CreateAgentRequest):
    """
    Create a new AI agent using Google ADK
    
    Args:
        request: Agent creation request
        
    Returns:
        Created agent configuration
    """
    try:
        agent_config = await google_adk_service.create_agent(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
            tools=request.tools,
            metadata=request.metadata
        )
        
        return CreateAgentResponse(
            success=True,
            agent_name=request.name,
            agent_config=agent_config
        )
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/execute", response_model=ExecuteAgentResponse)
async def execute_agent(request: ExecuteAgentRequest):
    """
    Execute an agent with given input
    
    Args:
        request: Agent execution request
        
    Returns:
        Agent response
    """
    try:
        # Create agent context
        context = AgentContext(
            agent_id=request.agent_id,
            project_id=request.project_id,
            organization_id=request.organization_id,
            session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
        )
        
        # Execute agent
        result = await google_adk_service.execute_agent(
            context=context,
            user_input=request.user_input,
            system_prompt=request.system_prompt
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ExecuteAgentResponse(
            success=True,
            agent_id=request.agent_id,
            response=result["response"],
            message_count=result.get("message_count")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/agentic-loop", response_model=ExecuteAgentResponse)
async def execute_agentic_loop(request: AgenticLoopRequest):
    """
    Execute agent with agentic loop (reasoning + iteration)
    
    Args:
        request: Agentic loop execution request
        
    Returns:
        Final agent response with reasoning steps
    """
    try:
        context = AgentContext(
            agent_id=request.agent_id,
            project_id=request.project_id,
            organization_id=request.organization_id,
            session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
        )
        
        result = await google_adk_service.execute_agentic_loop(
            context=context,
            user_input=request.user_input,
            max_iterations=request.max_iterations,
            system_prompt=request.system_prompt
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ExecuteAgentResponse(
            success=True,
            agent_id=request.agent_id,
            response=result
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in agentic loop: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-execute")
async def batch_execute(request: BatchExecuteRequest):
    """
    Execute agent on multiple inputs (batch processing)
    
    Args:
        request: Batch execution request
        
    Returns:
        Batch execution results
    """
    try:
        context = AgentContext(
            agent_id=request.agent_id,
            project_id=request.project_id,
            organization_id=request.organization_id,
            session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
        )
        
        result = await google_adk_service.batch_execute(
            context=context,
            inputs=request.inputs,
            system_prompt=request.system_prompt
        )
        
        return result
    except Exception as e:
        logger.error(f"Error in batch execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_agent_response(request: ExecuteAgentRequest):
    """
    Stream agent response (tokens arrive as they're generated)
    
    Args:
        request: Agent execution request
        
    Returns:
        Streaming response
    """
    from fastapi.responses import StreamingResponse
    
    async def response_generator():
        try:
            context = AgentContext(
                agent_id=request.agent_id,
                project_id=request.project_id,
                organization_id=request.organization_id,
                session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
            )
            
            async for chunk in google_adk_service.stream_agent_response(
                context=context,
                user_input=request.user_input,
                system_prompt=request.system_prompt
            ):
                yield chunk
        except Exception as e:
            yield f"ERROR: {str(e)}"
    
    return StreamingResponse(
        response_generator(),
        media_type="text/event-stream"
    )


@router.get("/health")
async def agent_health_check():
    """Check if Google ADK service is healthy and configured"""
    return {
        "status": "healthy",
        "google_adk_enabled": google_adk_service.enabled,
        "model": google_adk_service.model_name,
        "api_configured": bool(google_adk_service.api_key)
    }
