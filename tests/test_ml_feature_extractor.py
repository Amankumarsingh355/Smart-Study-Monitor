import numpy as np
import pytest
from src.ml.feature_extractor import FeatureExtractor
from src.ml.feature_schema import FEATURE_COLUMNS
from src.behavior.temporal_engine import TemporalEngine


def test_feature_extractor_complete_signals():
    extractor = FeatureExtractor()
    temporal = TemporalEngine()
    temporal.update("eyes_closed", True, current_time=1.0)
    temporal.update("eyes_closed", True, current_time=3.5)

    eye_data = {"average_ratio": 0.18, "left_eye": 0.18, "right_eye": 0.18}
    gaze_data = {"direction": "SCREEN", "offset_x": 0.0, "offset_y": 0.0}
    posture_data = {"shoulder_tilt_deg": 14.5, "head_lean_deg": 8.0, "is_slouching": True}

    vec = extractor.extract(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        posture_data=posture_data,
        phone_detected=True,
        phone_confidence=0.88,
        book_detected=False,
        temporal_engine=temporal,
        current_time=3.5
    )

    assert isinstance(vec, np.ndarray)
    assert vec.shape == (14,)
    feat_dict = extractor.extract_dict(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        posture_data=posture_data,
        phone_detected=True,
        phone_confidence=0.88,
        book_detected=False,
        temporal_engine=temporal,
        current_time=3.5
    )
    assert feat_dict["phone_detected"] == 1.0
    assert feat_dict["phone_confidence"] == pytest.approx(0.88, rel=1e-2)
    assert feat_dict["is_slouching"] == 1.0
    assert feat_dict["shoulder_angle"] == pytest.approx(14.5, rel=1e-2)
    assert feat_dict["eye_closure_duration"] == pytest.approx(2.5, rel=1e-1)


def test_feature_extractor_fallback_when_missing():
    extractor = FeatureExtractor()
    vec = extractor.extract(
        face_detected=False,
        eye_data=None,
        gaze_data=None,
        posture_data=None,
        phone_detected=False
    )
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (14,)
    # Should contain no NaNs or Infs
    assert not np.isnan(vec).any()
    assert not np.isinf(vec).any()
