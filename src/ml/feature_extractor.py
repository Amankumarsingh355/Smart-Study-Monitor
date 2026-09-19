"""
Feature Extractor for Phase 12 ML Subsystem.
Aggregates perceptual cues from Face, Eye, Gaze, Posture, YOLO, and Temporal tracking
into a standardized numerical feature vector.
"""

from collections import deque
from typing import Dict, Any, Optional, List, Union
import numpy as np

from .feature_schema import FEATURE_COLUMNS, DEFAULT_FEATURE_VALUES, GAZE_DIRECTION_MAP


class FeatureExtractor:
    """
    Extracts, normalizes, and validates behavioral feature vectors
    for machine learning inference.
    """

    def __init__(self, blink_window_seconds: float = 30.0):
        self.blink_window_seconds = blink_window_seconds
        self._blink_timestamps: deque = deque()
        self._last_ear_below = False
        self._ear_history: deque = deque(maxlen=30)
        self._prev_gaze_coords: Optional[tuple] = None
        self._gaze_coords_history: deque = deque(maxlen=20)

    def extract(
        self,
        face_detected: bool,
        eye_data: Optional[Dict[str, Any]] = None,
        gaze_data: Optional[Dict[str, Any]] = None,
        posture_data: Optional[Dict[str, Any]] = None,
        phone_detected: bool = False,
        phone_confidence: float = 0.0,
        book_detected: bool = False,
        temporal_engine: Optional[Any] = None,
        current_time: Optional[float] = None
    ) -> np.ndarray:
        """
        Extract a 14-dimensional feature vector as a numpy array.
        """
        now = current_time if current_time is not None else 0.0

        # 1. Eye features
        if face_detected and eye_data and "average_ratio" in eye_data:
            ear = float(eye_data["average_ratio"])
        else:
            ear = DEFAULT_FEATURE_VALUES["ear"]

        self._ear_history.append(ear)

        # Update blink tracking
        ear_threshold = 0.21
        is_below = ear < ear_threshold
        if is_below and not self._last_ear_below:
            self._blink_timestamps.append(now)
        self._last_ear_below = is_below

        # Prune older blinks outside window
        while self._blink_timestamps and (now - self._blink_timestamps[0] > self.blink_window_seconds):
            self._blink_timestamps.popleft()

        # Calculate estimated blink rate (blinks per minute)
        if len(self._blink_timestamps) > 0 and self.blink_window_seconds > 0:
            blink_rate = (len(self._blink_timestamps) / self.blink_window_seconds) * 60.0
        else:
            blink_rate = DEFAULT_FEATURE_VALUES["blink_rate"]

        # Eye closure duration from temporal engine
        if temporal_engine is not None:
            eye_closure_duration = temporal_engine.get_duration("eyes_closed", now)
            away_duration = temporal_engine.get_duration("looking_away", now)
        else:
            eye_closure_duration = 0.0
            away_duration = 0.0

        # 2. Gaze features
        if face_detected and gaze_data:
            dir_str = gaze_data.get("direction", "SCREEN")
            gaze_direction = float(GAZE_DIRECTION_MAP.get(dir_str, 0))
            offset_x = gaze_data.get("offset_x", 0.0)
            offset_y = gaze_data.get("offset_y", 0.0)
            self._gaze_coords_history.append((offset_x, offset_y))

            # Gaze stability: inverse of variance in gaze coordinates
            if len(self._gaze_coords_history) >= 5:
                coords = np.array(self._gaze_coords_history)
                var_x = float(np.var(coords[:, 0]))
                var_y = float(np.var(coords[:, 1]))
                variance = var_x + var_y
                gaze_stability = float(np.clip(1.0 - (variance * 2.0), 0.0, 1.0))
            else:
                gaze_stability = 0.9
        else:
            gaze_direction = DEFAULT_FEATURE_VALUES["gaze_direction"]
            gaze_stability = DEFAULT_FEATURE_VALUES["gaze_stability"]

        # 3. Posture and head features
        if posture_data:
            shoulder_angle = float(posture_data.get("shoulder_tilt_deg", 0.0))
            head_pitch = float(posture_data.get("head_lean_deg", 0.0))
            head_yaw = float(posture_data.get("head_yaw_deg", 0.0))
            is_slouching = 1.0 if posture_data.get("is_slouching", False) else 0.0
        else:
            shoulder_angle = DEFAULT_FEATURE_VALUES["shoulder_angle"]
            head_pitch = DEFAULT_FEATURE_VALUES["head_pitch"]
            head_yaw = DEFAULT_FEATURE_VALUES["head_yaw"]
            is_slouching = DEFAULT_FEATURE_VALUES["is_slouching"]

        # 4. Object detection features
        p_det = 1.0 if phone_detected else 0.0
        p_conf = float(phone_confidence) if phone_detected else 0.0
        b_det = 1.0 if book_detected else 0.0

        # 5. Movement intensity (variance of recent EAR and gaze changes)
        if len(self._ear_history) >= 5:
            ear_movement = float(np.std(self._ear_history))
            movement_intensity = float(np.clip(ear_movement * 5.0, 0.0, 1.0))
        else:
            movement_intensity = DEFAULT_FEATURE_VALUES["movement_intensity"]

        # Assemble in canonical FEATURE_COLUMNS order
        features_dict = {
            "ear": float(np.clip(ear, 0.0, 0.5)),
            "blink_rate": float(np.clip(blink_rate, 0.0, 60.0)),
            "eye_closure_duration": float(max(0.0, eye_closure_duration)),
            "gaze_direction": float(gaze_direction),
            "gaze_stability": float(np.clip(gaze_stability, 0.0, 1.0)),
            "away_duration": float(max(0.0, away_duration)),
            "head_pitch": float(np.clip(head_pitch, -45.0, 45.0)),
            "head_yaw": float(np.clip(head_yaw, -45.0, 45.0)),
            "shoulder_angle": float(np.clip(shoulder_angle, 0.0, 45.0)),
            "is_slouching": float(is_slouching),
            "phone_detected": float(p_det),
            "phone_confidence": float(np.clip(p_conf, 0.0, 1.0)),
            "book_detected": float(b_det),
            "movement_intensity": float(np.clip(movement_intensity, 0.0, 1.0))
        }

        feature_vector = np.array([features_dict[col] for col in FEATURE_COLUMNS], dtype=np.float32)
        return feature_vector

    def extract_dict(
        self,
        **kwargs
    ) -> Dict[str, float]:
        """Convenience method returning features as a dictionary."""
        vec = self.extract(**kwargs)
        return {col: float(val) for col, val in zip(FEATURE_COLUMNS, vec)}
