"""
Hybrid Decision Engine for Phase 12 ML Subsystem.
Fuses deterministic safety rules, statistical ML predictions, temporal persistence,
and personal adaptive baselines into a single robust behavioral decision.
"""

from typing import Dict, Any, Optional, Tuple
from collections import deque

from src.behavior.study_state import StudyState, StudyStateEngine
from .feature_extractor import FeatureExtractor
from .predictor import MLPredictor, PredictionResult
from .personalization import PersonalizationEngine


class HybridStudyStateEngine:
    """
    Hybrid decision engine combining rules and machine learning.
    Guarantees deterministic safety constraints while leveraging ML for nuanced classification.
    """

    def __init__(
        self,
        rule_engine: Optional[StudyStateEngine] = None,
        ml_predictor: Optional[MLPredictor] = None,
        feature_extractor: Optional[FeatureExtractor] = None,
        personalization: Optional[PersonalizationEngine] = None,
        debounce_frames: int = 3
    ):
        self.rule_engine = rule_engine or StudyStateEngine(debounce_frames=debounce_frames)
        self.ml_predictor = ml_predictor or MLPredictor()
        self.feature_extractor = feature_extractor or FeatureExtractor()
        self.personalization = personalization or PersonalizationEngine()

        self.debounce_frames = debounce_frames
        self._history = deque(maxlen=debounce_frames)
        self._current_state: StudyState = StudyState.FOCUSED
        self._current_confidence: float = 1.0
        self._decision_source: str = "INIT"

    @property
    def current_state(self) -> StudyState:
        return self._current_state

    @property
    def current_confidence(self) -> float:
        return self._current_confidence

    @property
    def decision_source(self) -> str:
        """Returns whether the last decision was made by 'RULE', 'ML', or 'HYBRID_FUSION'."""
        return self._decision_source

    def evaluate_fused(
        self,
        fused_features: Any,
        current_time: Optional[float] = None
    ) -> StudyState:
        """Convenience evaluation method matching StudyStateEngine interface."""
        state, _ = self.evaluate(
            face_detected=fused_features.face_detected,
            phone_detected=fused_features.phone_detected,
            book_detected=fused_features.book_detected,
            fused_features=fused_features,
            current_time=current_time
        )
        return state

    def evaluate(
        self,
        face_detected: bool,
        eye_data: Optional[Dict[str, Any]] = None,
        gaze_data: Optional[Dict[str, Any]] = None,
        posture_data: Optional[Dict[str, Any]] = None,
        phone_detected: bool = False,
        phone_confidence: float = 0.0,
        book_detected: bool = False,
        temporal_engine: Optional[Any] = None,
        fused_features: Optional[Dict[str, Any]] = None,
        current_time: Optional[float] = None
    ) -> Tuple[StudyState, float]:
        """
        Main decision loop for hybrid behavior classification.
        """
        now = current_time if current_time is not None else 0.0

        # 1. Evaluate Rule-based Engine
        if fused_features is not None:
            rule_state = self.rule_engine.evaluate_fused(fused_features)
        else:
            from src.behavior.feature_fusion import FeatureFusion
            ff = FeatureFusion()
            fused = ff.fuse(
                face_detected=face_detected,
                eye_data=eye_data,
                gaze_data=gaze_data,
                posture_data=posture_data,
                phone_detected=phone_detected,
                book_detected=book_detected,
                temporal_engine=temporal_engine
            )
            rule_state = self.rule_engine.evaluate_fused(fused)
        rule_conf = self.rule_engine.current_confidence

        # 2. Update Personalization Baseline if in focused state
        ear_val = float(eye_data.get("average_ratio", 0.28)) if (face_detected and eye_data) else 0.28
        shoulder_val = float(posture_data.get("shoulder_tilt_deg", 0.0)) if posture_data else 0.0
        self.personalization.update_baseline(
            ear=ear_val,
            shoulder_angle=shoulder_val,
            is_focused_state=(rule_state == StudyState.FOCUSED)
        )

        # 3. Deterministic Safety Overrides
        # Invariant 1: Persistent Phone usage confirmed by YOLO + Temporal
        phone_duration = temporal_engine.get_duration("phone", now) if temporal_engine else 0.0
        if phone_detected and phone_duration >= 2.0:
            self._decision_source = "RULE_SAFETY_OVERRIDE"
            return self._debounce(StudyState.PHONE_USAGE, max(0.95, phone_confidence))

        # Invariant 2: Absence from desk
        if not face_detected:
            self._decision_source = "RULE_SAFETY_OVERRIDE"
            return self._debounce(rule_state, rule_conf)

        # 4. Extract ML Feature Vector
        feature_vec = self.feature_extractor.extract(
            face_detected=face_detected,
            eye_data=eye_data,
            gaze_data=gaze_data,
            posture_data=posture_data,
            phone_detected=phone_detected,
            phone_confidence=phone_confidence,
            book_detected=book_detected,
            temporal_engine=temporal_engine,
            current_time=now
        )

        # 5. Run ML Prediction
        pred_result: PredictionResult = self.ml_predictor.predict(feature_vec)

        # 6. Behavioral Fusion
        if self.ml_predictor.is_available and not pred_result.is_ambiguous and pred_result.predicted_state:
            ml_state_str = pred_result.predicted_state
            try:
                ml_state = StudyState[ml_state_str]
            except KeyError:
                ml_state = rule_state

            if ml_state == rule_state:
                # Agreement boosts confidence
                fused_conf = min(0.99, (rule_conf + pred_result.confidence) / 2.0 + 0.08)
                self._decision_source = "HYBRID_AGREEMENT"
                return self._debounce(ml_state, fused_conf)
            else:
                # Disagreement: compare confidences and adaptive personal baselines
                adaptive_ear_thresh = self.personalization.get_adaptive_ear_threshold()
                if ear_val < adaptive_ear_thresh and temporal_engine and temporal_engine.get_duration("eyes_closed", now) > 2.0:
                    self._decision_source = "PERSONALIZED_DROWSINESS"
                    return self._debounce(StudyState.DROWSY, 0.92)

                if pred_result.confidence >= 0.78 and rule_conf < 0.85:
                    self._decision_source = "ML_DOMINANT"
                    return self._debounce(ml_state, pred_result.confidence)
                else:
                    self._decision_source = "RULE_DOMINANT"
                    return self._debounce(rule_state, rule_conf)
        else:
            # Fallback to rule engine
            self._decision_source = "RULE_FALLBACK"
            return self._debounce(rule_state, rule_conf)

    def _debounce(self, target_state: StudyState, confidence: float) -> Tuple[StudyState, float]:
        """Debounce rapid frame-by-frame state alterations."""
        self._history.append(target_state)
        if len(self._history) == self.debounce_frames and all(s == target_state for s in self._history):
            self._current_state = target_state
            self._current_confidence = round(confidence, 2)
        return self._current_state, self._current_confidence
