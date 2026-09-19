from typing import List
from fastapi import APIRouter, HTTPException, Depends, Query

from backend.schemas.event import EventResponse
from backend.services.session_service import SessionService, get_session_service

router = APIRouter(tags=["events"])


@router.get("/sessions/{session_id}/events", response_model=List[EventResponse])
def get_session_events(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """Retrieve all discrete behavioral events for a specific study session."""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    events = service.get_session_events(session_id)
    return [e.to_dict() for e in events]


@router.get("/events", response_model=List[EventResponse])
def list_events(
    limit: int = Query(100, ge=1, le=1000),
    service: SessionService = Depends(get_session_service)
):
    """Retrieve recent behavioral events across all study sessions."""
    events = service.get_all_events(limit=limit)
    return [e.to_dict() for e in events]
