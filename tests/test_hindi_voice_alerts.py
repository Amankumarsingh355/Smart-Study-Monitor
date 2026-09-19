"""
Unit and Integration Tests for Hindi Voice Alert System.

Validates:
1. Drowsiness: Eyes closed beyond threshold -> DROWSY -> "WAKE UP & STUDY!" -> wake_up_hi.wav
2. Face Obstruction: Book hiding face -> FACE_BLOCKED -> "DON'T COVER YOUR FACE!" -> face_blocked_hi.wav
3. Reading Differentiation: Book detected + face visible -> READING (NO alert)
4. Phone Usage: Phone detected persistently -> PHONE_USAGE -> "PUT THE PHONE AWAY!" -> phone_usage_hi.wav
5. Cooldown: 0-5 sec suppression, re-triggering after cooldown expires
6. Priority Preemption: DROWSY > PHONE_USAGE > FACE_BLOCKED
7. Audio Resilience: Missing audio file or playback error does NOT crash system
8. EventBus Integration: Structured payload matches required schema
"""

import os
import time
import pytest
from unittest.mock import MagicMock, patch

from config import ALERT_CONFIG, ALERT_COOLDOWN_SECONDS, SOUNDS_DIR
from src.alerts.audio_player import AudioPlayer
from src.alerts.alert_manager import AlertManager
from src.behavior.feature_fusion import FeatureFusion, FusedFeatures
from src.behavior.study_state import StudyState, StudyStateEngine
from src.behavior.temporal_engine import TemporalEngine
from src.events.event_bus import event_bus


# -------------------------------------------------------------------
# 1. Audio Assets Existence & Integrity
# -------------------------------------------------------------------
def test_hindi_audio_assets_exist():
    """Verify all required Hindi spoken WAV assets exist on local disk."""
    required_wavs = ["wake_up_hi.wav", "face_blocked_hi.wav", "phone_usage_hi.wav"]
    for wav_name in required_wavs:
        path = os.path.join(SOUNDS_DIR, wav_name)
        assert os.path.exists(path), f"Required Hindi audio asset missing: {wav_name}"
        assert os.path.getsize(path) > 10000, f"Audio file {wav_name} is abnormally small or empty"


# -------------------------------------------------------------------
# 2. Centralized Configuration Integrity
# -------------------------------------------------------------------
def test_alert_config_schema():
    """Verify ALERT_CONFIG contains all required fields and correct screen text."""
    expected_scenarios = {
        "DROWSY": {"audio": "wake_up_hi.wav", "screen_text": "WAKE UP & STUDY!", "priority": 1},
        "FACE_BLOCKED": {"audio": "face_blocked_hi.wav", "screen_text": "DON'T COVER YOUR FACE!", "priority": 3},
        "PHONE_USAGE": {"audio": "phone_usage_hi.wav", "screen_text": "PUT THE PHONE AWAY!", "priority": 2},
    }

    for alert_key, expected in expected_scenarios.items():
        assert alert_key in ALERT_CONFIG
        cfg = ALERT_CONFIG[alert_key]
        assert cfg["audio"] == expected["audio"]
        assert cfg["screen_text"] == expected["screen_text"]
        assert cfg["priority"] == expected["priority"]
        assert cfg["enabled"] is True


# -------------------------------------------------------------------
# 3. AudioPlayer Multi-Alert & Priority Preemption Tests
# -------------------------------------------------------------------
def test_audio_player_mapping():
    """Verify AudioPlayer maps alert types to proper sound files."""
    player = AudioPlayer()
    assert player.get_priority("DROWSY") == 1
    assert player.get_priority("PHONE_USAGE") == 2
    assert player.get_priority("PHONE_DETECTED") == 2
    assert player.get_priority("FACE_BLOCKED") == 3


def test_audio_player_priority_preemption():
    """Verify higher priority alert (DROWSY) preempts lower priority (PHONE_USAGE)."""
    player = AudioPlayer()
    player._initialized = True
    mock_channel = MagicMock()
    mock_channel.get_busy.return_value = True
    player._channel = mock_channel

    # Simulate PHONE_USAGE currently playing
    player._current_playing_type = "PHONE_USAGE"

    # Attempt to play FACE_BLOCKED (lower priority 3 vs 2) -> should be suppressed
    played_lower = player.play("FACE_BLOCKED")
    assert played_lower is False
    assert mock_channel.stop.call_count == 0

    # Attempt to play DROWSY (higher priority 1 vs 2) -> should stop channel and play!
    with patch("os.path.exists", return_value=True), patch("pygame.mixer.Sound"):
        played_higher = player.play("DROWSY")
        assert played_higher is True
        assert mock_channel.stop.call_count == 1
        assert player.current_playing_type == "DROWSY"


