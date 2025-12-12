"""
Tests for Agent Configs, Conversations, and Documents endpoints
"""

import pytest
from fastapi import status


class TestAgentConfigs:
    """Agent Config CRUD endpoint tests"""
    
    def test_list_agent_configs(self, client, auth_headers):
        """Test listing agent configs"""
        response = client.get(
            "/api/v1/agent-configs/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_list_agent_configs_with_filters(self, client, auth_headers):
        """Test listing agent configs with filters"""
        response = client.get(
            "/api/v1/agent-configs/?agent_type=rfp&skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["limit"] == 5
    
    def test_create_agent_config(self, client, admin_auth_headers):
        """Test creating agent config"""
        response = client.post(
            "/api/v1/agent-configs/",
            headers=admin_auth_headers,
            json={
                "name": "Test RFP Agent",
                "description": "Agent for RFP processing",
                "agent_type": "rfp",
                "llm_model": "gemini-2.5-pro",
                "system_prompt": "You are an RFP processing agent"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["name"] == "Test RFP Agent"
        assert data["agent_type"] == "rfp"
    
    def test_create_agent_config_as_regular_user_fails(self, client, auth_headers):
        """Test creating agent config as regular user fails"""
        response = client.post(
            "/api/v1/agent-configs/",
            headers=auth_headers,
            json={
                "name": "Test Agent",
                "description": "Test",
                "agent_type": "rfp"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_agent_config(self, client, auth_headers, agent_config):
        """Test getting agent config by ID"""
        response = client.get(
            f"/api/v1/agent-configs/{agent_config.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == agent_config.id
        assert data["name"] == agent_config.name
    
    def test_update_agent_config(self, client, admin_auth_headers, agent_config):
        """Test updating agent config"""
        response = client.put(
            f"/api/v1/agent-configs/{agent_config.id}",
            headers=admin_auth_headers,
            json={
                "description": "Updated description"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated description"
    
    def test_delete_agent_config(self, client, admin_auth_headers, agent_config):
        """Test deleting agent config"""
        response = client.delete(
            f"/api/v1/agent-configs/{agent_config.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK


class TestConversations:
    """Conversation CRUD endpoint tests"""
    
    def test_list_conversations(self, client, auth_headers):
        """Test listing conversations"""
        response = client.get(
            "/api/v1/conversations/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_create_conversation(self, client, auth_headers):
        """Test creating conversation"""
        response = client.post(
            "/api/v1/conversations/",
            headers=auth_headers,
            json={
                "title": "Test Conversation",
                "description": "A test conversation"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["title"] == "Test Conversation"
    
    def test_get_conversation(self, client, auth_headers, conversation):
        """Test getting conversation by ID"""
        response = client.get(
            f"/api/v1/conversations/{conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == conversation.id
    
    def test_update_conversation(self, client, auth_headers, conversation):
        """Test updating conversation"""
        response = client.put(
            f"/api/v1/conversations/{conversation.id}",
            headers=auth_headers,
            json={
                "title": "Updated Conversation"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Conversation"
    
    def test_delete_conversation(self, client, auth_headers, conversation):
        """Test deleting conversation"""
        response = client.delete(
            f"/api/v1/conversations/{conversation.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_archive_conversation(self, client, auth_headers, conversation):
        """Test archiving conversation"""
        response = client.post(
            f"/api/v1/conversations/{conversation.id}/archive",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_add_message_to_conversation(self, client, auth_headers, conversation):
        """Test adding message to conversation"""
        response = client.post(
            f"/api/v1/conversations/{conversation.id}/messages",
            headers=auth_headers,
            json={
                "content": "Hello, this is a test message"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]


class TestDocuments:
    """Document CRUD endpoint tests"""
    
    def test_list_documents(self, client, auth_headers):
        """Test listing documents"""
        response = client.get(
            "/api/v1/documents/",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "total" in data
    
    def test_list_documents_with_filters(self, client, auth_headers):
        """Test listing documents with filters"""
        response = client.get(
            "/api/v1/documents/?document_type=pdf&skip=0&limit=5",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["limit"] == 5
    
    def test_create_document(self, client, admin_auth_headers):
        """Test creating document"""
        response = client.post(
            "/api/v1/documents/",
            headers=admin_auth_headers,
            json={
                "title": "Test Document",
                "description": "A test document",
                "document_type": "pdf",
                "content": "This is test content"
            }
        )
        assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_200_OK]
        data = response.json()
        assert data["title"] == "Test Document"
    
    def test_create_document_as_regular_user_fails(self, client, auth_headers):
        """Test creating document as regular user fails"""
        response = client.post(
            "/api/v1/documents/",
            headers=auth_headers,
            json={
                "title": "Test",
                "document_type": "pdf"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_get_document(self, client, auth_headers, document):
        """Test getting document by ID"""
        response = client.get(
            f"/api/v1/documents/{document.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == document.id
    
    def test_update_document(self, client, admin_auth_headers, document):
        """Test updating document"""
        response = client.put(
            f"/api/v1/documents/{document.id}",
            headers=admin_auth_headers,
            json={
                "description": "Updated document description"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["description"] == "Updated document description"
    
    def test_delete_document(self, client, admin_auth_headers, document):
        """Test deleting document"""
        response = client.delete(
            f"/api/v1/documents/{document.id}",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_search_documents(self, client, auth_headers, document):
        """Test searching documents"""
        response = client.get(
            f"/api/v1/documents/search/query?query={document.title}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "results" in data
    
    def test_add_document_tags(self, client, admin_auth_headers, document):
        """Test adding tags to document"""
        response = client.post(
            f"/api/v1/documents/{document.id}/tags",
            headers=admin_auth_headers,
            json=["important", "urgent"]
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_remove_document_tag(self, client, admin_auth_headers, document):
        """Test removing tag from document"""
        # First add tag
        client.post(
            f"/api/v1/documents/{document.id}/tags",
            headers=admin_auth_headers,
            json=["test"]
        )
        
        # Then remove it
        response = client.delete(
            f"/api/v1/documents/{document.id}/tags/test",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
    
    def test_index_document(self, client, admin_auth_headers, document):
        """Test indexing document in vector DB"""
        response = client.post(
            f"/api/v1/documents/{document.id}/index",
            headers=admin_auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["success"] is True
    
    def test_get_documents_by_type(self, client, auth_headers, document):
        """Test getting documents by type"""
        response = client.get(
            f"/api/v1/documents/by-type/{document.document_type}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
