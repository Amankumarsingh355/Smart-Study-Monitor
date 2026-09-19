import sqlite3
from typing import List, Optional, Dict, Any
from .database import DatabaseManager
from .models import SessionRecord, EventRecord, BehaviorSampleRecord


class SessionRepository:
    """
    Data access repository for Sessions, Events, and Behavior Samples.
    Encapsulates all SQL query execution and transactional safety.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def _get_conn(self) -> sqlite3.Connection:
        return self.db_manager.get_connection()

    def create_session(self, session: SessionRecord) -> SessionRecord:
        """Insert a newly created session record."""
        conn = self._get_conn()
        try:
            with conn:
                conn.execute("""
                INSERT INTO sessions (
                    id, start_time, end_time, duration, focus_score,
                    focused_time, distracted_time, phone_time, drowsy_time,
                    reading_time, no_face_time, posture_issue_time,
                    longest_streak, distraction_count, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.id, session.start_time, session.end_time, session.duration,
                    session.focus_score, session.focused_time, session.distracted_time,
                    session.phone_time, session.drowsy_time, session.reading_time,
                    session.no_face_time, session.posture_issue_time,
                    session.longest_streak, session.distraction_count,
                    session.status, session.created_at
                ))
            return session
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def update_session(self, session: SessionRecord) -> None:
        """Update existing session fields."""
        conn = self._get_conn()
        try:
            with conn:
                conn.execute("""
                UPDATE sessions SET
                    end_time = ?,
                    duration = ?,
                    focus_score = ?,
                    focused_time = ?,
                    distracted_time = ?,
                    phone_time = ?,
                    drowsy_time = ?,
                    reading_time = ?,
                    no_face_time = ?,
                    posture_issue_time = ?,
                    longest_streak = ?,
                    distraction_count = ?,
                    status = ?
                WHERE id = ?
                """, (
                    session.end_time, session.duration, session.focus_score,
                    session.focused_time, session.distracted_time, session.phone_time,
                    session.drowsy_time, session.reading_time, session.no_face_time,
                    session.posture_issue_time, session.longest_streak,
                    session.distraction_count, session.status, session.id
                ))
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def end_session(
        self,
        session_id: str,
        end_time: str,
        duration: float,
        focus_score: float,
        metrics: Optional[Dict[str, Any]] = None
    ) -> None:
        """Finalize and close an active study session."""
        metrics = metrics or {}
        conn = self._get_conn()
        try:
            with conn:
                conn.execute("""
                UPDATE sessions SET
                    end_time = ?,
                    duration = ?,
                    focus_score = ?,
                    focused_time = ?,
                    distracted_time = ?,
                    phone_time = ?,
                    drowsy_time = ?,
                    reading_time = ?,
                    no_face_time = ?,
                    posture_issue_time = ?,
                    longest_streak = ?,
                    distraction_count = ?,
                    status = 'COMPLETED'
                WHERE id = ?
                """, (
                    end_time,
                    duration,
                    focus_score,
                    metrics.get("focused_time", 0.0),
                    metrics.get("distracted_time", 0.0),
                    metrics.get("phone_time", 0.0),
                    metrics.get("drowsy_time", 0.0),
                    metrics.get("reading_time", 0.0),
                    metrics.get("no_face_time", 0.0),
                    metrics.get("posture_issue_time", 0.0),
                    metrics.get("longest_streak", 0.0),
                    metrics.get("distraction_count", 0),
                    session_id
                ))
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def save_event(self, event: EventRecord) -> int:
        """Save a discrete behavioral episode."""
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute("""
                INSERT INTO events (
                    session_id, event_type, start_time, end_time,
                    duration, confidence, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    event.session_id, event.event_type, event.start_time,
                    event.end_time, event.duration, event.confidence, event.metadata
                ))
                event.id = cursor.lastrowid
                return cursor.lastrowid
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def save_behavior_sample(self, sample: BehaviorSampleRecord) -> int:
        """Save a periodic behavior state sample."""
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute("""
                INSERT INTO behavior_samples (
                    session_id, timestamp, state, confidence
                ) VALUES (?, ?, ?, ?)
                """, (
                    sample.session_id, sample.timestamp, sample.state, sample.confidence
                ))
                sample.id = cursor.lastrowid
                return cursor.lastrowid
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def save_behavior_samples_batch(self, samples: List[BehaviorSampleRecord]) -> None:
        """Efficiently batch-insert periodic behavior samples."""
        if not samples:
            return
        conn = self._get_conn()
        try:
            with conn:
                conn.executemany("""
                INSERT INTO behavior_samples (
                    session_id, timestamp, state, confidence
                ) VALUES (?, ?, ?, ?)
                """, [
                    (s.session_id, s.timestamp, s.state, s.confidence)
                    for s in samples
                ])
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """Fetch a single session by its unique ID."""
        conn = self._get_conn()
        try:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            return SessionRecord.from_row(row) if row else None
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def get_sessions(self, limit: int = 50, offset: int = 0) -> List[SessionRecord]:
        """Retrieve recent sessions sorted descending by start time."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM sessions ORDER BY start_time DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [SessionRecord.from_row(row) for row in cursor.fetchall()]
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def get_session_events(self, session_id: str) -> List[EventRecord]:
        """Retrieve all events recorded for a session."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM events WHERE session_id = ? ORDER BY start_time ASC",
                (session_id,)
            )
            return [EventRecord.from_row(row) for row in cursor.fetchall()]
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def get_session_samples(
        self,
        session_id: str,
        limit: int = 1000
    ) -> List[BehaviorSampleRecord]:
        """Retrieve timeline samples recorded for a session."""
        conn = self._get_conn()
        try:
            cursor = conn.execute(
                "SELECT * FROM behavior_samples WHERE session_id = ? ORDER BY timestamp ASC LIMIT ?",
                (session_id, limit)
            )
            return [BehaviorSampleRecord.from_row(row) for row in cursor.fetchall()]
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its associated events and samples (CASCADE)."""
        conn = self._get_conn()
        try:
            with conn:
                cursor = conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                return cursor.rowcount > 0
        finally:
            if self.db_manager.db_path != ":memory:":
                conn.close()
