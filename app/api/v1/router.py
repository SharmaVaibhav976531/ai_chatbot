# backend/app/api/v1/router.py

from fastapi import APIRouter
from app.api.v1.endpoints import auth, users

api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


# Future routers will be included here:
# from app.api.v1.endpoints import auth, chat, documents
# Include Authentication endpoints
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
# api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
# api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Include User Management endpoints
api_router.include_router(users.router, prefix="/users", tags=["Users"])