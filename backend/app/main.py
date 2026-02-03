from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.mongodb import MongoDB
from app.db.chromadb import ChromaDBManager
from app.api.v1 import api_router
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Medical Chat Bot API...")
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_db()
        
        # Connect to ChromaDB
        ChromaDBManager.connect()
        
        logger.info("All database connections established")
        
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Medical Chat Bot API...")
    await MongoDB.close_db()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Medical Chat Bot API",
    version="1.0.0",
    description="AI-powered medical chat bot with document processing and clinical decision support",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "name": "Medical Chat Bot API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    
    Returns system status and database connectivity.
    """
    health_status = {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "databases": {}
    }
    
    # Check MongoDB
    try:
        db = MongoDB.get_db()
        await db.command("ping")
        health_status["databases"]["mongodb"] = "connected"
    except Exception as e:
        health_status["databases"]["mongodb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check ChromaDB
    try:
        client = ChromaDBManager.get_client()
        client.heartbeat()
        health_status["databases"]["chromadb"] = "connected"
    except Exception as e:
        health_status["databases"]["chromadb"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    status_code = status.HTTP_200_OK if health_status["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(content=health_status, status_code=status_code)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
