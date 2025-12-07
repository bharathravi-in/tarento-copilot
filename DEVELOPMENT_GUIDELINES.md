# Development Guidelines & Best Practices

**Project:** Tarento Enterprise AI Co-Pilot  
**Version:** 1.0  
**Date:** December 7, 2025

---

## Table of Contents

1. [Code Style & Standards](#code-style--standards)
2. [Development Workflow](#development-workflow)
3. [API Design Patterns](#api-design-patterns)
4. [Database Best Practices](#database-best-practices)
5. [Frontend Patterns](#frontend-patterns)
6. [Testing Guidelines](#testing-guidelines)
7. [Git Workflow](#git-workflow)
8. [Security Practices](#security-practices)
9. [Performance Optimization](#performance-optimization)
10. [Documentation](#documentation)

---

## Code Style & Standards

### Python (Backend)

#### Formatting
- **Tool**: Black (automatic formatting)
- **Line Length**: 100 characters
- **Command**: `black backend/`

#### Linting
- **Tool**: Flake8
- **Command**: `flake8 backend/`
- **Ignore**: W503 (line break before binary operator)

#### Type Checking
- **Tool**: mypy
- **Command**: `mypy backend/`
- **Always**: Add type hints to function signatures

#### Import Sorting
- **Tool**: isort
- **Command**: `isort backend/`
- **Order**: stdlib → third-party → local

#### Example Python Code

```python
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> User:
    """
    Get user by ID.
    
    Args:
        user_id: The ID of the user to retrieve
        db: Database session dependency
        
    Returns:
        UserResponse with user details
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### TypeScript/React (Frontend)

#### Formatting
- **Tool**: Prettier
- **Command**: `npm run format`
- **Config**: `.prettierrc.json`

#### Linting
- **Tool**: ESLint
- **Command**: `npm run lint`
- **Fix**: `npm run lint -- --fix`

#### Example TypeScript Code

```typescript
import React, { useState, useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { Button, TextField } from '@mui/material'

interface LoginFormProps {
  onSuccess: (token: string) => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const [email, setEmail] = useState<string>('')
  const [password, setPassword] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) throw new Error('Login failed')
      const data = await response.json()
      onSuccess(data.access_token)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [email, password, onSuccess])

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        fullWidth
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        fullWidth
      />
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <Button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </Button>
    </form>
  )
}
```

---

## Development Workflow

### Local Development Setup

#### 1. Clone and Setup

```bash
git clone https://github.com/quardiccrew/tarento-copilot.git
cd tarento-copilot
```

#### 2. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

#### 3. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
```

#### 4. Setup Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with API endpoint
```

#### 5. Start Development

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Type checking (Optional)
npm run type-check
```

#### 6. Run Tests

```bash
# Backend
cd backend
pytest --watch

# Frontend
cd frontend
npm run test -- --watch
```

### Making Changes

1. **Create feature branch** with descriptive name
2. **Make atomic commits** with clear messages
3. **Keep commits small** (one feature per commit)
4. **Run tests** before committing
5. **Update documentation** as needed
6. **Create pull request** with description

---

## API Design Patterns

### RESTful Endpoints

#### Naming Convention
- **Plural nouns** for collections: `/api/v1/users`, `/api/v1/projects`
- **Actions** in URL only for non-standard operations
- **Version in URL**: `/api/v1/` not in headers

#### HTTP Methods
| Method | Use Case | Example |
|--------|----------|---------|
| GET | Retrieve data | `GET /api/v1/users/{id}` |
| POST | Create data | `POST /api/v1/users` |
| PUT | Full update | `PUT /api/v1/users/{id}` |
| PATCH | Partial update | `PATCH /api/v1/users/{id}` |
| DELETE | Delete data | `DELETE /api/v1/users/{id}` |

#### Status Codes
| Code | Meaning | When to Use |
|------|---------|------------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Missing/invalid auth |
| 403 | Forbidden | Valid auth but no permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate/conflict error |
| 500 | Server Error | Unexpected error |

#### Response Format

```json
{
  "success": true,
  "data": {
    "id": "user-123",
    "email": "user@example.com"
  }
}
```

#### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is already registered",
    "details": {
      "field": "email"
    }
  }
}
```

### Request/Response Schemas

#### Always Define Schemas

```python
# ✅ Good
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: datetime

    class Config:
        from_attributes = True

@router.post("/users", response_model=UserResponse)
def create_user(user_create: UserCreate, db: Session = Depends(get_db)):
    pass

# ❌ Avoid
@router.post("/users")
def create_user(data: dict):
    pass
```

#### Documentation

```python
@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str) -> User:
    """
    Retrieve a user by ID.
    
    **Parameters:**
    - `user_id`: The unique identifier of the user
    
    **Returns:**
    - `UserResponse` with complete user information
    
    **Raises:**
    - `404 Not Found`: If user doesn't exist
    
    **Example:**
    ```
    GET /api/v1/users/user-123
    Response: {
        "id": "user-123",
        "email": "user@example.com"
    }
    ```
    """
    pass
```

---

## Database Best Practices

### Schema Design

#### 1. Use UUIDs for Primary Keys

```python
# ✅ Good
id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

# ❌ Avoid
id = Column(Integer, primary_key=True, autoincrement=True)
```

#### 2. Always Include Timestamps

```python
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 3. Use Foreign Keys

```python
class Project(BaseModel):
    __tablename__ = "projects"
    
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    organization = relationship("Organization", back_populates="projects")
```

#### 4. Soft Deletes for Important Data

```python
class User(BaseModel):
    __tablename__ = "users"
    
    is_active = Column(Boolean, default=True)
    # Query: db.query(User).filter(User.is_active == True)
```

### Queries

#### 1. Use Parameterized Queries

```python
# ✅ Good - Safe from SQL injection
user = db.query(User).filter(User.email == email).first()

# ❌ Avoid - SQL injection vulnerability
user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

#### 2. Optimize Queries

```python
# ✅ Good - Eager loading
users = db.query(User).options(joinedload(User.organization)).all()

# ❌ Avoid - N+1 queries
for user in users:
    org = user.organization  # Database query in loop
```

#### 3. Use Pagination

```python
@router.get("/users")
def list_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### Migrations

#### Create Migration

```bash
alembic revision --autogenerate -m "Add user status field"
```

#### Review and Edit Migration

```python
def upgrade():
    op.add_column('users', sa.Column('status', sa.String(50), nullable=False, server_default='active'))

def downgrade():
    op.drop_column('users', 'status')
```

#### Apply Migration

```bash
alembic upgrade head
```

---

## Frontend Patterns

### Component Structure

```typescript
// ✅ Good structure
components/
├── UserCard/
│   ├── UserCard.tsx         # Component
│   ├── UserCard.test.tsx    # Tests
│   ├── UserCard.styles.ts   # Styles
│   ├── useUserCard.ts       # Custom hook
│   └── types.ts             # Types/Props
```

### Functional Components

```typescript
import React, { useState, useCallback, FC } from 'react'

interface Props {
  userId: string
  onUserUpdate: (user: User) => void
}

export const UserProfile: FC<Props> = ({ userId, onUserUpdate }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchUser = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.get(`/users/${userId}`)
      setUser(data)
      onUserUpdate(data)
    } catch (error) {
      console.error('Failed to fetch user', error)
    } finally {
      setLoading(false)
    }
  }, [userId, onUserUpdate])

  return (
    <div>
      {loading && <Spinner />}
      {user && <div>{user.name}</div>}
    </div>
  )
}
```

### Custom Hooks

```typescript
// hooks/useUser.ts
import { useState, useEffect } from 'react'
import { api } from '../services/api'

export const useUser = (userId: string) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await api.get(`/users/${userId}`)
        setUser(data)
      } catch (err) {
        setError(err as Error)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [userId])

  return { user, loading, error }
}
```

### Redux Patterns

```typescript
// store/userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface UserState {
  current: User | null
  loading: boolean
  error: string | null
}

const initialState: UserState = {
  current: null,
  loading: false,
  error: null
}

export const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.current = action.payload
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload
    }
  }
})

export const { setUser, setLoading, setError } = userSlice.actions
export default userSlice.reducer
```

---

## Testing Guidelines

### Backend Testing

#### Unit Tests

```python
# tests/unit/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.utils.security import hash_password

@pytest.fixture
def auth_service():
    return AuthService()

def test_password_verification(auth_service):
    password = "test_password"
    hashed = hash_password(password)
    
    assert auth_service.verify_password(password, hashed)
    assert not auth_service.verify_password("wrong", hashed)
```

#### Integration Tests

```python
# tests/integration/test_auth_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_login_endpoint(client, db):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
```

### Frontend Testing

#### Component Tests

```typescript
// components/LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { LoginForm } from './LoginForm'

test('renders login form', () => {
  render(<LoginForm onSuccess={jest.fn()} />)
  expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
})

test('submits form with valid data', async () => {
  const onSuccess = jest.fn()
  render(<LoginForm onSuccess={onSuccess} />)
  
  fireEvent.change(screen.getByLabelText(/email/i), {
    target: { value: 'test@example.com' }
  })
  fireEvent.click(screen.getByRole('button', { name: /login/i }))
  
  // Assertions...
})
```

### Test Coverage

```bash
# Backend
pytest --cov=app --cov-report=html

# Frontend
npm run test -- --coverage
```

---

## Git Workflow

### Branch Naming

```
feature/user-authentication
feature/agent-orchestration
bugfix/login-error
hotfix/database-connection
docs/api-documentation
refactor/code-organization
test/agent-execution
```

### Commit Messages

```
feat: Add user authentication endpoint
fix: Resolve database connection timeout
docs: Update API documentation
refactor: Simplify agent orchestration logic
test: Add integration tests for auth
chore: Update dependencies
```

### Pull Request Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   ```bash
   git add .
   git commit -m "feat: Describe your changes"
   ```

3. **Push to Remote**
   ```bash
   git push origin feature/your-feature
   ```

4. **Create Pull Request**
   - Use PR template
   - Describe changes and testing
   - Link related issues

5. **Code Review**
   - Address feedback
   - Update based on comments
   - Get approval

6. **Merge**
   ```bash
   git checkout main
   git pull origin main
   git merge --squash feature/your-feature
   git push origin main
   ```

---

## Security Practices

### Authentication

```python
# ✅ Good
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# ❌ Avoid
import hashlib
password_hash = hashlib.md5(password).hexdigest()  # Insecure!
```

### API Keys

```python
# ✅ Good - Use environment variables
api_key = os.getenv("GEMINI_API_KEY")

# ❌ Avoid - Hardcoding
api_key = "sk-1234567890"
```

### SQL Injection Prevention

```python
# ✅ Good - Parameterized query
user = db.query(User).filter(User.email == email).first()

# ❌ Avoid - String interpolation
query = f"SELECT * FROM users WHERE email = '{email}'"
```

### CORS Configuration

```python
# ✅ Good - Specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com", "https://admin.example.com"],
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["*"]
)

# ❌ Avoid - Allow all
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

---

## Performance Optimization

### Backend Optimization

#### Database Queries
- Use indexes on frequently queried fields
- Implement pagination
- Use eager loading for relationships
- Cache frequently accessed data

#### API Response
- Compress responses with gzip
- Implement rate limiting
- Use database connection pooling
- Cache at appropriate levels

```python
from fastapi_cache import cache
from fastapi import FastAPI

@cache(expire=300)  # Cache for 5 minutes
async def get_user(user_id: str):
    return db.query(User).filter(User.id == user_id).first()
```

### Frontend Optimization

#### Code Splitting
```typescript
const UserProfile = React.lazy(() => import('./UserProfile'))

<Suspense fallback={<Spinner />}>
  <UserProfile />
</Suspense>
```

#### Memoization
```typescript
const MemoizedUserCard = React.memo(UserCard)

const UserList = () => {
  const users = useMemo(() => 
    userList.filter(u => u.active),
    [userList]
  )
  return users.map(u => <MemoizedUserCard key={u.id} user={u} />)
}
```

---

## Documentation

### Code Documentation

```python
def calculate_proposal_cost(
    resources: List[Resource],
    daily_rate: float,
    markup_percent: float = 30
) -> dict:
    """
    Calculate total proposal cost based on resources and rates.
    
    This function takes a list of required resources, multiplies by
    their daily rates, and applies a markup percentage for profit margin.
    
    Args:
        resources: List of Resource objects with required days and type
        daily_rate: Base daily rate in USD
        markup_percent: Profit margin percentage (default: 30%)
        
    Returns:
        Dictionary containing:
            - base_cost: Total cost before markup
            - markup: Markup amount in USD
            - total_cost: Final cost including markup
            
    Raises:
        ValueError: If daily_rate is negative or markup_percent > 100
        
    Example:
        >>> resources = [Resource(days=5, type="developer")]
        >>> cost = calculate_proposal_cost(resources, 150.0)
        >>> cost['total_cost']
        975.0
    """
    pass
```

### API Documentation

```python
@router.post("/proposals/{proposal_id}/validate")
def validate_proposal(
    proposal_id: str,
    validation_rules: dict = Body(..., example={
        "check_compliance": True,
        "check_budget": True
    })
) -> ProposalValidationResponse:
    """
    Validate a proposal against compliance and budget rules.
    
    **Path Parameters:**
    - `proposal_id`: The ID of the proposal to validate
    
    **Request Body:**
    ```json
    {
        "check_compliance": true,
        "check_budget": true
    }
    ```
    
    **Response:**
    ```json
    {
        "is_valid": true,
        "issues": [],
        "warnings": []
    }
    ```
    
    **Status Codes:**
    - `200`: Validation completed
    - `404`: Proposal not found
    - `422`: Invalid request parameters
    """
    pass
```

---

## Checklist for Code Review

- [ ] Code follows style guidelines
- [ ] Descriptive commit messages
- [ ] No hardcoded secrets or API keys
- [ ] Tests added and passing
- [ ] No console.logs or debugging code
- [ ] Documentation updated
- [ ] No breaking changes without migration
- [ ] Performance impact considered
- [ ] Security implications reviewed
- [ ] Error handling implemented

---

**Document Version:** 1.0  
**Last Updated:** December 7, 2025  
**Status:** Ready for Development
