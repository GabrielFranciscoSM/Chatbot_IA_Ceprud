"""
Routes package for the CEPRUD chatbot API.

This module aggregates all route modules into a single router that can be
included in the main FastAPI application. This modular structure improves
code organization and maintainability.

Route modules:
- health: Health checks and monitoring endpoints
- sessions: LTI session validation
- chat: Chat and conversation management
- users: User account management
- subjects: Subject enrollment management
"""

from fastapi import APIRouter

from .health import router as health_router
from .sessions import router as sessions_router
from .chat import router as chat_router
from .users import router as users_router
from .subjects import router as subjects_router

# Create main router
router = APIRouter()

# Include all route modules
router.include_router(health_router)
router.include_router(sessions_router)
router.include_router(chat_router)
router.include_router(users_router)
router.include_router(subjects_router)

__all__ = ["router"]
