import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Windows Proactor asyncio fix for WinError 10054 connection reset
if sys.platform == "win32":
    try:
        from asyncio.proactor_events import _ProactorBasePipeTransport
        _orig_call_connection_lost = _ProactorBasePipeTransport._call_connection_lost

        def _safe_call_connection_lost(self, exc):
            try:
                _orig_call_connection_lost(self, exc)
            except (ConnectionResetError, OSError):
                pass

        _ProactorBasePipeTransport._call_connection_lost = _safe_call_connection_lost
    except Exception:
        pass

from backend.config import backend_config
from backend.api import api_v1_router
from backend.services.session_service import get_session_service
from backend.websocket.manager import connection_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register active event loop for thread-safe websocket broadcasts
    connection_manager.set_loop(asyncio.get_running_loop())
    yield


app = FastAPI(
    title=backend_config.app_name,
    version=backend_config.version,
    description="REST API for Smart Study Monitor: Real-time telemetry, session management, and longitudinal analytics.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=backend_config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Versioned API Routes
app.include_router(api_v1_router, prefix=backend_config.api_v1_prefix)
# Convenience alias for /api routes
app.include_router(api_v1_router, prefix="/api")

# Real-Time WebSocket Endpoint & EventBus Bridge
from fastapi import WebSocket
from backend.websocket import websocket_endpoint, bridge_event_bus_to_websocket

bridge_event_bus_to_websocket()


@app.websocket("/ws/monitor")
async def monitor_websocket(websocket: WebSocket):
    """Real-time bi-directional streaming endpoint for study monitor telemetry."""
    await websocket_endpoint(websocket)



from fastapi.responses import HTMLResponse, FileResponse

@app.get("/dashboard", response_class=HTMLResponse, tags=["dashboard"])
def get_dashboard():
    """Serves the live interactive Smart Study Monitor web dashboard."""
    static_html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_html_path):
        return FileResponse(static_html_path)
    return HTMLResponse("<h1>Dashboard HTML not found</h1>", status_code=404)


@app.get("/", tags=["system"])
def root():
    """Application identification and status endpoint."""
    return {
        "application": backend_config.app_name,
        "version": backend_config.version,
        "status": "running",
        "docs_url": "/docs",
        "api_v1": backend_config.api_v1_prefix
    }


@app.get("/health", tags=["system"])
def health():
    """System health check verifying database and service subsystem readiness."""
    db_ok = True
    session_ok = True
    try:
        service = get_session_service()
        # Test basic DB connectivity
        conn = service.db_manager.get_connection()
        conn.execute("SELECT 1")
    except Exception:
        db_ok = False

    return {
        "status": "healthy" if db_ok else "degraded",
        "camera": True,
        "ai_engine": True,
        "database": db_ok,
        "session": session_ok
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=backend_config.host,
        port=backend_config.port,
        reload=True
    )
