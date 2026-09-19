"""
Smart Study Monitor — Unified Application Launcher.

Provides flexible startup modes:
  python run_smart_study_monitor.py             # Launches Backend + AI Vision Engine together
  python run_smart_study_monitor.py --backend   # Launches FastAPI REST & WebSocket server only
  python run_smart_study_monitor.py --camera    # Launches AI Perception Vision Engine only
"""

import sys
import os
import argparse
import threading
import time

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

import uvicorn

from backend.config import backend_config
from backend.main import app as fastapi_app
import app as cv_app


def start_backend(host: str = "127.0.0.1", port: int = 8000):
    """Run FastAPI Uvicorn server."""
    config = uvicorn.Config(
        app=fastapi_app,
        host=host,
        port=port,
        log_level="info",
        ws="auto"
    )
    server = uvicorn.Server(config)
    server.run()


def main():
    parser = argparse.ArgumentParser(description="Smart Study Monitor Unified Launcher")
    parser.add_argument("--backend", action="store_true", help="Run FastAPI backend only")
    parser.add_argument("--camera", action="store_true", help="Run OpenCV camera perception only")
    parser.add_argument("--port", type=int, default=8000, help="FastAPI backend port (default: 8000)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="FastAPI backend host (default: 127.0.0.1)")
    args = parser.parse_args()

    print("=" * 65)
    print("      SMART STUDY MONITOR — AI FOCUS & BEHAVIOR PLATFORM")
    print("=" * 65)

    if args.backend:
        print(f"\n[MODE] Starting FastAPI Backend on http://{args.host}:{args.port}...")
        print(f"       * REST API Docs: http://{args.host}:{args.port}/docs")
        print(f"       * WebSocket URL: ws://{args.host}:{args.port}/ws/monitor\n")
        start_backend(args.host, args.port)

    elif args.camera:
        print("\n[MODE] Starting Computer Vision Perception Loop...")
        print("       * Press 'q' in the OpenCV window to exit.\n")
        cv_app.main()

    else:
        # Full Unified Mode: FastAPI in daemon thread + OpenCV Camera in main thread
        print(f"\n[MODE] Starting Unified System (FastAPI Backend + AI Camera Engine)...")
        print(f"       * Live Web Dashboard : http://{args.host}:{args.port}/dashboard")
        print(f"       * REST API Docs      : http://{args.host}:{args.port}/docs")
        print(f"       * Live WebSocket     : ws://{args.host}:{args.port}/ws/monitor")
        print("       * Press 'q' in OpenCV window to stop study monitor.\n")

        backend_thread = threading.Thread(
            target=start_backend,
            args=(args.host, args.port),
            daemon=True
        )
        backend_thread.start()

        # Wait briefly for FastAPI to bind and open browser
        time.sleep(1.2)
        try:
            import webbrowser
            webbrowser.open(f"http://{args.host}:{args.port}/dashboard")
        except Exception:
            pass

        # Run camera loop in main thread (OpenCV GUI requires main thread on Windows)
        try:
            cv_app.main()
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down Smart Study Monitor...")


if __name__ == "__main__":
    main()
