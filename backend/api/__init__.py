from fastapi import APIRouter
from .sessions import router as sessions_router
from .events import router as events_router
from .analytics import router as analytics_router

api_v1_router = APIRouter()
api_v1_router.include_router(sessions_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(analytics_router)

__all__ = ["api_v1_router", "sessions_router", "events_router", "analytics_router"]
