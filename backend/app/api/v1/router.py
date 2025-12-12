"""
API v1 router setup
Combines all v1 endpoint modules
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .agents import router as agents_router
from .users import router as users_router
from .organizations import router as organizations_router
from .projects import router as projects_router
from .roles import router as roles_router

router = APIRouter(prefix="/api/v1", tags=["api_v1"])

# Include auth routes
router.include_router(auth_router)

# Include resource routes
router.include_router(users_router)
router.include_router(organizations_router)
router.include_router(projects_router)
router.include_router(roles_router)

# Include agent routes
router.include_router(agents_router)

# API status endpoint
@router.get("/status")
async def api_status():
    """API v1 status check"""
    return {"status": "API v1 running", "version": "1.0.0"}
