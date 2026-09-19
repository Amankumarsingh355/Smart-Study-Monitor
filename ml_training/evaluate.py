"""
Independent Model Evaluation & Benchmarking for Phase 12.
Evaluates the champion model on held-out test split, computing:
- Multi-class Accuracy
- Macro & Weighted Precision, Recall, F1-Score
- Confusion Matrix
- Per-sample Inference Latency (p50, p95, p99)
"""

import os
import json
import time
from typing import Dict, Any
import numpy as np
import joblib
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


def evaluate_champion_model(
    model_path: str = "models/behavior_model.joblib",
    test_split_path: str = "ml_training/datasets/test_split.npz"
) -> Dict[str, Any]:
    """
    Run evaluation on the held-out test set.
    """
    print("=" * 60)
    print("PHASE 12 MODEL EVALUATION & LATENCY BENCHMARK")
    print("=" * 60)

    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model artifact not found at {model_path}. Run train.py first.")

    if not os.path.exists(test_split_path):
        raise FileNotFoundError(f"Test split not found at {test_split_path}. Run train.py first.")

    # Load artifacts
    artifact = joblib.load(model_path)
    model = artifact["model"]
    classes = artifact["classes"]

    data = np.load(test_split_path)
    X_test = data["X_test"]
    y_test = data["y_test"]

    print(f"\nLoaded model: {type(model).__name__}")
    print(f"Test samples: {len(y_test)}")
    print(f"Classes: {classes}")

    # 1. Predictions
    y_pred = model.predict(X_test)

    # 2. Metrics
    acc = float(accuracy_score(y_test, y_pred))
    prec_macro = float(precision_score(y_test, y_pred, average="macro", zero_division=0))
    rec_macro = float(recall_score(y_test, y_pred, average="macro", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_test, y_pred, labels=classes)
    report_dict = classification_report(y_test, y_pred, labels=classes, output_dict=True, zero_division=0)

    print("\n--- Test Set Performance ---")
    print(f"Accuracy         : {acc * 100:.2f}%")
    print(f"Macro Precision  : {prec_macro * 100:.2f}%")
    print(f"Macro Recall     : {rec_macro * 100:.2f}%")
    print(f"Macro F1-Score   : {f1_macro * 100:.2f}%")
    print(f"Weighted F1-Score: {f1_weighted * 100:.2f}%")

    print("\n--- Confusion Matrix ---")
    header = f"{'':15}" + "".join([f"{c[:8]:>10}" for c in classes])
    print(header)
    for i, row_class in enumerate(classes):
        row_str = f"{row_class[:14]:15}" + "".join([f"{cm[i, j]:>10}" for j in range(len(classes))])
        print(row_str)

    # 3. Latency Benchmarking (1,000 single-sample inferences)
    print("\n--- Inference Latency Benchmark ---")
    latencies = []
    # Warmup
    for _ in range(20):
        _ = model.predict(X_test[0:1])

    for i in range(min(500, len(X_test))):
        sample = X_test[i:i+1]
        t0 = time.perf_counter()
        _ = model.predict(sample)
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000.0)  # ms

    p50 = float(np.percentile(latencies, 50))
    p95 = float(np.percentile(latencies, 95))
    p99 = float(np.percentile(latencies, 99))
    mean_lat = float(np.mean(latencies))

    print(f"Single-sample latency (Mean): {mean_lat:.3f} ms")
    print(f"Single-sample latency (P50) : {p50:.3f} ms")
    print(f"Single-sample latency (P95) : {p95:.3f} ms")
    print(f"Single-sample latency (P99) : {p99:.3f} ms")

    eval_results = {
        "test_accuracy": acc,
        "macro_precision": prec_macro,
        "macro_recall": rec_macro,
        "macro_f1": f1_macro,
        "weighted_f1": f1_weighted,
        "confusion_matrix": cm.tolist(),
        "classes": classes,
        "latency_ms": {
            "mean": mean_lat,
            "p50": p50,
            "p95": p95,
            "p99": p99
        }
    }

    eval_out_path = "models/evaluation_results.json"
    with open(eval_out_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)
    print(f"\nEvaluation metrics saved to {eval_out_path}.")

    return eval_results


if __name__ == "__main__":
    evaluate_champion_model()
