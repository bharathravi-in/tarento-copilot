"""
API v1 router setup
Combines all v1 endpoint modules
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["api_v1"])

# Placeholder routes to be implemented
@router.get("/status")
async def api_status():
    """API v1 status check"""
    return {"status": "API v1 running"}
