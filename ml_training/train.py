"""
Model Training & Selection Pipeline for Phase 12.
Trains and compares Logistic Regression, Random Forest, and Gradient Boosting.
Selects best performing model based on validation macro F1-score and serializes artifact.
"""

import os
import json
import time
from typing import Dict, Any
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report
import joblib

from ml_training.datasets.generator import generate_behavior_samples
from ml_training.preprocessing.pipeline import BehavioralDataPipeline


def train_and_select_model(
    samples_per_class: int = 250,
    model_output_path: str = "models/behavior_model.joblib",
    metadata_output_path: str = "models/model_metadata.json"
) -> Dict[str, Any]:
    """
    Main training workflow:
    1. Generate balanced multi-modal behavioral dataset
    2. Preprocess with strict featurization split
    3. Train candidate models
    4. Evaluate on validation set
    5. Save champion model to disk
    """
    print("=" * 60)
    print("PHASE 12 ML MODEL TRAINING & SELECTION PIPELINE")
    print("=" * 60)

    # 1. Dataset Generation
    print(f"\n[1/5] Generating behavioral dataset ({samples_per_class} samples/class)...")
    X, y, feature_names = generate_behavior_samples(samples_per_class=samples_per_class)
    print(f"Total dataset shape: X={X.shape}, y={y.shape}")

    # 2. Preprocessing
    print("\n[2/5] Splitting data (70% train, 15% val, 15% test) & scaling...")
    pipeline = BehavioralDataPipeline(random_state=42)
    X_train, X_val, X_test, y_train, y_val, y_test = pipeline.split_and_preprocess(
        X, y, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15
    )
    print(f"Train samples: {len(y_train)} | Val samples: {len(y_val)} | Test samples: {len(y_test)}")

    # 3. Candidate Models
    candidates = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42, C=1.0),
        "RandomForest": RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)
    }

    results: Dict[str, Any] = {}
    best_name = None
    best_val_f1 = -1.0
    best_model = None

    # 4. Training & Validation
    print("\n[3/5] Training candidate models and evaluating on validation split...")
    for name, model in candidates.items():
        t0 = time.perf_counter()
        model.fit(X_train, y_train)
        fit_time_ms = (time.perf_counter() - t0) * 1000

        # Predict on validation set
        val_preds = model.predict(X_val)
        val_acc = float(accuracy_score(y_val, val_preds))
        val_f1_macro = float(f1_score(y_val, val_preds, average="macro"))
        val_f1_weighted = float(f1_score(y_val, val_preds, average="weighted"))

        results[name] = {
            "val_accuracy": round(val_acc, 4),
            "val_f1_macro": round(val_f1_macro, 4),
            "val_f1_weighted": round(val_f1_weighted, 4),
            "fit_time_ms": round(fit_time_ms, 2)
        }

        print(f"  * {name:18}: Acc={val_acc:.4f} | F1-Macro={val_f1_macro:.4f} | Time={fit_time_ms:.1f}ms")

        if val_f1_macro > best_val_f1:
            best_val_f1 = val_f1_macro
            best_name = name
            best_model = model

    print(f"\nChampion model selected: {best_name} (Validation Macro F1: {best_val_f1:.4f})")

    # 5. Serialization
    print(f"\n[4/5] Serializing champion model and scaler to {model_output_path}...")
    os.makedirs(os.path.dirname(model_output_path) or ".", exist_ok=True)
    classes = list(best_model.classes_)
    artifact = {
        "model": best_model,
        "scaler": pipeline.scaler,
        "imputer": pipeline.imputer,
        "classes": classes,
        "feature_names": feature_names
    }
    joblib.dump(artifact, model_output_path)

    metadata = {
        "champion_model": best_name,
        "classes": classes,
        "feature_names": feature_names,
        "validation_macro_f1": best_val_f1,
        "comparison_results": results,
        "dataset_size": int(len(y)),
        "trained_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }

    os.makedirs(os.path.dirname(metadata_output_path) or ".", exist_ok=True)
    with open(metadata_output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    # Save test set for independent evaluation script
    test_set_path = "ml_training/datasets/test_split.npz"
    os.makedirs(os.path.dirname(test_set_path) or ".", exist_ok=True)
    np.savez_compressed(test_set_path, X_test=X_test, y_test=y_test)

    print(f"[5/5] Pipeline complete. Metadata saved to {metadata_output_path}.")
    return metadata


if __name__ == "__main__":
    train_and_select_model()
