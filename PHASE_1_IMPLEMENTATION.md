# Phase 1 Implementation Guide - Foundation & Infrastructure

**Project:** Tarento Enterprise AI Co-Pilot  
**Phase:** Phase 1 (Weeks 1-4)  
**Status:** Implementation Ready  
**Date:** December 7, 2025

---

## Overview

Phase 1 establishes the foundational infrastructure for the entire platform. This phase includes:
1. Project setup and scaffolding
2. Database schema design and initialization
3. Authentication and authorization framework
4. Core backend setup with FastAPI
5. Core frontend setup with React
6. Development environment configuration

---

## Week 1: Project Setup & Architecture

### 1.1 Repository Structure Setup

#### Step 1: Create Project Directories

```bash
# From workspace root
mkdir -p backend frontend
cd backend

# Backend structure
mkdir -p app/{api/v1,models,schemas,services,agents,utils,middleware}
mkdir -p tests/{unit,integration,e2e}
mkdir -p migrations/alembic/versions
mkdir docker

touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/dependencies.py
touch requirements.txt
touch .env.example
touch .gitignore
touch docker/Dockerfile

# Go back to root
cd ..
cd frontend

# Frontend structure already handled by Vite, but we need to organize src/
# Structure will be created after npm init

cd ..
```

### 1.2 Backend Dependencies

#### Create `backend/requirements.txt`:

```
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
PyJWT==2.8.1

# LLM & AI
google-generativeai==0.3.0
google-ai-generativelanguage==0.4.0

# Vector Database
qdrant-client==2.7.1

# Caching & Session
redis==5.0.1

# Async & Background Tasks
celery==5.3.4
redis==5.0.1

# Data Processing
numpy==1.24.3
pandas==2.1.3
python-docx==0.8.11
PyPDF2==3.0.1

# Utilities
python-dotenv==1.0.0
requests==2.31.0
httpx==0.25.1

# Telemetry & Monitoring
opik==0.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1

# Development
black==23.12.0
flake8==6.1.0
isort==5.13.2
mypy==1.7.1

# CORS
fastapi-cors==0.0.6

# Logging
python-json-logger==2.0.7
```

### 1.3 Frontend Setup

#### Initialize Frontend with Vite:

```bash
cd frontend

# Create necessary directories
mkdir -p src/{components/{common,auth,dashboard,agents,admin,projects},pages,services,hooks,store,types,styles,utils,assets}

# Install core dependencies
npm install axios react-router-dom @reduxjs/toolkit react-redux
npm install @mui/material @emotion/react @emotion/styled
npm install date-fns lodash clsx classnames

# Install development dependencies
npm install -D @types/react-dom @types/node @types/lodash
npm install -D typescript ts-node

# Create env file
cp .env.example .env
```

#### Create `frontend/.env.example`:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_NAME=Tarento Enterprise AI
VITE_APP_VERSION=1.0.0
```

### 1.4 Docker Setup

#### Create `backend/docker/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start app
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

#### Create `docker-compose.yml` (root):

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: tarento
      POSTGRES_PASSWORD: tarento_dev
      POSTGRES_DB: tarento_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tarento"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: docker/Dockerfile
    environment:
      DATABASE_URL: postgresql://tarento:tarento_dev@postgres:5432/tarento_db
      REDIS_URL: redis://redis:6379
      QDRANT_URL: http://qdrant:6333
      ENVIRONMENT: development
      DEBUG: "true"
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      VITE_API_BASE_URL: http://localhost:8000
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
```

---

## Week 2: Database Schema & ORM Setup

### 2.1 Database Configuration

#### Create `backend/app/config.py`:

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://tarento:tarento_dev@localhost:5432/tarento_db"
    )
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Qdrant
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    
    # LLM
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = "gemini-2.5-pro"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # App
    app_name: str = "Tarento Enterprise AI"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

#### Create `backend/app/database.py`:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import settings

# Synchronous engine for migrations
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2.2 SQLAlchemy Models

#### Create `backend/app/models/__init__.py`:

```python
from .user import User
from .organization import Organization
from .project import Project
from .role import Role
from .permission import Permission
from .agent_config import AgentConfig
from .conversation import Conversation
from .message import Message
from .document import Document

__all__ = [
    "User",
    "Organization",
    "Project",
    "Role",
    "Permission",
    "AgentConfig",
    "Conversation",
    "Message",
    "Document",
]
```

#### Create `backend/app/models/base.py`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Create `backend/app/models/organization.py`:

```python
from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel

