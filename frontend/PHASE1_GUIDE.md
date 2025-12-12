# Frontend Phase 1 - Quick Reference Guide

## 📁 File Structure
```
frontend/src/
├── config/
│   └── index.ts              # All API endpoints and config constants
├── services/
│   ├── apiClient.ts          # Axios instance with interceptors
│   └── authService.ts        # Auth logic (login, logout, refresh)
├── types/
│   └── api.ts                # All TypeScript types for API
├── utils/
│   ├── logger.ts             # Logger utility
│   └── errorHandler.ts       # Error handling and parsing
├── App.tsx                   # Router and auth state
└── App.css                   # Styling
```

## 🔑 Key Imports

### API Client
```typescript
import { apiClient } from '@/services/apiClient'
import { API_ENDPOINTS } from '@/config'
```

### Auth Service
```typescript
import { authService } from '@/services/authService'
```

### Types
```typescript
import { User, Document, Conversation, Message, Agent } from '@/types/api'
```

### Utilities
```typescript
import { logger } from '@/utils/logger'
import { getErrorMessage, ApiError } from '@/utils/errorHandler'
```

## 🔐 Authentication Flow

### Login
```typescript
const response = await authService.login({
  email: 'user@example.com',
  password: 'password'
})
// Automatically stores token and user
```

### Check Auth Status
```typescript
if (authService.isAuthenticated()) {
  const user = authService.getCurrentUser()
  const token = authService.getToken()
}
```

### Logout
```typescript
await authService.logout()
// Clears all tokens and redirects to login
```

## 📡 Making API Calls

### GET Request
```typescript
const documents = await apiClient.get(API_ENDPOINTS.documents.list)
```

### POST Request
```typescript
const response = await apiClient.post(
  API_ENDPOINTS.documents.create,
  {
    title: 'My Document',
    summary: 'Summary',
    content: 'Full content here',
    tags: ['tag1', 'tag2']
  }
)
```

### PUT Request
```typescript
const response = await apiClient.put(
  API_ENDPOINTS.documents.update('doc-id'),
  { title: 'Updated Title' }
)
```

### DELETE Request
```typescript
await apiClient.delete(API_ENDPOINTS.documents.delete('doc-id'))
```

### With Error Handling
```typescript
try {
  const result = await apiClient.get(endpoint)
  return result.data
} catch (error) {
  const message = getErrorMessage(error)
  console.error(message)
  // Handle error
}
```

## 📝 Logging

```typescript
logger.debug('Debug info', { data })    // DEBUG level
logger.info('General info')              // INFO level
logger.warn('Warning message')           // WARN level
logger.error('Error occurred', error)    // ERROR level
```

## 🔗 Available Endpoints

All endpoints are in `src/config/index.ts`:

### Documents
```typescript
API_ENDPOINTS.documents.list              // GET /documents
API_ENDPOINTS.documents.create            // POST /documents
API_ENDPOINTS.documents.get('id')         // GET /documents/{id}
API_ENDPOINTS.documents.update('id')      // PUT /documents/{id}
API_ENDPOINTS.documents.delete('id')      // DELETE /documents/{id}
API_ENDPOINTS.documents.search.semantic   // POST /documents/search/semantic
API_ENDPOINTS.documents.search.hybrid     // POST /documents/search/hybrid
```

### Conversations
```typescript
API_ENDPOINTS.conversations.list                      // GET /conversations
API_ENDPOINTS.conversations.create                    // POST /conversations
API_ENDPOINTS.conversations.get('id')                 // GET /conversations/{id}
API_ENDPOINTS.conversations.messages.list('id')       // GET /conversations/{id}/messages
API_ENDPOINTS.conversations.messages.create('id')     // POST /conversations/{id}/messages
API_ENDPOINTS.conversations.messages.delete('id', 'msgId') // DELETE /conversations/{id}/messages/{msgId}
API_ENDPOINTS.conversations.messages.search('id')     // POST /conversations/{id}/search
```

### Agents
```typescript
API_ENDPOINTS.agents.list                             // GET /agents
API_ENDPOINTS.agents.execute.simple('id')             // POST /agents/{id}/execute
API_ENDPOINTS.agents.execute.rag                      // POST /agents/execute/rag
API_ENDPOINTS.agents.execute.fullRag                  // POST /agents/execute/full-rag
```

## 🌍 Environment Variables

Edit `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000
VITE_APP_NAME=Tarento Copilot
VITE_LOG_LEVEL=debug
```

## 🛡️ Token Management

Tokens are automatically handled:
- **Request**: Token automatically added to Authorization header
- **401 Response**: Token refresh attempted automatically
- **Refresh Token**: Stored in localStorage
- **Logout**: All tokens cleared

## ⚠️ Error Handling

Errors are converted to custom types:
- `ApiError`: HTTP errors with status code
- `NetworkError`: Connection issues
- `ValidationError`: Form validation failures

Use `getErrorMessage(error)` for user-friendly messages.

## 🎯 Common Patterns

### Search Documents
```typescript
const results = await apiClient.post(
  API_ENDPOINTS.documents.search.semantic,
  {
    query: 'search text',
    limit: 10,
    score_threshold: 0.7
  }
)
```

### Create Conversation
```typescript
const conv = await apiClient.post(
  API_ENDPOINTS.conversations.create,
  { title: 'My Conversation' }
)
```

### Send Message
```typescript
const message = await apiClient.post(
  API_ENDPOINTS.conversations.messages.create(conversationId),
  {
    role: 'user',
    content: 'Hello assistant!'
  }
)
```

### Execute Agent with RAG
```typescript
const response = await apiClient.post(
  API_ENDPOINTS.agents.execute.fullRag,
  {
    prompt: 'Your question here',
    conversation_id: convId,
    retrieve_documents: true,
    retrieve_conversation_context: true,
    document_limit: 5,
    message_limit: 10
  }
)
```

## 🚀 Next Phase Preparation

Phase 2 will add:
- Sidebar navigation
- Layout wrapper
- Page components
- User menu

Everything is ready for feature development!
