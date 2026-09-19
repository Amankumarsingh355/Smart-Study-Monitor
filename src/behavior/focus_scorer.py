from typing import Optional
from .study_state import StudyState
from .session_metrics import SessionMetrics


class FocusScorer:
    """
    Rule-based and time-weighted focus scoring engine.
    
    Supports:
    1. Instantaneous rule-based score calculation via calculate()
    2. Continuous session metric accumulation via update_session()
    """

    def __init__(self):
        self.score: float = 100.0
        self.session_metrics = SessionMetrics()

    def calculate(
        self,
        phone_detected: bool = False,
        drowsy: bool = False,
        face_missing: bool = False,
        distracted: bool = False
    ) -> float:
        """
        Calculate instantaneous focus score based on active flags.
        Starting Score = 100
        Phone usage   -25
        Drowsy        -20
        Face missing  -20
        Distracted    -15
        Clamped between 0 and 100.
        """
        score = 100.0

        if phone_detected:
            score -= 25.0

        if drowsy:
            score -= 20.0

        if face_missing:
            score -= 20.0

        if distracted:
            score -= 15.0

        score = max(0.0, min(100.0, score))
        self.score = score
        return self.score

    def update_session(self, current_state: StudyState, dt: float) -> float:
        """
        Update cumulative session metrics and calculate time-weighted score.
        """
        if dt <= 0.0:
            return self.score

        self.session_metrics.update(current_state, dt)

        # Score is the percentage of focused time during the session
        self.score = self.session_metrics.focus_percentage
        return self.score

    def get_score(self) -> float:
        return self.score

    def get_score_int(self) -> int:
        return int(round(self.score))

    def calculate_composite_score(
        self,
        focused_ratio: float = 1.0,
        distraction_ratio: float = 0.0,
        phone_ratio: float = 0.0,
        drowsy_ratio: float = 0.0,
        posture_issue_ratio: float = 0.0,
        recovery_speed_factor: float = 1.0,
        weights: Optional[dict] = None
    ) -> float:
        """
        Phase 12 Advanced Composite Focus Score.
        Weights default to:
          - 40% sustained focus duration
          - 15% distraction control
          - 15% phone avoidance
          - 10% drowsiness avoidance
          - 10% posture stability
          - 10% recovery speed
        """
        w = weights or {
            "focus": 0.40,
            "distraction": 0.15,
            "phone": 0.15,
            "drowsy": 0.10,
            "posture": 0.10,
            "recovery": 0.10
        }

        # Component subscores (0-100 each)
        s_focus = max(0.0, min(1.0, focused_ratio)) * 100.0
        s_distraction = max(0.0, 1.0 - min(1.0, distraction_ratio)) * 100.0
        s_phone = max(0.0, 1.0 - min(1.0, phone_ratio * 2.0)) * 100.0  # extra sensitive to phone
        s_drowsy = max(0.0, 1.0 - min(1.0, drowsy_ratio * 2.0)) * 100.0
        s_posture = max(0.0, 1.0 - min(1.0, posture_issue_ratio)) * 100.0
        s_recovery = max(0.0, min(1.0, recovery_speed_factor)) * 100.0

        composite = (
            w["focus"] * s_focus +
            w["distraction"] * s_distraction +
            w["phone"] * s_phone +
            w["drowsy"] * s_drowsy +
            w["posture"] * s_posture +
            w["recovery"] * s_recovery
        )
        self.score = round(max(0.0, min(100.0, composite)), 1)
        return self.score

    def reset(self):
        self.score = 100.0
        self.session_metrics = SessionMetrics()
