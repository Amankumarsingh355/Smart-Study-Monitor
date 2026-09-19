from src.behavior.study_state import StudyState
from src.behavior.session_metrics import SessionMetrics


def test_session_metrics_initial_state():
    metrics = SessionMetrics()
    assert metrics.total_time == 0.0
    assert metrics.focused_time == 0.0
    assert metrics.distracted_time == 0.0
    assert metrics.phone_time == 0.0
    assert metrics.drowsy_time == 0.0
    assert metrics.no_face_time == 0.0
    assert metrics.posture_issue_time == 0.0
    assert metrics.reading_time == 0.0
    assert metrics.current_focus_streak == 0.0
    assert metrics.longest_focus_streak == 0.0
    assert metrics.distraction_count == 0
    assert metrics.distraction_episodes == []
    assert metrics.recovery_times == []
    assert metrics.average_recovery_time == 0.0
    assert metrics.focus_ratio == 1.0
    assert metrics.focus_percentage == 100.0


def test_session_metrics_productive_streak():
    metrics = SessionMetrics()

    # 10 seconds of focused study
    metrics.update(StudyState.FOCUSED, dt=10.0)
    assert metrics.focused_time == 10.0
    assert metrics.current_focus_streak == 10.0
    assert metrics.longest_focus_streak == 10.0

    # 15 seconds of reading (also productive)
    metrics.update(StudyState.READING, dt=15.0)
    assert metrics.reading_time == 15.0
    assert metrics.current_focus_streak == 25.0
    assert metrics.longest_focus_streak == 25.0
    assert metrics.distraction_count == 0


def test_session_metrics_distraction_and_recovery():
    metrics = SessionMetrics()

    # 1. Focus for 60s
    metrics.update(StudyState.FOCUSED, dt=60.0)
    assert metrics.current_focus_streak == 60.0
    assert metrics.longest_focus_streak == 60.0

    # 2. Distraction starts: Phone usage for 20s
    metrics.update(StudyState.PHONE_USAGE, dt=20.0)
    assert metrics.phone_time == 20.0
    assert metrics.distracted_time == 20.0
    assert metrics.distraction_count == 1
    assert metrics.current_focus_streak == 0.0  # Streak broken!
    assert metrics.longest_focus_streak == 60.0  # Preserved

    # 3. Focus resumes: 15s
    metrics.update(StudyState.FOCUSED, dt=15.0)
    # Distraction ended -> recovery recorded!
    assert len(metrics.distraction_episodes) == 1
    assert metrics.distraction_episodes[0] == 20.0
    assert len(metrics.recovery_times) == 1
    assert metrics.recovery_times[0] == 20.0
    assert metrics.average_recovery_time == 20.0
    assert metrics.current_focus_streak == 15.0

    # 4. Second distraction: Looking away for 40s
    metrics.update(StudyState.LOOKING_AWAY, dt=40.0)
    assert metrics.distraction_count == 2
    assert metrics.current_focus_streak == 0.0

    # 5. Recovery back to reading: 30s
    metrics.update(StudyState.READING, dt=30.0)
    assert len(metrics.recovery_times) == 2
    assert metrics.recovery_times[1] == 40.0
    # Average of 20 and 40 is 30.0
    assert metrics.average_recovery_time == 30.0
    assert metrics.current_focus_streak == 30.0


def test_session_metrics_focus_ratio():
    metrics = SessionMetrics()

    # 50s focused, 25s reading, 25s phone = 100s total
    metrics.update(StudyState.FOCUSED, dt=50.0)
    metrics.update(StudyState.READING, dt=25.0)
    metrics.update(StudyState.PHONE_USAGE, dt=25.0)

    assert metrics.total_time == 100.0
    assert metrics.focus_ratio == 0.75
    assert metrics.focus_percentage == 75.0


def test_session_metrics_format_duration():
    assert SessionMetrics.format_duration(45) == "45s"
    assert SessionMetrics.format_duration(125) == "02m 05s"
    assert SessionMetrics.format_duration(3665) == "01h 01m"


def test_session_metrics_summary_and_reset():
    metrics = SessionMetrics()
    metrics.update(StudyState.FOCUSED, dt=100.0)
    summary = metrics.summary()
    assert summary["total_time"] == 100.0
    assert summary["focused_time"] == 100.0
    assert summary["focus_ratio"] == 1.0

    metrics.reset()
    assert metrics.total_time == 0.0
    assert metrics.focused_time == 0.0
