"""
Behavior Classifier for Phase 12 ML Subsystem.
Performs model inference, class probability calculation, and confidence evaluation.
"""

from typing import Dict, Any, Optional, Tuple, List
import numpy as np

from .model_manager import ModelManager
from .feature_schema import FEATURE_COLUMNS, StudyBehaviorClass


class BehaviorClassifier:
    """
    Executes behavioral prediction using a trained scikit-learn model.
    """

    def __init__(self, model_manager: Optional[ModelManager] = None):
        self.model_manager = model_manager or ModelManager()

    @property
    def is_available(self) -> bool:
        """Returns True if the ML model is loaded and ready for inference."""
        return self.model_manager.is_loaded

    def predict(
        self,
        feature_vector: np.ndarray
    ) -> Tuple[Optional[str], float, Dict[str, float]]:
        """
        Run inference on a single 14-dimensional feature vector.

        Returns:
            Tuple of (predicted_class_str, confidence_float, probabilities_dict)
            Returns (None, 0.0, {}) if model is unavailable.
        """
        if not self.is_available:
            return None, 0.0, {}

        # Reshape to 2D for scikit-learn
        X = np.asarray(feature_vector, dtype=np.float32).reshape(1, -1)

        # Apply scaler if present
        if self.model_manager.scaler is not None:
            X = self.model_manager.scaler.transform(X)

        model = self.model_manager.model
        classes = self.model_manager.classes

        try:
            if hasattr(model, "predict_proba"):
                probs = model.predict_proba(X)[0]
                best_idx = int(np.argmax(probs))
                confidence = float(probs[best_idx])
                best_class = str(classes[best_idx])

                prob_dict = {
                    str(cls_name): float(p)
                    for cls_name, p in zip(classes, probs)
                }
                return best_class, confidence, prob_dict
            else:
                pred = model.predict(X)[0]
                return str(pred), 1.0, {str(pred): 1.0}
        except Exception:
            return None, 0.0, {}
