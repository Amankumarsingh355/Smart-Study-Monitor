from dataclasses import dataclass
from typing import Dict, Any, Optional
from .temporal_engine import TemporalEngine


@dataclass
class FusedFeatures:
    face_detected: bool
    eye_ratio: float
    eyes_closed: bool
    phone_detected: bool
    book_detected: bool
    head_angle: float
    gaze_direction: str
    is_looking_away: bool
    is_looking_down: bool
    posture_score: float
    is_slouching: bool
    # Temporal durations
    phone_duration: float = 0.0
    eyes_closed_duration: float = 0.0
    face_missing_duration: float = 0.0
    looking_away_duration: float = 0.0
    poor_posture_duration: float = 0.0
    is_face_blocked: bool = False
    face_blocked_duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "face_detected": self.face_detected,
            "eye_ratio": round(self.eye_ratio, 3),
            "eyes_closed": self.eyes_closed,
            "phone_detected": self.phone_detected,
            "book_detected": self.book_detected,
            "head_angle": round(self.head_angle, 1),
            "gaze_direction": self.gaze_direction,
            "is_looking_away": self.is_looking_away,
            "is_looking_down": self.is_looking_down,
            "posture_score": round(self.posture_score, 2),
            "is_slouching": self.is_slouching,
            "phone_duration": round(self.phone_duration, 1),
            "eyes_closed_duration": round(self.eyes_closed_duration, 1),
            "face_missing_duration": round(self.face_missing_duration, 1),
            "looking_away_duration": round(self.looking_away_duration, 1),
            "poor_posture_duration": round(self.poor_posture_duration, 1),
            "is_face_blocked": self.is_face_blocked,
            "face_blocked_duration": round(self.face_blocked_duration, 1)
        }


class FeatureFusion:
    """
    Fuses Face, Gaze, Pose, YOLO, and Temporal features.
    """

    def fuse(
        self,
        face_detected: bool,
        eye_data: Optional[Dict[str, Any]],
        gaze_data: Optional[Dict[str, Any]],
        posture_data: Optional[Dict[str, Any]],
        phone_detected: bool,
        book_detected: bool,
        temporal_engine: TemporalEngine
    ) -> FusedFeatures:
        """
        Merge raw measurements into a FusedFeatures object.
        """
        eye_ratio = eye_data["average_ratio"] if (eye_data and "average_ratio" in eye_data) else 0.0
        eyes_closed = (eye_ratio < 0.20) if (face_detected and eye_data) else False

        gaze_dir = gaze_data["direction"] if gaze_data else "SCREEN"
        is_looking_away = gaze_data.get("is_looking_away", False) if gaze_data else False
        is_looking_down = gaze_data.get("is_looking_down", False) if gaze_data else False
        head_angle = gaze_data.get("head_yaw", 0.0) if gaze_data else 0.0

        posture_score = posture_data.get("posture_score", 1.0) if posture_data else 1.0
        is_slouching = posture_data.get("is_slouching", False) if posture_data else False

        phone_dur = temporal_engine.duration("phone") if temporal_engine else 0.0
        eyes_closed_dur = temporal_engine.duration("eyes_closed") if temporal_engine else 0.0
        face_missing_dur = temporal_engine.duration("no_face") if temporal_engine else 0.0
        looking_away_dur = temporal_engine.duration("looking_away") if temporal_engine else 0.0
        poor_posture_dur = temporal_engine.duration("poor_posture") if temporal_engine else 0.0

        # Face blocked condition: book or object hiding face while face is not detected
        is_face_blocked = bool(book_detected and not face_detected)
        face_blocked_dur = temporal_engine.duration("face_blocked") if temporal_engine else 0.0

        return FusedFeatures(
            face_detected=face_detected,
            eye_ratio=eye_ratio,
            eyes_closed=eyes_closed,
            phone_detected=phone_detected,
            book_detected=book_detected,
            head_angle=head_angle,
            gaze_direction=gaze_dir,
            is_looking_away=is_looking_away,
            is_looking_down=is_looking_down,
            posture_score=posture_score,
            is_slouching=is_slouching,
            phone_duration=phone_dur,
            eyes_closed_duration=eyes_closed_dur,
            face_missing_duration=face_missing_dur,
            looking_away_duration=looking_away_dur,
            poor_posture_duration=poor_posture_dur,
            is_face_blocked=is_face_blocked,
            face_blocked_duration=face_blocked_dur
        )

