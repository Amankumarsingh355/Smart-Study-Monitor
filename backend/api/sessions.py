from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from backend.schemas.session import (
    SessionResponse,
    CurrentSessionResponse,
    StartSessionRequest
)
from backend.services.session_service import SessionService, get_session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/start", response_model=SessionResponse, status_code=201)
def start_session(
    request: Optional[StartSessionRequest] = None,
    service: SessionService = Depends(get_session_service)
):
    """Start a new study session."""
    sid = request.session_id if request else None
    session = service.start_session(session_id=sid)
    return session.to_dict()


@router.get("/current", response_model=CurrentSessionResponse)
def get_current_session(service: SessionService = Depends(get_session_service)):
    """Retrieve telemetry for the currently active study session."""
    current = service.get_current_session()
    if not current:
        raise HTTPException(status_code=404, detail="No study session is currently active")
    return current


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """End a study session and finalize its cumulative analytics."""
    session = service.end_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session.to_dict()


@router.get("", response_model=List[SessionResponse])
def list_sessions(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service: SessionService = Depends(get_session_service)
):
    """Retrieve a paginated list of previous study sessions."""
    sessions = service.get_sessions(limit=limit, offset=offset)
    return [s.to_dict() for s in sessions]


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """Fetch full details for a specific session by its ID."""
    session = service.get_session(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session.to_dict()
