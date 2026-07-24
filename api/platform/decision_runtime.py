from __future__ import annotations

import uuid
from typing import Any

from .model_runtime import InferenceResult


class DecisionEngineAdapter:
    """Authoritative decision adapter for model, fallback, and threat outcomes."""

    version = "decision-policy-v1.0.3"

    def decide(
        self,
        inference: InferenceResult,
        threats: list[dict[str, Any]],
    ) -> dict[str, Any]:
        critical = [
            threat for threat in threats if threat.get("severity") == "CRITICAL"
        ]
        if critical:
            action = "BLOCK_TRANSACTION"
            source = "THREAT_POLICY"
            reason_codes = [
                f"THREAT_{threat['threat_category'].upper().replace(' ', '_')}"
                for threat in critical
            ]
        else:
            action = inference.action
            source = inference.implementation
            reason_codes = [
                reason.upper().replace(" ", "_")[:80]
                for reason in inference.reasons
            ]
        return {
            "decision_id": f"DEC_{uuid.uuid4().hex[:12].upper()}",
            "decision": action,
            "decision_source": source,
            "decision_policy_version": self.version,
            "confidence": (
                round(inference.fraud_probability * 100.0, 4)
                if inference.status == "EXECUTED"
                and inference.fraud_probability is not None
                else None
            ),
            "confidence_type": (
                "MODEL_PROBABILITY"
                if inference.status == "EXECUTED"
                else "NOT_AVAILABLE"
            ),
            "reason_codes": reason_codes,
            "model_status": inference.status,
        }


decision_engine = DecisionEngineAdapter()
