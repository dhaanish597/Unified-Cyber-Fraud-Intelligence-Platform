# ML Runtime

## Required artifacts

`ml/models/metadata.json` must name `best_baseline_model` and
`isolation_forest_cols`. The runtime requires the named baseline/fusion joblib
files and `isolation_forest.joblib`. It records SHA-256 hashes and reports the
metadata version/training timestamp.

## Inference

When artifacts exist, `ml.predict.tabular_score` executes the configured
LightGBM/XGBoost-compatible classifier and `anomaly_score` executes Isolation
Forest. Returned values are real artifact outputs.

When any artifact is missing or inference throws, the result is:

```json
{
  "status": "ModelUnavailable",
  "implementation": "POLICY_FALLBACK",
  "score": null,
  "fraud_probability": null,
  "anomaly_score": null,
  "error_code": "MODEL_METADATA_MISSING"
}
```

The policy may block/challenge based on observed critical/high threats, graph
findings, or the configured high-value threshold. It does not invent a model
score or confidence.

## GraphSAGE

GraphSAGE is a separate graph-runtime status. This checkout has no compatible
versioned `graph/models/graphsage.pt` plus metadata, so it is explicitly
unavailable and is not represented as executed.

## Local validation result

At the final validation point, `ml/models` was absent. Policy fallback executed;
LightGBM, Isolation Forest, and GraphSAGE inference did not execute. Training was
not started because repository guidance prohibits unrequested training and the
production contract explicitly supports unavailable artifacts.

