import numpy as np
from src.ml.feature_schema import (
    FEATURE_COLUMNS,
    DEFAULT_FEATURE_VALUES,
    StudyBehaviorClass,
    GAZE_DIRECTION_MAP
)


def test_feature_columns_schema():
    assert len(FEATURE_COLUMNS) == 14
    assert "ear" in FEATURE_COLUMNS
    assert "phone_detected" in FEATURE_COLUMNS
    assert "movement_intensity" in FEATURE_COLUMNS


def test_default_feature_values():
    for col in FEATURE_COLUMNS:
        assert col in DEFAULT_FEATURE_VALUES
        assert isinstance(DEFAULT_FEATURE_VALUES[col], (int, float))


def test_study_behavior_classes():
    classes = [c.value for c in StudyBehaviorClass]
    assert "FOCUSED" in classes
    assert "READING" in classes
    assert "LOOKING_AWAY" in classes
    assert "DROWSY" in classes
    assert "PHONE_USAGE" in classes
    assert "POOR_POSTURE" in classes


def test_gaze_direction_encoding():
    assert GAZE_DIRECTION_MAP["SCREEN"] == 0
    assert GAZE_DIRECTION_MAP["DOWN"] == 1
    assert GAZE_DIRECTION_MAP["LEFT"] == 2
    assert GAZE_DIRECTION_MAP["RIGHT"] == 3
    assert GAZE_DIRECTION_MAP["UP"] == 4
