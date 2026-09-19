import numpy as np
import pytest
from src.ml.model_manager import ModelManager
from src.ml.behavior_classifier import BehaviorClassifier


def test_model_manager_loading():
    manager = ModelManager()
    assert manager.is_loaded
    assert manager.model is not None
    assert len(manager.classes) == 6
    assert "FOCUSED" in [str(c) for c in manager.classes]


def test_model_manager_fallback_missing_path():
    manager = ModelManager(model_path="nonexistent_dir/model.joblib")
    assert not manager.is_loaded
    assert manager.model is None


def test_behavior_classifier_prediction():
    classifier = BehaviorClassifier()
    assert classifier.is_available

    # Clean focused feature vector
    # [ear, blink, closure, gaze_dir, gaze_stab, away_dur, pitch, yaw, shoulder, slouch, phone, pconf, book, movement]
    focused_vec = np.array([
        0.31, 14.0, 0.0, 0.0, 0.95, 0.0, 2.0, 0.0, 1.5, 0.0, 0.0, 0.0, 0.0, 0.05
    ], dtype=np.float32)

    pred_class, conf, probs = classifier.predict(focused_vec)
    assert pred_class == "FOCUSED"
    assert conf > 0.70
    assert "FOCUSED" in probs
    assert sum(probs.values()) == pytest.approx(1.0, rel=1e-2)

    # Phone usage vector
    phone_vec = np.array([
        0.28, 14.0, 0.0, 1.0, 0.85, 0.0, 20.0, 0.0, 3.0, 0.0, 1.0, 0.95, 0.0, 0.08
    ], dtype=np.float32)

    pred_class, conf, probs = classifier.predict(phone_vec)
    assert pred_class == "PHONE_USAGE"
    assert conf > 0.80

    # Drowsy vector
    drowsy_vec = np.array([
        0.14, 3.0, 3.0, 0.0, 0.80, 0.0, 22.0, 0.0, 4.0, 0.0, 0.0, 0.0, 0.0, 0.02
    ], dtype=np.float32)

    pred_class, conf, probs = classifier.predict(drowsy_vec)
    assert pred_class == "DROWSY"
    assert conf > 0.80
