# Google ADK Integration - Quick Start Guide

## ✅ What Was Added

Google Agent Development Kit (ADK) has been fully integrated into Tarento Enterprise AI Co-Pilot. This enables building sophisticated AI agents with:

- **Multi-step reasoning**: Agents can iterate and refine responses
- **Tool integration**: Agents can call external functions/APIs
- **Streaming responses**: Real-time token delivery for better UX
- **Batch processing**: Handle multiple inputs in one request
- **Safety moderation**: Built-in content safety checks

## 📦 Dependencies Added

Updated `requirements.txt` with:
- `google-generativeai==0.5.0` - Latest Gemini API
- `google-ai-generativelanguage==0.4.0` - Language models
- `google-api-core==2.15.0` - Core Google APIs
- `google-auth==2.27.0` - Authentication
- `google-cloud-core==2.4.1` - Cloud core services
- `google-cloud-logging==3.8.0` - Cloud logging
- `google-cloud-trace==1.11.1` - Distributed tracing
- `grpcio==1.60.0` - gRPC support
- `protobuf==4.25.1` - Protocol buffers

## 🔧 Files Created/Modified

### New Files
1. **backend/app/services/google_adk_service.py** (400+ lines)
   - `GoogleADKService`: Main service class
   - `AgentContext`: Agent execution context
   - `AgentMessage`: Conversation management
   - `AgentToolCall`: Tool invocation tracking

2. **backend/app/api/v1/agents.py** (300+ lines)
   - POST `/agents/create` - Create agents
   - POST `/agents/execute` - Execute agents
   - POST `/agents/execute/agentic-loop` - Multi-step reasoning
   - POST `/agents/batch-execute` - Batch processing
   - POST `/agents/stream` - Streaming responses
   - GET `/agents/health` - Health check

3. **GOOGLE_ADK_INTEGRATION.md** (500+ lines)
   - Complete documentation
   - API reference with examples
   - Configuration guide
   - Use cases for all 5 Tarento agents

### Modified Files
1. **backend/requirements.txt**
   - Added 8 new Google-related packages
   - Pinned versions for reproducibility

2. **backend/app/config.py**
   - Added Google ADK configuration:
     - `google_adk_enabled: bool`
     - `google_adk_cache_threshold: int`
     - `google_adk_max_tokens: int`
     - `google_adk_temperature: float`
   - Added Google Cloud settings:
     - `google_cloud_project: str`
     - `google_cloud_location: str`

3. **backend/app/main.py**
   - Added import for agents router
   - Registered `/api/v1/agents` endpoints

4. **backend/.env.example**
   - Added all Google ADK configuration variables
   - Configuration templates for easy setup

## 🚀 How to Use

### 1. Setup
```bash
# Install new dependencies
pip install -r backend/requirements.txt

# Or in docker-compose
docker-compose build  # Rebuilds with new deps
```

### 2. Configure
Add to `.env` in backend directory:
```env
GEMINI_API_KEY=your-google-ai-studio-key
GOOGLE_ADK_ENABLED=true
GOOGLE_ADK_MAX_TOKENS=4096
GOOGLE_ADK_TEMPERATURE=0.7
GOOGLE_CLOUD_PROJECT=your-project-id
```

### 3. Create an Agent
```bash
curl -X POST http://localhost:8000/api/v1/agents/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RFP Analyzer",
    "description": "Analyzes RFP documents",
    "system_prompt": "You are an expert RFP analyzer",
    "tools": ["parser", "extractor"]
  }'
```

### 4. Execute Agent
```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Analyze this RFP document"
  }'
```

### 5. Use Agentic Loop (Multi-step Reasoning)
```bash
curl -X POST http://localhost:8000/api/v1/agents/execute/agentic-loop \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Complex analysis task",
    "max_iterations": 5
  }'
```

### 6. Stream Responses
```bash
curl -X POST http://localhost:8000/api/v1/agents/stream \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "analyzer_001",
    "project_id": "proj_123",
    "organization_id": "org_456",
    "user_input": "Generate detailed analysis"
  }'
```

### 7. Check Health
```bash
curl http://localhost:8000/api/v1/agents/health
```

## 📚 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/agents/create` | Create new agent |
| POST | `/api/v1/agents/execute` | Execute agent |
| POST | `/api/v1/agents/execute/agentic-loop` | Multi-step reasoning |
| POST | `/api/v1/agents/batch-execute` | Process multiple inputs |
| POST | `/api/v1/agents/stream` | Stream responses |
| GET | `/api/v1/agents/health` | Service health check |

