from enum import Enum
from typing import Dict, Tuple, Optional, Any
from .feature_fusion import FusedFeatures


class StudyState(Enum):
    FOCUSED = "focused"
    READING = "reading"
    LOOKING_AWAY = "looking_away"
    PHONE_USAGE = "phone_usage"
    DROWSY = "drowsy"
    POOR_POSTURE = "poor_posture"
    AWAY_FROM_DESK = "away_from_desk"
    FACE_BLOCKED = "face_blocked"
    DISTRACTED = "distracted"
    NO_FACE = "no_face"
    UNKNOWN = "unknown"


class StudyStateEngine:
    """
    Phase 7 Behavioral State & Confidence Machine.
    
    Evaluates fused perception signals (Face, Eye, Pose, Gaze, Objects, Temporal)
    into rich contextual study states with evidence-based confidence and debouncing:
    - FOCUSED: Active screen study
    - READING: Head down + book detected + eyes open
    - LOOKING_AWAY: Sustained off-screen gaze
    - PHONE_USAGE: Sustained phone presence
    - DROWSY: Sustained eye closure / head dropping
    - POOR_POSTURE: Sustained slouching or severe head/shoulder misalignment
    - AWAY_FROM_DESK: Student absent
    """

    def __init__(
        self,
        phone_persistence_seconds: float = 1.0,
        drowsy_duration_seconds: float = 2.0,
        looking_away_duration_seconds: float = 2.5,
        poor_posture_duration_seconds: float = 3.0,
        away_duration_seconds: float = 2.0,
        face_block_duration_seconds: float = 1.5,
        debounce_frames: int = 1
    ):
        self.phone_persistence_seconds = phone_persistence_seconds
        self.drowsy_duration_seconds = drowsy_duration_seconds
        self.looking_away_duration_seconds = looking_away_duration_seconds
        self.poor_posture_duration_seconds = poor_posture_duration_seconds
        self.away_duration_seconds = away_duration_seconds
        self.face_block_duration_seconds = face_block_duration_seconds
        self.debounce_frames = max(1, debounce_frames)

        self._current_state: StudyState = StudyState.FOCUSED
        self._current_confidence: float = 1.0
        self._current_evidence: Dict[str, float] = {}

        # Debouncing tracking
        self._pending_state: Optional[StudyState] = None
        self._pending_count: int = 0

    def determine_state(
        self,
        face_detected: bool,
        phone_detected: bool,
        eyes_closed: bool,
        drowsy: bool,
        face_blocked: bool = False
    ) -> StudyState:
        """
        Legacy rule evaluation preserved for backwards compatibility.
        """
        if face_blocked:
            self._current_state = StudyState.FACE_BLOCKED
            self._current_confidence = 0.92
            return self._current_state

        if not face_detected:
            self._current_state = StudyState.NO_FACE
            self._current_confidence = 0.95
            return self._current_state

        if phone_detected:
            self._current_state = StudyState.PHONE_USAGE
            self._current_confidence = 0.92
            return self._current_state

        if drowsy or eyes_closed:
            self._current_state = StudyState.DROWSY
            self._current_confidence = 0.88
            return self._current_state

        self._current_state = StudyState.FOCUSED
        self._current_confidence = 0.95
        return self._current_state

    def _evaluate_candidate(self, features: FusedFeatures) -> StudyState:
        """
        Determine candidate state using multi-modal priority rules.
        """
        # 1. Absence / Missing Face vs Face Blocked by Book/Object
        if not features.face_detected:
            if getattr(features, "is_face_blocked", False) and getattr(features, "face_blocked_duration", 0.0) >= self.face_block_duration_seconds:
                return StudyState.FACE_BLOCKED
            if features.face_missing_duration >= self.away_duration_seconds:
                return StudyState.AWAY_FROM_DESK
            else:
                return StudyState.NO_FACE

        # 2. Phone Usage (High-priority distraction)
        if features.phone_detected and features.phone_duration >= self.phone_persistence_seconds:
            return StudyState.PHONE_USAGE

        # 3. Drowsiness (Sustained eye closure)
        if features.eyes_closed and features.eyes_closed_duration >= self.drowsy_duration_seconds:
            return StudyState.DROWSY

        # 4. Reading Detection (Book detected + Looking down + Eyes open)
        if features.book_detected and features.is_looking_down and not features.eyes_closed:
            return StudyState.READING

        # 5. Looking Away (Head turned or off-screen gaze sustained)
        if features.is_looking_away and features.looking_away_duration >= self.looking_away_duration_seconds:
            return StudyState.LOOKING_AWAY

        # 6. Poor Posture (Severe tilt or slouch sustained)
        if features.is_slouching and features.poor_posture_duration >= self.poor_posture_duration_seconds:
            return StudyState.POOR_POSTURE

        # 7. Default: Focused study
        return StudyState.FOCUSED

    def calculate_confidence(
        self,
        state: StudyState,
        features: FusedFeatures
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate evidence metrics and confidence score (0.0 - 1.0) for a state.
        Features -> Evidence -> Confidence
        """
        evidence: Dict[str, float] = {}
        confidence = 0.85

        if state == StudyState.FOCUSED:
            evidence["face_detected"] = 1.0 if features.face_detected else 0.0
            evidence["gaze_screen"] = 1.0 if features.gaze_direction == "SCREEN" else 0.70
            evidence["posture"] = max(0.0, min(1.0, features.posture_score))
            evidence["eyes_open"] = 1.0 if not features.eyes_closed else 0.0
            raw_conf = (
                0.40 * evidence["face_detected"] +
                0.30 * evidence["gaze_screen"] +
                0.20 * evidence["posture"] +
                0.10 * evidence["eyes_open"]
            )
            confidence = max(0.50, min(0.99, raw_conf))

        elif state == StudyState.READING:
            evidence["book_detected"] = 0.95 if features.book_detected else 0.40
            evidence["gaze_down"] = 0.90 if features.is_looking_down else 0.50
            evidence["eyes_open"] = 1.0 if not features.eyes_closed else 0.0
            raw_conf = (
                0.45 * evidence["book_detected"] +
                0.40 * evidence["gaze_down"] +
                0.15 * evidence["eyes_open"]
            )
            confidence = max(0.50, min(0.98, raw_conf))

        elif state == StudyState.PHONE_USAGE:
            persistence = min(1.0, features.phone_duration / max(0.1, self.phone_persistence_seconds))
            evidence["phone_detected"] = 0.92 if features.phone_detected else 0.0
            evidence["persistence"] = round(persistence, 2)
            raw_conf = 0.70 * evidence["phone_detected"] + 0.30 * persistence
            confidence = max(0.50, min(0.98, raw_conf))

        elif state == StudyState.DROWSY:
            ear_severity = min(1.0, max(0.0, (0.22 - features.eye_ratio) / 0.15)) if features.eyes_closed else 0.40
            duration_factor = min(1.0, features.eyes_closed_duration / max(0.1, self.drowsy_duration_seconds))
            evidence["eye_closure"] = round(ear_severity, 2)
            evidence["duration"] = round(duration_factor, 2)
            raw_conf = 0.50 * ear_severity + 0.50 * duration_factor
            confidence = max(0.50, min(0.96, raw_conf))

        elif state == StudyState.LOOKING_AWAY:
            duration_factor = min(1.0, features.looking_away_duration / max(0.1, self.looking_away_duration_seconds))
            evidence["gaze_away"] = 0.88 if features.is_looking_away else 0.40
            evidence["duration"] = round(duration_factor, 2)
            raw_conf = 0.55 * evidence["gaze_away"] + 0.45 * duration_factor
            confidence = max(0.50, min(0.95, raw_conf))

        elif state == StudyState.POOR_POSTURE:
            posture_defect = max(0.0, min(1.0, 1.0 - features.posture_score))
            duration_factor = min(1.0, features.poor_posture_duration / max(0.1, self.poor_posture_duration_seconds))
            evidence["posture_defect"] = round(posture_defect, 2)
            evidence["duration"] = round(duration_factor, 2)
            raw_conf = 0.55 * posture_defect + 0.45 * duration_factor
            confidence = max(0.50, min(0.95, raw_conf))

        elif state == StudyState.FACE_BLOCKED:
            evidence["face_blocked"] = 1.0 if getattr(features, "is_face_blocked", False) else 0.5
            duration_factor = min(1.0, getattr(features, "face_blocked_duration", 0.0) / max(0.1, self.face_block_duration_seconds))
            evidence["duration"] = round(duration_factor, 2)
            raw_conf = 0.60 * evidence["face_blocked"] + 0.40 * duration_factor
            confidence = max(0.50, min(0.98, raw_conf))

        elif state in (StudyState.AWAY_FROM_DESK, StudyState.NO_FACE):
            duration_factor = min(1.0, features.face_missing_duration / max(0.1, self.away_duration_seconds))
            evidence["face_missing"] = 1.0 if not features.face_detected else 0.0
            evidence["duration"] = round(duration_factor, 2)
            raw_conf = 0.70 * evidence["face_missing"] + 0.30 * duration_factor
            confidence = max(0.50, min(0.98, raw_conf))

        return round(confidence, 2), evidence


    def evaluate_fused(self, features: FusedFeatures) -> StudyState:
        """
        Primary evaluation using fused multi-modal features with debouncing.
        """
        raw_candidate = self._evaluate_candidate(features)
        conf, evidence = self.calculate_confidence(raw_candidate, features)

        if self.debounce_frames <= 1:
            self._current_state = raw_candidate
            self._current_confidence = conf
            self._current_evidence = evidence
            return self._current_state

        # Debouncing across frames
        if raw_candidate == self._current_state:
            self._pending_state = None
            self._pending_count = 0
            self._current_confidence = conf
            self._current_evidence = evidence
        else:
            if raw_candidate == self._pending_state:
                self._pending_count += 1
                if self._pending_count >= self.debounce_frames:
                    self._current_state = raw_candidate
                    self._current_confidence = conf
                    self._current_evidence = evidence
                    self._pending_state = None
                    self._pending_count = 0
            else:
                self._pending_state = raw_candidate
                self._pending_count = 1

        return self._current_state

    def evaluate(
        self,
        temporal_engine,
        face_detected: bool,
        phone_visible: bool,
        eyes_closed: bool,
        current_time: Optional[float] = None
    ) -> StudyState:
        """
        Temporal-aware evaluation for basic pipelines.
        """
        if not face_detected:
            self._current_state = StudyState.NO_FACE
            self._current_confidence = 0.95
            return self._current_state

        is_phone_persistent = temporal_engine.active_for(
            "phone", self.phone_persistence_seconds, current_time=current_time
        )
        is_drowsy_persistent = temporal_engine.active_for(
            "eyes_closed", self.drowsy_duration_seconds, current_time=current_time
        )

        return self.determine_state(
            face_detected=face_detected,
            phone_detected=is_phone_persistent,
            eyes_closed=False,
            drowsy=is_drowsy_persistent
        )

    @property
    def current_state(self) -> StudyState:
        return self._current_state

    @property
    def current_confidence(self) -> float:
        return self._current_confidence

    @property
    def current_evidence(self) -> Dict[str, float]:
        return self._current_evidence
