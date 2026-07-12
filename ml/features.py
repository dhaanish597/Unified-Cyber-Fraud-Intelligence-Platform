"""
ml/features.py — Feature engineering for the tabular fraud model.

Features produced
-----------------
Core (both baseline and fusion):
  - txn_type_enc         : label-encoded transaction type (CASH_OUT=0, TRANSFER=1)
  - log_amount           : log1p(amount) — compresses heavy tail
  - orig_balance_delta   : newbalanceOrig  - oldbalanceOrg
  - dest_balance_delta   : newbalanceDest  - oldbalanceDest
  - orig_balance_ratio   : newbalanceOrig  / (oldbalanceOrg  + 1)
  - dest_balance_ratio   : newbalanceDest  / (oldbalanceDest + 1)
  - zero_orig_after      : 1 if newbalanceOrig == 0 (money drained)
  - zero_dest_before     : 1 if oldbalanceDest == 0 (fresh/mule account)
  - velocity_1h          : txns by same user in the same step (proxy 1-hour window)
  - velocity_24h         : txns by same user within ±12 steps (proxy 24-hour window)
  - time_since_last_txn  : steps since user's previous transaction (0 = first ever)

Fusion-only (excluded from tabular-only baseline):
  - cyber_flag           : 1 if cyber_compromise_in_window else 0

The FEATURE_COLS_BASELINE and FEATURE_COLS_FUSION lists are the single source
of truth used by training and inference.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ── column name constants ────────────────────────────────────────────────────
TARGET_COL = "isFraud"

FEATURE_COLS_BASELINE: list[str] = [
    "txn_type_enc",
    "log_amount",
    "orig_balance_delta",
    "dest_balance_delta",
    "orig_balance_ratio",
    "dest_balance_ratio",
    "zero_orig_after",
    "zero_dest_before",
    "velocity_1h",
    "velocity_24h",
    "time_since_last_txn",
]

FEATURE_COLS_FUSION: list[str] = FEATURE_COLS_BASELINE + ["cyber_flag"]

# ── type encoding map ─────────────────────────────────────────────────────────
_TYPE_MAP: dict[str, int] = {
    "CASH_OUT": 0,
    "TRANSFER": 1,
    # add future types here; unknown falls back to -1
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _compute_velocities(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """
    Velocity features using the `step` column (1 step ≈ 1 hour in PaySim).

    velocity_1h  : number of transactions by the same user in the exact same step.
    velocity_24h : number of transactions by the same user within a ±12-step window.

    Both use fully vectorized pandas groupby operations for performance.
    """
    # Preserve original index
    orig_index = df.index

    # 1-hour velocity: count rows per (user_id, step)
    v1h = (
        df.groupby(["user_id", "step"])["step"]
        .transform("count")
        .astype(np.int32)
    )

    # 24-hour velocity: for each row, count how many rows from same user
    # have step in [step-12, step+12].
    # Strategy: for each user, build a cumulative count series on the step
    # axis using a sorted frame, then subtract counts outside window.
    # This is equivalent to a rolling window but works without fixed offset.
    #
    # Efficient approach: sort by (user_id, step), then for each user block
    # use searchsorted to find window boundaries — pure numpy, very fast.
    tmp = df[["user_id", "step"]].copy()
    tmp["_orig_pos"] = np.arange(len(tmp))
    tmp_sorted = tmp.sort_values(["user_id", "step"]).reset_index(drop=True)

    user_arr = tmp_sorted["user_id"].values
    step_arr = tmp_sorted["step"].values.astype(np.int64)
    v24h_arr = np.empty(len(tmp_sorted), dtype=np.int32)

    # Process each user block with numpy searchsorted (very fast)
    i = 0
    n = len(tmp_sorted)
    while i < n:
        # find end of user block
        uid = user_arr[i]
        j = i
        while j < n and user_arr[j] == uid:
            j += 1
        # block is tmp_sorted[i:j], steps are already sorted
        block_steps = step_arr[i:j]
        # for each row k in block, count rows where block_steps in [s-12, s+12]
        lo = np.searchsorted(block_steps, block_steps - 12, side="left")
        hi = np.searchsorted(block_steps, block_steps + 12, side="right")
        v24h_arr[i:j] = (hi - lo).astype(np.int32)
        i = j

    # Map back to original order
    orig_pos = tmp_sorted["_orig_pos"].values
    v24h_reordered = np.empty(n, dtype=np.int32)
    v24h_reordered[orig_pos] = v24h_arr

    v24h = pd.Series(v24h_reordered, index=orig_index)
    return v1h, v24h


def _compute_time_since_last(df: pd.DataFrame) -> pd.Series:
    """
    For each transaction, number of steps since the same user's last transaction.
    First transaction per user gets 0.
    """
    # Sort by (user_id, step), compute shift, map back
    tmp = df[["user_id", "step"]].copy()
    tmp["_orig_pos"] = np.arange(len(tmp))
    tmp_sorted = tmp.sort_values(["user_id", "step"])

    prev_step = tmp_sorted.groupby("user_id")["step"].shift(1)
    delta = (tmp_sorted["step"] - prev_step).fillna(0).astype(float)

    # Map back to original order
    result = np.empty(len(tmp), dtype=float)
    result[tmp_sorted["_orig_pos"].values] = delta.values
    return pd.Series(result, index=df.index)


# ── main entry point ──────────────────────────────────────────────────────────

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the raw/processed transactions DataFrame and returns a new DataFrame
    with all engineered features appended.  The original columns are preserved
    so callers can still access `isFraud`, `user_id`, `step`, etc.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain at minimum: step, type, amount, nameOrig, user_id,
        oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest,
        isFraud (if labels are needed), cyber_compromise_in_window.

    Returns
    -------
    pd.DataFrame with all original columns plus the engineered feature columns.
    """
    out = df.copy()

    # 1. Transaction-type encoding
    out["txn_type_enc"] = out["type"].map(_TYPE_MAP).fillna(-1).astype(int)

    # 2. Log-scaled amount
    out["log_amount"] = np.log1p(out["amount"])

    # 3. Balance deltas
    out["orig_balance_delta"] = out["newbalanceOrig"] - out["oldbalanceOrg"]
    out["dest_balance_delta"] = out["newbalanceDest"] - out["oldbalanceDest"]

    # 4. Balance ratios (avoid division by zero with +1 smoothing)
    out["orig_balance_ratio"] = out["newbalanceOrig"] / (out["oldbalanceOrg"] + 1.0)
    out["dest_balance_ratio"] = out["newbalanceDest"] / (out["oldbalanceDest"] + 1.0)

    # 5. Zero-balance flags (strong fraud signals in PaySim / TRANSFER+CASH_OUT)
    out["zero_orig_after"] = (out["newbalanceOrig"] == 0.0).astype(int)
    out["zero_dest_before"] = (out["oldbalanceDest"] == 0.0).astype(int)

    # 6. Velocity features (vectorized)
    v1h, v24h = _compute_velocities(out)
    out["velocity_1h"] = v1h.values
    out["velocity_24h"] = v24h.values

    # 7. Time-since-last-transaction per user
    out["time_since_last_txn"] = _compute_time_since_last(out).values

    # 8. Cyber-context flag (fusion feature — excluded from baseline)
    if "cyber_compromise_in_window" in out.columns:
        out["cyber_flag"] = out["cyber_compromise_in_window"].astype(int)
    else:
        out["cyber_flag"] = 0

    return out


def get_feature_matrix(
    df: pd.DataFrame,
    include_cyber: bool = True,
) -> tuple[pd.DataFrame, "pd.Series | None"]:
    """
    Convenience wrapper: engineers features and returns (X, y).

    Parameters
    ----------
    df            : raw transactions DataFrame
    include_cyber : if True, includes cyber_flag (fusion model);
                    if False, returns tabular-only baseline features.

    Returns
    -------
    X : pd.DataFrame  -- feature matrix
    y : pd.Series | None -- labels (isFraud), or None if column absent
    """
    fe = engineer_features(df)
    cols = FEATURE_COLS_FUSION if include_cyber else FEATURE_COLS_BASELINE
    X = fe[cols].copy()
    y = fe[TARGET_COL].copy() if TARGET_COL in fe.columns else None
    return X, y
