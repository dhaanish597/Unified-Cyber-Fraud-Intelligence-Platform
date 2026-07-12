# /ml

Feature engineering, model training, saved models, and honest metrics reporting.

- `features.py` (not yet written) — velocity, balance deltas, time-since-last-txn, log-scaled
  amount, transaction-type encoding.
- Training scripts for XGBoost/LightGBM (+ SMOTE on the training split only) and Isolation Forest.
- `predict.py` (not yet written) — exposes `tabular_score(txn)` and `anomaly_score(txn)` loading the
  saved models.
- `models/` — gitignored. Saved model binaries.
- `metrics_report.md` (not yet written) — PR-AUC, F1, recall at a fixed low FPR, confusion matrix,
  and the fusion-uplift headline number. Never plain accuracy on the imbalanced set.

See root `CLAUDE.md` for the metrics-honesty rule this directory must follow.
