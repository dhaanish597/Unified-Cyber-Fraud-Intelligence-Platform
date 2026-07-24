from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ComponentName(str, Enum):
    IDENTITY = "identity"
    DEVICE = "device"
    RUNTIME = "runtime"
    BEHAVIOUR = "behaviour"
    NETWORK = "network"
    GEO = "geo"
    THREAT = "threat"
    GRAPH = "graph"
    TRANSACTION = "transaction"


class SessionLifecycle(str, Enum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    SUSPICIOUS = "SUSPICIOUS"
    CHALLENGED = "CHALLENGED"
    BLOCKED = "BLOCKED"
    CLOSED = "CLOSED"


class TrustTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STABLE = "STABLE"
    DECLINING = "DECLINING"


class ActiveSignal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    component: ComponentName
    impact: float
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str
    source: str
    observed_at: datetime = Field(default_factory=utc_now)
    recoverable: bool = True


class SessionContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    session_id: str
    user_id: str
    device_id: str = ""
    location: str = ""
    created_at: datetime = Field(default_factory=utc_now)
    last_activity: datetime = Field(default_factory=utc_now)
    lifecycle: SessionLifecycle = SessionLifecycle.CREATED
    threat_count: int = 0
    event_count: int = 0
    coverage: dict[ComponentName, set[str]] = Field(
        default_factory=lambda: {name: set() for name in ComponentName}
    )
    signals: dict[ComponentName, dict[str, ActiveSignal]] = Field(
        default_factory=lambda: {name: {} for name in ComponentName}
    )
    facts: dict[str, Any] = Field(default_factory=dict)


class TrustComponent(BaseModel):
    name: ComponentName
    value: float = Field(ge=0.0, le=100.0)
    confidence: float = Field(ge=0.0, le=100.0)
    previous_value: float = Field(ge=0.0, le=100.0)
    difference: float
    trend: TrustTrend
    reasons: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=utc_now)


class TrustPassport(BaseModel):
    passport_id: str
    session_id: str
    user_id: str
    identity_trust: float
    device_trust: float
    runtime_trust: float
    behaviour_trust: float
    network_trust: float
    geo_trust: float
    threat_trust: float
    graph_trust: float
    transaction_trust: float
    overall_trust: float
    confidence: float
    current_status: SessionLifecycle
    created_time: datetime
    updated_time: datetime
    version: str
    trust_trend: TrustTrend
    components: dict[ComponentName, TrustComponent]

    def to_compatible_dict(self) -> dict[str, Any]:
        """Return the enterprise model plus fields expected by the Phase 1 SDK."""
        payload = self.model_dump(mode="json")
        payload.update(
            {
                "composite_trust": self.overall_trust,
                "session_trust": self.overall_trust,
                "policy_version": self.version,
                "sync_timestamp": self.updated_time.isoformat(),
            }
        )
        return payload


class TrustDelta(BaseModel):
    delta_id: str
    session_id: str
    passport_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str
    component: str
    previous_trust: float
    current_trust: float
    difference: float
    reason: str
    source: str
    is_recovery: bool = False


class TrustSnapshot(BaseModel):
    snapshot_id: str
    session_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    event_type: str
    previous_trust: float
    current_trust: float
    delta: float
    reason: str
    passport: TrustPassport


class SessionSummary(BaseModel):
    session_id: str
    user_id: str
    trust: float
    confidence: float
    threat_count: int
    last_activity: datetime
    current_state: SessionLifecycle
    current_device: str
    location: str
    created_at: datetime
    closed_at: datetime | None = None
    trust_trend: TrustTrend


class TrustUpdate(BaseModel):
    msg_type: str = "trust_passport_update"
    session_id: str
    event_type: str
    passport: TrustPassport
    deltas: list[TrustDelta] = Field(default_factory=list)
    snapshot: TrustSnapshot
    processing_time_ms: float
