import json
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from backend.websocket.manager import connection_manager, ConnectionManager
from src.events.event_bus import event_bus


# Standard protocol event types
class MessageType:
    MONITOR_UPDATE = "MONITOR_UPDATE"
    BEHAVIOR_CHANGE = "BEHAVIOR_CHANGE"
    ALERT = "ALERT"
    SESSION_STARTED = "SESSION_STARTED"
    SESSION_ENDED = "SESSION_ENDED"
    METRIC_UPDATE = "METRIC_UPDATE"
    PONG = "PONG"
    ERROR = "ERROR"


def bridge_event_bus_to_websocket(manager: ConnectionManager = connection_manager) -> None:
    """
    Subscribes the WebSocket ConnectionManager to the application event bus.
    All events published across the system will be automatically broadcast to active clients.
    """
    def _forwarder(data: dict):
        manager.broadcast_sync(data)

    event_bus.subscribe("*", _forwarder)


async def websocket_endpoint(
    websocket: WebSocket,
    manager: ConnectionManager = connection_manager
) -> None:
    """
    WebSocket endpoint handler for /ws/monitor.
    Manages connection lifecycle and incoming client heartbeats.
    """
    await manager.connect(websocket)
    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)
                # Handle client ping keepalive
                if msg.get("type") in ("ping", "PING"):
                    await websocket.send_json({
                        "type": MessageType.PONG,
                        "timestamp": datetime.now().isoformat()
                    })
            except json.JSONDecodeError:
                if raw_data.strip().lower() == "ping":
                    await websocket.send_json({
                        "type": MessageType.PONG,
                        "timestamp": datetime.now().isoformat()
                    })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
