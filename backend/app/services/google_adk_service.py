"""
Google Agent Development Kit Service
Integrates Google's Agent Development Kit for building sophisticated AI agents
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


class AgentMessage(BaseModel):
    """Model for agent messages"""
    role: str  # "user" or "model"
    content: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class AgentToolCall(BaseModel):
    """Model for tool calls made by agents"""
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[str] = None


class AgentContext(BaseModel):
    """Context for agent execution"""
    agent_id: str
    project_id: str
    organization_id: str
    session_id: str
    messages: List[AgentMessage] = []
    tools: List[str] = []
    metadata: Dict[str, Any] = {}


class GoogleADKService:
    """
    Google Agent Development Kit Service
    Manages agent creation, execution, and management using Google's Generative AI
    """
    
    def __init__(self):
        """Initialize Google ADK Service"""
        self.enabled = settings.google_adk_enabled
        self.api_key = settings.gemini_api_key
        self.model_name = settings.gemini_model
        self.temperature = settings.google_adk_temperature
        self.max_tokens = settings.google_adk_max_tokens
        
        if self.enabled and self.api_key:
            genai.configure(api_key=self.api_key)
            logger.info(f"Google ADK initialized with model: {self.model_name}")
        else:
            logger.warning("Google ADK is disabled or API key not configured")
    
    async def create_agent(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new AI agent with Google ADK
        
        Args:
            name: Agent name
            description: Agent description
            system_prompt: System prompt for agent behavior
            tools: List of tool names the agent can use
            metadata: Additional metadata
            
        Returns:
            Agent configuration dictionary
        """
        if not self.enabled:
            raise ValueError("Google ADK is not enabled")
        
        agent_config = {
            "name": name,
            "description": description,
            "system_prompt": system_prompt,
            "tools": tools or [],
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Created agent: {name}")
        return agent_config
    
    async def execute_agent(
        self,
        context: AgentContext,
        user_input: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with given input
        
        Args:
            context: Agent execution context
            user_input: User input to process
            system_prompt: Optional system prompt override
            
        Returns:
            Agent response with metadata
        """
        if not self.enabled:
            raise ValueError("Google ADK is not enabled")
        
        try:
            # Prepare conversation history
            conversation_history = self._prepare_conversation(context.messages)
            
            # Build the full prompt
            full_prompt = self._build_prompt(
                system_prompt or context.metadata.get("system_prompt", ""),
                user_input,
                conversation_history
            )
            
            # Generate response using Gemini
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            # Extract and structure response
            agent_response = self._parse_response(response)
            
            # Update context with new message
            context.messages.append(AgentMessage(role="user", content=user_input))
            context.messages.append(AgentMessage(role="model", content=agent_response["content"]))
            
            return {
                "success": True,
                "agent_id": context.agent_id,
                "response": agent_response,
                "context_updated": True,
                "message_count": len(context.messages)
            }
            
        except Exception as e:
            logger.error(f"Agent execution error: {str(e)}")
            return {
                "success": False,
                "agent_id": context.agent_id,
                "error": str(e)
            }
    
    async def execute_agentic_loop(
        self,
        context: AgentContext,
        user_input: str,
        max_iterations: int = 5,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute agent with agentic loop (reasoning + action)
        Allows agent to iteratively refine responses
        
        Args:
            context: Agent execution context
            user_input: User input to process
            max_iterations: Maximum iterations for agent loop
            system_prompt: Optional system prompt
            
        Returns:
            Final agent response with reasoning
        """
        if not self.enabled:
            raise ValueError("Google ADK is not enabled")
        
        iteration = 0
        agent_response = None
        reasoning_steps = []
        
        try:
            while iteration < max_iterations:
                iteration += 1
                
                # Run agent iteration
                response = await self.execute_agent(
                    context,
                    user_input if iteration == 1 else f"Continue processing: {agent_response}",
                    system_prompt
                )
                
                if not response["success"]:
                    break
                
                agent_response = response["response"]["content"]
                reasoning_steps.append({
                    "iteration": iteration,
                    "response": agent_response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Check if response indicates completion
                if any(marker in agent_response.lower() for marker in ["complete", "done", "final"]):
                    break
            
            return {
                "success": True,
                "agent_id": context.agent_id,
                "final_response": agent_response,
                "iterations": iteration,
                "reasoning_steps": reasoning_steps
            }
            
        except Exception as e:
            logger.error(f"Agentic loop error: {str(e)}")
            return {
                "success": False,
                "agent_id": context.agent_id,
                "error": str(e),
                "iterations": iteration
            }
    
    async def batch_execute(
        self,
        context: AgentContext,
        inputs: List[str],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute agent on multiple inputs (batch processing)
        
        Args:
            context: Agent execution context
            inputs: List of user inputs
            system_prompt: Optional system prompt
            
        Returns:
            Batch execution results
        """
        if not self.enabled:
            raise ValueError("Google ADK is not enabled")
        
        results = []
        
        for i, user_input in enumerate(inputs):
            try:
                response = await self.execute_agent(context, user_input, system_prompt)
                results.append({
                    "index": i,
                    "input": user_input,
                    "success": response["success"],
                    "response": response.get("response", {}).get("content", "")
                })
            except Exception as e:
                logger.error(f"Batch execution error at index {i}: {str(e)}")
                results.append({
                    "index": i,
                    "input": user_input,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": all(r["success"] for r in results),
            "agent_id": context.agent_id,
            "total_inputs": len(inputs),
            "successful": sum(1 for r in results if r["success"]),
            "results": results
        }
    
    def _prepare_conversation(self, messages: List[AgentMessage]) -> str:
        """Prepare conversation history for the prompt"""
        if not messages:
            return ""
        
        conversation = []
        for msg in messages[-10:]:  # Keep last 10 messages for context
            conversation.append(f"{msg.role.upper()}: {msg.content}")
        
        return "\n".join(conversation)
    
    def _build_prompt(
        self,
        system_prompt: str,
        user_input: str,
        conversation_history: str
    ) -> str:
        """Build the complete prompt for the model"""
        prompt_parts = []
        
        if system_prompt:
            prompt_parts.append(f"SYSTEM:\n{system_prompt}\n")
        
        if conversation_history:
            prompt_parts.append(f"CONVERSATION HISTORY:\n{conversation_history}\n")
        
        prompt_parts.append(f"USER: {user_input}")
        
        return "".join(prompt_parts)
    
    def _parse_response(self, response: GenerateContentResponse) -> Dict[str, Any]:
        """Parse Gemini API response into structured format"""
        try:
            content = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "content": content,
                "finish_reason": response.candidates[0].finish_reason if response.candidates else "UNKNOWN",
                "safety_ratings": self._extract_safety_ratings(response)
            }
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            return {
                "content": str(response),
                "finish_reason": "ERROR",
                "error": str(e)
            }
    
    def _extract_safety_ratings(self, response: GenerateContentResponse) -> List[Dict[str, str]]:
        """Extract safety ratings from response"""
        try:
            if not response.candidates:
                return []
            
            ratings = []
            candidate = response.candidates[0]
            
            if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                for rating in candidate.safety_ratings:
                    ratings.append({
                        "category": str(rating.category),
                        "probability": str(rating.probability)
                    })
            
            return ratings
        except Exception as e:
            logger.warning(f"Could not extract safety ratings: {str(e)}")
            return []
    
    async def stream_agent_response(
        self,
        context: AgentContext,
        user_input: str,
        system_prompt: Optional[str] = None
    ):
        """
        Stream agent response (yields tokens as they arrive)
        
        Args:
            context: Agent execution context
            user_input: User input
            system_prompt: Optional system prompt
            
        Yields:
            Response tokens as they arrive
        """
        if not self.enabled:
            raise ValueError("Google ADK is not enabled")
        
        try:
            conversation_history = self._prepare_conversation(context.messages)
            full_prompt = self._build_prompt(
                system_prompt or "",
                user_input,
                conversation_history
            )
            
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(
                full_prompt,
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens
                )
            )
            
            full_response = ""
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield chunk.text
            
            # Update context after streaming is complete
            context.messages.append(AgentMessage(role="user", content=user_input))
            context.messages.append(AgentMessage(role="model", content=full_response))
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            yield f"ERROR: {str(e)}"


# Initialize singleton instance
google_adk_service = GoogleADKService()