def test_audio_player_reentrancy_suppression():
    """Verify that playing the same alert while it's already playing does NOT restart it."""
    player = AudioPlayer()
    player._initialized = True
    mock_channel = MagicMock()
    mock_channel.get_busy.return_value = True
    player._channel = mock_channel

    player._current_playing_type = "PHONE_USAGE"

    # Same alert arrives while playing
    assert player.play("PHONE_USAGE") is False
    assert mock_channel.stop.call_count == 0


def test_audio_player_missing_file_resilience():
    """Missing audio file must log a warning and return False without throwing an exception."""
    player = AudioPlayer()
    with patch("os.path.exists", return_value=False):
        # Should not raise exception
        result = player.play("DROWSY")
        assert result is False


# -------------------------------------------------------------------
# 4. AlertManager Synchronized Audio & Screen Alerts
# -------------------------------------------------------------------
def test_alert_manager_drowsy_alert():
    """DROWSY triggers 'WAKE UP & STUDY!' and wake_up_hi.wav."""
    mock_player = MagicMock()
    mock_player.play.return_value = True
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_player)

    triggered = alert_mgr.process_event("DROWSY", current_time=100.0)

    assert triggered is True
    assert alert_mgr.is_visual_alert_active is True
    assert alert_mgr.alert_message == "WAKE UP & STUDY!"
    mock_player.play.assert_called_once_with("DROWSY")


def test_alert_manager_face_blocked_alert():
    """FACE_BLOCKED triggers 'DON'T COVER YOUR FACE!' and face_blocked_hi.wav."""
    mock_player = MagicMock()
    mock_player.play.return_value = True
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_player)

    triggered = alert_mgr.process_event("FACE_BLOCKED", current_time=100.0)

    assert triggered is True
    assert alert_mgr.is_visual_alert_active is True
    assert alert_mgr.alert_message == "DON'T COVER YOUR FACE!"
    mock_player.play.assert_called_once_with("FACE_BLOCKED")


def test_alert_manager_phone_usage_alert():
    """PHONE_USAGE triggers 'PUT THE PHONE AWAY!' and phone_usage_hi.wav."""
    mock_player = MagicMock()
    mock_player.play.return_value = True
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_player)

    triggered = alert_mgr.process_event("PHONE_USAGE", current_time=100.0)

    assert triggered is True
    assert alert_mgr.is_visual_alert_active is True
    assert alert_mgr.alert_message == "PUT THE PHONE AWAY!"
    mock_player.play.assert_called_once_with("PHONE_USAGE")


def test_alert_manager_cooldown_and_repeat():
    """Test 5-second cooldown suppression and subsequent re-triggering."""
    mock_player = MagicMock()
    mock_player.play.return_value = True
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_player)

    # 1. Initial trigger at t=10.0 -> Audio 1 plays
    t1 = alert_mgr.process_event("PHONE_USAGE", current_time=10.0)
    assert t1 is True
    assert mock_player.play.call_count == 1

    # 2. Within 5s cooldown (t=12.0) -> Audio suppressed, screen alert remains active
    t2 = alert_mgr.process_event("PHONE_USAGE", current_time=12.0)
    assert t2 is False
    assert mock_player.play.call_count == 1
    assert alert_mgr.is_visual_alert_active is True

    # 3. Exactly at t=14.99s -> Still suppressed
    t3 = alert_mgr.process_event("PHONE_USAGE", current_time=14.99)
    assert t3 is False
    assert mock_player.play.call_count == 1

    # 4. After cooldown expires (t=15.01s) -> Audio 2 triggers if condition persists
    t4 = alert_mgr.process_event("PHONE_USAGE", current_time=15.01)
    assert t4 is True
    assert mock_player.play.call_count == 2


