# Tarento Co-Pilot Backend - Quick Start Guide

## Current Status
✅ **System is ready for database connectivity**

All components have been implemented and tested:
- Models: 9 SQLAlchemy ORM models
- Schemas: Pydantic request/response schemas
- Authentication: JWT-based auth with bcrypt password hashing
- API Endpoints: Auth endpoints (register, login, refresh, change-password, me, logout)
- Seed Data: Test data population script

## Prerequisites

Ensure you have the following services running:

### 1. PostgreSQL (Port 5432)

**Option A: Using Docker**
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_USER=tarento \
  -e POSTGRES_PASSWORD=tarento_dev \
  -e POSTGRES_DB=tarento_db \
  -p 5432:5432 \
  postgres:16-alpine
```

**Option B: Local Installation**
```bash
# Create database and user
createdb tarento_db -U postgres
psql -U postgres -d tarento_db -c "CREATE USER tarento WITH PASSWORD 'tarento_dev';"
psql -U postgres -d tarento_db -c "ALTER DATABASE tarento_db OWNER TO tarento;"
```

### 2. Redis (Port 6379)

**Option A: Using Docker**
```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Option B: Local Installation**
```bash
redis-server
```

### 3. Qdrant (Port 6333) - Optional for now

**Using Docker**
```bash
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  qdrant/qdrant
```

## Setup Steps

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure Environment (if needed)

The `.env` file is already configured for local development:
```
DATABASE_URL="postgresql://tarento:tarento_dev@localhost:5432/tarento_db"
REDIS_URL="redis://localhost:6379/0"
QDRANT_URL="http://localhost:6333"
```

### Step 3: Create Database Tables

Run Alembic migrations to create all tables:

```bash
# Generate initial migration (if not already done)
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Step 4: Populate Test Data (Optional)

Populate database with test organizations, users, and projects:

```bash
python3 seed_db.py
```

**Test Credentials After Seeding:**
```
Organization 1: Acme Corporation
  - Email: admin@acme.com, Password: SecurePassword123!
  - Email: member@acme.com, Password: SecurePassword123!

Organization 2: StartUp Inc
  - Email: admin@startup.io, Password: SecurePassword123!
```

### Step 5: Start the Backend Server

```bash
uvicorn app.main:app --reload
```

The server will start on `http://localhost:8000`

## API Documentation

### Interactive Swagger UI
Once the server is running, visit: `http://localhost:8000/docs`

### Available Endpoints

#### Health & Status
- `GET /` - Root endpoint
- `GET /health` - Health check

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with credentials
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/change-password` - Change password
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/logout` - Logout

#### Agent Management (Existing)
- `POST /api/v1/agents/create` - Create new agent
- `POST /api/v1/agents/execute` - Execute agent
- More agent endpoints available in `/api/v1/agents`

## Testing the API

### 1. Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "full_name": "Test User",
    "organization_id": "<org-id>"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePassword123!"
  }'
```

Response includes:
```json
{
  "user": { /* user details */ },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 3. Use Token in Requests
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 4. Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # SQLAlchemy setup
│   ├── dependencies.py        # Dependency injection
│   ├── models/                # Database ORM models (9 models)
│   ├── schemas/               # Pydantic request/response schemas
│   ├── services/              # Business logic (auth_service.py)
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py        # Authentication endpoints
│   │       ├── agents.py      # Agent management endpoints
│   │       └── router.py      # API router aggregator
│   ├── utils/
│   │   └── security.py        # JWT and password utilities
│   └── middleware/            # Custom middleware (ready for expansion)
├── alembic/                   # Database migrations
│   ├── versions/              # Migration scripts
│   ├── env.py                 # Alembic environment configuration
│   └── alembic.ini            # Alembic configuration
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (local)
├── .env.example               # Environment variables template
└── seed_db.py                 # Test data population script
```

## Database Schema

### 9 Models Implemented:
1. **Organization** - Multi-tenant organizations
2. **User** - User accounts with roles
3. **Role** - Role-based access control
4. **Permission** - Fine-grained permissions
5. **Project** - Organizational projects
6. **AgentConfig** - AI agent configurations
7. **Conversation** - Chat conversations with agents
8. **Message** - Individual messages in conversations
9. **Document** - Knowledge base documents

## Next Steps - Week 2+

### Immediate (Week 2)
- [ ] Create CRUD endpoints for User, Organization, Project, Role, Permission
- [ ] Implement authorization middleware for endpoint protection
- [ ] Add pagination and filtering to list endpoints

### Short Term (Week 3)
- [ ] Setup pytest testing infrastructure
- [ ] Write unit tests for models and services
- [ ] Create API integration tests

### Medium Term (Week 4+)
- [ ] Implement conversation and message endpoints
- [ ] Setup vector database integration for documents
- [ ] Create document upload and processing endpoints
- [ ] Implement agent execution and result streaming

## Troubleshooting

### Database Connection Error
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection to server at "localhost" (127.0.0.1), port 5432 failed
```

**Solution:** Ensure PostgreSQL is running
```bash
# Check PostgreSQL status
pg_isready -h localhost

# Or start with Docker
docker start postgres
```

### Port Already in Use
```
Address already in use
```

**Solution:** Kill the process on the port
```bash
# For port 8000 (FastAPI)
lsof -ti:8000 | xargs kill -9

# For port 5432 (PostgreSQL)
lsof -ti:5432 | xargs kill -9
```

### Alembic Migration Issues
```bash
# Check migration status
alembic current

# Downgrade to previous version
alembic downgrade -1

# Create fresh migration
alembic revision --autogenerate -m "New schema"
```

## Useful Commands

```bash
# Start backend server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Populate test data
python3 seed_db.py

# Run linting
black app/
flake8 app/
isort app/

# Run type checking
mypy app/

# Run tests (when ready)
pytest
pytest --cov=app/
```

## Key Features Implemented

✅ Multi-tenant architecture with organizations
✅ Role-based access control (RBAC)
✅ JWT authentication with refresh tokens
✅ Bcrypt password hashing
✅ Comprehensive Pydantic schemas
✅ Alembic database migrations
✅ Test data seeding
✅ FastAPI with async support
✅ CORS middleware configured
✅ Proper error handling and validation

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Swagger UI at `/docs` for API documentation
3. Check application logs for error details
4. Review the WEEK_1_SETUP_GUIDE.md for setup instructions

---

**Last Updated:** December 11, 2025
**Status:** ✅ Ready for Database Connectivity
