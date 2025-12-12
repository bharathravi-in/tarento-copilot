"""
Main FastAPI application entry point
Initializes the application with routes, middleware, and configuration
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router as api_router

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Multi-tenant SaaS platform for enterprise AI agents"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize Qdrant collections on startup"""
    try:
        from app.services.qdrant_service import qdrant_service
        
        # Create documents collection if it doesn't exist
        success = qdrant_service.create_collection("documents")
        if success:
            logger.info("✅ Qdrant 'documents' collection ready for indexing")
        else:
            logger.warning("⚠️ Could not create Qdrant 'documents' collection")
    except Exception as e:
        logger.error(f"❌ Startup error initializing Qdrant: {e}")


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "message": "Tarento Enterprise AI Co-Pilot",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name
    }


# Include API v1 routes
app.include_router(api_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

