"""Initialize API v1 router."""
from fastapi import APIRouter
from app.api.v1 import auth, documents, clinical

# Create main router for API v1
api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(clinical.router)

