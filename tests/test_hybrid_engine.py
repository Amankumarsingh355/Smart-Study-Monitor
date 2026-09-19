import pytest
from src.ml.hybrid_engine import HybridStudyStateEngine
from src.behavior.study_state import StudyState
from src.behavior.temporal_engine import TemporalEngine


def test_hybrid_engine_phone_safety_override():
    engine = HybridStudyStateEngine(debounce_frames=1)
    temporal = TemporalEngine()
    # Simulate persistent phone detection for 3 seconds
    temporal.update("phone", True, current_time=1.0)
    temporal.update("phone", True, current_time=4.0)

    state, conf = engine.evaluate(
        face_detected=True,
        phone_detected=True,
        phone_confidence=0.92,
        temporal_engine=temporal,
        current_time=4.0
    )
    assert state == StudyState.PHONE_USAGE
    assert conf >= 0.90
    assert engine.decision_source == "RULE_SAFETY_OVERRIDE"


def test_hybrid_engine_agreement_boost():
    engine = HybridStudyStateEngine(debounce_frames=1)
    # Normal focused student
    eye_data = {"average_ratio": 0.31}
    gaze_data = {"direction": "SCREEN", "offset_x": 0.0, "offset_y": 0.0}

    state, conf = engine.evaluate(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        phone_detected=False
    )
    assert state == StudyState.FOCUSED
    assert conf > 0.85
    assert engine.decision_source == "HYBRID_AGREEMENT"


def test_hybrid_engine_fallback_when_model_missing():
    # Pass a dummy predictor that is not loaded
    from src.ml.predictor import MLPredictor
    from src.ml.behavior_classifier import BehaviorClassifier
    from src.ml.model_manager import ModelManager

    unloaded_manager = ModelManager(model_path="nonexistent.joblib")
    predictor = MLPredictor(classifier=BehaviorClassifier(model_manager=unloaded_manager))

    engine = HybridStudyStateEngine(ml_predictor=predictor, debounce_frames=1)
    eye_data = {"average_ratio": 0.30}
    gaze_data = {"direction": "SCREEN"}

    state, conf = engine.evaluate(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        phone_detected=False
    )
    assert state == StudyState.FOCUSED
    assert engine.decision_source == "RULE_FALLBACK"
