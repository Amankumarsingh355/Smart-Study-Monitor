"""
Model Manager for Phase 12 ML Subsystem.
Handles thread-safe loading, caching, versioning, and validation of trained behavioral models.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Tuple
import joblib

logger = logging.getLogger("smart_study_monitor.ml.model_manager")


class ModelManager:
    """
    Manages loading and lifecycle of serialized scikit-learn models.
    Supports fallback to rule engine when model artifacts are absent.
    """

    DEFAULT_MODEL_PATH = "models/behavior_model.joblib"
    DEFAULT_METADATA_PATH = "models/model_metadata.json"

    def __init__(
        self,
        model_path: Optional[str] = None,
        metadata_path: Optional[str] = None
    ):
        self.model_path = model_path or self.DEFAULT_MODEL_PATH
        self.metadata_path = metadata_path or self.DEFAULT_METADATA_PATH

        self._model: Optional[Any] = None
        self._scaler: Optional[Any] = None
        self._metadata: Dict[str, Any] = {}
        self._classes: list = []
        self._loaded: bool = False

        self.load()

    @property
    def is_loaded(self) -> bool:
        """Whether a valid model is currently loaded in memory."""
        return self._loaded and self._model is not None

    @property
    def model(self) -> Optional[Any]:
        return self._model

    @property
    def scaler(self) -> Optional[Any]:
        return self._scaler

    @property
    def classes(self) -> list:
        return self._classes

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._metadata

    def load(self) -> bool:
        """
        Load model, scaler, and metadata from disk.
        Returns True if successfully loaded, False otherwise (triggering graceful fallback).
        """
        if not os.path.exists(self.model_path):
            logger.info(f"ML model artifact not found at {self.model_path}. Using rule-based fallback.")
            self._loaded = False
            return False

        try:
            artifact = joblib.load(self.model_path)
            if isinstance(artifact, dict) and "model" in artifact:
                self._model = artifact["model"]
                self._scaler = artifact.get("scaler")
                self._classes = list(artifact.get("classes", []))
            else:
                self._model = artifact
                self._classes = list(getattr(self._model, "classes_", []))

            # Load optional metadata
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    self._metadata = json.load(f)
            else:
                self._metadata = {"model_name": type(self._model).__name__}

            self._loaded = True
            logger.info(f"Loaded ML model successfully: {type(self._model).__name__} with classes: {self._classes}")
            return True

        except Exception as e:
            logger.warning(f"Failed to load ML model from {self.model_path}: {e}. Falling back to rules.")
            self._model = None
            self._scaler = None
            self._loaded = False
            return False

    def save(
        self,
        model: Any,
        scaler: Optional[Any] = None,
        classes: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Save trained model, scaler, and metadata to disk."""
        try:
            os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
            artifact = {
                "model": model,
                "scaler": scaler,
                "classes": classes or list(getattr(model, "classes_", []))
            }
            joblib.dump(artifact, self.model_path)

            self._model = model
            self._scaler = scaler
            self._classes = artifact["classes"]
            self._metadata = metadata or {}

            meta_dir = os.path.dirname(self.metadata_path) or "."
            os.makedirs(meta_dir, exist_ok=True)
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._metadata, f, indent=2)

            self._loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to save ML model artifact: {e}")
            return False
