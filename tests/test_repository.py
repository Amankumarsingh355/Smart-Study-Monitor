from datetime import datetime
from src.database.database import DatabaseManager
from src.database.models import SessionRecord, EventRecord, BehaviorSampleRecord
from src.database.repository import SessionRepository


def test_session_repository_create_and_get():
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)

    session = SessionRecord(
        id="SSM-TEST-001",
        start_time=datetime.now().isoformat(),
        status="ACTIVE"
    )
    repo.create_session(session)

    fetched = repo.get_session("SSM-TEST-001")
    assert fetched is not None
    assert fetched.id == "SSM-TEST-001"
    assert fetched.status == "ACTIVE"
    assert fetched.duration == 0.0


def test_session_repository_end_session():
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)

    session = SessionRecord(
        id="SSM-TEST-002",
        start_time=datetime.now().isoformat(),
        status="ACTIVE"
    )
    repo.create_session(session)

    end_time = datetime.now().isoformat()
    repo.end_session(
        session_id="SSM-TEST-002",
        end_time=end_time,
        duration=3600.0,
        focus_score=85.0,
        metrics={
            "focused_time": 3000.0,
            "distracted_time": 600.0,
            "phone_time": 300.0,
            "drowsy_time": 100.0,
            "reading_time": 200.0,
            "longest_streak": 1800.0,
            "distraction_count": 3
        }
    )

    finalized = repo.get_session("SSM-TEST-002")
    assert finalized.status == "COMPLETED"
    assert finalized.duration == 3600.0
    assert finalized.focus_score == 85.0
    assert finalized.focused_time == 3000.0
    assert finalized.distraction_count == 3


def test_session_repository_events_and_samples():
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)

    session = SessionRecord(id="SSM-TEST-003", start_time=datetime.now().isoformat())
    repo.create_session(session)

    # Save event
    event = EventRecord(
        session_id="SSM-TEST-003",
        event_type="PHONE_DETECTED",
        start_time="2026-09-11T10:00:00",
        end_time="2026-09-11T10:00:15",
        duration=15.0,
        confidence=0.92,
        metadata='{"app": "instagram"}'
    )
    event_id = repo.save_event(event)
    assert event_id > 0

    events = repo.get_session_events("SSM-TEST-003")
    assert len(events) == 1
    assert events[0].event_type == "PHONE_DETECTED"
    assert events[0].duration == 15.0

    # Save behavior sample
    sample = BehaviorSampleRecord(
        session_id="SSM-TEST-003",
        timestamp="2026-09-11T10:00:05",
        state="phone_usage",
        confidence=0.92
    )
    repo.save_behavior_sample(sample)

    samples = repo.get_session_samples("SSM-TEST-003")
    assert len(samples) == 1
    assert samples[0].state == "phone_usage"


def test_session_repository_cascade_delete():
    db = DatabaseManager(":memory:")
    repo = SessionRepository(db)

    session = SessionRecord(id="SSM-TEST-004", start_time=datetime.now().isoformat())
    repo.create_session(session)

    event = EventRecord(session_id="SSM-TEST-004", event_type="DROWSY", start_time="2026-09-11T10:00:00")
    repo.save_event(event)

    sample = BehaviorSampleRecord(session_id="SSM-TEST-004", timestamp="2026-09-11T10:00:00", state="drowsy")
    repo.save_behavior_sample(sample)

    assert len(repo.get_session_events("SSM-TEST-004")) == 1
    assert len(repo.get_session_samples("SSM-TEST-004")) == 1

    # Delete session
    assert repo.delete_session("SSM-TEST-004") is True
    assert repo.get_session("SSM-TEST-004") is None

    # Foreign key CASCADE should remove child rows
    assert len(repo.get_session_events("SSM-TEST-004")) == 0
    assert len(repo.get_session_samples("SSM-TEST-004")) == 0
