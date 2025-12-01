from fastapi import APIRouter

from novel_system.backend.api import routes

api_router = APIRouter()
api_router.include_router(routes.router)

__all__ = ["api_router"]
