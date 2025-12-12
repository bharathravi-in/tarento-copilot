"""
Google ADK Agent API Endpoints
Provides REST API for agent creation, execution, and management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel, Field
import logging
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.google_adk_service import (
    GoogleADKService,
    AgentContext,
    AgentMessage,
    google_adk_service
)
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation, Message

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


class ContextDocument(BaseModel):
    """Retrieved context document"""
    id: str
    title: str
    preview: str
    relevance_score: float


class ContextMessage(BaseModel):
    """Retrieved context message"""
    id: str
    conversation_id: str
    role: str
    content: str
    relevance_score: float


class RAGContext(BaseModel):
    """Complete RAG context from documents and conversations"""
    documents: List[ContextDocument] = []
    messages: List[ContextMessage] = []
    context_summary: str


class ExecuteAgentWithFullRAGRequest(BaseModel):
    """Request to execute an agent with full RAG pipeline"""
    agent_id: str
    project_id: str
    organization_id: str
    conversation_id: Optional[str] = None
    user_input: str
    system_prompt: Optional[str] = None
    retrieve_documents: bool = Field(default=True, description="Retrieve relevant documents")
    retrieve_conversation_context: bool = Field(default=True, description="Retrieve conversation history")
    document_limit: int = Field(default=5, ge=1, le=20, description="Max documents to retrieve")
    message_limit: int = Field(default=10, ge=1, le=50, description="Max messages to retrieve")
    context_score_threshold: float = Field(default=0.7, ge=0, le=1, description="Min similarity score")
    include_agent_system_context: bool = Field(default=True, description="Include agent context in prompt")


class ExecuteAgentWithFullRAGResponse(BaseModel):
    """Response from full RAG agent execution"""
    success: bool
    agent_id: str
    response: Dict[str, Any]
    context: RAGContext
    context_used: bool
    message_count: Optional[int] = None
    execution_time_ms: Optional[int] = None


class ExecuteAgentWithRAGRequest(BaseModel):
    """Request to execute an agent with RAG (document context)"""
    agent_id: str
    project_id: str
    organization_id: str
    user_input: str
    system_prompt: Optional[str] = None
    retrieve_context: bool = True
    context_limit: int = 5
    context_score_threshold: float = 0.7


class ExecuteAgentWithRAGResponse(BaseModel):
    """Response from agent execution with RAG"""
    success: bool
    agent_id: str
    response: dict
    context_documents: Optional[List[dict]] = None
    context_used: bool = False
    message_count: Optional[int] = None


# ============================================================================
# RAG Pipeline Helper Functions
# ============================================================================

async def retrieve_document_context(
    query: str,
    organization_id: str,
    db: Session,
    limit: int = 5,
    score_threshold: float = 0.7
) -> tuple[List[ContextDocument], str]:
    """
    Retrieve relevant documents for RAG context
    
    Returns:
        Tuple of (documents list, context text)
    """
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.embed_text(query)
        
        if not query_embedding:
            logger.warning("Failed to generate query embedding for documents")
            return [], ""
        
        # Search Qdrant for similar documents
        search_results = qdrant_service.search_similar(
            collection_name="documents",
            query_vector=query_embedding,
            organization_id=organization_id,
            limit=limit,
            score_threshold=score_threshold
        )
        
        if not search_results:
            return [], ""
        
        # Fetch document details from database
        document_ids = [r["document_id"] for r in search_results]
        documents = db.query(Document).filter(
            Document.id.in_(document_ids),
            Document.organization_id == organization_id,
            Document.is_active == True
        ).all()
        
        # Build context documents and text
        context_docs = []
        context_text_parts = []
        
        for result in search_results:
            doc = next((d for d in documents if d.id == result["document_id"]), None)
            if doc:
                score = result.get("score", 0)
                context_docs.append(ContextDocument(
                    id=doc.id,
                    title=doc.title or "Untitled",
                    preview=doc.content[:200] if doc.content else "",
                    relevance_score=float(score)
                ))
                context_text_parts.append(
                    f"Document: {doc.title}\nContent: {doc.content[:500] if doc.content else 'N/A'}"
                )
        
        context_text = "\n\n".join(context_text_parts)
        logger.info(f"Retrieved {len(context_docs)} documents for RAG context")
        
        return context_docs, context_text
        
    except Exception as e:
        logger.error(f"Error retrieving document context: {str(e)}")
        return [], ""


async def retrieve_conversation_context(
    query: str,
    conversation_id: Optional[str],
    user_id: str,
    organization_id: str,
    db: Session,
    limit: int = 10,
    score_threshold: float = 0.7
) -> tuple[List[ContextMessage], str]:
    """
    Retrieve relevant messages from conversations for RAG context
    
    Returns:
        Tuple of (messages list, context text)
    """
    try:
        # Generate embedding for query
        query_embedding = await embedding_service.embed_text(query)
        
        if not query_embedding:
            logger.warning("Failed to generate query embedding for messages")
            return [], ""
        
        # Search Qdrant for similar messages
        search_results = qdrant_service.search_similar(
            collection_name="conversations",
            query_vector=query_embedding,
            organization_id=organization_id,
            limit=limit,
            score_threshold=score_threshold
        )
        
        if not search_results:
            return [], ""
        
        # Fetch message details from database
        message_ids = [r["document_id"] for r in search_results]
        
        # Build query with optional conversation filter
        query_obj = db.query(Message).filter(Message.id.in_(message_ids))
        
        if conversation_id:
            query_obj = query_obj.filter(Message.conversation_id == conversation_id)
        
        # Also verify conversation belongs to user
        messages_with_conv = []
        for msg_id in message_ids:
            msg = db.query(Message).filter(Message.id == msg_id).first()
            if msg:
                conv = db.query(Conversation).filter(
                    Conversation.id == msg.conversation_id,
                    Conversation.user_id == user_id
                ).first()
                if conv:
                    messages_with_conv.append(msg)
        
        # Build context messages and text
        context_msgs = []
        context_text_parts = []
        
        for result in search_results:
            msg = next((m for m in messages_with_conv if m.id == result["document_id"]), None)
            if msg:
                score = result.get("score", 0)
                context_msgs.append(ContextMessage(
                    id=msg.id,
                    conversation_id=msg.conversation_id,
                    role=msg.role,
                    content=msg.content,
                    relevance_score=float(score)
                ))
                context_text_parts.append(
                    f"{msg.role.upper()}: {msg.content[:300]}"
                )
        
        context_text = "\n\n".join(context_text_parts)
        logger.info(f"Retrieved {len(context_msgs)} messages for RAG context")
        
        return context_msgs, context_text
        
    except Exception as e:
        logger.error(f"Error retrieving conversation context: {str(e)}")
        return [], ""


def build_rag_system_prompt(
    base_prompt: Optional[str],
    document_context: str,
    message_context: str,
    include_system_context: bool = True
) -> str:
    """
    Build enhanced system prompt with RAG context
    """
    context_parts = []
    
    if include_system_context:
        context_parts.append(
            "You are a helpful assistant. Use the following context to answer questions."
        )
    
    if document_context:
        context_parts.append(f"DOCUMENT CONTEXT:\n{document_context}")
    
    if message_context:
        context_parts.append(f"CONVERSATION CONTEXT:\n{message_context}")
    
    context_section = "\n\n".join(context_parts)
    
    if base_prompt:
        return f"{base_prompt}\n\n{context_section}"
    else:
        return context_section


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


@router.post("/execute/rag", response_model=ExecuteAgentWithRAGResponse)
async def execute_agent_with_rag(
    request: ExecuteAgentWithRAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute an agent with RAG (Retrieval-Augmented Generation)
    
    This endpoint:
    1. Retrieves relevant documents from the vector database
    2. Injects them as context into the system prompt
    3. Executes the agent with enhanced context
    
    Args:
        request: Agent execution request with RAG settings
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Agent response with context documents
    """
    try:
        context_documents = []
        enhanced_system_prompt = request.system_prompt
        
        if request.retrieve_context:
            try:
                # Generate embedding for the user query
                query_embedding = await embedding_service.embed_text(request.user_input)
                
                if query_embedding:
                    # Search for relevant documents
                    search_results = qdrant_service.search_similar(
                        collection_name="documents",
                        query_vector=query_embedding,
                        organization_id=str(request.organization_id),
                        limit=request.context_limit,
                        score_threshold=request.context_score_threshold
                    )
                    
                    # Fetch document details from database
                    if search_results:
                        document_ids = [r["document_id"] for r in search_results]
                        documents = db.query(Document).filter(
                            Document.id.in_(document_ids),
                            Document.organization_id == request.organization_id,
                            Document.is_active == True
                        ).all()
                        
                        # Build context from retrieved documents
                        context_text = "\\n\\n".join([
                            f"Document: {doc.title}\\nContent: {doc.content[:500]}..."
                            for doc in documents
                        ])
                        
                        # Add context to system prompt
                        if enhanced_system_prompt:
                            enhanced_system_prompt += f"\\n\\nContext from documents:\\n{context_text}"
                        else:
                            enhanced_system_prompt = f"You are a helpful assistant. Use the following documents to answer questions:\\n\\n{context_text}"
                        
                        # Track retrieved documents
                        context_documents = [
                            {
                                "id": doc.id,
                                "title": doc.title,
                                "preview": doc.content[:200] if doc.content else ""
                            }
                            for doc in documents
                        ]
                        
                        logger.info(f"Retrieved {len(context_documents)} documents for RAG")
            except Exception as e:
                logger.error(f"Error retrieving context: {str(e)}")
                # Continue without context if retrieval fails
        
        # Create agent context
        agent_context = AgentContext(
            agent_id=request.agent_id,
            project_id=request.project_id,
            organization_id=request.organization_id,
            session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
        )
        
        # Execute agent with enhanced prompt
        result = await google_adk_service.execute_agent(
            context=agent_context,
            user_input=request.user_input,
            system_prompt=enhanced_system_prompt
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        return ExecuteAgentWithRAGResponse(
            success=True,
            agent_id=request.agent_id,
            response=result["response"],
            context_documents=context_documents,
            context_used=len(context_documents) > 0,
            message_count=result.get("message_count")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent with RAG: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute/full-rag", response_model=ExecuteAgentWithFullRAGResponse)
async def execute_agent_with_full_rag(
    request: ExecuteAgentWithFullRAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Execute an agent with full RAG pipeline
    
    Combines:
    1. Document context retrieval (semantic search on documents)
    2. Conversation message context (semantic search on messages)
    3. Multi-source context assembly
    4. Enhanced system prompt with context
    5. Agent execution with enriched prompt
    
    Args:
        request: Full RAG execution request
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Agent response with complete context metadata
    """
    start_time = datetime.utcnow()
    
    try:
        # Initialize context variables
        context_documents: List[ContextDocument] = []
        context_messages: List[ContextMessage] = []
        enhanced_system_prompt = request.system_prompt
        
        # Retrieve document context
        if request.retrieve_documents:
            try:
                context_documents, doc_context_text = await retrieve_document_context(
                    query=request.user_input,
                    organization_id=request.organization_id,
                    db=db,
                    limit=request.document_limit,
                    score_threshold=request.context_score_threshold
                )
            except Exception as e:
                logger.error(f"Document context retrieval failed: {str(e)}")
        
        # Retrieve conversation context
        if request.retrieve_conversation_context:
            try:
                context_messages, msg_context_text = await retrieve_conversation_context(
                    query=request.user_input,
                    conversation_id=request.conversation_id,
                    user_id=current_user.id,
                    organization_id=request.organization_id,
                    db=db,
                    limit=request.message_limit,
                    score_threshold=request.context_score_threshold
                )
            except Exception as e:
                logger.error(f"Conversation context retrieval failed: {str(e)}")
        
        # Build enhanced system prompt with all context
        if context_documents or context_messages:
            doc_context = "\n\n".join([
                f"Document: {doc.title}\n{doc.preview}"
                for doc in context_documents
            ])
            
            msg_context = "\n\n".join([
                f"{msg.role.upper()}: {msg.content}"
                for msg in context_messages
            ])
            
            enhanced_system_prompt = build_rag_system_prompt(
                base_prompt=request.system_prompt,
                document_context=doc_context,
                message_context=msg_context,
                include_system_context=request.include_agent_system_context
            )
            
            logger.info(
                f"Enhanced prompt with {len(context_documents)} documents "
                f"and {len(context_messages)} messages"
            )
        
        # Create agent context
        agent_context = AgentContext(
            agent_id=request.agent_id,
            project_id=request.project_id,
            organization_id=request.organization_id,
            session_id=f"{request.organization_id}_{request.project_id}_{request.agent_id}"
        )
        
        # Execute agent with enhanced prompt
        result = await google_adk_service.execute_agent(
            context=agent_context,
            user_input=request.user_input,
            system_prompt=enhanced_system_prompt
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        # Calculate execution time
        execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Build comprehensive context summary
        context_summary = f"Retrieved {len(context_documents)} documents and {len(context_messages)} messages"
        
        return ExecuteAgentWithFullRAGResponse(
            success=True,
            agent_id=request.agent_id,
            response=result["response"],
            context=RAGContext(
                documents=context_documents,
                messages=context_messages,
                context_summary=context_summary
            ),
            context_used=len(context_documents) > 0 or len(context_messages) > 0,
            message_count=result.get("message_count"),
            execution_time_ms=execution_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent with full RAG: {str(e)}")
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
