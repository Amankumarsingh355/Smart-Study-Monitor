from typing import List, Optional, Dict, Any

from backend.config import backend_config
from src.database.database import DatabaseManager
from src.database.models import SessionRecord, EventRecord
from src.database.repository import SessionRepository
from src.session.session_manager import SessionManager


class SessionService:
    """
    Business service for managing study sessions and bridging
    FastAPI controllers with repository persistence and active session lifecycle.
    """

    def __init__(self, db_path: Optional[str] = None):
        target_db = db_path or backend_config.db_path
        self.db_manager = DatabaseManager(target_db)
        self.repository = SessionRepository(self.db_manager)
        self.session_manager = SessionManager(self.repository)

    def start_session(self, session_id: Optional[str] = None) -> SessionRecord:
        """Start a new active study session."""
        return self.session_manager.start_session(session_id=session_id)

    def end_session(self, session_id: Optional[str] = None) -> Optional[SessionRecord]:
        """
        End a study session.
        If session_id matches current active session, end via session manager.
        Otherwise mark session completed in repository if still active.
        """
        if self.session_manager.is_active:
            if session_id is None or session_id == self.session_manager.session_id:
                return self.session_manager.end_session()

        # Target session is not currently running active in session manager
        if session_id:
            record = self.repository.get_session(session_id)
            if record and record.status == "ACTIVE":
                self.repository.end_session(
                    session_id=session_id,
                    end_time=record.created_at,
                    duration=record.duration,
                    focus_score=record.focus_score,
                    metrics=record.to_dict()
                )
                return self.repository.get_session(session_id)
            return record

        return None

    def get_current_session(self) -> Optional[Dict[str, Any]]:
        """
        Return the state and live metrics of the currently active study session.
        Returns None if no session is currently active.
        """
        if not self.session_manager.is_active:
            # Fallback: check if latest session in database is ACTIVE
            recent = self.repository.get_sessions(limit=1)
            if recent and recent[0].status == "ACTIVE":
                s = recent[0]
                return {
                    "session_id": s.id,
                    "status": s.status,
                    "state": "FOCUSED",
                    "focus_score": s.focus_score,
                    "duration": s.duration,
                    "focused_time": s.focused_time,
                    "distracted_time": s.distracted_time,
                    "phone_time": s.phone_time,
                    "drowsy_time": s.drowsy_time,
                    "reading_time": s.reading_time,
                    "current_streak": 0.0,
                    "longest_streak": s.longest_streak,
                    "distraction_count": s.distraction_count,
                    "average_recovery_time": 0.0
                }
            return None

        # Return live in-memory metrics from active session manager
        curr = self.session_manager.current_session
        metrics = self.session_manager.session_metrics
        return {
            "session_id": curr.id,
            "status": curr.status,
            "state": "FOCUSED",
            "focus_score": metrics.focus_percentage,
            "duration": metrics.total_time,
            "focused_time": metrics.focused_time,
            "distracted_time": metrics.distracted_time,
            "phone_time": metrics.phone_time,
            "drowsy_time": metrics.drowsy_time,
            "reading_time": metrics.reading_time,
            "current_streak": metrics.current_focus_streak,
            "longest_streak": metrics.longest_focus_streak,
            "distraction_count": metrics.distraction_count,
            "average_recovery_time": metrics.average_recovery_time
        }

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """Fetch a specific session by ID."""
        return self.repository.get_session(session_id)

    def get_sessions(self, limit: int = 50, offset: int = 0) -> List[SessionRecord]:
        """List historical sessions with pagination."""
        return self.repository.get_sessions(limit=limit, offset=offset)

    def get_session_events(self, session_id: str) -> List[EventRecord]:
        """Retrieve all events recorded for a session."""
        return self.repository.get_session_events(session_id)

    def get_all_events(self, limit: int = 100) -> List[EventRecord]:
        """Retrieve recent events across all sessions."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.execute(
                "SELECT * FROM events ORDER BY start_time DESC LIMIT ?",
                (limit,)
            )
            return [EventRecord.from_row(row) for row in cursor.fetchall()]
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()


# Shared singleton instance
_session_service_instance: Optional[SessionService] = None


def get_session_service() -> SessionService:
    global _session_service_instance
    if _session_service_instance is None:
        _session_service_instance = SessionService()
    return _session_service_instance


def set_session_service(service: SessionService) -> None:
    """Helper to inject custom test service."""
    global _session_service_instance
    _session_service_instance = service
