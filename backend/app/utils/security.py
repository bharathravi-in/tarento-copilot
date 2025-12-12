"""
Security utilities for JWT token management and password hashing
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, TYPE_CHECKING
import jwt
from passlib.context import CryptContext
from app.config import settings
from app.schemas import TokenPayload
from fastapi import Depends, HTTPException, status, Request

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
