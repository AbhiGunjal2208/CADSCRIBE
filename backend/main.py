"""
CADSCRIBE Backend API - FastAPI application entry point.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import uvicorn


# Import routes
from routes.auth import router as auth_router
from routes.models import router as models_router
from routes.ai import router as ai_router
from routes.misc import misc_router
from routes.user import router as user_router
from routes.projects import router as projects_router
from routes.scripts import router as scripts_router
from routes.monitoring import router as monitoring_router
from routes.project_data import router as project_data_router

# Import services
from services.database import db_service
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CADSCRIBE Backend API",
    description="AI-powered parametric CAD design platform backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(models_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(misc_router)  # already has /api prefix in router
app.include_router(user_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(scripts_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")
app.include_router(project_data_router, prefix="/api")


@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "cadscribe-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if db_service.client else "disconnected"
    }


@app.get("/health")
async def detailed_health_check():
    """Detailed health check with service status"""
    try:
        # Test database connection
        db_status = "connected"
        try:
            db_service.client.admin.command('ping')
        except Exception:
            db_status = "disconnected"
        
        return {
            "status": "ok",
            "service": "cadscribe-backend",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": db_status,
                "ai_service": "available",
                "cad_service": "available"
            },
            "environment": {
                "mongodb_uri": settings.mongodb_uri[:20] + "..." if len(settings.mongodb_uri) > 20 else settings.mongodb_uri,
                "cad_service_url": settings.cad_service_url,
                "openai_configured": bool(settings.openai_api_key),
                "gemini_configured": bool(settings.gemini_api_key)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "service": "cadscribe-backend",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
