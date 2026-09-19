import pytest
from src.ml.personalization import PersonalizationEngine


def test_personalization_baseline_adaptation():
    engine = PersonalizationEngine(calibration_samples_required=10, default_ear=0.28)
    assert not engine.is_calibrated

    # Feed 15 samples of a user with naturally smaller eyes (EAR ~ 0.22)
    for _ in range(15):
        engine.update_baseline(
            ear=0.22,
            blink_rate=12.0,
            shoulder_angle=1.5,
            is_focused_state=True
        )

    assert engine.is_calibrated
    assert engine.baseline_ear == pytest.approx(0.22, abs=0.01)
    assert engine.baseline_blink_rate == pytest.approx(12.0, abs=0.5)

    # Adaptive EAR threshold should be lower than default
    adaptive_thresh = engine.get_adaptive_ear_threshold(ratio_factor=0.75)
    # 0.22 * 0.75 = 0.165
    assert adaptive_thresh < 0.20
    assert adaptive_thresh == pytest.approx(0.165, abs=0.02)


def test_personalization_serialization():
    engine = PersonalizationEngine()
    engine.baseline_ear = 0.32
    engine.baseline_blink_rate = 18.0
    engine.is_calibrated = True

    data = engine.to_dict()
    assert data["baseline_ear"] == 0.32
    assert data["is_calibrated"] is True

    new_engine = PersonalizationEngine()
    new_engine.load_profile(data)
    assert new_engine.baseline_ear == 0.32
    assert new_engine.baseline_blink_rate == 18.0
    assert new_engine.is_calibrated is True
