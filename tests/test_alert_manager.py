from src.alerts.alert_manager import AlertManager


class MockAudioPlayer:
    def __init__(self):
        self.play_count = 0

    def play_phone_alert(self):
        self.play_count += 1

    def close(self):
        pass


def test_alert_manager_initial_trigger():
    mock_audio = MockAudioPlayer()
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_audio)

    # Initial trigger at t=10.0
    triggered = alert_mgr.process_event("PHONE_DETECTED", current_time=10.0)

    assert triggered is True
    assert mock_audio.play_count == 1
    assert alert_mgr.is_visual_alert_active is True
    assert alert_mgr.alert_message == "PUT THE PHONE AWAY!"


def test_alert_manager_cooldown_suppression():
    mock_audio = MockAudioPlayer()
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_audio)

    # Initial trigger
    alert_mgr.process_event("PHONE_DETECTED", current_time=10.0)
    assert mock_audio.play_count == 1

    # Consecutive frame 0.5 seconds later (within 5.0s cooldown)
    triggered = alert_mgr.process_event("PHONE_DETECTED", current_time=10.5)
    assert triggered is False
    assert mock_audio.play_count == 1  # Not replayed!
    assert alert_mgr.is_visual_alert_active is True  # Visual banner still visible

    # Another frame 4.0 seconds later
    triggered = alert_mgr.process_event("PHONE_DETECTED", current_time=14.0)
    assert triggered is False
    assert mock_audio.play_count == 1


def test_alert_manager_cooldown_expiration():
    mock_audio = MockAudioPlayer()
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_audio)

    # Initial trigger
    alert_mgr.process_event("PHONE_DETECTED", current_time=10.0)
    assert mock_audio.play_count == 1

    # After cooldown expires (t=15.1, elapsed = 5.1s)
    triggered = alert_mgr.process_event("PHONE_DETECTED", current_time=15.1)
    assert triggered is True
    assert mock_audio.play_count == 2  # Sound plays again


def test_alert_manager_event_cleared():
    mock_audio = MockAudioPlayer()
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_audio)

    alert_mgr.process_event("PHONE_DETECTED", current_time=10.0)
    assert alert_mgr.is_visual_alert_active is True

    # No event on next frame
    triggered = alert_mgr.process_event(None, current_time=10.1)
    assert triggered is False
    assert alert_mgr.is_visual_alert_active is False
