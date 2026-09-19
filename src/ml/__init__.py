"""
Machine Learning Subsystem for Smart Study Monitor.
Provides feature extraction, scikit-learn behavior classification,
hybrid rule/ML fusion, personalization baselines, and intelligent study recommendations.
"""

from .feature_schema import FEATURE_COLUMNS, StudyBehaviorClass
from .feature_extractor import FeatureExtractor
from .model_manager import ModelManager
from .behavior_classifier import BehaviorClassifier
from .predictor import MLPredictor
from .hybrid_engine import HybridStudyStateEngine
from .personalization import PersonalizationEngine
from .recommendations import RecommendationEngine

__all__ = [
    "FEATURE_COLUMNS",
    "StudyBehaviorClass",
    "FeatureExtractor",
    "ModelManager",
    "BehaviorClassifier",
    "MLPredictor",
    "HybridStudyStateEngine",
    "PersonalizationEngine",
    "RecommendationEngine",
]
