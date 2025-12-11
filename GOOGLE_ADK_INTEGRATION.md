# Google Agent Development Kit (ADK) Integration

## Overview

Google Agent Development Kit (ADK) has been integrated into Tarento Enterprise AI Co-Pilot to enable sophisticated agent-based workflows powered by Google's Gemini AI models.

## What is Google ADK?

Google Agent Development Kit is a framework that enables:
- **Multi-step reasoning**: Agents can think through problems iteratively
- **Tool use**: Agents can call external functions/APIs
- **Streaming responses**: Real-time token streaming for better UX
- **Batch processing**: Handle multiple inputs efficiently
- **Safety & content moderation**: Built-in safety checks

## Features Implemented

### 1. Agent Creation
Create intelligent agents with custom system prompts, descriptions, and assigned tools.

```python
agent_config = await google_adk_service.create_agent(
    name="RFP Analyzer",
    description="Analyzes RFP documents for key requirements",
    system_prompt="You are an expert RFP analyzer...",
    tools=["document_parser", "requirement_extractor"],
    metadata={"version": "1.0"}
)
```

### 2. Agent Execution
Execute agents with user input and get structured responses.

```python
result = await google_adk_service.execute_agent(
    context=agent_context,
    user_input="Analyze this RFP...",
    system_prompt="Optional override"
)
```

### 3. Agentic Loop
Enable multi-step reasoning where agents can iterate and refine responses.

```python
result = await google_adk_service.execute_agentic_loop(
    context=agent_context,
    user_input="Complex problem...",
    max_iterations=5
)
```

### 4. Batch Processing
Process multiple inputs in parallel for efficiency.

```python
results = await google_adk_service.batch_execute(
    context=agent_context,
    inputs=["input1", "input2", "input3"]
)
```

### 5. Streaming Responses
Stream responses token-by-token for better UX.

```python
async for chunk in google_adk_service.stream_agent_response(
    context=agent_context,
    user_input="Generate analysis..."
):
    print(chunk, end="")
```

## API Endpoints

### Create Agent
**POST** `/api/v1/agents/create`

Create a new AI agent.

```json
{
    "name": "RFP Analyzer",
    "description": "Analyzes RFP documents",
    "system_prompt": "You are an RFP analysis expert...",
    "tools": ["parser", "extractor"],
    "metadata": {"version": "1.0"}
}
```

Response:
```json
{
    "success": true,
    "agent_name": "RFP Analyzer",
    "agent_config": {...}
}
```

### Execute Agent
**POST** `/api/v1/agents/execute`

Execute an agent with input.

```json
{
    "agent_id": "rrf_analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Analyze this RFP...",
    "system_prompt": "Optional override"
}
```

Response:
```json
{
    "success": true,
    "agent_id": "rrf_analyzer_001",
    "response": {
        "content": "Analysis results...",
        "finish_reason": "STOP",
        "safety_ratings": [...]
    },
    "message_count": 2
}
```

### Execute Agentic Loop
**POST** `/api/v1/agents/execute/agentic-loop`

Execute agent with multi-step reasoning.

```json
{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Complex analysis task...",
    "max_iterations": 5,
    "system_prompt": "Optional override"
}
```

Response:
```json
{
    "success": true,
    "agent_id": "analyzer_001",
    "response": {
        "final_response": "Final analysis...",
        "iterations": 3,
        "reasoning_steps": [
            {"iteration": 1, "response": "Step 1..."},
            {"iteration": 2, "response": "Step 2..."},
            {"iteration": 3, "response": "Step 3..."}
        ]
    }
}
```

### Batch Execute
**POST** `/api/v1/agents/batch-execute`

Process multiple inputs in one request.

```json
{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "inputs": ["input1", "input2", "input3"],
    "system_prompt": "Optional override"
}
```

Response:
```json
{
    "success": true,
    "agent_id": "analyzer_001",
    "total_inputs": 3,
    "successful": 3,
    "results": [
        {"index": 0, "input": "input1", "success": true, "response": "..."},
        {"index": 1, "input": "input2", "success": true, "response": "..."},
        {"index": 2, "input": "input3", "success": true, "response": "..."}
    ]
}
```

### Stream Agent Response
**POST** `/api/v1/agents/stream`

Stream response tokens as they're generated.

```json
{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Generate analysis...",
    "system_prompt": "Optional override"
}
```

Response: Server-Sent Events (SSE) stream of text chunks

### Health Check
**GET** `/api/v1/agents/health`

Check Google ADK service status.

Response:
```json
{
    "status": "healthy",
    "google_adk_enabled": true,
    "model": "gemini-2.5-pro",
    "api_configured": true
}
```

## Configuration

### Environment Variables

```env
# Google Gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemini-2.5-pro

# Google ADK Settings
GOOGLE_ADK_ENABLED=true
GOOGLE_ADK_CACHE_THRESHOLD=100
GOOGLE_ADK_MAX_TOKENS=4096
GOOGLE_ADK_TEMPERATURE=0.7

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Configuration File

Settings in `app/config.py`:

```python
# Google ADK Settings
google_adk_enabled: bool = True
google_adk_cache_threshold: int = 100
google_adk_max_tokens: int = 4096
google_adk_temperature: float = 0.7

