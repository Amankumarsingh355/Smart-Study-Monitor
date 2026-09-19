from src.behavior.feature_fusion import FeatureFusion, FusedFeatures
from src.behavior.temporal_engine import TemporalEngine


def test_feature_fusion_structure():
    fusion = FeatureFusion()
    temporal = TemporalEngine()

    eye_data = {"average_ratio": 0.28}
    gaze_data = {"direction": "SCREEN", "head_yaw": 2.5, "is_looking_away": False, "is_looking_down": False}
    posture_data = {"posture_score": 0.95, "is_slouching": False}

    fused = fusion.fuse(
        face_detected=True,
        eye_data=eye_data,
        gaze_data=gaze_data,
        posture_data=posture_data,
        phone_detected=False,
        book_detected=False,
        temporal_engine=temporal
    )

    assert isinstance(fused, FusedFeatures)
    assert fused.face_detected is True
    assert fused.eye_ratio == 0.28
    assert fused.eyes_closed is False
    assert fused.phone_detected is False
    assert fused.book_detected is False
    assert fused.gaze_direction == "SCREEN"
    assert fused.posture_score == 0.95
    assert fused.is_slouching is False

    d = fused.to_dict()
    assert "face_detected" in d
    assert "posture_score" in d
    assert "phone_duration" in d
