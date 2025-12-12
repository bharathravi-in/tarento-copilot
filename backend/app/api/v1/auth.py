"""
Authentication API endpoints (v1)
Includes user registration, login, token refresh, and password management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    PasswordChangeRequest,
    TokenRefreshRequest,
    TokenResponse,
    AuthResponse,
)
from app.services.auth_service import AuthService
from app.utils.security import verify_token as verify_jwt
from typing import Optional

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)


def get_current_user_from_token(
    token: str,
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    Extract user from JWT token
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User information from token
        
    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Remove "Bearer " prefix if present
    if token.startswith("Bearer "):
        token = token[7:]
    
    payload = verify_jwt(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user
    
    Args:
        authorization: Authorization header
        db: Database session
        
    Returns:
        Current user object
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )
    
    payload = get_current_user_from_token(authorization, db)
    user = AuthService.get_user_by_id(db, payload["user_id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


@router.post("/register", response_model=AuthResponse)
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Args:
        user_create: User registration data
        db: Database session
        
    Returns:
        AuthResponse with user data and tokens
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        user, tokens = AuthService.register_user(db, user_create)
        return AuthResponse(
            user=UserResponse.from_orm(user),
            tokens=tokens
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=AuthResponse)
async def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
):
    """
    User login with username/email and password
    
    Args:
        user_login: Login credentials
        db: Database session
        
    Returns:
        AuthResponse with user data and tokens
        
    Raises:
        HTTPException: If login fails
    """
    try:
        user, tokens = AuthService.login(db, user_login.username, user_login.password)
        return AuthResponse(
            user=UserResponse.from_orm(user),
            tokens=tokens
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    Args:
        request: TokenRefreshRequest with refresh token
        db: Database session
        
    Returns:
        TokenResponse with new access token
        
    Raises:
        HTTPException: If refresh fails
    """
    try:
        tokens = AuthService.refresh_access_token(db, request.refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/change-password")
async def change_password(
    request: PasswordChangeRequest,
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Change user password
    
    Args:
        request: Password change request
        authorization: Authorization header
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If password change fails
    """
    user = await get_current_user(authorization, db)
    
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    try:
        AuthService.change_password(
            db,
            user,
            request.current_password,
            request.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    authorization: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    
    Args:
        authorization: Authorization header
        db: Database session
        
    Returns:
        Current user profile
    """
    user = await get_current_user(authorization, db)
    return UserResponse.from_orm(user)


@router.post("/logout")
async def logout():
    """
    Logout user (client-side token invalidation)
    
    Note: Since we use JWT tokens, logout is handled client-side.
    This endpoint exists for consistency and future enhancement.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
