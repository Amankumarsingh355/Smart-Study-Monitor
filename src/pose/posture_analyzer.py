import math
from typing import List, Tuple, Dict, Any, Optional


class PostureAnalyzer:
    """
    Analyzes body landmark geometry to quantify ergonomic posture.
    
    Extracts:
    - Head position & lateral offset
    - Shoulder tilt / alignment
    - Posture score (0.0 to 1.0)
    - Slouching / poor posture boolean flag
    """

    NOSE = 0
    LEFT_EAR = 7
    RIGHT_EAR = 8
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12

    def __init__(
        self,
        max_shoulder_tilt_ratio: float = 0.15,
        max_head_offset_ratio: float = 0.25,
        min_posture_score_threshold: float = 0.65
    ):
        self.max_shoulder_tilt_ratio = max_shoulder_tilt_ratio
        self.max_head_offset_ratio = max_head_offset_ratio
        self.min_posture_score_threshold = min_posture_score_threshold

    @staticmethod
    def _distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx * dx + dy * dy)

    def analyze(self, landmarks: List[Tuple[int, int, float, float]]) -> Dict[str, Any]:
        """
        Analyze body landmarks.

        Returns:
            Dictionary with posture features and score.
        """
        if not landmarks or len(landmarks) < 13:
            return {
                "detected": False,
                "posture_score": 1.0,
                "is_slouching": False,
                "shoulder_tilt": 0.0,
                "head_offset": 0.0,
                "head_y": 0,
                "shoulder_y": 0
            }

        head = (landmarks[self.NOSE][0], landmarks[self.NOSE][1])
        l_sh = (landmarks[self.LEFT_SHOULDER][0], landmarks[self.LEFT_SHOULDER][1])
        r_sh = (landmarks[self.RIGHT_SHOULDER][0], landmarks[self.RIGHT_SHOULDER][1])

        shoulder_width = self._distance(l_sh, r_sh)
        if shoulder_width <= 1.0:
            shoulder_width = 1.0

        # Shoulder midpoint
        sh_mid_x = (l_sh[0] + r_sh[0]) / 2.0
        sh_mid_y = (l_sh[1] + r_sh[1]) / 2.0

        # Lateral head offset (leaning left or right)
        head_lateral_offset = abs(head[0] - sh_mid_x) / shoulder_width

        # Shoulder tilt (one shoulder dropped)
        shoulder_tilt = abs(l_sh[1] - r_sh[1]) / shoulder_width

        # Posture score calculation: starts at 1.0, deducted for tilt and offset
        score = 1.0
        if shoulder_tilt > 0.05:
            score -= (shoulder_tilt - 0.05) * 2.0
        if head_lateral_offset > 0.10:
            score -= (head_lateral_offset - 0.10) * 2.0

        score = max(0.0, min(1.0, score))

        is_slouching = (
            score < self.min_posture_score_threshold
            or shoulder_tilt > self.max_shoulder_tilt_ratio
            or head_lateral_offset > self.max_head_offset_ratio
        )

        return {
            "detected": True,
            "posture_score": round(score, 2),
            "is_slouching": is_slouching,
            "shoulder_tilt": round(shoulder_tilt, 3),
            "head_offset": round(head_lateral_offset, 3),
            "head_position": head,
            "shoulder_midpoint": (int(sh_mid_x), int(sh_mid_y)),
            "shoulder_width": round(shoulder_width, 1)
        }
