from src.events.event_manager import EventManager


def test_event_manager_transient_noise_ignored():
    manager = EventManager(phone_persistence_seconds=1.0)
    base_time = 100.0

    # Phone appears at t=100.0 (duration = 0.0s)
    event = manager.update_phone_detection(is_visible=True, current_time=base_time)
    assert event is None
    assert not manager.is_phone_event_active

    # Phone still visible at t=100.2 (duration = 0.2s)
    event = manager.update_phone_detection(is_visible=True, current_time=base_time + 0.2)
    assert event is None
    assert not manager.is_phone_event_active

    # Phone still visible at t=100.5 (duration = 0.5s)
    event = manager.update_phone_detection(is_visible=True, current_time=base_time + 0.5)
    assert event is None
    assert not manager.is_phone_event_active


def test_event_manager_persistent_detection_triggers_event():
    manager = EventManager(phone_persistence_seconds=1.0)
    base_time = 100.0

    manager.update_phone_detection(is_visible=True, current_time=base_time)
    manager.update_phone_detection(is_visible=True, current_time=base_time + 0.8)

    # Crosses 1.0s threshold at t=101.0
    event = manager.update_phone_detection(is_visible=True, current_time=base_time + 1.0)
    assert event == "PHONE_DETECTED"
    assert manager.is_phone_event_active


def test_event_manager_resets_when_phone_removed():
    manager = EventManager(phone_persistence_seconds=1.0)
    base_time = 100.0

    manager.update_phone_detection(is_visible=True, current_time=base_time)
    manager.update_phone_detection(is_visible=True, current_time=base_time + 1.2)
    assert manager.is_phone_event_active

    # Phone removed
    event = manager.update_phone_detection(is_visible=False, current_time=base_time + 1.3)
    assert event is None
    assert not manager.is_phone_event_active

    # Phone reappears briefly at t=102.0
    event = manager.update_phone_detection(is_visible=True, current_time=base_time + 2.0)
    assert event is None
    assert not manager.is_phone_event_active