def test_alert_manager_event_bus_publishing():
    """Verify that alert dispatches structured event to EventBus with correct schema."""
    published_events = []

    def subscriber(data):
        published_events.append(data)

    event_bus.subscribe("ALERT", subscriber)

    mock_player = MagicMock()
    mock_player.play.return_value = True
    alert_mgr = AlertManager(cooldown_seconds=5.0, audio_player=mock_player)

    alert_mgr.process_event("PHONE_USAGE", current_time=50.0, confidence=0.98)

    assert len(published_events) > 0
    last_event = published_events[-1]
    assert last_event["event_type"] == "PHONE_USAGE"
    assert last_event["screen_message"] == "PUT THE PHONE AWAY!"
    assert last_event["audio"] == "phone_usage_hi.wav"
    assert last_event["confidence"] == 0.98
    assert last_event["timestamp"] == 50.0


# -------------------------------------------------------------------
# 5. Behavior Pipeline: Drowsiness & Temporal Logic
# -------------------------------------------------------------------
def test_drowsiness_temporal_pipeline():
    """
    Eyes open -> No alert
    Eyes closed briefly -> No alert
    Eyes closed persistently -> DROWSY -> Alert triggered
    """
    engine = StudyStateEngine(drowsy_duration_seconds=2.0, debounce_frames=1)
    temporal = TemporalEngine()

    # Frame 1 (t=0.0): Eyes closed
    temporal.update("eyes_closed", True, current_time=0.0)
    fused_1 = FusedFeatures(
        face_detected=True,
        eye_ratio=0.15,
        eyes_closed=True,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=1.0,
        is_slouching=False,
        eyes_closed_duration=temporal.duration("eyes_closed", current_time=0.5)
    )
    # At 0.5s (< 2.0s threshold) -> Not drowsy yet
    state_1 = engine.evaluate_fused(fused_1)
    assert state_1 != StudyState.DROWSY

    # Frame 2 (t=2.5s): Eyes closed for 2.5s (>= 2.0s threshold)
    fused_2 = FusedFeatures(
        face_detected=True,
        eye_ratio=0.14,
        eyes_closed=True,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=1.0,
        is_slouching=False,
        eyes_closed_duration=temporal.duration("eyes_closed", current_time=2.5)
    )
    state_2 = engine.evaluate_fused(fused_2)
    assert state_2 == StudyState.DROWSY


# -------------------------------------------------------------------
# 6. Face Obstruction vs Reading Differentiation
# -------------------------------------------------------------------
def test_reading_vs_face_blocked_differentiation():
    """
    Case A: Book detected + face visible + looking down -> READING (NOT Face Blocked!)
    Case B: Book detected + face NOT visible persistently -> FACE_BLOCKED
    """
    fusion = FeatureFusion()
    engine = StudyStateEngine(face_block_duration_seconds=1.5, debounce_frames=1)
    temporal = TemporalEngine()

    # Case A: Normal Reading with Book visible and face visible
    eye_data = {"average_ratio": 0.26}
    gaze_data = {"direction": "DOWN", "is_looking_down": True, "is_looking_away": False}
    posture_data = {"posture_score": 0.90, "is_slouching": False}

    fused_reading = fusion.fuse(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        posture_data=posture_data,
        phone_detected=False,
        book_detected=True,
        temporal_engine=temporal
    )

    assert fused_reading.is_face_blocked is False
    state_reading = engine.evaluate_fused(fused_reading)
    assert state_reading == StudyState.READING  # Correct! Must NOT trigger FACE_BLOCKED

    # Case B: Book hiding face (Face Mesh drops detection, book visible)
    temporal.update("face_blocked", True, current_time=0.0)

    # Before threshold (0.8s < 1.5s)
    fused_blocked_brief = fusion.fuse(
        face_detected=False,
        eye_data=None,
        gaze_data=None,
        posture_data=None,
        phone_detected=False,
        book_detected=True,
        temporal_engine=temporal
    )
    # Manually pass current duration for evaluation
    fused_blocked_brief.face_blocked_duration = 0.8
    state_brief = engine.evaluate_fused(fused_blocked_brief)
    assert state_brief != StudyState.FACE_BLOCKED  # Not triggered yet

    # After threshold (2.0s >= 1.5s)
    fused_blocked_persist = fusion.fuse(
        face_detected=False,
        eye_data=None,
        gaze_data=None,
        posture_data=None,
        phone_detected=False,
        book_detected=True,
        temporal_engine=temporal
    )
    fused_blocked_persist.face_blocked_duration = 2.0
    state_persist = engine.evaluate_fused(fused_blocked_persist)
    assert state_persist == StudyState.FACE_BLOCKED  # Confirmed FACE_BLOCKED!
