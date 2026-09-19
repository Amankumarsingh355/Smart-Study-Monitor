import os
import sqlite3
from typing import Optional


class DatabaseManager:
    """
    Manages SQLite database connections and schema initialization.
    """

    def __init__(self, db_path: str = "data/study_monitor.db"):
        self.db_path = db_path
        if self.db_path != ":memory:":
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        self._connection: Optional[sqlite3.Connection] = None
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        """
        Get an active SQLite connection with row factory and foreign keys enabled.
        For :memory: databases, caches a persistent connection.
        """
        if self.db_path == ":memory:":
            if self._connection is None:
                self._connection = sqlite3.connect(":memory:", check_same_thread=False)
                self._connection.row_factory = sqlite3.Row
                self._connection.execute("PRAGMA foreign_keys = ON;")
            return self._connection

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def create_tables(self):
        """
        Initialize database schema for sessions, events, and behavior_samples.
        """
        conn = self.get_connection()
        try:
            with conn:
                conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL DEFAULT 0.0,
                    focus_score REAL DEFAULT 100.0,
                    focused_time REAL DEFAULT 0.0,
                    distracted_time REAL DEFAULT 0.0,
                    phone_time REAL DEFAULT 0.0,
                    drowsy_time REAL DEFAULT 0.0,
                    reading_time REAL DEFAULT 0.0,
                    no_face_time REAL DEFAULT 0.0,
                    posture_issue_time REAL DEFAULT 0.0,
                    longest_streak REAL DEFAULT 0.0,
                    distraction_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'ACTIVE',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 1.0,
                    metadata TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS behavior_samples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    state TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);
                CREATE INDEX IF NOT EXISTS idx_samples_session_id ON behavior_samples(session_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
                """)
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def close(self):
        """Close cached connection if present."""
        if self._connection:
            try:
                self._connection.close()
            except Exception:
                pass
            self._connection = None
