"""
Preprocessing Pipeline for Phase 12 ML Training.
Adheres strictly to ML Best Practices:
1. Featurization Ordering: Always split data BEFORE fitting scalers or transformations.
2. Missing value imputation: Checks for and handles NaN / null values.
3. Feature scaling: StandardScaler fit strictly on train split, applied to val/test.
"""

from typing import Tuple, Dict, Any, Optional
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


class BehavioralDataPipeline:
    """
    Handles data splitting, cleaning, imputation, and feature standardization.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()
        self.is_fitted = False

    def split_and_preprocess(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split dataset into train, validation, and test sets.
        Fit imputer and scaler ONLY on train data, then transform val and test data.

        Returns:
            (X_train_scaled, X_val_scaled, X_test_scaled, y_train, y_val, y_test)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"

        # 1. First split: Train vs Temp (Val + Test)
        temp_ratio = val_ratio + test_ratio
        X_train, X_temp, y_train, y_temp = train_test_split(
            X, y,
            test_size=temp_ratio,
            stratify=y,
            random_state=self.random_state
        )

        # 2. Second split: Val vs Test
        relative_test_ratio = test_ratio / temp_ratio
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp,
            test_size=relative_test_ratio,
            stratify=y_temp,
            random_state=self.random_state
        )

        # 3. Fit Imputer and Scaler strictly on X_train
        X_train_clean = self.imputer.fit_transform(X_train)
        X_train_scaled = self.scaler.fit_transform(X_train_clean)

        # 4. Transform Validation and Test sets using train parameters
        X_val_clean = self.imputer.transform(X_val)
        X_val_scaled = self.scaler.transform(X_val_clean)

        X_test_clean = self.imputer.transform(X_test)
        X_test_scaled = self.scaler.transform(X_test_clean)

        self.is_fitted = True

        return (
            X_train_scaled,
            X_val_scaled,
            X_test_scaled,
            y_train,
            y_val,
            y_test
        )
