"""
Feature Schema & Behavioral Classes Specification for ML Subsystem.
Defines canonical 14-dimensional feature vector ordering, type constraints, and target labels.
"""

from enum import Enum
from typing import List, Dict, Any


class StudyBehaviorClass(str, Enum):
    FOCUSED = "FOCUSED"
    READING = "READING"
    LOOKING_AWAY = "LOOKING_AWAY"
    DROWSY = "DROWSY"
    PHONE_USAGE = "PHONE_USAGE"
    POOR_POSTURE = "POOR_POSTURE"


# Canonical feature column names in deterministic order
FEATURE_COLUMNS: List[str] = [
    "ear",                    # Eye Aspect Ratio (0.0 - 0.5)
    "blink_rate",             # Blinks per minute (0.0 - 60.0)
    "eye_closure_duration",   # Consecutive seconds eyes closed (0.0 - 10.0+)
    "gaze_direction",         # 0=SCREEN, 1=DOWN, 2=LEFT, 3=RIGHT, 4=UP
    "gaze_stability",         # Stability score / variance metric (0.0 - 1.0)
    "away_duration",          # Consecutive seconds looking away
    "head_pitch",             # Vertical head angle in degrees (-45.0 to 45.0)
    "head_yaw",               # Horizontal head angle in degrees (-45.0 to 45.0)
    "shoulder_angle",         # Shoulder tilt in degrees (0.0 to 45.0)
    "is_slouching",           # 1.0 if slouching / hunched, 0.0 otherwise
    "phone_detected",         # 1.0 if phone detected by YOLO, 0.0 otherwise
    "phone_confidence",       # YOLO confidence for phone (0.0 to 1.0)
    "book_detected",          # 1.0 if book / reading material detected, 0.0 otherwise
    "movement_intensity"      # Landmark motion / optical jitter (0.0 to 1.0)
]

# Canonical default / neutral feature values for missing sensor data
DEFAULT_FEATURE_VALUES: Dict[str, float] = {
    "ear": 0.28,
    "blink_rate": 15.0,
    "eye_closure_duration": 0.0,
    "gaze_direction": 0.0,
    "gaze_stability": 0.9,
    "away_duration": 0.0,
    "head_pitch": 0.0,
    "head_yaw": 0.0,
    "shoulder_angle": 0.0,
    "is_slouching": 0.0,
    "phone_detected": 0.0,
    "phone_confidence": 0.0,
    "book_detected": 0.0,
    "movement_intensity": 0.05
}

# Gaze direction encoding map
GAZE_DIRECTION_MAP: Dict[str, int] = {
    "SCREEN": 0,
    "DOWN": 1,
    "LEFT": 2,
    "RIGHT": 3,
    "UP": 4,
    "AWAY": 2  # default away maps to lateral
}
