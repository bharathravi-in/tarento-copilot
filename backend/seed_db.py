"""
Seed data script for development and testing
Populates the database with initial test data
"""

import uuid
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import (
    Organization,
    User,
    Role,
    Permission,
    Project,
    AgentConfig,
)
from app.utils.security import hash_password


def seed_database():
    """Populate the database with test data"""
    
    # Create database engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Organization).count() > 0:
            print("Database already seeded. Skipping...")
            return
        
        print("Starting database seeding...")
        
        # 1. Create Organizations
        print("Creating organizations...")
        org1 = Organization(
            id=str(uuid.uuid4()),
            name="Acme Corporation",
            domain="acme.com",
            description="Leading enterprise solutions provider",
            logo_url="https://via.placeholder.com/200",
            subscription_plan="enterprise",
            is_active=True,
            settings={
                "theme": "dark",
                "locale": "en-US",
                "timezone": "UTC"
            },
            metadata={"industry": "Technology", "employees": 5000},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        org2 = Organization(
            id=str(uuid.uuid4()),
            name="StartUp Inc",
            domain="startup.io",
            description="Innovative startup focused on AI solutions",
            logo_url="https://via.placeholder.com/200",
            subscription_plan="professional",
            is_active=True,
            settings={
                "theme": "light",
                "locale": "en-US",
                "timezone": "EST"
            },
            metadata={"industry": "AI/ML", "employees": 50},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(org1)
        db.add(org2)
        db.commit()
        print(f"✓ Created 2 organizations")
        
        # 2. Create Permissions
        print("Creating permissions...")
        permissions_data = [
            {"resource": "users", "action": "create", "name": "Create Users"},
            {"resource": "users", "action": "read", "name": "Read Users"},
            {"resource": "users", "action": "update", "name": "Update Users"},
            {"resource": "users", "action": "delete", "name": "Delete Users"},
            {"resource": "projects", "action": "create", "name": "Create Projects"},
            {"resource": "projects", "action": "read", "name": "Read Projects"},
            {"resource": "projects", "action": "update", "name": "Update Projects"},
            {"resource": "projects", "action": "delete", "name": "Delete Projects"},
            {"resource": "agents", "action": "create", "name": "Create Agents"},
            {"resource": "agents", "action": "execute", "name": "Execute Agents"},
            {"resource": "agents", "action": "manage", "name": "Manage Agents"},
            {"resource": "documents", "action": "upload", "name": "Upload Documents"},
            {"resource": "documents", "action": "delete", "name": "Delete Documents"},
        ]
        
        permissions = []
        for perm_data in permissions_data:
            perm = Permission(
                id=str(uuid.uuid4()),
                name=perm_data["name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                description=f"Permission to {perm_data['action']} {perm_data['resource']}",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            permissions.append(perm)
            db.add(perm)
        
        db.commit()
        print(f"✓ Created {len(permissions)} permissions")
        
        # 3. Create Roles for each organization
        print("Creating roles...")
        
        # Admin role
        admin_role_1 = Role(
            id=str(uuid.uuid4()),
            name="Admin",
            organization_id=org1.id,
            description="Administrator with full access",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        admin_role_1.permissions = permissions  # Grant all permissions
        
        # Member role
        member_role_1 = Role(
            id=str(uuid.uuid4()),
            name="Member",
            organization_id=org1.id,
            description="Regular member with limited access",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        member_role_1.permissions = permissions[:6]  # Grant read/create permissions
        
        # Admin role for org2
        admin_role_2 = Role(
            id=str(uuid.uuid4()),
            name="Admin",
            organization_id=org2.id,
            description="Administrator with full access",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        admin_role_2.permissions = permissions
        
        db.add(admin_role_1)
        db.add(member_role_1)
        db.add(admin_role_2)
        db.commit()
        print(f"✓ Created roles")
        
        # 4. Create Users
        print("Creating users...")
        
        user1 = User(
            id=str(uuid.uuid4()),
            email="admin@acme.com",
            username="admin_acme",
            password_hash=hash_password("SecurePassword123!"),
            full_name="Alice Administrator",
            organization_id=org1.id,
            role_id=admin_role_1.id,
            is_active=True,
            email_verified=True,
            two_factor_enabled=False,
            avatar_url="https://via.placeholder.com/150",
            bio="Enterprise administrator",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        user2 = User(
            id=str(uuid.uuid4()),
            email="member@acme.com",
            username="member_acme",
            password_hash=hash_password("SecurePassword123!"),
            full_name="Bob Member",
            organization_id=org1.id,
            role_id=member_role_1.id,
            is_active=True,
            email_verified=True,
            two_factor_enabled=False,
            avatar_url="https://via.placeholder.com/150",
            bio="Team member",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        user3 = User(
            id=str(uuid.uuid4()),
            email="admin@startup.io",
            username="admin_startup",
            password_hash=hash_password("SecurePassword123!"),
            full_name="Charlie Startup",
            organization_id=org2.id,
            role_id=admin_role_2.id,
            is_active=True,
            email_verified=True,
            two_factor_enabled=False,
            avatar_url="https://via.placeholder.com/150",
            bio="Startup founder",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user1)
        db.add(user2)
        db.add(user3)
        db.commit()
        print(f"✓ Created 3 users")
        
        # 5. Create Projects
        print("Creating projects...")
        
        project1 = Project(
            id=str(uuid.uuid4()),
            name="AI Assistant Platform",
            description="Internal AI assistant for document analysis",
            organization_id=org1.id,
            created_by=user1.id,
            is_active=True,
            settings={
                "max_agents": 10,
                "max_documents": 1000,
                "api_rate_limit": 1000
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        project2 = Project(
            id=str(uuid.uuid4()),
            name="Customer Support Bot",
            description="AI-powered customer support chatbot",
            organization_id=org2.id,
            created_by=user3.id,
            is_active=True,
            settings={
                "max_agents": 5,
                "max_documents": 500,
                "api_rate_limit": 500
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Add users to projects
        project1.users.append(user1)
        project1.users.append(user2)
        project2.users.append(user3)
        
        db.add(project1)
        db.add(project2)
        db.commit()
        print(f"✓ Created 2 projects")
        
        # 6. Create Agent Configs
        print("Creating agent configurations...")
        
        agent_config1 = AgentConfig(
            id=str(uuid.uuid4()),
            name="Document Analyzer",
            description="Analyzes and extracts information from documents",
            project_id=project1.id,
            agent_type="document_analyzer",
            llm_config={
                "model": "gemini-2.5-pro",
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9
            },
            tools_config=[
                {"name": "document_parser", "enabled": True},
                {"name": "text_extractor", "enabled": True},
                {"name": "entity_recognizer", "enabled": True}
            ],
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        agent_config2 = AgentConfig(
            id=str(uuid.uuid4()),
            name="Chat Support Agent",
            description="Handles customer inquiries and provides support",
            project_id=project2.id,
            agent_type="chat_agent",
            llm_config={
                "model": "gemini-2.5-pro",
                "temperature": 0.5,
                "max_tokens": 1024,
                "top_p": 0.9
            },
            tools_config=[
                {"name": "knowledge_base_search", "enabled": True},
                {"name": "ticket_system", "enabled": True},
                {"name": "email_sender", "enabled": False}
            ],
            is_active=True,
            version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(agent_config1)
        db.add(agent_config2)
        db.commit()
        print(f"✓ Created 2 agent configurations")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\nTest Credentials:")
        print(f"  Organization 1: acme.com")
        print(f"    - Email: admin@acme.com, Password: SecurePassword123!")
        print(f"    - Email: member@acme.com, Password: SecurePassword123!")
        print(f"  Organization 2: startup.io")
        print(f"    - Email: admin@startup.io, Password: SecurePassword123!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
