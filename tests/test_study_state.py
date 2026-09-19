from src.behavior.study_state import StudyState, StudyStateEngine
from src.behavior.temporal_engine import TemporalEngine
from src.behavior.feature_fusion import FusedFeatures


def test_scenario_1_normal_study():
    """Scenario 1: Sitting normally + Looking at screen + No phone + Eyes open -> FOCUSED"""
    engine = StudyStateEngine()
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.29,
        eyes_closed=False,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.95,
        is_slouching=False
    )
    assert engine.evaluate_fused(features) == StudyState.FOCUSED


def test_scenario_2_reading():
    """Scenario 2: Head down + Book detected + Eyes active -> READING"""
    engine = StudyStateEngine()
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.27,
        eyes_closed=False,
        phone_detected=False,
        book_detected=True,
        head_angle=0.0,
        gaze_direction="DOWN",
        is_looking_away=False,
        is_looking_down=True,
        posture_score=0.88,
        is_slouching=False
    )
    assert engine.evaluate_fused(features) == StudyState.READING


def test_scenario_3_looking_away():
    """Scenario 3: Head turned + Gaze away + Sustained -> LOOKING_AWAY"""
    engine = StudyStateEngine(looking_away_duration_seconds=2.0)
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.28,
        eyes_closed=False,
        phone_detected=False,
        book_detected=False,
        head_angle=25.0,
        gaze_direction="RIGHT",
        is_looking_away=True,
        is_looking_down=False,
        posture_score=0.90,
        is_slouching=False,
        looking_away_duration=2.5  # Sustained >= 2.0s
    )
    assert engine.evaluate_fused(features) == StudyState.LOOKING_AWAY


def test_scenario_4_drowsy_prolonged():
    """Scenario 4: Eyes closed + Head dropping + Sustained -> DROWSY"""
    engine = StudyStateEngine(drowsy_duration_seconds=2.0)
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.10,
        eyes_closed=True,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="DOWN",
        is_looking_away=False,
        is_looking_down=True,
        posture_score=0.60,
        is_slouching=True,
        eyes_closed_duration=2.5  # Sustained >= 2.0s
    )
    assert engine.evaluate_fused(features) == StudyState.DROWSY


def test_scenario_5_poor_posture():
    """Scenario 5: Shoulder/head alignment abnormal + Sustained -> POOR_POSTURE"""
    engine = StudyStateEngine(poor_posture_duration_seconds=3.0)
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.29,
        eyes_closed=False,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.50,
        is_slouching=True,
        poor_posture_duration=3.5  # Sustained >= 3.0s
    )
    assert engine.evaluate_fused(features) == StudyState.POOR_POSTURE


def test_scenario_6_phone_usage():
    """Scenario 6: Phone detected + Persistent -> PHONE_USAGE"""
    engine = StudyStateEngine(phone_persistence_seconds=1.0)
    features = FusedFeatures(
        face_detected=True,
        eye_ratio=0.28,
        eyes_closed=False,
        phone_detected=True,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.90,
        is_slouching=False,
        phone_duration=1.5  # Sustained >= 1.0s
    )
    assert engine.evaluate_fused(features) == StudyState.PHONE_USAGE


def test_behavioral_confidence():
    """Verify that evaluated states produce realistic confidence scores."""
    engine = StudyStateEngine()

    focused_feat = FusedFeatures(
        face_detected=True,
        eye_ratio=0.30,
        eyes_closed=False,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.95,
        is_slouching=False
    )
    assert engine.evaluate_fused(focused_feat) == StudyState.FOCUSED
    assert 0.80 <= engine.current_confidence <= 1.0
    assert "face_detected" in engine.current_evidence

    phone_feat = FusedFeatures(
        face_detected=True,
        eye_ratio=0.28,
        eyes_closed=False,
        phone_detected=True,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.90,
        is_slouching=False,
        phone_duration=2.0
    )
    assert engine.evaluate_fused(phone_feat) == StudyState.PHONE_USAGE
    assert 0.85 <= engine.current_confidence <= 1.0


def test_state_debouncing_prevents_false_switching():
    """Verify that transient single-frame spikes do not cause immediate state switching when debounce_frames > 1."""
    engine = StudyStateEngine(debounce_frames=3)

    focused_feat = FusedFeatures(
        face_detected=True,
        eye_ratio=0.30,
        eyes_closed=False,
        phone_detected=False,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.95,
        is_slouching=False
    )

    phone_feat = FusedFeatures(
        face_detected=True,
        eye_ratio=0.28,
        eyes_closed=False,
        phone_detected=True,
        book_detected=False,
        head_angle=0.0,
        gaze_direction="SCREEN",
        is_looking_away=False,
        is_looking_down=False,
        posture_score=0.90,
        is_slouching=False,
        phone_duration=1.5
    )

    # Initial state is FOCUSED
    assert engine.evaluate_fused(focused_feat) == StudyState.FOCUSED

    # Frame 1 of phone: candidate is PHONE_USAGE, but confirmed stays FOCUSED
    assert engine.evaluate_fused(phone_feat) == StudyState.FOCUSED

    # Frame 2 of phone: candidate is PHONE_USAGE, confirmed still FOCUSED
    assert engine.evaluate_fused(phone_feat) == StudyState.FOCUSED

    # Frame 3 of phone: candidate sustained for 3 frames -> switches to PHONE_USAGE!
    assert engine.evaluate_fused(phone_feat) == StudyState.PHONE_USAGE

    # Single-frame dropout back to focused does NOT immediately switch confirmed state
    assert engine.evaluate_fused(focused_feat) == StudyState.PHONE_USAGE

