"""
Synthetic Behavioral Dataset Generator for Phase 12 ML Training.
Generates realistic multi-modal feature vectors reflecting real-world study conditions,
biometric distributions, sensor noise, and edge cases.
"""

from typing import Tuple, List, Dict, Any
import numpy as np

from src.ml.feature_schema import FEATURE_COLUMNS, StudyBehaviorClass


def generate_behavior_samples(
    samples_per_class: int = 250,
    random_seed: int = 42
) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """
    Generate synthetic dataset of behavioral samples.

    Returns:
        (X, y, feature_names) where:
            X: np.ndarray of shape (N, 14)
            y: np.ndarray of string labels of shape (N,)
            feature_names: list of feature names
    """
    np.random.seed(random_seed)

    X_list: List[np.ndarray] = []
    y_list: List[str] = []

    classes = [
        StudyBehaviorClass.FOCUSED,
        StudyBehaviorClass.READING,
        StudyBehaviorClass.LOOKING_AWAY,
        StudyBehaviorClass.DROWSY,
        StudyBehaviorClass.PHONE_USAGE,
        StudyBehaviorClass.POOR_POSTURE,
    ]

    for cls in classes:
        n = samples_per_class

        if cls == StudyBehaviorClass.FOCUSED:
            ear = np.random.uniform(0.26, 0.35, n)
            blink_rate = np.random.normal(14.0, 3.0, n)
            eye_closure = np.random.uniform(0.0, 0.2, n)
            gaze_dir = np.zeros(n)  # SCREEN
            gaze_stab = np.random.uniform(0.85, 0.98, n)
            away_dur = np.zeros(n)
            head_pitch = np.random.normal(2.0, 4.0, n)
            head_yaw = np.random.normal(0.0, 3.0, n)
            shoulder_angle = np.random.uniform(0.5, 3.5, n)
            is_slouch = np.zeros(n)
            phone_det = np.zeros(n)
            phone_conf = np.random.uniform(0.0, 0.05, n)
            book_det = np.random.choice([0.0, 1.0], size=n, p=[0.85, 0.15])
            movement = np.random.uniform(0.03, 0.12, n)

        elif cls == StudyBehaviorClass.READING:
            ear = np.random.uniform(0.24, 0.32, n)
            blink_rate = np.random.normal(11.0, 2.5, n)
            eye_closure = np.random.uniform(0.0, 0.25, n)
            gaze_dir = np.ones(n)  # DOWN
            gaze_stab = np.random.uniform(0.65, 0.85, n)
            away_dur = np.zeros(n)
            head_pitch = np.random.normal(16.0, 4.0, n)
            head_yaw = np.random.normal(0.0, 4.0, n)
            shoulder_angle = np.random.uniform(1.0, 4.5, n)
            is_slouch = np.zeros(n)
            phone_det = np.zeros(n)
            phone_conf = np.random.uniform(0.0, 0.05, n)
            book_det = np.random.choice([1.0, 0.0], size=n, p=[0.75, 0.25])
            movement = np.random.uniform(0.06, 0.18, n)

        elif cls == StudyBehaviorClass.LOOKING_AWAY:
            ear = np.random.uniform(0.25, 0.34, n)
            blink_rate = np.random.normal(16.0, 4.0, n)
            eye_closure = np.random.uniform(0.0, 0.3, n)
            gaze_dir = np.random.choice([2.0, 3.0, 4.0], size=n)  # LEFT, RIGHT, UP
            gaze_stab = np.random.uniform(0.35, 0.70, n)
            away_dur = np.random.uniform(1.8, 6.5, n)
            head_pitch = np.random.normal(0.0, 8.0, n)
            head_yaw = np.random.choice([-1.0, 1.0], size=n) * np.random.uniform(15.0, 35.0, n)
            shoulder_angle = np.random.uniform(1.0, 5.0, n)
            is_slouch = np.zeros(n)
            phone_det = np.zeros(n)
            phone_conf = np.random.uniform(0.0, 0.08, n)
            book_det = np.zeros(n)
            movement = np.random.uniform(0.12, 0.35, n)

        elif cls == StudyBehaviorClass.DROWSY:
            ear = np.random.uniform(0.12, 0.19, n)
            blink_rate = np.random.uniform(2.0, 7.0, n)
            eye_closure = np.random.uniform(1.6, 5.5, n)
            gaze_dir = np.random.choice([0.0, 1.0], size=n)
            gaze_stab = np.random.uniform(0.70, 0.95, n)
            away_dur = np.zeros(n)
            head_pitch = np.random.normal(18.0, 7.0, n)
            head_yaw = np.random.normal(0.0, 4.0, n)
            shoulder_angle = np.random.uniform(1.0, 6.0, n)
            is_slouch = np.random.choice([0.0, 1.0], size=n, p=[0.4, 0.6])
            phone_det = np.zeros(n)
            phone_conf = np.random.uniform(0.0, 0.05, n)
            book_det = np.zeros(n)
            movement = np.random.uniform(0.01, 0.04, n)

        elif cls == StudyBehaviorClass.PHONE_USAGE:
            ear = np.random.uniform(0.24, 0.33, n)
            blink_rate = np.random.normal(15.0, 3.5, n)
            eye_closure = np.random.uniform(0.0, 0.2, n)
            gaze_dir = np.ones(n)  # DOWN
            gaze_stab = np.random.uniform(0.75, 0.95, n)
            away_dur = np.zeros(n)
            head_pitch = np.random.normal(20.0, 5.0, n)
            head_yaw = np.random.normal(0.0, 5.0, n)
            shoulder_angle = np.random.uniform(2.0, 7.0, n)
            is_slouch = np.random.choice([0.0, 1.0], size=n, p=[0.5, 0.5])
            phone_det = np.ones(n)
            phone_conf = np.random.uniform(0.72, 0.98, n)
            book_det = np.zeros(n)
            movement = np.random.uniform(0.05, 0.15, n)

        elif cls == StudyBehaviorClass.POOR_POSTURE:
            ear = np.random.uniform(0.25, 0.34, n)
            blink_rate = np.random.normal(14.0, 3.0, n)
            eye_closure = np.random.uniform(0.0, 0.2, n)
            gaze_dir = np.random.choice([0.0, 1.0], size=n)
            gaze_stab = np.random.uniform(0.75, 0.95, n)
            away_dur = np.zeros(n)
            head_pitch = np.random.uniform(15.0, 35.0, n)
            head_yaw = np.random.normal(0.0, 8.0, n)
            shoulder_angle = np.random.uniform(9.0, 24.0, n)
            is_slouch = np.ones(n)
            phone_det = np.zeros(n)
            phone_conf = np.random.uniform(0.0, 0.05, n)
            book_det = np.random.choice([0.0, 1.0], size=n, p=[0.8, 0.2])
            movement = np.random.uniform(0.04, 0.12, n)

        # Add Gaussian noise across all dimensions
        feature_matrix = np.column_stack([
            np.clip(ear + np.random.normal(0, 0.01, n), 0.05, 0.45),
            np.clip(blink_rate + np.random.normal(0, 0.8, n), 0.0, 50.0),
            np.clip(eye_closure + np.random.normal(0, 0.05, n), 0.0, 10.0),
            gaze_dir,
            np.clip(gaze_stab + np.random.normal(0, 0.02, n), 0.0, 1.0),
            np.clip(away_dur + np.random.normal(0, 0.1, n), 0.0, 15.0),
            np.clip(head_pitch + np.random.normal(0, 1.0, n), -45.0, 45.0),
            np.clip(head_yaw + np.random.normal(0, 1.0, n), -45.0, 45.0),
            np.clip(shoulder_angle + np.random.normal(0, 0.5, n), 0.0, 40.0),
            is_slouch,
            phone_det,
            np.clip(phone_conf, 0.0, 1.0),
            book_det,
            np.clip(movement + np.random.normal(0, 0.01, n), 0.0, 1.0)
        ]).astype(np.float32)

        X_list.append(feature_matrix)
        y_list.extend([cls.value] * n)

    X = np.vstack(X_list)
    y = np.array(y_list)

    # Shuffle the dataset
    indices = np.random.permutation(len(y))
    return X[indices], y[indices], FEATURE_COLUMNS
