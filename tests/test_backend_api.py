import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.session_service import SessionService, set_session_service
from backend.services.analytics_service import AnalyticsService, set_analytics_service
from src.behavior.study_state import StudyState
from src.database.models import EventRecord


@pytest.fixture
def test_client():
    """Fixture initializing a clean in-memory database and test client."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    service = SessionService(db_path=tmp_db_path)
    analytics = AnalyticsService(session_service=service)

    set_session_service(service)
    set_analytics_service(analytics)

    client = TestClient(app)
    yield client, service

    service.db_manager.close()
    if os.path.exists(tmp_db_path):
        try:
            os.remove(tmp_db_path)
        except Exception:
            pass


def test_root_and_health(test_client):
    client, _ = test_client

    # 1. Root endpoint
    res_root = client.get("/")
    assert res_root.status_code == 200
    data = res_root.json()
    assert data["application"] == "Smart Study Monitor API"
    assert data["status"] == "running"

    # 2. Health check endpoint
    res_health = client.get("/health")
    assert res_health.status_code == 200
    h_data = res_health.json()
    assert h_data["status"] == "healthy"
    assert h_data["database"] is True

    # 3. Docs endpoint
    res_docs = client.get("/docs")
    assert res_docs.status_code == 200

    # 4. Live Dashboard endpoint
    res_dash = client.get("/dashboard")
    assert res_dash.status_code == 200
    assert "Smart Study Monitor" in res_dash.text


def test_session_lifecycle_api(test_client):
    client, service = test_client

    # 1. Start Session via API
    res_start = client.post("/api/v1/sessions/start", json={"session_id": "SSM-API-001"})
    assert res_start.status_code == 201
    s_data = res_start.json()
    assert s_data["id"] == "SSM-API-001"
    assert s_data["status"] == "ACTIVE"

    # 2. Current Session API
    res_curr = client.get("/api/v1/sessions/current")
    assert res_curr.status_code == 200
    curr_data = res_curr.json()
    assert curr_data["session_id"] == "SSM-API-001"
    assert curr_data["status"] == "ACTIVE"
    assert curr_data["focus_score"] == 100.0

    # 3. Simulate study updates in background
    service.session_manager.update(StudyState.FOCUSED, confidence=0.95, dt=30.0)
    service.session_manager.update(StudyState.PHONE_USAGE, confidence=0.90, dt=10.0)

    # 4. End Session via API
    res_end = client.post("/api/v1/sessions/SSM-API-001/end")
    assert res_end.status_code == 200
    end_data = res_end.json()
    assert end_data["status"] == "COMPLETED"
    assert end_data["duration"] == 40.0
    assert end_data["focused_time"] == 30.0

    # 5. Get Individual Session
    res_get = client.get("/api/v1/sessions/SSM-API-001")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == "SSM-API-001"

    # 6. List Sessions
    res_list = client.get("/api/v1/sessions")
    assert res_list.status_code == 200
    all_sessions = res_list.json()
    assert len(all_sessions) >= 1
    assert all_sessions[0]["id"] == "SSM-API-001"


def test_session_events_api(test_client):
    client, service = test_client

    # Start session and record event
    service.start_session("SSM-EVENT-001")
    service.repository.save_event(EventRecord(
        session_id="SSM-EVENT-001",
        event_type="PHONE_DETECTED",
        start_time="2026-09-11T10:00:00",
        end_time="2026-09-11T10:00:12",
        duration=12.0,
        confidence=0.94
    ))
    service.repository.save_event(EventRecord(
        session_id="SSM-EVENT-001",
        event_type="LOOKING_AWAY",
        start_time="2026-09-11T10:00:20",
        end_time="2026-09-11T10:00:28",
        duration=8.0,
        confidence=0.85
    ))

    # Query events for session
    res_events = client.get("/api/v1/sessions/SSM-EVENT-001/events")
    assert res_events.status_code == 200
    events = res_events.json()
    assert len(events) == 2
    assert events[0]["event_type"] == "PHONE_DETECTED"
    assert events[0]["duration"] == 12.0
    assert events[1]["event_type"] == "LOOKING_AWAY"

    # Query all events
    res_all = client.get("/api/v1/events")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 2


def test_analytics_api(test_client):
    client, service = test_client

    # Session 1
    s1 = service.start_session("SSM-ANALYTICS-001")
    service.session_manager.update(StudyState.FOCUSED, confidence=0.95, dt=80.0)
    service.session_manager.update(StudyState.READING, confidence=0.90, dt=20.0)
    service.end_session("SSM-ANALYTICS-001")

    # Session Analytics
    res_session_an = client.get("/api/v1/analytics/session/SSM-ANALYTICS-001")
    assert res_session_an.status_code == 200
    an_data = res_session_an.json()
    assert an_data["session_id"] == "SSM-ANALYTICS-001"
    assert an_data["duration"] == 100.0
    assert an_data["focus_score"] == 100.0

    # Aggregated Summary
    res_summary = client.get("/api/v1/analytics/summary")
    assert res_summary.status_code == 200
    sum_data = res_summary.json()
    assert sum_data["total_sessions"] >= 1
    assert sum_data["total_study_time"] >= 100.0
    assert sum_data["average_focus_score"] == 100.0


def test_error_handling_404(test_client):
    client, _ = test_client

    # Query nonexistent session
    res = client.get("/api/v1/sessions/nonexistent-session-id")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

    # Query events for nonexistent session
    res_ev = client.get("/api/v1/sessions/nonexistent-session-id/events")
    assert res_ev.status_code == 404

    # Query analytics for nonexistent session
    res_an = client.get("/api/v1/analytics/session/nonexistent-session-id")
    assert res_an.status_code == 404
