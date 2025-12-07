"""
Dependency injection setup for FastAPI
Provides commonly needed dependencies like current user, database session, etc.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db


async def get_current_user(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user from JWT token
    To be implemented in auth service
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    # JWT validation logic to be implemented
    pass


async def get_current_admin(
    current_user = Depends(get_current_user)
):
    """
    Get current user and verify admin role
    """
    # Admin check logic to be implemented
    pass