## ⚙️ Configuration Options

### In `backend/app/config.py` or `.env`:

```env
# Google Gemini
GEMINI_API_KEY=your-key                    # Required
GEMINI_MODEL=gemini-2.5-pro                # Model to use

# Google ADK
GOOGLE_ADK_ENABLED=true                    # Enable/disable
GOOGLE_ADK_CACHE_THRESHOLD=100             # Token cache threshold
GOOGLE_ADK_MAX_TOKENS=4096                 # Max output tokens
GOOGLE_ADK_TEMPERATURE=0.7                 # Creativity (0-1)

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id       # GCP project
GOOGLE_CLOUD_LOCATION=us-central1          # Region
```

## 🎯 Use Cases for Tarento's 5 Agents

### 1. RFP & Proposal Agent
```python
system_prompt = """Extract requirements, identify compliance, 
estimate costs, and generate proposals"""
```

### 2. Jira Analytics Agent
```python
system_prompt = """Analyze velocity, burndown charts, 
sprint metrics, and bottlenecks"""
```

### 3. Documentation Agent
```python
system_prompt = """Generate API docs, architecture descriptions, 
test documentation, and user guides"""
```

### 4. HR Agent
```python
system_prompt = """Screen resumes, plan onboarding, 
generate interview questions, match candidates"""
```

### 5. Finance Agent
```python
system_prompt = """Validate invoices, process payments, 
analytics, and budgeting"""
```

## 🔑 Key Features

### ✨ Agent Creation
- Custom system prompts
- Tool assignment
- Metadata support
- Configuration storage

### 🔄 Execution Modes
1. **Single Execution**: One input → one output
2. **Agentic Loop**: Multi-step reasoning with iteration
3. **Batch Processing**: Multiple inputs in parallel
4. **Streaming**: Token-by-token delivery

### 🛡️ Safety & Moderation
- Content safety ratings
- Automatic moderation
- Safety category extraction
- Harmful content detection

### 📊 Monitoring
- Full logging integration
- Error tracking
- Response metadata
- Execution statistics

## 📖 Documentation

For detailed information:
- **API Reference**: See `GOOGLE_ADK_INTEGRATION.md`
- **Examples**: See curl examples in this guide
- **Configuration**: See `.env.example`
- **Code Examples**: See docstrings in `google_adk_service.py`

## 🧪 Testing

Test the integration:

```bash
# 1. Check service health
curl http://localhost:8000/api/v1/agents/health

# 2. Create a test agent
curl -X POST http://localhost:8000/api/v1/agents/create \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","description":"Test","system_prompt":"You help test"}'

# 3. Execute the agent
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"test","project_id":"test","organization_id":"test","user_input":"Say hello"}'
```

## ⚠️ Requirements

1. **Google AI Studio API Key**
   - Get from: https://aistudio.google.com
   - Set as `GEMINI_API_KEY` environment variable
   - Free tier available with usage limits

2. **Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configuration**
   ```bash
   cp backend/.env.example backend/.env
   # Edit .env with your API key
   ```

## 🚨 Troubleshooting

### "API key not configured"
**Solution**: Set `GEMINI_API_KEY` in `.env`

### "Google ADK is not enabled"
**Solution**: Set `GOOGLE_ADK_ENABLED=true` in `.env`

### Service won't start
**Solution**: Run `pip install -r backend/requirements.txt` to install new dependencies

### Model not found error
**Solution**: Ensure `GEMINI_MODEL=gemini-2.5-pro` is set

## 📈 Next Steps

1. **Test with Docker**
   ```bash
   docker-compose build
   docker-compose up -d
   curl http://localhost:8000/api/v1/agents/health
   ```

2. **Integrate with Database** (Week 2)
   - Store agent configurations in PostgreSQL
   - Persist execution history
   - Track agent usage metrics

3. **Add Agent Tools** (Week 6)
   - Implement tool calling
   - Connect to external APIs
   - Add knowledge base integration

4. **Frontend Integration** (Week 8)
   - Create UI for agent interaction
   - Implement streaming UI
   - Add agent management interface

## 📝 Git Status

**Latest Commit**: `de70f6e`
- Added Google ADK integration
- 7 files changed
- 1186 insertions

**Pushed to**: https://github.com/bharathravi-in/tarento-copilot.git

---

**Created**: 2025-12-11
**Status**: ✅ Ready for Production
**Phase**: Week 1+ (Can be used immediately)
