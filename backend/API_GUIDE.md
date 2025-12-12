## API Guide

# Tarento Co-Pilot API Documentation

**Version**: 1.0.0  
**Base URL**: `http://localhost:8000/api/v1`  
**Authentication**: JWT Bearer Token

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Organization Management](#organization-management)
4. [Project Management](#project-management)
5. [Roles & Permissions](#roles--permissions)
6. [Agent Configurations](#agent-configurations)
7. [Conversations & Messages](#conversations--messages)
8. [Document Management](#document-management)
9. [Error Handling](#error-handling)

---

## Authentication

### Register New User

**Endpoint**: `POST /auth/register`

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "organization_id": "org-uuid"
  }'
```

**Response** (201):
```json
{
  "user": {
    "id": "user-uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "organization_id": "org-uuid",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-12-12T10:00:00",
    "updated_at": "2025-12-12T10:00:00"
  },
  "tokens": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### Login

**Endpoint**: `POST /auth/login`

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePassword123!"
  }'
```

**Response** (200): Same as register

### Get Current User

**Endpoint**: `GET /auth/me`

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Refresh Token

**Endpoint**: `POST /auth/refresh`

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGc..."
  }'
```

### Change Password

**Endpoint**: `POST /auth/change-password`

```bash
curl -X POST http://localhost:8000/api/v1/auth/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "current_password": "OldPassword123!",
    "new_password": "NewPassword123!"
  }'
```

---

## User Management

### List Users

**Endpoint**: `GET /users/`

**Parameters**:
- `skip` (int, default: 0) - Records to skip
- `limit` (int, default: 10, max: 100) - Records per page
- `search` (string) - Search by username, email, or full_name
- `organization_id` (string) - Filter by organization

```bash
curl -X GET "http://localhost:8000/api/v1/users/?skip=0&limit=10&search=john" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response** (200):
```json
{
  "data": [
    {
      "id": "user-uuid",
      "email": "john@example.com",
      "username": "john",
      "full_name": "John Doe",
      "organization_id": "org-uuid",
      "role_id": "role-uuid",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2025-12-12T10:00:00"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10,
  "has_more": false
}
```

### Get User by ID

**Endpoint**: `GET /users/{user_id}`

```bash
curl -X GET http://localhost:8000/api/v1/users/user-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create User (Admin Only)

**Endpoint**: `POST /users/`

```bash
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "SecurePassword123!",
    "full_name": "New User"
  }'
```

### Update User

**Endpoint**: `PUT /users/{user_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/users/user-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "Updated Name",
    "email": "newemail@example.com"
  }'
```

### Delete User (Admin Only, Soft Delete)

**Endpoint**: `DELETE /users/{user_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/users/user-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Change User Role (Admin Only)

**Endpoint**: `POST /users/{user_id}/role`

```bash
curl -X POST http://localhost:8000/api/v1/users/user-uuid/role \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "role_id": "role-uuid"
  }'
```

---

## Organization Management

### List Organizations

**Endpoint**: `GET /organizations/`

```bash
curl -X GET "http://localhost:8000/api/v1/organizations/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Organization

**Endpoint**: `GET /organizations/{org_id}`

```bash
curl -X GET http://localhost:8000/api/v1/organizations/org-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Organization (Superuser Only)

**Endpoint**: `POST /organizations/`

```bash
curl -X POST http://localhost:8000/api/v1/organizations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SUPERUSER_TOKEN" \
  -d '{
    "name": "Acme Corp",
    "description": "Acme Corporation",
    "domain": "acme.com"
  }'
```

### Update Organization

**Endpoint**: `PUT /organizations/{org_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/organizations/org-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "description": "Updated description"
  }'
```

### List Organization Members

**Endpoint**: `GET /organizations/{org_id}/members`

```bash
curl -X GET "http://localhost:8000/api/v1/organizations/org-uuid/members?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add Member to Organization

**Endpoint**: `POST /organizations/{org_id}/members/{user_id}`

```bash
curl -X POST http://localhost:8000/api/v1/organizations/org-uuid/members/user-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Project Management

### List Projects

**Endpoint**: `GET /projects/`

```bash
curl -X GET "http://localhost:8000/api/v1/projects/?skip=0&limit=10&search=rfp" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Project

**Endpoint**: `GET /projects/{project_id}`

```bash
curl -X GET http://localhost:8000/api/v1/projects/project-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Project

**Endpoint**: `POST /projects/`

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "RFP Processing",
    "description": "Process company RFPs",
    "project_metadata": {"type": "rfp"}
  }'
```

### Update Project

**Endpoint**: `PUT /projects/{project_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/projects/project-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "description": "Updated description"
  }'
```

### Delete Project

**Endpoint**: `DELETE /projects/{project_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/project-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add Member to Project

**Endpoint**: `POST /projects/{project_id}/members/{user_id}`

```bash
curl -X POST http://localhost:8000/api/v1/projects/project-uuid/members/user-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Remove Member from Project

**Endpoint**: `DELETE /projects/{project_id}/members/{user_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/projects/project-uuid/members/user-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Roles & Permissions

### List Roles

**Endpoint**: `GET /roles/`

```bash
curl -X GET "http://localhost:8000/api/v1/roles/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Role

**Endpoint**: `GET /roles/{role_id}`

```bash
curl -X GET http://localhost:8000/api/v1/roles/role-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Role (Admin Only)

**Endpoint**: `POST /roles/`

```bash
curl -X POST http://localhost:8000/api/v1/roles/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "name": "Project Manager",
    "description": "Can manage projects"
  }'
```

### Add Permission to Role

**Endpoint**: `POST /roles/{role_id}/permissions/{permission_id}`

```bash
curl -X POST http://localhost:8000/api/v1/roles/role-uuid/permissions/perm-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Remove Permission from Role

**Endpoint**: `DELETE /roles/{role_id}/permissions/{permission_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/roles/role-uuid/permissions/perm-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### List Permissions

**Endpoint**: `GET /roles/permissions/`

```bash
curl -X GET "http://localhost:8000/api/v1/roles/permissions/?skip=0&limit=50" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Agent Configurations

### List Agent Configs

**Endpoint**: `GET /agent-configs/`

```bash
curl -X GET "http://localhost:8000/api/v1/agent-configs/?skip=0&limit=10&agent_type=rfp" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Agent Config

**Endpoint**: `GET /agent-configs/{config_id}`

```bash
curl -X GET http://localhost:8000/api/v1/agent-configs/config-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Agent Config (Admin Only)

**Endpoint**: `POST /agent-configs/`

```bash
curl -X POST http://localhost:8000/api/v1/agent-configs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "name": "RFP Processing Agent",
    "description": "Processes RFP documents",
    "agent_type": "rfp",
    "llm_model": "gemini-2.5-pro",
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "You are an RFP processing agent..."
  }'
```

### Update Agent Config

**Endpoint**: `PUT /agent-configs/{config_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/agent-configs/config-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "temperature": 0.5
  }'
```

### Delete Agent Config

**Endpoint**: `DELETE /agent-configs/{config_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/agent-configs/config-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Conversations & Messages

### List Conversations

**Endpoint**: `GET /conversations/`

```bash
curl -X GET "http://localhost:8000/api/v1/conversations/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Conversation

**Endpoint**: `GET /conversations/{conversation_id}`

```bash
curl -X GET http://localhost:8000/api/v1/conversations/conv-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Conversation

**Endpoint**: `POST /conversations/`

```bash
curl -X POST http://localhost:8000/api/v1/conversations/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "RFP Analysis",
    "description": "Analysis of new RFP",
    "agent_config_id": "config-uuid",
    "project_id": "project-uuid"
  }'
```

### Add Message to Conversation

**Endpoint**: `POST /conversations/{conversation_id}/messages`

```bash
curl -X POST http://localhost:8000/api/v1/conversations/conv-uuid/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "content": "Please analyze this RFP",
    "role": "user"
  }'
```

### Archive Conversation

**Endpoint**: `POST /conversations/{conversation_id}/archive`

```bash
curl -X POST http://localhost:8000/api/v1/conversations/conv-uuid/archive \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Document Management

### List Documents

**Endpoint**: `GET /documents/`

```bash
curl -X GET "http://localhost:8000/api/v1/documents/?skip=0&limit=10&document_type=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Document

**Endpoint**: `GET /documents/{document_id}`

```bash
curl -X GET http://localhost:8000/api/v1/documents/doc-uuid \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Document (Admin Only)

**Endpoint**: `POST /documents/`

```bash
curl -X POST http://localhost:8000/api/v1/documents/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "title": "RFP Document",
    "description": "Client RFP submission",
    "document_type": "pdf",
    "content": "Full document content here...",
    "is_public": false,
    "tags": ["rfp", "client"]
  }'
```

### Update Document

**Endpoint**: `PUT /documents/{document_id}`

```bash
curl -X PUT http://localhost:8000/api/v1/documents/doc-uuid \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '{
    "description": "Updated description",
    "is_public": true
  }'
```

### Delete Document

**Endpoint**: `DELETE /documents/{document_id}`

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/doc-uuid \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Search Documents

**Endpoint**: `GET /documents/search/query`

```bash
curl -X GET "http://localhost:8000/api/v1/documents/search/query?query=requirements&skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Add Tags to Document

**Endpoint**: `POST /documents/{document_id}/tags`

```bash
curl -X POST http://localhost:8000/api/v1/documents/doc-uuid/tags \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -d '["important", "urgent"]'
```

### Remove Tag from Document

**Endpoint**: `DELETE /documents/{document_id}/tags/{tag}`

```bash
curl -X DELETE http://localhost:8000/api/v1/documents/doc-uuid/tags/important \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Index Document (Vector DB)

**Endpoint**: `POST /documents/{document_id}/index`

```bash
curl -X POST http://localhost:8000/api/v1/documents/doc-uuid/index \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### Get Documents by Type

**Endpoint**: `GET /documents/by-type/{document_type}`

```bash
curl -X GET "http://localhost:8000/api/v1/documents/by-type/pdf?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Error Handling

All endpoints return standard error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Missing or invalid authorization header"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Authentication Patterns

### Bearer Token
Always include the JWT token in the Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### Token Expiration
- Access tokens expire after 30 minutes
- Use refresh_token to get a new access token
- Refresh tokens expire after 7 days

### Superuser vs Admin
- **Superuser**: Can access/modify any organization's resources
- **Admin**: Can only manage resources within their organization

---

## Rate Limiting

Currently no rate limiting is enforced. Future versions will implement:
- 100 requests per minute per user
- 1000 requests per minute per organization

---

## Pagination

All list endpoints support pagination:
- `skip`: Number of items to skip (default: 0)
- `limit`: Number of items to return (default: 10, max: 100-200)

Response includes:
- `data`: Array of items
- `total`: Total number of items
- `skip`: Applied skip value
- `limit`: Applied limit value
- `has_more`: Boolean indicating if more items exist

---

## Filtering & Searching

Most list endpoints support:
- `search`: Full-text search across multiple fields
- Field-specific filters (e.g., `document_type`, `agent_type`)
- Organization scoping (automatic for regular users)

---

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (not in localStorage)
3. **Refresh tokens before expiration**
4. **Use specific error handling** for different status codes
5. **Implement retry logic** for transient failures
6. **Log all API interactions** for debugging
7. **Use meaningful search queries** for better results

---

## Support & Contact

For API issues or questions:
1. Check the documentation
2. Review application logs
3. Submit issue to repository
4. Contact development team

---

**Last Updated**: December 12, 2025  
**API Version**: 1.0.0
