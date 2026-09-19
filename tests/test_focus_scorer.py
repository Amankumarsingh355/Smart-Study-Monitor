from src.behavior.study_state import StudyState
from src.behavior.focus_scorer import FocusScorer, SessionMetrics


def test_focus_scorer_initial_and_perfect():
    scorer = FocusScorer()
    score = scorer.calculate(phone_detected=False, drowsy=False, face_missing=False, distracted=False)
    assert score == 100.0


def test_focus_scorer_deductions():
    scorer = FocusScorer()

    # Phone deduction: -25
    assert scorer.calculate(phone_detected=True) == 75.0

    # Drowsy deduction: -20
    assert scorer.calculate(drowsy=True) == 80.0

    # Face missing deduction: -20
    assert scorer.calculate(face_missing=True) == 80.0

    # Distracted deduction: -15
    assert scorer.calculate(distracted=True) == 85.0

    # Multiple infractions
    assert scorer.calculate(phone_detected=True, drowsy=True) == 55.0


def test_focus_scorer_clamped_bounds():
    scorer = FocusScorer()
    # All deductions sum to -80, so 100 - 80 = 20
    score = scorer.calculate(phone_detected=True, drowsy=True, face_missing=True, distracted=True)
    assert score == 20.0

    # Additional manual penalty
    scorer.score = -10.0
    # Clamping ensures calculate returns >= 0
    assert scorer.calculate(phone_detected=True, drowsy=True, face_missing=True, distracted=True) == 20.0


def test_session_metrics_time_weighted_focus():
    scorer = FocusScorer()

    # 48 min focused, 4 min phone, 3 min drowsy, 2 min no face, 3 min other = 60 min
    # Total focused = 48 / 60 = 80.0%
    scorer.update_session(StudyState.FOCUSED, dt=48 * 60)
    scorer.update_session(StudyState.PHONE_USAGE, dt=4 * 60)
    scorer.update_session(StudyState.DROWSY, dt=3 * 60)
    scorer.update_session(StudyState.NO_FACE, dt=2 * 60)
    scorer.update_session(StudyState.DISTRACTED, dt=3 * 60)

    assert scorer.session_metrics.total_duration == 3600.0
    assert scorer.session_metrics.focused_duration == 2880.0
    assert scorer.get_score() == 80.0
