from __future__ import annotations

from datetime import datetime

from .models import ComponentName, SessionContext, TrustComponent, TrustPassport, TrustTrend, utc_now
from .policy import COMPONENT_WEIGHTS, TRUST_POLICY_VERSION


def clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def trend_for(current: float, previous: float, tolerance: float = 0.25) -> TrustTrend:
    if current > previous + tolerance:
        return TrustTrend.IMPROVING
    if current < previous - tolerance:
        return TrustTrend.DECLINING
    return TrustTrend.STABLE


def calculate_component(
    component: ComponentName,
    context: SessionContext,
    previous_value: float,
    now: datetime | None = None,
) -> TrustComponent:
    """Pure independent component calculation from observed active signals."""
    now = now or utc_now()
    active = context.signals.get(component, {})
    score = clamp(100.0 + sum(signal.impact for signal in active.values()))
    source_count = len(context.coverage.get(component, set()))
    signal_confidence = max((signal.confidence for signal in active.values()), default=0.0)
    confidence = clamp((0.2 + min(source_count, 3) * 0.2 + signal_confidence * 0.4) * 100.0)
    reasons = [signal.reason for signal in active.values()]

    return TrustComponent(
        name=component,
        value=round(score, 2),
        confidence=round(confidence, 2),
        previous_value=round(previous_value, 2),
        difference=round(score - previous_value, 2),
        trend=trend_for(score, previous_value),
        reasons=reasons,
        updated_at=now,
    )


def calculate_passport(
    context: SessionContext,
    passport_id: str,
    previous: TrustPassport | None,
    created_time: datetime,
    now: datetime | None = None,
) -> TrustPassport:
    now = now or utc_now()
    previous_values = {
        name: (
            previous.components[name].value
            if previous and name in previous.components
            else 100.0
        )
        for name in ComponentName
    }
    components = {
        name: calculate_component(name, context, previous_values[name], now)
        for name in ComponentName
    }

    overall = sum(
        components[name].value * COMPONENT_WEIGHTS[name] for name in ComponentName
    )
    confidence = sum(
        components[name].confidence * COMPONENT_WEIGHTS[name] for name in ComponentName
    )
    previous_overall = previous.overall_trust if previous else overall

    return TrustPassport(
        passport_id=passport_id,
        session_id=context.session_id,
        user_id=context.user_id,
        identity_trust=components[ComponentName.IDENTITY].value,
        device_trust=components[ComponentName.DEVICE].value,
        runtime_trust=components[ComponentName.RUNTIME].value,
        behaviour_trust=components[ComponentName.BEHAVIOUR].value,
        network_trust=components[ComponentName.NETWORK].value,
        geo_trust=components[ComponentName.GEO].value,
        threat_trust=components[ComponentName.THREAT].value,
        graph_trust=components[ComponentName.GRAPH].value,
        transaction_trust=components[ComponentName.TRANSACTION].value,
        overall_trust=round(overall, 2),
        confidence=round(confidence, 2),
        current_status=context.lifecycle,
        created_time=created_time,
        updated_time=now,
        version=TRUST_POLICY_VERSION,
        trust_trend=trend_for(overall, previous_overall),
        components=components,
    )
