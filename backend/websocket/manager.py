import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages active WebSocket client connections, disconnections,
    and thread-safe broadcast dispatches across threads.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Explicitly configure the event loop for cross-thread dispatches."""
        self._loop = loop

    async def connect(self, websocket: WebSocket) -> None:
        """Accept an incoming connection and register it."""
        await websocket.accept()
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
        self.active_connections.append(websocket)
        await websocket.send_json({
            "type": "CONNECTED",
            "message": "Connected to Smart Study Monitor WebSocket",
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a disconnected client from the active list."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Send a JSON message to all currently connected clients."""
        dead_connections: List[WebSocket] = []
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

    def broadcast_sync(self, message: Dict[str, Any]) -> None:
        """
        Thread-safe synchronous broadcast entrypoint.
        Dispatches broadcast coroutine into the server's event loop from any thread.
        """
        if not self.active_connections:
            return

        # If a server event loop is active, schedule cleanly across threads
        loop = self._loop
        if loop is not None and loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast(message), loop)
                return
            except Exception:
                pass

        # Fallback if called within the same thread's active loop
        try:
            current_loop = asyncio.get_running_loop()
            if current_loop.is_running():
                current_loop.create_task(self.broadcast(message))
        except RuntimeError:
            pass


# Global connection manager singleton
connection_manager = ConnectionManager()
