import numpy as np
from src.ml.predictor import MLPredictor
from src.ml.behavior_classifier import BehaviorClassifier


def test_predictor_high_confidence():
    predictor = MLPredictor(min_confidence_threshold=0.60)
    focused_vec = np.array([
        0.31, 14.0, 0.0, 0.0, 0.95, 0.0, 2.0, 0.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.05
    ], dtype=np.float32)

    result = predictor.predict(focused_vec)
    assert not result.is_ambiguous
    assert result.predicted_state == "FOCUSED"
    assert result.confidence >= 0.60
    assert result.fallback_reason is None


def test_predictor_ambiguity_filter():
    # If we set an impossibly high confidence threshold (0.999), it should flag as ambiguous
    strict_predictor = MLPredictor(min_confidence_threshold=0.999)
    test_vec = np.array([
        0.28, 12.0, 0.0, 0.0, 0.85, 0.0, 5.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0, 0.06
    ], dtype=np.float32)

    result = strict_predictor.predict(test_vec)
    assert result.is_ambiguous
    assert "LOW_CONFIDENCE" in result.fallback_reason
