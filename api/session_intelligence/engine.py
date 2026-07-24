from __future__ import annotations

import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .components import calculate_passport
from .models import (
    ActiveSignal,
    ComponentName,
    SessionContext,
    SessionLifecycle,
    TrustDelta,
    TrustPassport,
    TrustSnapshot,
    TrustUpdate,
    utc_now,
)
from .policy import (
    EVENT_CONTEXT_SIGNALS,
    LIFECYCLE_THRESHOLDS,
    RECOVERY_EVENTS,
    SEVERITY_THREAT_IMPACT,
    THREAT_IMPACT_COMPONENT_MAP,
)
from .repository import SessionTrustRepository


class SessionIntelligenceEngine:
    """Event-driven coordinator for session state and Trust Passport evolution."""

    def __init__(self, repository: SessionTrustRepository | None = None):
        self.repository = repository or SessionTrustRepository()

    @staticmethod
    def _passport_id(session_id: str) -> str:
        return f"PASS_{session_id}_{uuid4().hex[:10].upper()}"

    @staticmethod
    def _event_type(event: dict[str, Any]) -> str:
        return str(event.get("event_type") or event.get("msg_type") or "UNKNOWN").upper()

    @staticmethod
    def _mark_coverage(context: SessionContext, event: dict[str, Any], event_type: str) -> None:
        if event_type in {"SESSION_CREATED", "SESSION_STARTED", "USER_LOGIN", "BIOMETRIC_VERIFIED"}:
            context.coverage[ComponentName.IDENTITY].add("sdk_identity_event")
        if event.get("device_id") or any(
            key in event
            for key in ("root_detected", "emulator_detected", "frida_detected", "debugger_attached")
        ):
            context.coverage[ComponentName.DEVICE].add("sdk_device")
            context.coverage[ComponentName.RUNTIME].add("sdk_runtime")
        if any(key in event for key in ("vpn_detected", "proxy_detected", "network_type", "carrier")):
            context.coverage[ComponentName.NETWORK].add("sdk_network")
        if any(key in event for key in ("latitude", "longitude", "location", "city")):
            context.coverage[ComponentName.GEO].add("geo_telemetry")
        if any(key in event for key in ("typing_speed", "touch_pressure", "navigation_speed")):
            context.coverage[ComponentName.BEHAVIOUR].add("behaviour_telemetry")
        if event_type in {
            "BENEFICIARY_ADDED",
            "TRANSFER_INITIATED",
            "TRANSFER",
            "QR_PAYMENT",
            "BILL_PAYMENT",
            "RAPID_TRANSFER_SEQUENCE",
        } or float(event.get("amount", 0.0) or 0.0) > 0:
            context.coverage[ComponentName.TRANSACTION].add("sdk_transaction")

    @staticmethod
    def _apply_context_rules(
        context: SessionContext, event_type: str, now: datetime
    ) -> list[str]:
        reasons: list[str] = []
        for rule in EVENT_CONTEXT_SIGNALS.get(event_type, ()):
            signal = ActiveSignal(
                key=rule.key,
                component=rule.component,
                impact=rule.impact,
                confidence=rule.confidence,
                reason=rule.reason,
                source="SDK_EVENT",
                observed_at=now,
            )
            context.signals[rule.component][rule.key] = signal
            context.coverage[rule.component].add("sdk_context_event")
            reasons.append(rule.reason)
        return reasons

    @staticmethod
    def _apply_transaction_context(
        context: SessionContext, event: dict[str, Any], event_type: str, now: datetime
    ) -> list[str]:
        if event_type not in {
            "TRANSFER",
            "TRANSFER_INITIATED",
            "RAPID_TRANSFER_SEQUENCE",
            "QR_PAYMENT",
            "BILL_PAYMENT",
        }:
            return []
        amount = max(0.0, float(event.get("amount", 0.0) or 0.0))
        key = "transaction_exposure"
        if amount <= 0:
            context.signals[ComponentName.TRANSACTION].pop(key, None)
            return []
        # Smooth exposure grows with amount and is bounded. This is session
        # context posture, not a fraud probability or transaction risk score.
        impact = -min(25.0, max(0.0, math.log10(amount + 1.0) - 3.0) * 8.0)
        if event_type == "RAPID_TRANSFER_SEQUENCE":
            impact -= 8.0
        reason = f"Observed {event_type.lower().replace('_', ' ')} amount {amount:.2f}"
        context.signals[ComponentName.TRANSACTION][key] = ActiveSignal(
            key=key,
            component=ComponentName.TRANSACTION,
            impact=max(-35.0, impact),
            confidence=0.9,
            reason=reason,
            source="SDK_TRANSACTION_CONTEXT",
            observed_at=now,
        )
        return [reason]

    @staticmethod
    def _apply_threats(
        context: SessionContext, threats: list[dict[str, Any]], now: datetime
    ) -> list[str]:
        reasons: list[str] = []
        for threat in threats:
            name = str(threat.get("threat_name", "Unspecified threat"))
            confidence = max(0.0, min(1.0, float(threat.get("confidence", 0.0)) / 100.0))
            source = str(threat.get("detection_source", "CyberThreatEngine"))
            impact_map = threat.get("trust_impact") or {}

            context.coverage[ComponentName.THREAT].add("cyber_threat_engine")
            severity = str(threat.get("severity", "MEDIUM")).upper()
            threat_impact = SEVERITY_THREAT_IMPACT.get(severity, -10.0)
            threat_key = f"threat:{name}"
            context.signals[ComponentName.THREAT][threat_key] = ActiveSignal(
                key=threat_key,
                component=ComponentName.THREAT,
                impact=threat_impact,
                confidence=confidence,
                reason=f"{severity} threat observed: {name}",
                source=source,
                observed_at=now,
            )

            for raw_component, raw_impact in impact_map.items():
                for component in THREAT_IMPACT_COMPONENT_MAP.get(raw_component, ()):
                    if component == ComponentName.THREAT:
                        continue
                    context.coverage[component].add("cyber_threat_engine")
                    key = f"threat:{name}"
                    context.signals[component][key] = ActiveSignal(
                        key=key,
                        component=component,
                        impact=max(-60.0, min(0.0, float(raw_impact))),
                        confidence=confidence,
                        reason=f"{name} affected {component.value} trust",
                        source=source,
                        observed_at=now,
                    )
            reasons.append(f"{severity} threat observed: {name}")
        context.threat_count = len(context.signals[ComponentName.THREAT])
        return reasons

    @staticmethod
    def _apply_recovery(
        context: SessionContext, event_type: str
    ) -> list[str]:
        reasons: list[str] = []
        for component, signal_key, reason in RECOVERY_EVENTS.get(event_type, ()):
            if signal_key == "*":
                removed = list(context.signals[component])
                context.signals[component].clear()
                if component == ComponentName.THREAT:
                    # Clear threat-derived component effects by source key.
                    for other in ComponentName:
                        if other == ComponentName.THREAT:
                            continue
                        for key in list(context.signals[other]):
                            if key.startswith("threat:"):
                                context.signals[other].pop(key, None)
                if removed:
                    reasons.append(reason)
            elif context.signals[component].pop(signal_key, None):
                reasons.append(reason)
        context.threat_count = len(context.signals[ComponentName.THREAT])
        return reasons

    @staticmethod
    def _lifecycle(
        context: SessionContext, event_type: str, overall_trust: float
    ) -> SessionLifecycle:
        if context.lifecycle == SessionLifecycle.CLOSED:
            return SessionLifecycle.CLOSED
        if event_type in {"SESSION_ENDED", "SESSION_CLOSED", "LOGOUT"}:
            return SessionLifecycle.CLOSED
        if event_type in {"SESSION_BLOCKED", "TERMINATE_SESSION"}:
            return SessionLifecycle.BLOCKED
        if event_type in {"CHALLENGE_REQUIRED", "BIOMETRIC_CHALLENGE", "OTP_CHALLENGE"}:
            return SessionLifecycle.CHALLENGED
        if event_type == "SESSION_IDLE":
            return SessionLifecycle.IDLE
        if overall_trust < LIFECYCLE_THRESHOLDS["blocked_below"]:
            return SessionLifecycle.BLOCKED
        if overall_trust < LIFECYCLE_THRESHOLDS["suspicious_below"]:
            return SessionLifecycle.SUSPICIOUS
        return SessionLifecycle.ACTIVE

    @staticmethod
    def _reason(
        event_type: str, reasons: list[str], previous: float, current: float
    ) -> str:
        if reasons:
            return "; ".join(dict.fromkeys(reasons))
        if abs(current - previous) < 0.01:
            return f"{event_type} updated session context without changing active trust signals"
        return f"{event_type} changed the observed session trust posture"

    def start_session(
        self,
        session_data: dict[str, Any],
        initial_event: dict[str, Any] | None = None,
        threats: list[dict[str, Any]] | None = None,
    ) -> TrustUpdate:
        session_id = str(session_data["session_id"])
        existing = self.repository.get_context(session_id)
        if existing:
            return self.process_event(
                {"session_id": session_id, "event_type": "SESSION_STARTED"},
                threats or [],
            )
        now = utc_now()
        context = SessionContext(
            session_id=session_id,
            user_id=str(session_data.get("user_id", "unknown")),
            device_id=str(session_data.get("device_id", "")),
            created_at=now,
            last_activity=now,
            lifecycle=SessionLifecycle.CREATED,
        )
        event = {
            **(initial_event or {}),
            "session_id": session_id,
            "user_id": context.user_id,
            "device_id": context.device_id,
            "event_type": "SESSION_CREATED",
        }
        return self._reduce(context, event, threats or [], previous=None)

    def process_event(
        self, event: dict[str, Any], threats: list[dict[str, Any]] | None = None
    ) -> TrustUpdate:
        session_id = str(event.get("session_id") or "")
        if not session_id:
            raise ValueError("session_id is required for session intelligence")
        context = self.repository.get_context(session_id)
        previous = self.repository.get_passport(session_id)
        if not context:
            context = SessionContext(
                session_id=session_id,
                user_id=str(event.get("user_id", "unknown")),
                device_id=str(event.get("device_id", "")),
            )
        return self._reduce(context, event, threats or [], previous)

    def _reduce(
        self,
        context: SessionContext,
        event: dict[str, Any],
        threats: list[dict[str, Any]],
        previous: TrustPassport | None,
    ) -> TrustUpdate:
        t0 = time.perf_counter()
        now = utc_now()
        event_type = self._event_type(event)
        context.last_activity = now
        context.event_count += 1
        if event.get("device_id"):
            context.device_id = str(event["device_id"])
        context.location = str(
            event.get("location") or event.get("city") or context.location
        )
        context.facts["last_event_type"] = event_type
        context.facts["last_event"] = event

        self._mark_coverage(context, event, event_type)
        reasons = self._apply_context_rules(context, event_type, now)
        reasons.extend(self._apply_transaction_context(context, event, event_type, now))
        reasons.extend(self._apply_threats(context, threats, now))
        reasons.extend(self._apply_recovery(context, event_type))

        passport_id = previous.passport_id if previous else self._passport_id(context.session_id)
        created_time = previous.created_time if previous else context.created_at
        provisional = calculate_passport(context, passport_id, previous, created_time, now)
        context.lifecycle = self._lifecycle(context, event_type, provisional.overall_trust)
        passport = provisional.model_copy(update={"current_status": context.lifecycle})

        previous_overall = previous.overall_trust if previous else passport.overall_trust
        overall_delta = round(passport.overall_trust - previous_overall, 2)
        reason = self._reason(event_type, reasons, previous_overall, passport.overall_trust)
        deltas: list[TrustDelta] = []
        for component, state in passport.components.items():
            if abs(state.difference) < 0.01:
                continue
            deltas.append(
                TrustDelta(
                    delta_id=f"DELTA_{uuid4().hex[:12].upper()}",
                    session_id=context.session_id,
                    passport_id=passport.passport_id,
                    timestamp=now,
                    event_type=event_type,
                    component=component.value,
                    previous_trust=state.previous_value,
                    current_trust=state.value,
                    difference=state.difference,
                    reason="; ".join(state.reasons) or reason,
                    source="SESSION_INTELLIGENCE_ENGINE",
                    is_recovery=state.difference > 0,
                )
            )
        if abs(overall_delta) >= 0.01:
            deltas.append(
                TrustDelta(
                    delta_id=f"DELTA_{uuid4().hex[:12].upper()}",
                    session_id=context.session_id,
                    passport_id=passport.passport_id,
                    timestamp=now,
                    event_type=event_type,
                    component="overall",
                    previous_trust=previous_overall,
                    current_trust=passport.overall_trust,
                    difference=overall_delta,
                    reason=reason,
                    source="SESSION_INTELLIGENCE_ENGINE",
                    is_recovery=overall_delta > 0,
                )
            )

        snapshot = TrustSnapshot(
            snapshot_id=f"SNAP_{uuid4().hex[:12].upper()}",
            session_id=context.session_id,
            timestamp=now,
            event_type=event_type,
            previous_trust=previous_overall,
            current_trust=passport.overall_trust,
            delta=overall_delta,
            reason=reason,
            passport=passport,
        )
        self.repository.save_state(context, passport, snapshot, deltas)
        return TrustUpdate(
            session_id=context.session_id,
            event_type=event_type,
            passport=passport,
            deltas=deltas,
            snapshot=snapshot,
            processing_time_ms=round((time.perf_counter() - t0) * 1000.0, 3),
        )

    def recalculate(self, session_id: str) -> TrustUpdate:
        context = self.repository.get_context(session_id)
        if not context:
            raise KeyError(session_id)
        return self._reduce(
            context,
            {"session_id": session_id, "event_type": "TRUST_RECALCULATED"},
            [],
            self.repository.get_passport(session_id),
        )

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        context = self.repository.get_context(session_id)
        passport = self.repository.get_passport(session_id)
        if not context or not passport:
            return None
        return {
            "session": context.model_dump(mode="json"),
            "passport": passport.to_compatible_dict(),
            "deltas": [
                delta.model_dump(mode="json")
                for delta in self.repository.get_deltas(session_id, limit=100)
            ],
            "recovery_events": [
                delta.model_dump(mode="json")
                for delta in self.repository.get_recovery_events(session_id, limit=100)
            ],
        }

    def get_history(
        self,
        session_id: str,
        range_name: str = "last_hour",
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 1000,
    ) -> list[TrustSnapshot]:
        now = datetime.now(timezone.utc)
        if range_name == "last_minute":
            start = now - timedelta(minutes=1)
        elif range_name == "last_hour":
            start = now - timedelta(hours=1)
        elif range_name == "last_day":
            start = now - timedelta(days=1)
        elif range_name != "custom":
            raise ValueError("range must be last_minute, last_hour, last_day, or custom")
        return self.repository.get_snapshots(session_id, start, end, limit)


session_intelligence = SessionIntelligenceEngine()
