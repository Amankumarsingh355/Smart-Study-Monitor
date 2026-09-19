"""
Predictor for Phase 12 ML Subsystem.
Implements confidence-aware behavioral prediction and ambiguity detection
to prevent false alerts from borderline probability distributions.
"""

from typing import Dict, Any, Optional, Tuple, NamedTuple
import numpy as np

from .behavior_classifier import BehaviorClassifier


class PredictionResult(NamedTuple):
    predicted_state: Optional[str]
    confidence: float
    is_ambiguous: bool
    probabilities: Dict[str, float]
    fallback_reason: Optional[str] = None


class MLPredictor:
    """
    Confidence-aware predictor wrapping the BehaviorClassifier.
    Filters out uncertain or borderline predictions.
    """

    def __init__(
        self,
        classifier: Optional[BehaviorClassifier] = None,
        min_confidence_threshold: float = 0.55,
        min_margin_threshold: float = 0.10
    ):
        self.classifier = classifier or BehaviorClassifier()
        self.min_confidence_threshold = min_confidence_threshold
        self.min_margin_threshold = min_margin_threshold

    @property
    def is_available(self) -> bool:
        return self.classifier.is_available

    def predict(self, feature_vector: np.ndarray) -> PredictionResult:
        """
        Evaluate feature vector with confidence and margin filtering.
        """
        if not self.classifier.is_available:
            return PredictionResult(
                predicted_state=None,
                confidence=0.0,
                is_ambiguous=True,
                probabilities={},
                fallback_reason="MODEL_NOT_LOADED"
            )

        best_class, confidence, probabilities = self.classifier.predict(feature_vector)

        if best_class is None:
            return PredictionResult(
                predicted_state=None,
                confidence=0.0,
                is_ambiguous=True,
                probabilities={},
                fallback_reason="INFERENCE_FAILED"
            )

        # 1. Absolute confidence check
        if confidence < self.min_confidence_threshold:
            return PredictionResult(
                predicted_state=best_class,
                confidence=confidence,
                is_ambiguous=True,
                probabilities=probabilities,
                fallback_reason=f"LOW_CONFIDENCE_{confidence:.2f}"
            )

        # 2. Margin check: top-1 vs top-2 probability difference
        sorted_probs = sorted(probabilities.values(), reverse=True)
        if len(sorted_probs) >= 2:
            top1, top2 = sorted_probs[0], sorted_probs[1]
            if (top1 - top2) < self.min_margin_threshold:
                return PredictionResult(
                    predicted_state=best_class,
                    confidence=confidence,
                    is_ambiguous=True,
                    probabilities=probabilities,
                    fallback_reason=f"AMBIGUOUS_MARGIN_{top1 - top2:.2f}"
                )

        # Confident, distinct prediction
        return PredictionResult(
            predicted_state=best_class,
            confidence=confidence,
            is_ambiguous=False,
            probabilities=probabilities,
            fallback_reason=None
        )
