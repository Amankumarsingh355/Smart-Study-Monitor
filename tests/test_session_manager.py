import os
import tempfile
import time
from src.behavior.study_state import StudyState
from src.database.database import DatabaseManager
from src.database.repository import SessionRepository
from src.session.session_manager import SessionManager


def test_1_start_session():
    """Test 1: Start session -> Session created with unique ID and status ACTIVE."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)

    session = manager.start_session()
    assert session is not None
    assert session.id.startswith("SSM-")
    assert session.status == "ACTIVE"
    assert manager.is_active is True

    # Verify in DB
    in_db = repo.get_session(session.id)
    assert in_db is not None
    assert in_db.id == session.id


def test_2_focus_time():
    """Test 2: Student focused for 120 seconds -> focused_time ≈ 120s."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)
    manager.start_session("SSM-TEST-FOCUS")

    # Simulate 120 seconds of focused study in steps
    for _ in range(12):
        manager.update(StudyState.FOCUSED, confidence=0.95, dt=10.0)

    summary = manager.summary()
    assert summary["focused_time"] == 120.0
    assert summary["total_time"] == 120.0
    assert summary["focus_ratio"] == 1.0


def test_3_phone_detection_event():
    """Test 3: Phone detected for 10 seconds -> Single aggregated PHONE_DETECTED event with duration ≈ 10s."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)
    manager.start_session("SSM-TEST-PHONE")

    start_ts = 1000.0
    # Phone detected for 10 consecutive seconds (dt = 1.0s)
    for i in range(10):
        manager.update(
            StudyState.PHONE_USAGE,
            confidence=0.92,
            dt=1.0,
            current_time=start_ts + i
        )

    # During active phone detection, event is not yet completed in DB
    events_mid = repo.get_session_events("SSM-TEST-PHONE")
    assert len(events_mid) == 0

    # Phone is put down -> student resumes focus at T+10s
    manager.update(
        StudyState.FOCUSED,
        confidence=0.95,
        dt=1.0,
        current_time=start_ts + 10.0
    )

    # Now the completed event is saved!
    events_after = repo.get_session_events("SSM-TEST-PHONE")
    assert len(events_after) == 1
    assert events_after[0].event_type == "PHONE_DETECTED"
    assert events_after[0].duration == 10.0
    assert events_after[0].confidence == 0.92


def test_4_drowsiness_event():
    """Test 4: Drowsy state -> Single DROWSINESS event created on resolution."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)
    manager.start_session("SSM-TEST-DROWSY")

    start_ts = 2000.0
    for i in range(5):
        manager.update(
            StudyState.DROWSY,
            confidence=0.85,
            dt=1.0,
            current_time=start_ts + i
        )

    # Student wakes up
    manager.update(
        StudyState.FOCUSED,
        confidence=0.90,
        dt=1.0,
        current_time=start_ts + 5.0
    )

    events = repo.get_session_events("SSM-TEST-DROWSY")
    assert len(events) == 1
    assert events[0].event_type == "DROWSINESS"
    assert events[0].duration == 5.0


def test_5_end_session():
    """Test 5: End session -> Final metrics calculated and database record updated to COMPLETED."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)
    manager.start_session("SSM-TEST-END")

    # 40s focus, 10s phone
    manager.update(StudyState.FOCUSED, confidence=0.95, dt=40.0)
    manager.update(StudyState.PHONE_USAGE, confidence=0.90, dt=10.0)

    final_session = manager.end_session()
    assert final_session.status == "COMPLETED"
    assert final_session.duration == 50.0
    assert final_session.focus_score == 80.0  # 40 / 50 * 100 = 80%
    assert final_session.focused_time == 40.0
    assert final_session.phone_time == 10.0

    # Ensure ongoing phone event was also finalized at session close
    events = repo.get_session_events("SSM-TEST-END")
    assert len(events) == 1
    assert events[0].event_type == "PHONE_DETECTED"


def test_6_restart_persistence():
    """Test 6: Critical restart test -> Closing application and reopening preserves past sessions."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        # Run Session 1
        db1 = DatabaseManager(tmp_path)
        repo1 = SessionRepository(db1)
        manager1 = SessionManager(repo1)
        manager1.start_session("SSM-PERSIST-001")
        manager1.update(StudyState.FOCUSED, confidence=0.95, dt=60.0)
        manager1.end_session()
        db1.close()

        # Simulate Application Restart: New instances pointing to same SQLite file
        db2 = DatabaseManager(tmp_path)
        repo2 = SessionRepository(db2)
        past_session = repo2.get_session("SSM-PERSIST-001")

        assert past_session is not None
        assert past_session.id == "SSM-PERSIST-001"
        assert past_session.status == "COMPLETED"
        assert past_session.focused_time == 60.0

        # Start Session 2 on reopened DB
        manager2 = SessionManager(repo2)
        manager2.start_session("SSM-PERSIST-002")
        manager2.update(StudyState.READING, confidence=0.88, dt=45.0)
        manager2.end_session()

        # Verify all sessions are retrievable
        all_sessions = repo2.get_sessions()
        assert len(all_sessions) == 2
        session_ids = [s.id for s in all_sessions]
        assert "SSM-PERSIST-001" in session_ids
        assert "SSM-PERSIST-002" in session_ids

        db2.close()
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def test_7_no_duplicate_event_per_frame():
    """Test 7: 100 consecutive frames in PHONE_USAGE state produce exactly ONE aggregated event on completion."""
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)
    manager = SessionManager(repo)
    manager.start_session("SSM-DEDUP-001")

    base_ts = 5000.0
    # Simulate 100 video frames at 30 FPS (~3.33 seconds)
    for frame_idx in range(100):
        manager.update(
            StudyState.PHONE_USAGE,
            confidence=0.93,
            dt=1.0 / 30.0,
            current_time=base_ts + (frame_idx * (1.0 / 30.0))
        )

    # During the 100 frames, no duplicate events are in the database!
    assert len(repo.get_session_events("SSM-DEDUP-001")) == 0

    # End of distraction
    manager.update(
        StudyState.FOCUSED,
        confidence=0.95,
        dt=1.0 / 30.0,
        current_time=base_ts + (100 * (1.0 / 30.0))
    )

    # Exactly ONE event is persisted
    events = repo.get_session_events("SSM-DEDUP-001")
    assert len(events) == 1
    assert events[0].event_type == "PHONE_DETECTED"
    assert round(events[0].duration, 1) == 3.3
