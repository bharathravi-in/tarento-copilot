"""
Security utilities for JWT token management and password hashing
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, TYPE_CHECKING, List, Callable
import jwt
from passlib.context import CryptContext
from app.config import settings
from app.schemas import TokenPayload
from fastapi import Depends, HTTPException, status, Request
from functools import wraps

if TYPE_CHECKING:
    from app.models import User

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
        
    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, int]:
    """
    Create a JWT access token
    
    Args:
        data: Payload data to encode in token
        expires_delta: Custom expiration time (defaults to config value)
        
    Returns:
        Tuple of (token, expires_in_seconds)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    
    return encoded_jwt, expires_in


def create_refresh_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> tuple[str, int]:
    """
    Create a JWT refresh token with longer expiration
    
    Args:
        data: Payload data to encode in token
        expires_delta: Custom expiration time (defaults to config value)
        
    Returns:
        Tuple of (token, expires_in_seconds)
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    expires_in = int((expire - datetime.now(timezone.utc)).total_seconds())
    
    return encoded_jwt, expires_in


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except jwt.InvalidTokenError:
        return None
    except jwt.ExpiredSignatureError:
        return None


def verify_token(token: str) -> Optional[TokenPayload]:
    """
    Verify and parse a JWT token into TokenPayload
    
    Args:
        token: JWT token string
        
    Returns:
        TokenPayload if valid, None otherwise
    """
    payload = decode_token(token)
    if payload is None:
        return None
    
    try:
        return TokenPayload(**payload)
    except (ValueError, TypeError):
        return None


async def get_current_user(
    request: Request
) -> "User":
    """
    Get the current authenticated user from JWT token
    
    Args:
        request: HTTP request with Authorization header
        
    Returns:
        Current user object
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    from app.database import SessionLocal
    from app.models import User
    
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split(" ")[1]
    
    # Verify token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user


async def check_user_permission(
    user: "User",
    permission_name: str,
    db_session = None
) -> bool:
    """
    Check if user has a specific permission
    
    Args:
        user: User object
        permission_name: Name of the permission to check
        db_session: Database session (optional, creates new if not provided)
        
    Returns:
        True if user has permission, False otherwise
    """
    from app.database import SessionLocal
    from app.models import Permission
    
    should_close = False
    if db_session is None:
        db_session = SessionLocal()
        should_close = True
    
    try:
        # Check if user's role has the permission
        permission = db_session.query(Permission).filter(
            Permission.name == permission_name
        ).first()
        
        if not permission:
            return False
        
        # Check if user's role has this permission
        has_permission = False
        if user.role:
            has_permission = permission in user.role.permissions
        
        return has_permission
    finally:
        if should_close:
            db_session.close()


async def check_user_permissions(
    user: "User",
    permission_names: List[str],
    require_all: bool = False,
    db_session = None
) -> bool:
    """
    Check if user has multiple permissions
    
    Args:
        user: User object
        permission_names: List of permission names to check
        require_all: If True, user must have ALL permissions. If False, user needs ANY.
        db_session: Database session (optional, creates new if not provided)
        
    Returns:
        True if user has required permissions, False otherwise
    """
    from app.database import SessionLocal
    
    should_close = False
    if db_session is None:
        db_session = SessionLocal()
        should_close = True
    
    try:
        results = []
        for permission_name in permission_names:
            has_perm = await check_user_permission(user, permission_name, db_session)
            results.append(has_perm)
        
        if require_all:
            return all(results)
        else:
            return any(results)
    finally:
        if should_close:
            db_session.close()


def require_permission(*permissions: str, require_all: bool = False):
    """
    Decorator to require specific permissions for an endpoint
    
    Usage:
        @require_permission("user:read")
        async def get_users(...):
            pass
            
        @require_permission("user:create", "user:update", require_all=True)
        async def update_user(...):
            pass
    
    Args:
        *permissions: Permission names required
        require_all: If True, all permissions required. If False, any permission required.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not authenticated",
                )
            
            # Get database session
            db = kwargs.get('db')
            if not db:
                from app.database import SessionLocal
                db = SessionLocal()
                kwargs['db'] = db
            
            # Check permissions
            has_perm = await check_user_permissions(
                current_user,
                list(permissions),
                require_all=require_all,
                db_session=db
            )
            
            if not has_perm:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def require_superuser(func: Callable) -> Callable:
    """
    Decorator to require superuser role for an endpoint
    
    Usage:
        @require_superuser
        async def delete_organization(...):
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated",
            )
        
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation requires superuser privileges",
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


def require_admin(func: Callable) -> Callable:
    """
    Decorator to require admin role within user's organization
    
    Usage:
        @require_admin
        async def create_user(...):
            pass
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated",
            )
        
        # Check if user is superuser or has admin role
        from app.models import Role
        is_admin = (
            current_user.is_superuser or 
            (current_user.role and current_user.role.name.lower() == 'admin')
        )
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This operation requires admin privileges",
            )
        
        return await func(*args, **kwargs)
    
    return wrapper


async def verify_organization_access(
    user: "User",
    organization_id: str
) -> bool:
    """
    Verify that user has access to the specified organization
    
    Args:
        user: User object
        organization_id: Organization ID to check
        
    Returns:
        True if user can access the organization, False otherwise
    """
    # Superusers can access any organization
    if user.is_superuser:
        return True
    
    # Regular users can only access their own organization
    return user.organization_id == organization_id


def verify_resource_ownership(user_id: str, resource_owner_id: str) -> bool:
    """
    Verify that user owns the resource
    
    Args:
        user_id: User's ID
        resource_owner_id: Resource owner's ID
        
    Returns:
        True if user owns the resource, False otherwise
    """
    return user_id == resource_owner_id

