import math
from typing import List, Tuple, Dict, Any


class GazeAnalyzer:
    """
    Estimates approximate gaze and head orientation direction.

    NOTE: Normal webcams provide approximate gaze estimation,
    not clinical eye tracking.

    Directions:
    - SCREEN (Looking centered at the screen)
    - DOWN   (Looking down towards desk/book/keyboard)
    - LEFT   (Turned or looking left)
    - RIGHT  (Turned or looking right)
    - AWAY   (Looking far off-screen)
    """

    NOSE_TIP = 1
    CHIN = 152
    FOREHEAD = 10
    LEFT_TEMPLE = 234
    RIGHT_TEMPLE = 454

    # Eye landmarks
    LEFT_EYE_OUTER = 33
    LEFT_EYE_INNER = 133
    RIGHT_EYE_INNER = 362
    RIGHT_EYE_OUTER = 263

    # Iris landmarks (available in MediaPipe 478-landmark models)
    LEFT_IRIS = 468
    RIGHT_IRIS = 473

    def __init__(
        self,
        yaw_threshold: float = 0.18,
        pitch_down_threshold: float = 0.15,
        pitch_up_threshold: float = 0.18
    ):
        self.yaw_threshold = yaw_threshold
        self.pitch_down_threshold = pitch_down_threshold
        self.pitch_up_threshold = pitch_up_threshold

    def analyze(self, landmarks: List[Tuple[int, int]]) -> Dict[str, Any]:
        """
        Analyze facial landmarks to derive approximate gaze direction.
        """
        if not landmarks or len(landmarks) < 455:
            return {
                "direction": "SCREEN",
                "head_yaw": 0.0,
                "head_pitch": 0.0,
                "is_looking_away": False,
                "is_looking_down": False
            }

        nose = landmarks[self.NOSE_TIP]
        forehead = landmarks[self.FOREHEAD]
        chin = landmarks[self.CHIN]
        left_t = landmarks[self.LEFT_TEMPLE]
        right_t = landmarks[self.RIGHT_TEMPLE]

        # 1. Horizontal Yaw Ratio
        face_width = abs(right_t[0] - left_t[0])
        if face_width <= 1.0:
            face_width = 1.0

        temple_mid_x = (left_t[0] + right_t[0]) / 2.0
        # Positive = looking right, Negative = looking left
        yaw_ratio = (nose[0] - temple_mid_x) / face_width

        # 2. Vertical Pitch Ratio
        face_height = abs(chin[1] - forehead[1])
        if face_height <= 1.0:
            face_height = 1.0

        face_mid_y = (forehead[1] + chin[1]) / 2.0
        # Positive = looking down, Negative = looking up
        pitch_ratio = (nose[1] - face_mid_y) / face_height

        # 3. Iris refinement (if 478 landmarks present)
        iris_offset_x = 0.0
        if len(landmarks) >= 474:
            left_eye_w = abs(landmarks[self.LEFT_EYE_INNER][0] - landmarks[self.LEFT_EYE_OUTER][0])
            if left_eye_w > 1.0:
                l_eye_center = (landmarks[self.LEFT_EYE_INNER][0] + landmarks[self.LEFT_EYE_OUTER][0]) / 2.0
                iris_offset_x = (landmarks[self.LEFT_IRIS][0] - l_eye_center) / left_eye_w

        # Combined lateral metric
        combined_yaw = yaw_ratio + (iris_offset_x * 0.3)

        # 4. Classify discrete direction
        if combined_yaw < -self.yaw_threshold:
            direction = "LEFT"
            is_looking_away = True
            is_looking_down = False
        elif combined_yaw > self.yaw_threshold:
            direction = "RIGHT"
            is_looking_away = True
            is_looking_down = False
        elif pitch_ratio > self.pitch_down_threshold:
            direction = "DOWN"
            is_looking_away = False
            is_looking_down = True
        elif pitch_ratio < -self.pitch_up_threshold:
            direction = "AWAY"
            is_looking_away = True
            is_looking_down = False
        else:
            direction = "SCREEN"
            is_looking_away = False
            is_looking_down = False

        return {
            "direction": direction,
            "head_yaw": round(combined_yaw * 100, 1),
            "head_pitch": round(pitch_ratio * 100, 1),
            "is_looking_away": is_looking_away,
            "is_looking_down": is_looking_down
        }
