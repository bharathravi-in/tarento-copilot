# Phase 1 Week 1 - Backend Setup Instructions

This guide covers setting up the Tarento Enterprise AI Co-Pilot backend for local development.

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

## Quick Start (Docker Compose)

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment Variables

```bash
cd backend
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Start Services with Docker Compose

From the project root:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Qdrant (port 6333)
- FastAPI Backend (port 8000)

### 4. Verify Services

```bash
# Check all containers are running
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test Qdrant
curl http://localhost:6333/health
```

## Manual Setup (Without Docker)

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL

Install PostgreSQL 16 locally and create database:

```bash
createdb tarento_db -U postgres
psql -U postgres -d tarento_db -c "CREATE USER tarento WITH PASSWORD 'tarento_dev';"
psql -U postgres -d tarento_db -c "ALTER DATABASE tarento_db OWNER TO tarento;"
```

### 4. Setup Redis

Install and start Redis:

```bash
redis-server
```

### 5. Setup Qdrant

Download and run Qdrant Docker container:

```bash
docker run -d -p 6333:6333 qdrant/qdrant
```

### 6. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual configuration
```

### 7. Run Backend

```bash
cd backend
python -m app.main
# Or use uvicorn directly
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration management
│   ├── database.py                # SQLAlchemy setup
│   ├── dependencies.py            # Dependency injection
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── router.py          # API v1 routes
│   ├── models/                    # SQLAlchemy ORM models (Week 2)
│   ├── schemas/                   # Pydantic request/response schemas (Week 2)
│   ├── services/                  # Business logic (Week 3+)
│   ├── agents/                    # AI Agent implementations (Week 5+)
│   ├── middleware/                # Custom middleware (Week 3+)
│   └── utils/                     # Utility functions (Week 3+)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
└── main.py                        # Legacy entry point (optional)

root/
├── docker-compose.yml             # Multi-container setup
├── Dockerfile                     # Backend container configuration
└── (frontend files)
```

## Testing the Setup

### 1. Test API Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "app": "Tarento Enterprise AI Co-Pilot"}
```

### 2. Test Root Endpoint

```bash
curl http://localhost:8000/
# Expected: {"message": "Tarento Enterprise AI Co-Pilot", "version": "0.1.0", "status": "running"}
```

### 3. Test Database Connection

Once database models are created (Week 2), you can test with:

```bash
python -c "from app.database import engine; engine.connect()"
```

### 4. Test Redis Connection

```bash
python -c "import redis; r = redis.Redis(); r.ping()"
```

## Next Steps (Week 2)

1. Create SQLAlchemy database models:
   - User, Organization, Project
   - Role, Permission
   - AgentConfig, Conversation, Message
   - Document

2. Initialize Alembic for database migrations:
   ```bash
   alembic init alembic
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

3. Create seed data script for testing

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# For Docker Compose
docker-compose down
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U tarento -d tarento_db -c "SELECT 1"

# Check connection string in .env
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Should respond with PONG
```

## Development Commands

```bash
# Format code
black app/

# Check linting
flake8 app/

# Sort imports
isort app/

# Type checking
mypy app/

# Run tests (Week 4)
pytest

# Run with coverage
pytest --cov=app/
```

## Documentation References

- Full architecture: See `TECHNICAL_ARCHITECTURE.md`
- Implementation guide: See `PHASE_1_IMPLEMENTATION.md`
- API specifications: See `TECHNICAL_ARCHITECTURE.md` (API section)
- Feature specifications: See `FEATURES_AND_CONFIGURATION.md`