class Organization(BaseModel):
    __tablename__ = "organizations"
    
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, nullable=True)
    logo_url = Column(String(500), nullable=True)
    subscription_plan = Column(String(50), default="starter")
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    
    # Relationships
    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")
    roles = relationship("Role", back_populates="organization")
    agent_configs = relationship("AgentConfig", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
```

#### Create `backend/app/models/user.py`:

```python
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    role = relationship("Role", back_populates="users")
    conversations = relationship("Conversation", back_populates="user")
    projects = relationship("Project", secondary="project_users", back_populates="members")
```

#### Create `backend/app/models/project.py`:

```python
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from .base import BaseModel

# Association table for project members
project_users = Table(
    'project_users',
    BaseModel.registry.metadata,
    Column('project_id', String(36), ForeignKey('projects.id')),
    Column('user_id', String(36), ForeignKey('users.id'))
)

class Project(BaseModel):
    __tablename__ = "projects"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    
    # Relationships
    organization = relationship("Organization", back_populates="projects")
    creator = relationship("User", foreign_keys=[created_by])
    members = relationship("User", secondary=project_users, back_populates="projects")
    conversations = relationship("Conversation", back_populates="project")
    agent_configs = relationship("AgentConfig", back_populates="project")
```

#### Create `backend/app/models/role.py`:

```python
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Role(BaseModel):
    __tablename__ = "roles"
    
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    
    permissions = Column(JSON, default={})
    
    # Relationships
    organization = relationship("Organization", back_populates="roles")
    users = relationship("User", back_populates="role")
```

#### Create `backend/app/models/agent_config.py`:

```python
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class AgentConfig(BaseModel):
    __tablename__ = "agent_configs"
    
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # rfp, jira, documentation, hr, finance
    
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    
    llm_model = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=True)
    parameters = Column(JSON, default={})
    knowledge_bases = Column(JSON, default={})
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="agent_configs")
    project = relationship("Project", back_populates="agent_configs")
```

#### Create `backend/app/models/conversation.py`:

```python
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Conversation(BaseModel):
    __tablename__ = "conversations"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    
    title = Column(String(255), nullable=True)
    agent_id = Column(String(50), nullable=True)
    agent_type = Column(String(50), nullable=True)
    
    metadata = Column(JSON, default={})
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    project = relationship("Project", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
```

#### Create `backend/app/models/message.py`:

```python
from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"
    
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False)
    
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, form, result
    
    metadata = Column(JSON, default={})
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
```

#### Create `backend/app/models/document.py`:

```python
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel

class Document(BaseModel):
    __tablename__ = "documents"
    
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    document_type = Column(String(50), nullable=False)  # pdf, docx, txt
    
    agent_id = Column(String(50), nullable=True)
    content_hash = Column(String(255), nullable=True)
    chunks_count = Column(Integer, default=0)
    
    is_indexed = Column(Boolean, default=False)
    metadata = Column(JSON, default={})
    
    # Relationships
    organization = relationship("Organization", back_populates="documents")
```

### 2.3 Alembic Migrations Setup

#### Initialize Alembic:

```bash
cd backend
alembic init migrations
```

#### Update `backend/migrations/env.py`:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.config import settings
from app.database import Base
import os

# Import all models
from app.models import *

config = context.config

# Set sqlalchemy.url
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### Create initial migration:

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

---

## Week 3: Authentication & Authorization

### 3.1 Security Utilities

#### Create `backend/app/utils/security.py`:

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
```

#### Create `backend/app/schemas/user.py`:

```python
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: str
    organization_id: str
    role_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse
```

### 3.2 Authentication Service

#### Create `backend/app/services/auth_service.py`:

```python
from typing import Optional
from sqlalchemy.orm import Session
from app.models import User, Organization, Role
from app.schemas.user import UserCreate, LoginRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.config import settings
from datetime import timedelta
from fastapi import HTTPException, status

class AuthService:
    @staticmethod
    def register_user(db: Session, user_create: UserCreate, organization_id: str) -> User:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_create.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Get default role for organization
        default_role = db.query(Role).filter(
            Role.organization_id == organization_id,
            Role.name == "user"
        ).first()
        
        if not default_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization not configured properly"
            )
        
        # Create new user
        user = User(
            email=user_create.email,
            username=user_create.username,
            password_hash=hash_password(user_create.password),
            full_name=user_create.full_name,
            organization_id=organization_id,
            role_id=default_role.id
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, login: LoginRequest) -> Optional[User]:
        user = db.query(User).filter(User.email == login.email).first()
        if not user or not verify_password(login.password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
```

### 3.3 API Endpoints

#### Create `backend/app/api/v1/auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, LoginRequest, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.models import User
from app.utils.security import decode_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Get default organization (for now, first one)
    from app.models import Organization
    org = db.query(Organization).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No organization found"
        )
    
    return AuthService.register_user(db, user, org.id)