# Google Cloud
google_cloud_project: str = ""
google_cloud_location: str = "us-central1"
```

## How to Use

### 1. Setup

Ensure you have:
1. Google Gemini API key from [Google AI Studio](https://aistudio.google.com)
2. Set `GEMINI_API_KEY` in `.env`
3. Install dependencies: `pip install -r requirements.txt`

### 2. Create an Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RFP Analyzer",
    "description": "Analyzes RFP documents",
    "system_prompt": "You are an expert at analyzing RFP documents...",
    "tools": ["document_parser"],
    "metadata": {"version": "1.0"}
  }'
```

### 3. Execute Agent

```bash
curl -X POST "http://localhost:8000/api/v1/agents/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "rrf_analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Analyze this RFP document for key requirements"
  }'
```

### 4. Use Agentic Loop

```bash
curl -X POST "http://localhost:8000/api/v1/agents/execute/agentic-loop" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Provide a comprehensive analysis with recommendations",
    "max_iterations": 5
  }'
```

### 5. Stream Responses

```bash
curl -X POST "http://localhost:8000/api/v1/agents/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Generate detailed analysis"
  }'
```

## Architecture

### Service Layer (`app/services/google_adk_service.py`)

**GoogleADKService** class provides:
- Agent creation and configuration
- Multi-step execution with reasoning
- Batch processing capabilities
- Streaming response handling
- Safety rating extraction
- Error handling and logging

### Models (`app/services/google_adk_service.py`)

- **AgentMessage**: Represents a message in agent conversation
- **AgentToolCall**: Represents a tool invocation
- **AgentContext**: Encapsulates agent execution context

### API Layer (`app/api/v1/agents.py`)

REST endpoints for:
- Agent CRUD operations
- Execution management
- Response streaming
- Health monitoring

## Agent Capabilities

### Supported by Google ADK

1. **Natural Language Understanding**: Process complex instructions
2. **Reasoning**: Multi-step problem solving with iteration
3. **Tool Integration**: Call external APIs and functions
4. **Content Safety**: Built-in content moderation
5. **Token Management**: Efficient token usage with caching
6. **Streaming**: Real-time token streaming

### Integration with Tarento's 5 Agents

#### 1. RFP & Proposal Agent
```python
system_prompt = """You are an expert RFP analyzer. Your responsibilities:
- Extract key requirements from RFP documents
- Identify compliance requirements
- Estimate project costs and timeline
- Generate proposal drafts"""
```

#### 2. Jira Analytics Agent
```python
system_prompt = """You are a Jira analytics expert. Analyze:
- Team velocity trends
- Burndown charts
- Sprint performance metrics
- Bottleneck identification"""
```

#### 3. Documentation Agent
```python
system_prompt = """You are a technical documentation expert. Generate:
- API documentation from code
- Architecture diagrams descriptions
- Test documentation
- User guides"""
```

#### 4. HR Agent
```python
system_prompt = """You are an HR operations expert. Help with:
- Resume screening and ranking
- Onboarding workflow planning
- Interview question generation
- Candidate matching"""
```

#### 5. Finance Agent
```python
system_prompt = """You are a finance analyst. Process:
- Invoice validation and OCR
- Payment processing
- Financial analytics
- Budget forecasting"""
```

## Performance Optimization

### Token Caching
- Threshold: 100 tokens (configurable)
- Reduces latency for repeated queries
- Lower costs for similar requests

### Streaming
- Real-time response delivery
- Better user experience
- Progressive rendering

### Batch Processing
- Process multiple items efficiently
- Reduced API call overhead
- Parallel execution

## Error Handling

The service includes comprehensive error handling:

```python
{
    "success": false,
    "agent_id": "analyzer_001",
    "error": "API key not configured"
}
```

Common errors:
- `API key not configured`: Set `GEMINI_API_KEY`
- `Service disabled`: Enable with `GOOGLE_ADK_ENABLED=true`
- `Max iterations exceeded`: Reduce `max_iterations`
- `Model not found`: Check `GEMINI_MODEL` setting

## Monitoring & Logging

All agent operations are logged:

```python
logger.info(f"Created agent: {name}")
logger.error(f"Agent execution error: {str(e)}")
logger.warning("Could not extract safety ratings")
```

Logs available in Docker: `docker-compose logs backend`

## Next Steps

1. **Integration**: Connect agents to knowledge base (Week 5)
2. **Tool Definition**: Implement actual agent tools (Week 6)
3. **Monitoring**: Add observability with Opik (Week 7)
4. **Frontend**: Create UI for agent interaction (Week 8)

## References

- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/tutorials/python_quickstart)
- [Agent Design Patterns](https://ai.google.dev/docs/agents)

## Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Verify API key is set
3. Test health endpoint: `curl http://localhost:8000/api/v1/agents/health`
4. Review error messages in response
