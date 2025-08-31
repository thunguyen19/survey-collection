from fastapi import APIRouter

from app.api.routes import (
    feedback_response_types,
    feedback_responses,
    feedback_sessions,
    items,
    login,
    organizations,
    private,
    survey_templates,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()

# Authentication routes
api_router.include_router(login.router)

# User management routes
api_router.include_router(users.router)

# Organization management routes
api_router.include_router(organizations.router)

# Core survey collection routes (admin-only for MVP)
api_router.include_router(survey_templates.router)
api_router.include_router(feedback_sessions.router)
api_router.include_router(feedback_responses.router)
api_router.include_router(feedback_response_types.router)

# Utility routes
api_router.include_router(utils.router)

# Legacy/example routes (keeping for compatibility)
api_router.include_router(items.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