@router.post("/login", response_model=dict)
def login(login: LoginRequest, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    tokens = AuthService.create_tokens(user)
    return {
        **tokens,
        "user": UserResponse.from_orm(user)
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out successfully"}
```

### 3.4 Dependencies & Middleware

#### Create `backend/app/dependencies.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils.security import decode_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

---

## Week 4: FastAPI Setup & Basic Endpoints

### 4.1 Main Application

#### Create `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.v1 import auth
from app.database import Base, engine
import logging

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Tarento Enterprise AI Co-Pilot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4.2 Seed Data Script

#### Create `backend/seed_data.py`:

```python
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Organization, Role, User
from app.utils.security import hash_password
import uuid

def create_initial_data():
    """Create initial organizations, roles, and admin user"""
    db = SessionLocal()
    
    try:
        # Create organization
        org_id = str(uuid.uuid4())
        org = Organization(
            id=org_id,
            name="Tarento",
            domain="tarento.io",
            subscription_plan="enterprise"
        )
        db.add(org)
        db.commit()
        
        # Create roles
        admin_role = Role(
            id=str(uuid.uuid4()),
            name="admin",
            organization_id=org_id,
            description="Administrator with full access",
            permissions={
                "users.manage": True,
                "agents.manage": True,
                "config.manage": True,
                "organization.manage": True
            }
        )
        
        user_role = Role(
            id=str(uuid.uuid4()),
            name="user",
            organization_id=org_id,
            description="Regular user with agent access",
            permissions={
                "agents.execute": True,
                "conversations.view": True,
                "conversations.create": True
            }
        )
        
        db.add_all([admin_role, user_role])
        db.commit()
        
        # Create admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            email="admin@tarento.io",
            username="admin",
            password_hash=hash_password("admin@123"),
            full_name="Admin User",
            organization_id=org_id,
            role_id=admin_role.id,
            is_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        
        print("✓ Initial data created successfully")
        print(f"  Organization: {org.name}")
        print(f"  Admin Email: {admin_user.email}")
        print(f"  Admin Password: admin@123")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error creating initial data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()
```

### 4.3 Frontend Basic Setup

#### Create `frontend/src/main.tsx`:

```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { Provider } from 'react-redux'
import store from './store/store'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>,
)
```

#### Create `frontend/src/App.tsx`:

```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import theme from './styles/theme'
import LoginPage from './pages/Login'
import DashboardPage from './pages/Dashboard'
import ProtectedRoute from './components/auth/ProtectedRoute'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
```

#### Create `frontend/src/store/store.ts`:

```typescript
import { configureStore } from '@reduxjs/toolkit'
import authSlice from './authSlice'
import uiSlice from './uiSlice'

const store = configureStore({
  reducer: {
    auth: authSlice,
    ui: uiSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store
```

---

## Phase 1 Checklist

### Week 1: Project Setup
- [ ] Create backend and frontend directory structure
- [ ] Setup Python virtual environment and install dependencies
- [ ] Setup Node.js dependencies and Vite configuration
- [ ] Create Docker and docker-compose configuration
- [ ] Setup .env files for both backend and frontend
- [ ] Initialize Git repository with .gitignore

### Week 2: Database
- [ ] Setup PostgreSQL database configuration
- [ ] Create all SQLAlchemy models (User, Organization, Project, etc.)
- [ ] Setup Alembic migration system
- [ ] Create and test initial database migration
- [ ] Create seed data script

### Week 3: Authentication
- [ ] Implement JWT token generation and validation
- [ ] Create password hashing utilities
- [ ] Implement registration endpoint
- [ ] Implement login endpoint
- [ ] Create authentication middleware

### Week 4: FastAPI & Frontend Basics
- [ ] Create main FastAPI application
- [ ] Configure CORS and middleware
- [ ] Create health check endpoint
- [ ] Setup Redux store with auth slice
- [ ] Create basic login and dashboard pages
- [ ] Setup React routing

### Testing
- [ ] Test database connections
- [ ] Test API endpoints with Postman/Insomnia
- [ ] Test authentication flow
- [ ] Test Docker compose setup

---

## Commands to Run

### Local Development Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
python seed_data.py
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev

# Or with Docker
docker-compose up
```

---

## Key Decisions Made

1. **Database**: PostgreSQL for relational data with SQLAlchemy ORM
2. **Authentication**: JWT-based with refresh tokens
3. **Architecture**: Service-based architecture for scalability
4. **Frontend State**: Redux for centralized state management
5. **API Design**: RESTful API with FastAPI
6. **Containerization**: Docker for consistent development environment

---

## Next Phase Preview

Phase 2 (Weeks 5-7) will focus on:
- Complete user management system
- Organization and project management
- RBAC (Role-Based Access Control)
- Admin dashboard basics

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Ready for Implementation
