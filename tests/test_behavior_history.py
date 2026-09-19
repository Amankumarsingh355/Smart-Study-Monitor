from datetime import datetime, timedelta
from src.behavior.behavior_history import BehaviorHistory, BehaviorSample


def test_behavior_sample_creation():
    now = datetime.now()
    sample = BehaviorSample(timestamp=now, state="focused", confidence=0.95, duration=1.2)
    assert sample.timestamp == now
    assert sample.state == "focused"
    assert sample.confidence == 0.95
    assert sample.duration == 1.2


def test_behavior_history_bounded_deque():
    history = BehaviorHistory(max_samples=5)
    assert len(history) == 0

    for i in range(10):
        history.add(state=f"state_{i}", confidence=1.0)

    # Must be bounded to 5 items
    assert len(history) == 5
    recent = history.get_recent()
    assert [s.state for s in recent] == ["state_5", "state_6", "state_7", "state_8", "state_9"]
    assert history.get_last_sample().state == "state_9"


def test_behavior_history_get_window():
    history = BehaviorHistory(max_samples=100)
    base_time = datetime(2026, 9, 11, 10, 0, 0)

    # Add samples at T+0s, T+5s, T+10s, T+15s
    history.add(state="focused", timestamp=base_time)
    history.add(state="focused", timestamp=base_time + timedelta(seconds=5))
    history.add(state="looking_away", timestamp=base_time + timedelta(seconds=10))
    history.add(state="looking_away", timestamp=base_time + timedelta(seconds=15))

    ref = base_time + timedelta(seconds=15)
    # Window of 6 seconds should include samples at 10s and 15s (15 - 6 = 9s cutoff)
    window = history.get_window(seconds=6, reference_time=ref)
    assert len(window) == 2
    assert all(s.state == "looking_away" for s in window)

    # Window of 20 seconds includes all 4
    window_all = history.get_window(seconds=20, reference_time=ref)
    assert len(window_all) == 4


def test_behavior_history_dominant_state_and_distribution():
    history = BehaviorHistory(max_samples=100)
    base_time = datetime(2026, 9, 11, 10, 0, 0)

    # 3 focused, 1 phone_usage
    history.add(state="focused", timestamp=base_time)
    history.add(state="focused", timestamp=base_time + timedelta(seconds=1))
    history.add(state="phone_usage", timestamp=base_time + timedelta(seconds=2))
    history.add(state="focused", timestamp=base_time + timedelta(seconds=3))

    ref = base_time + timedelta(seconds=3)
    dom = history.get_dominant_state(seconds=10, reference_time=ref)
    assert dom == "focused"

    dist = history.get_state_distribution(seconds=10, reference_time=ref)
    assert dist["focused"] == 0.75
    assert dist["phone_usage"] == 0.25


def test_behavior_history_clear():
    history = BehaviorHistory(max_samples=10)
    history.add(state="focused")
    history.add(state="reading")
    assert len(history) == 2

    history.clear()
    assert len(history) == 0
    assert history.get_last_sample() is None
    assert history.get_window(seconds=10) == []
