"""
CRUD endpoint tests
"""

import pytest
from fastapi import status


class TestUsers:
    """User CRUD endpoint tests"""
    
    def test_list_users(self, client, auth_headers, test_user):
        """Test listing users"""
        response = client.get(
            "/api/v1/users/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert data["total"] >= 1
    
    def test_list_users_with_pagination(self, client, auth_headers):
        """Test listing users with pagination"""
        response = client.get(
            "/api/v1/users/?skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 5
    
    def test_get_user_by_id(self, client, auth_headers, test_user):
        """Test getting user by ID"""
        response = client.get(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
    
    def test_get_nonexistent_user(self, client, auth_headers):
        """Test getting non-existent user"""
        response = client.get(
            "/api/v1/users/nonexistent-id",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_user_as_admin(self, client, admin_auth_headers):
        """Test creating user as admin"""
        response = client.post(
            "/api/v1/users/",
            headers=admin_auth_headers,
            json={
                "email": "createduser@example.com",
                "username": "createduser",
                "password": "Password123!",
                "full_name": "Created User"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["username"] == "createduser"
        assert data["email"] == "createduser@example.com"
    
    def test_create_user_as_regular_user_fails(self, client, auth_headers):
        """Test creating user as regular user fails"""
        response = client.post(
            "/api/v1/users/",
            headers=auth_headers,
            json={
                "email": "failuser@example.com",
                "username": "failuser",
                "password": "Password123!",
                "full_name": "Fail User"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_own_user(self, client, auth_headers, test_user):
        """Test updating own user profile"""
        response = client.put(
            f"/api/v1/users/{test_user.id}",
            headers=auth_headers,
            json={
                "full_name": "Updated User Name"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Updated User Name"
    
    def test_delete_user_as_admin(self, client, admin_auth_headers, test_user):
        """Test deleting user as admin"""
        response = client.delete(
            f"/api/v1/users/{test_user.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestAgentConfigs:
    """Agent config CRUD endpoint tests"""
    
    def test_list_agent_configs(self, client, auth_headers, test_agent_config):
        """Test listing agent configs"""
        response = client.get(
            "/api/v1/agent-configs/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_agent_config(self, client, auth_headers, test_agent_config):
        """Test getting agent config by ID"""
        response = client.get(
            f"/api/v1/agent-configs/{test_agent_config.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_agent_config.id
        assert data["name"] == test_agent_config.name
    
    def test_create_agent_config_as_admin(self, client, admin_auth_headers, test_project):
        """Test creating agent config as admin"""
        response = client.post(
            "/api/v1/agent-configs/",
            headers=admin_auth_headers,
            json={
                "name": "New Agent",
                "description": "New test agent",
                "agent_type": "test",
                "project_id": test_project.id,
                "llm_model": "gemini-pro",
                "temperature": 0.8,
                "max_tokens": 3000
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["name"] == "New Agent"
    
    def test_create_agent_config_as_regular_user_fails(self, client, auth_headers):
        """Test creating agent config as regular user fails"""
        response = client.post(
            "/api/v1/agent-configs/",
            headers=auth_headers,
            json={
                "name": "Unauthorized Agent",
                "agent_type": "test",
                "llm_model": "gemini-pro"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConversations:
    """Conversation CRUD endpoint tests"""
    
    def test_list_conversations(self, client, auth_headers, test_conversation):
        """Test listing conversations"""
        response = client.get(
            "/api/v1/conversations/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_get_conversation(self, client, auth_headers, test_conversation):
        """Test getting conversation by ID"""
        response = client.get(
            f"/api/v1/conversations/{test_conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_conversation.id
    
    def test_create_conversation(self, client, auth_headers, test_project):
        """Test creating conversation"""
        response = client.post(
            "/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "New Conversation",
                "description": "Test conversation",
                "project_id": test_project.id
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["title"] == "New Conversation"
    
    def test_add_message_to_conversation(self, client, auth_headers, test_conversation):
        """Test adding message to conversation"""
        response = client.post(
            f"/api/v1/conversations/{test_conversation.id}/messages/",
            headers=auth_headers,
            json={
                "content": "Test message",
                "role": "user"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["content"] == "Test message"
        assert data["role"] == "user"
    
    def test_list_conversation_messages(self, client, auth_headers, test_conversation):
        """Test listing messages in conversation"""
        # First add a message
        client.post(
            f"/api/v1/conversations/{test_conversation.id}/messages/",
            headers=auth_headers,
            json={
                "content": "Test message",
                "role": "user"
            }
        )
        
        # Then list messages
        response = client.get(
            f"/api/v1/conversations/{test_conversation.id}/messages/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data


class TestProjects:
    """Project CRUD endpoint tests"""
    
    def test_list_projects(self, client, auth_headers, test_project):
        """Test listing projects"""
        response = client.get(
            "/api/v1/projects/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 1
    
    def test_get_project(self, client, auth_headers, test_project):
        """Test getting project by ID"""
        response = client.get(
            f"/api/v1/projects/{test_project.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_project.id
        assert data["name"] == test_project.name
    
    def test_create_project(self, client, auth_headers):
        """Test creating project"""
        response = client.post(
            "/api/v1/projects/",
            headers=auth_headers,
            json={
                "name": "New Project",
                "description": "Test project"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["name"] == "New Project"
