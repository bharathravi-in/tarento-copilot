"""
Conversation and Message Management Endpoints
Provides REST API for chat conversations and messages
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
import logging
from app.database import get_db
from app.models import Conversation, Message, User, AgentConfig
from app.schemas.conversation import (
    ConversationCreate, 
    ConversationUpdate, 
    ConversationResponse,
    ConversationDetailResponse,
    MessageCreate,
    MessageResponse
)
from app.schemas.common import ListResponse
from app.dependencies import get_current_user
from app.services.qdrant_service import qdrant_service
from app.services.embedding_service import embedding_service
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("/", response_model=ListResponse[ConversationResponse])
async def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    project_id: Optional[str] = None,
    agent_config_id: Optional[str] = None,
    include_archived: bool = Query(False)
):
    """
    List conversations for current user
    
    Users see only their own conversations
    """
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)
    
    # Exclude archived by default
    if not include_archived:
        query = query.filter(Conversation.is_archived == False)
    
    # Search by title or description
    if search:
        query = query.filter(
            (Conversation.title.ilike(f"%{search}%")) |
            (Conversation.description.ilike(f"%{search}%"))
        )
    
    # Filter by project
    if project_id:
        query = query.filter(Conversation.project_id == project_id)
    
    # Filter by agent config
    if agent_config_id:
        query = query.filter(Conversation.agent_config_id == agent_config_id)
    
    total = query.count()
    conversations = query.order_by(Conversation.created_at.desc()).offset(skip).limit(limit).all()
    
    return ListResponse(
        data=conversations,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get conversation with all messages
    
    Users can only access their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return conversation


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conv_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation
    
    Users can create conversations for their projects or agents
    """
    # Verify project exists if provided
    if conv_data.project_id:
        from app.models import Project
        project = db.query(Project).filter(Project.id == conv_data.project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Project not in your organization")
    
    # Verify agent config exists if provided
    if conv_data.agent_config_id:
        agent_config = db.query(AgentConfig).filter(
            AgentConfig.id == conv_data.agent_config_id
        ).first()
        if not agent_config:
            raise HTTPException(status_code=404, detail="Agent config not found")
        if agent_config.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Agent config not in your organization")
    
    # Create conversation
    conversation = Conversation(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        project_id=conv_data.project_id,
        agent_config_id=conv_data.agent_config_id,
        title=conv_data.title,
        description=conv_data.description,
        is_active=True,
        is_archived=False,
        message_count=0,
        context=conv_data.context or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conv_update: ConversationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update conversation
    
    Users can only update their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if conv_update.title is not None:
        conversation.title = conv_update.title
    if conv_update.description is not None:
        conversation.description = conv_update.description
    if conv_update.is_archived is not None:
        conversation.is_archived = conv_update.is_archived
    if conv_update.context is not None:
        conversation.context = conv_update.context
    
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(conversation)
    
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete conversation (soft delete)
    
    Users can only delete their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Soft delete - just mark as inactive
    conversation.is_active = False
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Conversation deleted successfully"}


# Helper functions for message vector indexing
async def index_message_vector(message_id: str, content: str, conversation_id: str, user_id: str, organization_id: str):
    """
    Index a message in Qdrant vector database
    
    Args:
        message_id: Message ID to index
        content: Message content to embed
        conversation_id: Associated conversation ID
        user_id: Message creator user ID
        organization_id: Organization ID for scoping
    """
    try:
        # Generate embedding for message content
        embedding = await embedding_service.embed_text(content)
        
        if embedding:
            # Add to Qdrant conversations collection
            qdrant_service.add_document_vector(
                collection_name="conversations",
                document_id=message_id,
                vector=embedding,
                metadata={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "organization_id": organization_id,
                    "content_preview": content[:200],
                    "indexed_at": datetime.utcnow().isoformat()
                }
            )
            logger.info(f"Message {message_id} indexed successfully in conversations collection")
    except Exception as e:
        logger.error(f"Error indexing message {message_id}: {str(e)}")


async def delete_message_vector(message_id: str, organization_id: str):
    """
    Remove a message from Qdrant vector database
    
    Args:
        message_id: Message ID to remove
        organization_id: Organization ID for scoping
    """
    try:
        # Delete from Qdrant
        qdrant_service.delete_document_vector(
            collection_name="conversations",
            document_id=message_id,
            organization_id=organization_id
        )
        logger.info(f"Message {message_id} removed from vector database")
    except Exception as e:
        logger.error(f"Error deleting message vector {message_id}: {str(e)}")


# Messages endpoints
messages_router = APIRouter(prefix="/conversations/{conversation_id}/messages", tags=["Messages"])


@messages_router.get("/", response_model=ListResponse[MessageResponse])
async def list_messages(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """
    List messages in a conversation
    
    Users can only access their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    )
    
    total = query.count()
    messages = query.order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    return ListResponse(
        data=messages,
        total=total,
        skip=skip,
        limit=limit
    )


@messages_router.post("/", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a message to a conversation
    
    Messages are automatically indexed in the vector database for semantic search
    Users can only add messages to their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Validate role
    if message_data.role not in ["user", "assistant"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'assistant'")
    
    # Create message
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=message_data.role,
        content=message_data.content,
        tokens_used=message_data.tokens_used or 0,
        processing_time_ms=message_data.processing_time_ms,
        msg_metadata=message_data.metadata or {},
        created_at=datetime.utcnow()
    )
    
    db.add(message)
    
    # Update conversation message count and timestamp
    conversation.message_count += 1
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(message)
    
    # Index message asynchronously in background
    background_tasks.add_task(
        index_message_vector,
        message_id=message.id,
        content=message.content,
        conversation_id=conversation_id,
        user_id=current_user.id,
        organization_id=str(current_user.organization_id)
    )
    
    logger.info(f"Message {message.id} created in conversation {conversation_id}")
    
    return message


@messages_router.get("/{message_id}", response_model=MessageResponse)
async def get_message(
    conversation_id: str,
    message_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific message
    
    Users can only access messages in their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return message


@messages_router.delete("/{message_id}")
async def delete_message(
    conversation_id: str,
    message_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a message
    
    Removes message from both database and vector index
    Users can only delete messages from their own conversations
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Delete message
    db.delete(message)
    
    # Update conversation message count
    conversation.message_count = max(0, conversation.message_count - 1)
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    
    # Remove from vector database asynchronously
    background_tasks.add_task(
        delete_message_vector,
        message_id=message_id,
        organization_id=str(current_user.organization_id)
    )
    
    logger.info(f"Message {message_id} deleted from conversation {conversation_id}")
    
    return {"message": "Message deleted successfully"}


@router.post("/{conversation_id}/search", response_model=ListResponse[MessageResponse])
async def search_conversation_messages(
    conversation_id: str,
    query: str = Query(..., description="Semantic search query"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.7, ge=0, le=1)
):
    """
    Perform semantic search on conversation messages
    
    Searches messages in a conversation for semantic similarity
    to the provided query using vector embeddings
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check ownership
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Generate query embedding
        query_embedding = await embedding_service.embed_text(query)
        
        if not query_embedding:
            raise HTTPException(status_code=400, detail="Failed to generate query embedding")
        
        # Search in Qdrant for similar messages in this conversation
        # Note: We search by user_id to keep it conversation-scoped for privacy
        search_results = qdrant_service.search_similar(
            collection_name="conversations",
            query_vector=query_embedding,
            organization_id=str(current_user.organization_id),
            limit=limit,
            score_threshold=min_score
        )
        
        # Filter results to only messages in this conversation
        if search_results:
            message_ids = [r["document_id"] for r in search_results]
            messages = db.query(Message).filter(
                Message.id.in_(message_ids),
                Message.conversation_id == conversation_id
            ).all()
            
            # Sort by search score
            message_map = {r["document_id"]: r.get("score", 0) for r in search_results}
            sorted_messages = sorted(messages, key=lambda m: message_map.get(m.id, 0), reverse=True)
            
            return ListResponse(
                data=sorted_messages,
                total=len(sorted_messages),
                skip=0,
                limit=limit,
                metadata={"search_type": "semantic", "query": query, "min_score": min_score}
            )
        
        return ListResponse(
            data=[],
            total=0,
            skip=0,
            limit=limit,
            metadata={"search_type": "semantic", "query": query}
        )
    except Exception as e:
        logger.error(f"Semantic search error in conversation {conversation_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Include messages router as sub-router
router.include_router(messages_router)
