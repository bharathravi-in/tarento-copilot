"""
Pytest configuration and fixtures for testing
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import tempfile
import os
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import (
    Organization, User, Role, Permission, Project, 
    AgentConfig, Conversation, Message, Document
)
from app.utils.security import hash_password
import uuid
from datetime import datetime


# Create in-memory SQLite database for testing
@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Override get_db dependency
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield SessionLocal()
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_org(test_db):
    """Create test organization"""
    org = Organization(
        id=str(uuid.uuid4()),
        name="Test Org",
        description="Test Organization",
        domain="testorg",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org


@pytest.fixture
def test_role(test_db, test_org):
    """Create test role with basic permissions"""
    role = Role(
        id=str(uuid.uuid4()),
        name="Admin",
        description="Administrator role",
        organization_id=test_org.id,
        is_system_role=False,
        role_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(role)
    test_db.commit()
    test_db.refresh(role)
    return role


@pytest.fixture
def test_permissions(test_db, test_org):
    """Create test permissions"""
    permissions = []
    perm_names = [
        "user:create", "user:read", "user:update", "user:delete",
        "project:create", "project:read", "project:update", "project:delete",
        "role:read", "role:update"
    ]
    
    for perm_name in perm_names:
        parts = perm_name.split(":")
        perm = Permission(
            id=str(uuid.uuid4()),
            name=perm_name,
            description=f"Permission to {parts[1]} {parts[0]}",
            resource=parts[0],
            action=parts[1],
            organization_id=test_org.id,
            is_system_permission=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(perm)
        permissions.append(perm)
    
    test_db.commit()
    return permissions


@pytest.fixture
def test_user(test_db, test_org, test_role, test_permissions):
    """Create test user"""
    user = User(
        id=str(uuid.uuid4()),
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("TestPassword123!"),
        full_name="Test User",
        organization_id=test_org.id,
        role_id=test_role.id,
        is_active=True,
        is_superuser=False,
        email_verified=False,
        two_factor_enabled=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(test_db, test_org):
    """Create test admin user"""
    admin_role = Role(
        id=str(uuid.uuid4()),
        name="Admin",
        description="Admin role",
        organization_id=test_org.id,
        is_system_role=False,
        role_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(admin_role)
    test_db.commit()
    
    admin_user = User(
        id=str(uuid.uuid4()),
        email="admin@example.com",
        username="admin",
        hashed_password=hash_password("AdminPassword123!"),
        full_name="Admin User",
        organization_id=test_org.id,
        role_id=admin_role.id,
        is_active=True,
        is_superuser=False,
        email_verified=False,
        two_factor_enabled=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(admin_user)
    test_db.commit()
    test_db.refresh(admin_user)
    return admin_user


@pytest.fixture
def test_project(test_db, test_org, test_user):
    """Create test project"""
    project = Project(
        id=str(uuid.uuid4()),
        name="Test Project",
        description="Test project for testing",
        organization_id=test_org.id,
        created_by=test_user.id,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(project)
    test_db.commit()
    test_db.refresh(project)
    return project


@pytest.fixture
def test_agent_config(test_db, test_org, test_project):
    """Create test agent config"""
    agent = AgentConfig(
        id=str(uuid.uuid4()),
        name="Test Agent",
        description="Test agent config",
        agent_type="test",
        organization_id=test_org.id,
        project_id=test_project.id,
        llm_model="gemini-pro",
        temperature=0.7,
        max_tokens=2000,
        system_prompt=None,
        tools=[],
        knowledge_bases=[],
        parameters={},
        is_active=True,
        is_default=False,
        agent_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(agent)
    test_db.commit()
    test_db.refresh(agent)
    return agent


@pytest.fixture
def test_conversation(test_db, test_user, test_project, test_agent_config):
    """Create test conversation"""
    conv = Conversation(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        project_id=test_project.id,
        agent_config_id=test_agent_config.id,
        title="Test Conversation",
        description="Test conversation for testing",
        is_active=True,
        is_archived=False,
        message_count=0,
        context={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(conv)
    test_db.commit()
    test_db.refresh(conv)
    return conv


@pytest.fixture
def test_document(test_db, test_org):
    """Create test document"""
    doc = Document(
        id=str(uuid.uuid4()),
        title="Test Document",
        description="Test document for testing",
        document_type="pdf",
        organization_id=test_org.id,
        file_name="test.pdf",
        file_size=1024,
        mime_type="application/pdf",
        content="This is test content",
        summary="Test summary",
        is_active=True,
        is_public=False,
        processing_status="completed",
        is_indexed=False,
        vector_ids=[],
        embedding_model="text-embedding-3-small",
        tags=["test"],
        doc_metadata={},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_db.add(doc)
    test_db.commit()
    test_db.refresh(doc)
    return doc


# Aliases for fixtures to match test file naming conventions
@pytest.fixture
def agent_config(test_agent_config):
    """Alias for test_agent_config"""
    return test_agent_config


@pytest.fixture
def conversation(test_conversation):
    """Alias for test_conversation"""
    return test_conversation


@pytest.fixture
def document(test_document):
    """Alias for test_document"""
    return test_document


@pytest.fixture
def client(test_db):
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123!"
        }
    )
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(client, test_admin_user):
    """Get auth headers for admin user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_admin_user.username,
            "password": "AdminPassword123!"
        }
    )
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
