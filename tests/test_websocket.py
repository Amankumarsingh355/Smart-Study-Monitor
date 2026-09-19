import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.session_service import SessionService, set_session_service
from backend.services.analytics_service import AnalyticsService, set_analytics_service
from backend.websocket.manager import connection_manager
from src.events.event_bus import event_bus
from src.behavior.study_state import StudyState


@pytest.fixture
def ws_client():
    """Fixture providing clean services and TestClient for WebSocket testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db_path = tmp.name

    service = SessionService(db_path=tmp_db_path)
    analytics = AnalyticsService(session_service=service)

    set_session_service(service)
    set_analytics_service(analytics)

    # Ensure connection manager starts clean
    connection_manager.active_connections.clear()

    client = TestClient(app)
    yield client, service

    service.db_manager.close()
    connection_manager.active_connections.clear()
    if os.path.exists(tmp_db_path):
        try:
            os.remove(tmp_db_path)
        except Exception:
            pass


def test_websocket_connect_and_handshake(ws_client):
    """Test 1: WebSocket connection establishes and sends handshake."""
    client, _ = ws_client

    with client.websocket_connect("/ws/monitor") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "CONNECTED"
        assert "Connected to Smart Study Monitor" in msg["message"]
        assert len(connection_manager.active_connections) == 1

    # After exit, disconnected
    assert len(connection_manager.active_connections) == 0


def test_websocket_ping_pong_heartbeat(ws_client):
    """Test 2: Heartbeat ping/pong keeps connection alive."""
    client, _ = ws_client

    with client.websocket_connect("/ws/monitor") as ws:
        # Initial greeting
        ws.receive_json()

        # Send JSON ping
        ws.send_json({"type": "ping"})
        reply = ws.receive_json()
        assert reply["type"] == "PONG"
        assert "timestamp" in reply

        # Send raw string ping
        ws.send_text("ping")
        reply2 = ws.receive_json()
        assert reply2["type"] == "PONG"


def test_websocket_broadcast_behavior_change(ws_client):
    """Test 3: Publishing BEHAVIOR_CHANGE pushes immediately to connected client."""
    client, _ = ws_client

    with client.websocket_connect("/ws/monitor") as ws:
        ws.receive_json()  # Handshake

        event_bus.publish("BEHAVIOR_CHANGE", {
            "type": "BEHAVIOR_CHANGE",
            "session_id": "SSM-WS-001",
            "previous": "FOCUSED",
            "current": "PHONE_USAGE",
            "confidence": 0.94,
            "focus_score": 82.0
        })

        msg = ws.receive_json()
        assert msg["type"] == "BEHAVIOR_CHANGE"
        assert msg["current"] == "PHONE_USAGE"
        assert msg["focus_score"] == 82.0


def test_websocket_broadcast_alert(ws_client):
    """Test 4: Alert publishing reaches connected client."""
    client, _ = ws_client

    with client.websocket_connect("/ws/monitor") as ws:
        ws.receive_json()  # Handshake

        event_bus.publish("ALERT", {
            "type": "ALERT",
            "alert_type": "PHONE_DETECTED",
            "severity": "WARNING",
            "message": "PUT THE PHONE AWAY!"
        })

        msg = ws.receive_json()
        assert msg["type"] == "ALERT"
        assert msg["alert_type"] == "PHONE_DETECTED"
        assert msg["message"] == "PUT THE PHONE AWAY!"


def test_websocket_session_lifecycle_broadcasts(ws_client):
    """Test 5: SessionManager start & end events are broadcast over WebSocket."""
    client, service = ws_client

    with client.websocket_connect("/ws/monitor") as ws:
        ws.receive_json()  # Handshake

        # Start session
        session = service.start_session("SSM-WS-LIFECYCLE")
        msg_start = ws.receive_json()
        assert msg_start["type"] == "SESSION_STARTED"
        assert msg_start["session_id"] == "SSM-WS-LIFECYCLE"

        # 1. Update state to FOCUSED -> triggers initial MONITOR_UPDATE
        service.session_manager.update(StudyState.FOCUSED, confidence=0.95, dt=10.0)
        msg_update = ws.receive_json()
        assert msg_update["type"] == "MONITOR_UPDATE"
        assert msg_update["state"] == "focused"

        # 2. Update state to PHONE_USAGE -> triggers BEHAVIOR_CHANGE
        service.session_manager.update(StudyState.PHONE_USAGE, confidence=0.92, dt=5.0)
        msg_change = ws.receive_json()
        assert msg_change["type"] == "BEHAVIOR_CHANGE"
        assert msg_change["current"] == "phone_usage"

        # 3. End session -> triggers SESSION_ENDED
        service.end_session("SSM-WS-LIFECYCLE")
        msg_end = ws.receive_json()
        assert msg_end["type"] == "SESSION_ENDED"
        assert msg_end["session_id"] == "SSM-WS-LIFECYCLE"


def test_websocket_multiple_clients(ws_client):
    """Test 6: Multiple concurrent WebSocket clients all receive broadcasts."""
    client, _ = ws_client

    with client.websocket_connect("/ws/monitor") as ws1:
        ws1.receive_json()

        with client.websocket_connect("/ws/monitor") as ws2:
            ws2.receive_json()
            assert len(connection_manager.active_connections) == 2

            event_bus.publish("ALERT", {
                "type": "ALERT",
                "message": "MULTI_CLIENT_BROADCAST"
            })

            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()

            assert msg1["message"] == "MULTI_CLIENT_BROADCAST"
            assert msg2["message"] == "MULTI_CLIENT_BROADCAST"
