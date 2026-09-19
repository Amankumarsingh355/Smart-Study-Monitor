from fastapi import APIRouter, HTTPException, Depends

from backend.schemas.analytics import SessionAnalyticsResponse, AggregatedAnalyticsResponse
from backend.services.analytics_service import AnalyticsService, get_analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AggregatedAnalyticsResponse)
@router.get("/overview", response_model=AggregatedAnalyticsResponse)
@router.get("/today", response_model=AggregatedAnalyticsResponse)
def get_aggregated_analytics(service: AnalyticsService = Depends(get_analytics_service)):
    """Retrieve statistical summary and total study metrics across all sessions."""
    return service.get_aggregated_analytics()


@router.get("/session/{session_id}", response_model=SessionAnalyticsResponse)
def get_session_analytics(
    session_id: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    """Retrieve in-depth analytics and event breakdown for a specific study session."""
    analytics = service.get_session_analytics(session_id=session_id)
    if not analytics:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return analytics


@router.get("/recommendations")
def get_study_recommendations(service: AnalyticsService = Depends(get_analytics_service)):
    """Retrieve personalized AI recommendations and study patterns based on past sessions."""
    return service.get_recommendations()
