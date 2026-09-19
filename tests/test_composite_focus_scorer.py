import pytest
from src.behavior.focus_scorer import FocusScorer


def test_composite_focus_score_perfect():
    scorer = FocusScorer()
    score = scorer.calculate_composite_score(
        focused_ratio=1.0,
        distraction_ratio=0.0,
        phone_ratio=0.0,
        drowsy_ratio=0.0,
        posture_issue_ratio=0.0,
        recovery_speed_factor=1.0
    )
    assert score == pytest.approx(100.0, abs=0.5)


def test_composite_focus_score_heavy_phone():
    scorer = FocusScorer()
    score = scorer.calculate_composite_score(
        focused_ratio=0.6,
        distraction_ratio=0.4,
        phone_ratio=0.3,
        drowsy_ratio=0.0,
        posture_issue_ratio=0.0,
        recovery_speed_factor=0.5
    )
    # With phone usage and distractions, score should drop substantially
    assert score < 70.0
