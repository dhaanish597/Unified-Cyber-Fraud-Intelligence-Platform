from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "ml" / "models"


@dataclass
class InferenceResult:
    status: str
    implementation: str
    version: str | None
    action: str
    score: float | None
    fraud_probability: float | None
    anomaly_score: float | None
    reasons: list[str] = field(default_factory=list)
    artifacts: list[dict[str, str]] = field(default_factory=list)
    latency_ms: float = 0.0
    error_code: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "implementation": self.implementation,
            "version": self.version,
            "action": self.action,
            "score": self.score,
            "fraud_probability": self.fraud_probability,
            "anomaly_score": self.anomaly_score,
            "reasons": self.reasons,
            "artifacts": self.artifacts,
            "latency_ms": self.latency_ms,
            "error_code": self.error_code,
        }


class ModelRuntime:
    """Availability-aware adapter around the repository's trained model loader."""

    REQUIRED_METADATA_KEYS = {
        "best_baseline_model",
        "isolation_forest_cols",
    }

    def __init__(self, models_dir: Path = MODELS_DIR):
        self.models_dir = models_dir
        self._availability = self._inspect()

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _inspect(self) -> dict[str, Any]:
        metadata_path = self.models_dir / "metadata.json"
        if not metadata_path.exists():
            return {
                "status": "UNAVAILABLE",
                "reason": "MODEL_METADATA_MISSING",
                "models_dir": str(self.models_dir),
            }
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"status": "FAILED", "reason": "MODEL_METADATA_INVALID"}
        missing_keys = sorted(self.REQUIRED_METADATA_KEYS - set(metadata))
        if missing_keys:
            return {
                "status": "FAILED",
                "reason": "MODEL_METADATA_INCOMPLETE",
                "missing_keys": missing_keys,
            }
        baseline_name = metadata["best_baseline_model"]
        fusion_name = metadata.get("best_fusion_model") or baseline_name
        paths = {
            "baseline": self.models_dir / f"{baseline_name}.joblib",
            "fusion": self.models_dir / f"{fusion_name}.joblib",
            "isolation_forest": self.models_dir / "isolation_forest.joblib",
        }
        missing = [name for name, path in paths.items() if not path.exists()]
        if missing:
            return {
                "status": "UNAVAILABLE",
                "reason": "MODEL_ARTIFACTS_MISSING",
                "missing_artifacts": missing,
                "metadata": metadata,
            }
        return {
            "status": "AVAILABLE",
            "reason": None,
            "metadata": metadata,
            "artifacts": [
                {"name": name, "path": str(path), "sha256": self._sha256(path)}
                for name, path in paths.items()
            ],
        }

    def status(self) -> dict[str, Any]:
        return dict(self._availability)

    @staticmethod
    def _policy_fallback(
        transaction: dict[str, Any],
        threats: list[dict[str, Any]],
        graph_findings: list[dict[str, Any]],
        reason: str,
        started: float,
    ) -> InferenceResult:
        amount = max(0.0, float(transaction.get("amount", 0.0) or 0.0))
        critical_threat = any(threat.get("severity") == "CRITICAL" for threat in threats)
        high_threat = any(threat.get("severity") == "HIGH" for threat in threats)
        graph_alert = any(finding.get("severity") in {"HIGH", "CRITICAL"} for finding in graph_findings)
        reasons = [f"ML unavailable: {reason}"]
        if critical_threat:
            action = "BLOCK_TRANSACTION"
            reasons.append("Observed critical threat evidence")
        elif high_threat or graph_alert:
            action = "REQUIRE_FACE_AUTHENTICATION"
            reasons.append("Observed high-severity threat or graph evidence")
        elif amount > 50_000:
            action = "REQUIRE_BIOMETRIC"
            reasons.append("Configured high-value transaction policy")
        else:
            action = "ALLOW"
            reasons.append("No blocking deterministic policy matched")
        return InferenceResult(
            status="ModelUnavailable",
            implementation="POLICY_FALLBACK",
            version="policy-v1.0.3",
            action=action,
            score=None,
            fraud_probability=None,
            anomaly_score=None,
            reasons=reasons,
            latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
            error_code=reason,
        )

    def infer(
        self,
        transaction: dict[str, Any],
        threats: list[dict[str, Any]] | None = None,
        graph_findings: list[dict[str, Any]] | None = None,
    ) -> InferenceResult:
        started = time.perf_counter()
        threats = threats or []
        graph_findings = graph_findings or []
        if self._availability["status"] != "AVAILABLE":
            return self._policy_fallback(
                transaction,
                threats,
                graph_findings,
                self._availability["reason"],
                started,
            )
        try:
            from ml.predict import anomaly_score, tabular_score

            fraud_probability = float(tabular_score(transaction, use_fusion=True))
            anomaly = float(anomaly_score(transaction))
            if fraud_probability >= 0.5 or anomaly < -0.15:
                action = "BLOCK_TRANSACTION"
            elif fraud_probability >= 0.15 or anomaly < -0.05:
                action = "REQUIRE_BIOMETRIC"
            else:
                action = "ALLOW"
            return InferenceResult(
                status="EXECUTED",
                implementation="LIGHTGBM_OR_XGBOOST_PLUS_ISOLATION_FOREST",
                version=str(
                    self._availability["metadata"].get("model_version")
                    or self._availability["metadata"].get("trained_at")
                    or "metadata-unversioned"
                ),
                action=action,
                score=round(fraud_probability * 100.0, 6),
                fraud_probability=round(fraud_probability, 8),
                anomaly_score=round(anomaly, 8),
                reasons=["Decision derived from loaded model artifacts"],
                artifacts=self._availability["artifacts"],
                latency_ms=round((time.perf_counter() - started) * 1000.0, 3),
            )
        except Exception:
            return self._policy_fallback(
                transaction,
                threats,
                graph_findings,
                "MODEL_INFERENCE_FAILED",
                started,
            )


model_runtime = ModelRuntime()
