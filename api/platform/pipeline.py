from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from api.cyber_threat_engine import CyberThreatEngine, cyber_threat_engine
from api.sdk_engine import FusionAdaptiveTrustSDKEngine, sdk_engine
from api.session_intelligence import session_intelligence, trust_update_broker

from .graph_runtime import GraphRuntime, graph_runtime
from .model_runtime import ModelRuntime, model_runtime
from .decision_runtime import DecisionEngineAdapter, decision_engine


class PipelineValidationError(ValueError):
    pass


@dataclass
class PipelineResult:
    pipeline_id: str
    timestamp: str
    normalized_event: dict[str, Any]
    event_ack: dict[str, Any]
    threats: list[dict[str, Any]]
    graph: dict[str, Any]
    inference: dict[str, Any]
    decision: dict[str, Any]
    session_update: dict[str, Any] | None
    timings: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_id": self.pipeline_id,
            "timestamp": self.timestamp,
            "normalized_event": self.normalized_event,
            "event_ack": self.event_ack,
            "threats": self.threats,
            "graph": self.graph,
            "inference": self.inference,
            "decision": self.decision,
            "session_update": self.session_update,
            "timings": self.timings,
        }


class AuthoritativePlatformPipeline:
    """Single orchestration path for SDK and transaction security evaluation."""

    def __init__(
        self,
        sdk: FusionAdaptiveTrustSDKEngine = sdk_engine,
        threats: CyberThreatEngine = cyber_threat_engine,
        graph: GraphRuntime = graph_runtime,
        models: ModelRuntime = model_runtime,
        decisions: DecisionEngineAdapter = decision_engine,
    ):
        self.sdk = sdk
        self.threat_engine = threats
        self.graph_runtime = graph
        self.model_runtime = models
        self.decision_engine = decisions

    @staticmethod
    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        event = dict(payload)
        event_type = str(event.get("event_type") or event.get("type") or "").upper().strip()
        if not event_type:
            raise PipelineValidationError("event_type is required")
        session_id = str(event.get("session_id") or "").strip()
        if not session_id:
            raise PipelineValidationError("session_id is required")
        device_id = str(event.get("device_id") or "").strip()
        event["event_type"] = event_type
        event["session_id"] = session_id
        event["device_id"] = device_id
        event["amount"] = max(0.0, float(event.get("amount", 0.0) or 0.0))
        event["timestamp"] = str(
            event.get("timestamp") or datetime.now(timezone.utc).isoformat()
        )
        event.setdefault("event_id", f"EVT_{uuid.uuid4().hex[:12].upper()}")
        return event

    async def process(
        self,
        payload: dict[str, Any],
        *,
        require_existing_session: bool,
        publish: bool = True,
    ) -> PipelineResult:
        total_started = time.perf_counter()
        event = self.normalize(payload)
        if require_existing_session and event["session_id"] not in self.sdk.sdk_sessions:
            raise PipelineValidationError("session_id is not active")

        stage_started = time.perf_counter()
        event_ack = self.sdk.ingest_event(event)
        normalize_ingest_ms = (time.perf_counter() - stage_started) * 1000.0

        stage_started = time.perf_counter()
        direct_threats = self.threat_engine.evaluate_event(event)
        threat_ms = (time.perf_counter() - stage_started) * 1000.0

        stage_started = time.perf_counter()
        graph_result = self.graph_runtime.process(event)
        graph_ms = (time.perf_counter() - stage_started) * 1000.0
        graph_payload = graph_result.to_dict()

        graph_threats: list[dict[str, Any]] = []
        if graph_result.findings:
            graph_event = {
                "session_id": event["session_id"],
                "device_id": event["device_id"],
                "user_id": event.get("user_id", "unknown"),
                "event_type": "GRAPH_INTELLIGENCE_RESULT",
                "_graph_backend": graph_result.backend,
                "_graph_findings": [
                    finding.to_dict() for finding in graph_result.findings
                ],
            }
            graph_threats = self.threat_engine.evaluate_event(graph_event)
        all_threats = direct_threats + graph_threats

        inference = self.model_runtime.infer(
            event,
            threats=all_threats,
            graph_findings=graph_payload["findings"],
        )
        decision = self.decision_engine.decide(inference, all_threats)
        decision["session_id"] = event["session_id"]

        session_update = None
        passport = session_intelligence.repository.get_passport(event["session_id"])
        if passport:
            update = session_intelligence.process_event(event, all_threats)
            session_update = update.model_dump(mode="json")
            if publish:
                await trust_update_broker.publish(session_update)

        total_ms = (time.perf_counter() - total_started) * 1000.0
        return PipelineResult(
            pipeline_id=f"PIPE_{uuid.uuid4().hex[:12].upper()}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            normalized_event=event,
            event_ack=event_ack,
            threats=all_threats,
            graph=graph_payload,
            inference=inference.to_dict(),
            decision=decision,
            session_update=session_update,
            timings={
                "normalization_and_ingest_ms": round(normalize_ingest_ms, 3),
                "threat_engine_ms": round(threat_ms, 3),
                "graph_engine_ms": round(graph_ms, 3),
                "model_or_fallback_ms": inference.latency_ms,
                "total_ms": round(total_ms, 3),
            },
        )


platform_pipeline = AuthoritativePlatformPipeline()
