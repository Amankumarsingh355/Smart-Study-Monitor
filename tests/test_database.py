import sqlite3
from src.database.database import DatabaseManager


def test_database_initialization_in_memory():
    db = DatabaseManager(":memory:")
    conn = db.get_connection()
    assert isinstance(conn, sqlite3.Connection)

    # Check foreign keys pragma
    cursor = conn.execute("PRAGMA foreign_keys;")
    assert cursor.fetchone()[0] == 1

    # Check tables exist
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    assert "sessions" in tables
    assert "events" in tables
    assert "behavior_samples" in tables


def test_database_indices_created():
    db = DatabaseManager(":memory:")
    conn = db.get_connection()

    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indices = {row[0] for row in cursor.fetchall()}
    assert "idx_events_session_id" in indices
    assert "idx_samples_session_id" in indices
    assert "idx_sessions_start_time" in indices
