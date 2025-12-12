"""
Authentication endpoint tests
"""

import pytest
from fastapi import status


def test_register_new_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123!",
            "full_name": "New User",
            "organization_id": "test-org-id"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user"]["username"] == "newuser"
    assert data["user"]["email"] == "newuser@example.com"
    assert "access_token" in data["tokens"]


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123!"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data["tokens"]
    assert data["user"]["username"] == test_user.username


def test_login_invalid_password(client, test_user):
    """Test login with invalid password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "WrongPassword123!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_user_not_found(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "Password123!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, test_user, auth_headers):
    """Test getting current user profile"""
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


def test_get_current_user_without_token(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, test_user):
    """Test token refresh"""
    # Login first
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123!"
        }
    )
    refresh_token = login_response.json()["tokens"]["refresh_token"]
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data["tokens"]


def test_change_password(client, test_user, auth_headers):
    """Test changing password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!",
            "confirm_password": "NewPassword123!"
        }
    )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
    
    # Verify old password doesn't work
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "TestPassword123!"
        }
    )
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Verify new password works
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "NewPassword123!"
        }
    )
    assert login_response.status_code == status.HTTP_200_OK
