"""
Personalization Engine for Phase 12 ML Subsystem.
Tracks individual user baselines (resting EAR, blink frequency, posture angles)
and adapts operational thresholds dynamically to prevent individual false positives.
"""

from typing import Dict, Any, Optional, List
import numpy as np


class PersonalizationEngine:
    """
    Learns and maintains personal behavioral baselines for a user.
    Adapts static thresholds (EAR, blink rate, posture limits) to personal morphology.
    """

    def __init__(
        self,
        calibration_samples_required: int = 60,
        default_ear: float = 0.28,
        default_blink_rate: float = 15.0,
        default_shoulder_angle: float = 2.0
    ):
        self.calibration_samples_required = calibration_samples_required

        # Defaults
        self.default_ear = default_ear
        self.default_blink_rate = default_blink_rate
        self.default_shoulder_angle = default_shoulder_angle

        # Calibration buffers
        self._ear_samples: List[float] = []
        self._blink_samples: List[float] = []
        self._shoulder_samples: List[float] = []
        self._head_pitch_samples: List[float] = []

        # Learned Baselines
        self.baseline_ear: float = default_ear
        self.baseline_blink_rate: float = default_blink_rate
        self.baseline_shoulder_angle: float = default_shoulder_angle
        self.baseline_head_pitch: float = 0.0
        self.is_calibrated: bool = False

    @property
    def calibration_progress(self) -> float:
        """Percentage progress toward full calibration (0.0 to 1.0)."""
        count = len(self._ear_samples)
        return min(1.0, count / max(1, self.calibration_samples_required))

    def update_baseline(
        self,
        ear: float,
        blink_rate: Optional[float] = None,
        shoulder_angle: Optional[float] = None,
        head_pitch: Optional[float] = None,
        is_focused_state: bool = True
    ) -> None:
        """
        Feed live observations into calibration buffer when in focused state.
        Once enough samples are gathered, updates the personal baseline.
        """
        if not is_focused_state:
            return

        if 0.15 <= ear <= 0.45:
            self._ear_samples.append(ear)
        if blink_rate is not None and 2.0 <= blink_rate <= 50.0:
            self._blink_samples.append(blink_rate)
        if shoulder_angle is not None and 0.0 <= shoulder_angle <= 30.0:
            self._shoulder_samples.append(shoulder_angle)
        if head_pitch is not None and -30.0 <= head_pitch <= 30.0:
            self._head_pitch_samples.append(head_pitch)

        # Update running median if samples threshold reached
        if len(self._ear_samples) >= self.calibration_samples_required:
            self.baseline_ear = float(np.median(self._ear_samples))
            if self._blink_samples:
                self.baseline_blink_rate = float(np.median(self._blink_samples))
            if self._shoulder_samples:
                self.baseline_shoulder_angle = float(np.median(self._shoulder_samples))
            if self._head_pitch_samples:
                self.baseline_head_pitch = float(np.median(self._head_pitch_samples))
            self.is_calibrated = True

    def get_adaptive_ear_threshold(self, ratio_factor: float = 0.75) -> float:
        """
        Calculate personalized drowsiness EAR threshold.
        Default is 75% of resting open EAR (e.g. 0.28 * 0.75 = 0.21).
        For someone with naturally smaller eyes (EAR 0.22), threshold is 0.165.
        """
        adaptive = self.baseline_ear * ratio_factor
        return float(np.clip(adaptive, 0.14, 0.26))

    def get_adaptive_slouch_threshold(self, margin_deg: float = 12.0) -> float:
        """Calculate personalized shoulder slouch tilt limit."""
        return float(self.baseline_shoulder_angle + margin_deg)

    def compute_ear_deviation(self, current_ear: float) -> float:
        """
        Compute percentage deviation of current EAR from personal baseline.
        Negative values indicate eyes are closing.
        """
        if self.baseline_ear <= 0.0:
            return 0.0
        return (current_ear - self.baseline_ear) / self.baseline_ear

    def to_dict(self) -> Dict[str, Any]:
        """Export serialized profile."""
        return {
            "baseline_ear": round(self.baseline_ear, 4),
            "baseline_blink_rate": round(self.baseline_blink_rate, 2),
            "baseline_shoulder_angle": round(self.baseline_shoulder_angle, 2),
            "baseline_head_pitch": round(self.baseline_head_pitch, 2),
            "is_calibrated": self.is_calibrated,
            "samples_collected": len(self._ear_samples)
        }

    def load_profile(self, profile: Dict[str, Any]) -> None:
        """Load profile from storage."""
        self.baseline_ear = profile.get("baseline_ear", self.default_ear)
        self.baseline_blink_rate = profile.get("baseline_blink_rate", self.default_blink_rate)
        self.baseline_shoulder_angle = profile.get("baseline_shoulder_angle", self.default_shoulder_angle)
        self.baseline_head_pitch = profile.get("baseline_head_pitch", 0.0)
        self.is_calibrated = profile.get("is_calibrated", True)
