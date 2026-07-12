"""
ml/predict.py — Reusable inference module for the tabular fraud and anomaly models.

Public API
----------
    tabular_score(txn: dict | pd.DataFrame, use_fusion: bool = True) -> float | np.ndarray
        Returns fraud probability in [0, 1] for a single transaction dict
        or a batch DataFrame.  use_fusion=True uses the fusion model (includes
        cyber_flag); use_fusion=False uses the tabular-only baseline.

    anomaly_score(txn: dict | pd.DataFrame) -> float | np.ndarray
        Returns the Isolation Forest anomaly score for a transaction.
        More negative → more anomalous. Typical range is roughly [-0.5, 0.5].
        A score below -0.1 is considered suspicious.

    score_transaction(txn: dict) -> dict
        Convenience wrapper that returns both scores plus a risk tier
        (LOW / MEDIUM / HIGH) in a single dict.

Models are loaded lazily on first call and cached for the lifetime of the
process.  Call `reload_models()` to force a fresh load (e.g. after retraining).

Usage
-----
    from ml.predict import tabular_score, anomaly_score, score_transaction

    txn = {
        "step": 42,
        "type": "TRANSFER",
        "amount": 250000.0,
        "user_id": "usr_001234",
        "oldbalanceOrg": 250000.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 250000.0,
        "cyber_compromise_in_window": True,
    }
    print(score_transaction(txn))
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

# ── project paths ─────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
MODELS_DIR = ROOT / "ml" / "models"

# ── model cache ───────────────────────────────────────────────────────────────
_CACHE: dict[str, Any] = {}


def _load_metadata() -> dict:
    if "_meta" not in _CACHE:
        meta_path = MODELS_DIR / "metadata.json"
        if not meta_path.exists():
            raise FileNotFoundError(
                f"Model metadata not found at {meta_path}. "
                "Run `python ml/train.py` first."
            )
        with open(meta_path) as f:
            _CACHE["_meta"] = json.load(f)
    return _CACHE["_meta"]


def _load_model(key: str, filename: str) -> Any:
    if key not in _CACHE:
        path = MODELS_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Model not found at {path}. Run `python ml/train.py` first."
            )
        _CACHE[key] = joblib.load(path)
    return _CACHE[key]


def _get_baseline_model():
    meta = _load_metadata()
    name = meta.get("best_baseline_model", "xgboost_baseline")
    return _load_model("baseline", f"{name}.joblib")


def _get_fusion_model():
    meta = _load_metadata()
    name = meta.get("best_fusion_model")
    if name is None:
        # Fall back to baseline if fusion wasn't trained
        return _get_baseline_model()
    return _load_model("fusion", f"{name}.joblib")


def _get_isolation_forest():
    return _load_model("iso", "isolation_forest.joblib")


def reload_models() -> None:
    """Clear the model cache so models are reloaded on next call."""
    _CACHE.clear()


# ── feature preparation for single-row inference ──────────────────────────────

def _prepare_single(txn: dict | pd.DataFrame) -> pd.DataFrame:
    """
    Convert a single transaction dict (or single-row DataFrame) into a
    DataFrame suitable for feature engineering.  Missing optional fields
    are filled with safe defaults.
    """
    import sys
    sys.path.insert(0, str(ROOT))

    if isinstance(txn, dict):
        row = pd.DataFrame([txn])
    else:
        row = txn.copy()

    # Required columns with defaults
    defaults = {
        "step": 1,
        "type": "TRANSFER",
        "amount": 0.0,
        "user_id": "unknown",
        "oldbalanceOrg": 0.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "cyber_compromise_in_window": False,
    }
    for col, val in defaults.items():
        if col not in row.columns:
            row[col] = val

    return row


# ── public API ────────────────────────────────────────────────────────────────

def tabular_score(
    txn: dict | pd.DataFrame,
    use_fusion: bool = True,
) -> float | np.ndarray:
    """
    Return fraud probability for a transaction.

    Parameters
    ----------
    txn        : single transaction as dict or pd.DataFrame (batch supported).
    use_fusion : if True, use the fusion model (includes cyber_flag);
                 if False, use the tabular-only baseline.

    Returns
    -------
    float if input is a dict, np.ndarray if input is a DataFrame.
    """
    from ml.features import (
        FEATURE_COLS_BASELINE,
        FEATURE_COLS_FUSION,
        engineer_features,
    )

    is_single = isinstance(txn, dict)
    df = _prepare_single(txn)

    fe = engineer_features(df)
    cols = FEATURE_COLS_FUSION if use_fusion else FEATURE_COLS_BASELINE
    X = fe[cols]

    model = _get_fusion_model() if use_fusion else _get_baseline_model()
    probs = model.predict_proba(X)[:, 1]

    return float(probs[0]) if is_single else probs


def anomaly_score(txn: dict | pd.DataFrame) -> float | np.ndarray:
    """
    Return the Isolation Forest anomaly score for a transaction.

    Score interpretation:
        > 0.0  : normal (unlikely anomaly)
        < 0.0  : anomalous; more negative = more unusual
        < -0.1 : flag for review

    Parameters
    ----------
    txn : single transaction dict or DataFrame batch.

    Returns
    -------
    float if input is a dict, np.ndarray if input is a DataFrame.
    """
    from ml.features import (
        FEATURE_COLS_BASELINE,
        FEATURE_COLS_FUSION,
        engineer_features,
    )

    meta = _load_metadata()
    if_cols = meta.get("isolation_forest_cols", FEATURE_COLS_FUSION)

    is_single = isinstance(txn, dict)
    df = _prepare_single(txn)
    fe = engineer_features(df)
    X = fe[if_cols]

    iso = _get_isolation_forest()
    scores = iso.score_samples(X)  # higher = more normal; raw decision function

    return float(scores[0]) if is_single else scores


def score_transaction(txn: dict) -> dict:
    """
    Compute all model scores for a single transaction and return a structured dict.

    Returns
    -------
    {
        "fraud_prob_fusion"  : float,   # 0–1, from fusion model
        "fraud_prob_baseline": float,   # 0–1, from tabular-only baseline
        "anomaly_score"      : float,   # negative = anomalous
        "risk_tier"          : str,     # "LOW" | "MEDIUM" | "HIGH"
        "signals"            : list[str]
    }
    """
    fp_fusion = tabular_score(txn, use_fusion=True)
    fp_base = tabular_score(txn, use_fusion=False)
    a_score = anomaly_score(txn)

    # Risk tier logic (thresholds tuned to ~0.5% FPR operating point)
    if fp_fusion >= 0.5 or a_score < -0.15:
        tier = "HIGH"
    elif fp_fusion >= 0.15 or a_score < -0.05:
        tier = "MEDIUM"
    else:
        tier = "LOW"

    signals: list[str] = []
    if txn.get("cyber_compromise_in_window"):
        signals.append("cyber_compromise_in_window")
    if txn.get("newbalanceOrig", 1) == 0:
        signals.append("originator_balance_drained")
    if txn.get("oldbalanceDest", 1) == 0:
        signals.append("destination_was_empty")
    if fp_fusion > fp_base + 0.05:
        signals.append("cyber_context_increased_risk")
    if a_score < -0.1:
        signals.append("anomalous_pattern_detected")

    return {
        "fraud_prob_fusion": round(fp_fusion, 6),
        "fraud_prob_baseline": round(fp_base, 6),
        "anomaly_score": round(float(a_score), 6),
        "risk_tier": tier,
        "signals": signals,
    }


# ── CLI quick-test ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("Loading models and scoring a sample transaction …")

    sample = {
        "step": 400,
        "type": "TRANSFER",
        "amount": 300_000.0,
        "user_id": "usr_demo_001",
        "oldbalanceOrg": 300_000.0,
        "newbalanceOrig": 0.0,
        "oldbalanceDest": 0.0,
        "newbalanceDest": 300_000.0,
        "cyber_compromise_in_window": True,
    }

    result = score_transaction(sample)
    print("\n=== score_transaction output ===")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("\n✓ predict.py working correctly")
