"""
Authentication service for user login, registration, and token management
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import User, Organization, Role
from app.schemas import UserCreate, TokenPayload, TokenResponse, UserResponse, AuthResponse
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
import uuid
from datetime import datetime


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def register_user(
        db: Session,
        user_create: UserCreate
    ) -> Tuple[User, TokenResponse]:
        """
        Register a new user
        
        Args:
            db: Database session
            user_create: User creation data
            
        Returns:
            Tuple of (User, TokenResponse)
            
        Raises:
            ValueError: If user already exists
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            or_(
                User.email == user_create.email,
                User.username == user_create.username
            )
        ).first()
        
        if existing_user:
            raise ValueError("User with this email or username already exists")
        
        # Get organization
        organization = db.query(Organization).filter(
            Organization.id == user_create.organization_id
        ).first()
        
        if not organization:
            raise ValueError("Organization not found")
        
        # Get default role (or first available role)
        default_role = db.query(Role).filter(
            Role.organization_id == user_create.organization_id
        ).first()
        
        if not default_role:
            raise ValueError("No roles available for this organization")
        
        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=user_create.email,
            username=user_create.username,
            password_hash=hash_password(user_create.password),
            full_name=user_create.full_name,
            avatar_url=user_create.avatar_url,
            bio=user_create.bio,
            organization_id=user_create.organization_id,
            role_id=default_role.id,
            is_active=True,
            email_verified=False,
            two_factor_enabled=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Generate tokens
        tokens = AuthService.create_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def login(
        db: Session,
        username: str,
        password: str
    ) -> Tuple[User, TokenResponse]:
        """
        Authenticate a user with username and password
        
        Args:
            db: Database session
            username: Username or email
            password: Plain text password
            
        Returns:
            Tuple of (User, TokenResponse)
            
        Raises:
            ValueError: If credentials are invalid
        """
        # Find user by username or email
        user = db.query(User).filter(
            or_(
                User.username == username,
                User.email == username
            )
        ).first()
        
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        tokens = AuthService.create_tokens(user)
        
        return user, tokens
    
    @staticmethod
    def create_tokens(user: User) -> TokenResponse:
        """
        Create access and refresh tokens for a user
        
        Args:
            user: User object
            
        Returns:
            TokenResponse with access and refresh tokens
        """
        token_data = {
            "sub": user.id,
            "user_id": user.id,
            "username": user.username,
            "organization_id": user.organization_id,
        }
        
        access_token, access_expires_in = create_access_token(token_data)
        refresh_token, refresh_expires_in = create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=access_expires_in
        )
    
    @staticmethod
    def refresh_access_token(
        db: Session,
        refresh_token: str
    ) -> TokenResponse:
        """
        Generate new access token from refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token string
            
        Returns:
            TokenResponse with new access token
            
        Raises:
            ValueError: If refresh token is invalid
        """
        payload = decode_token(refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get("sub")
        
        # Verify user still exists
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")
        
        # Create new tokens
        return AuthService.create_tokens(user)
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenPayload]:
        """
        Verify and extract token payload
        
        Args:
            token: JWT token string
            
        Returns:
            TokenPayload if valid, None otherwise
        """
        from app.utils.security import verify_token as verify_jwt
        return verify_jwt(token)
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object or None
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_password: str,
        new_password: str
    ) -> None:
        """
        Change user password
        
        Args:
            db: Database session
            user: User object
            current_password: Current plain text password
            new_password: New plain text password
            
        Raises:
            ValueError: If current password is incorrect
        """
        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")
        
        user.password_hash = hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
