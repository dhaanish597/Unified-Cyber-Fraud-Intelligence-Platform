# Enterprise Trust Passport Specification

## Contract

The Trust Passport is the authoritative, versioned security posture of one banking session. It changes after every accepted SDK event, threat object, recovery event, or explicit recalculation.

Overall Trust is a trust posture from 0–100. It is not a fraud probability, risk score, or transaction decision.

## Passport fields

| Field | Type | Rule |
|---|---|---|
| `passport_id` | string | Stable for the session |
| `session_id` | string | Required session identifier |
| `user_id` | string | Session owner |
| `identity_trust` | float | 0–100 |
| `device_trust` | float | 0–100 |
| `runtime_trust` | float | 0–100 |
| `behaviour_trust` | float | 0–100 |
| `network_trust` | float | 0–100 |
| `geo_trust` | float | 0–100 |
| `threat_trust` | float | 0–100 |
| `graph_trust` | float | 0–100 |
| `transaction_trust` | float | 0–100 |
| `overall_trust` | float | Weighted component trust posture, 0–100 |
| `confidence` | float | Weighted evidence confidence, 0–100 |
| `current_status` | enum | Session lifecycle state |
| `created_time` | UTC datetime | Passport creation |
| `updated_time` | UTC datetime | Most recent reduction |
| `version` | string | `trust-v1.0.0` |
| `trust_trend` | enum | `IMPROVING`, `STABLE`, or `DECLINING` |
| `components` | object | Full independent component states |

Compatibility aliases are emitted as `composite_trust`, `session_trust`, `policy_version`, and `sync_timestamp`. They mirror Trust Passport fields for older SDK deserialization; no Composite Risk Score is calculated.

## Component contract

Each `components.<name>` object contains:

```json
{
  "name": "network",
  "value": 75.0,
  "confidence": 73.0,
  "previous_value": 100.0,
  "difference": -25.0,
  "trend": "DECLINING",
  "reasons": ["Anonymizing Network / VPN Tunnel Active affected network trust"],
  "updated_at": "2026-07-24T12:00:00Z"
}
```

Components start at 100 with low confidence, not fabricated assurance. Score and confidence are separate:

- score reflects currently active positive/negative session signals;
- confidence reflects source coverage and signal confidence;
- absence of graph/behavior/geo evidence keeps the component score neutral while confidence stays low.

## Versioned calculation

Policy: `trust-v1.0.0`.

| Component | Weight |
|---|---:|
| Identity | 0.14 |
| Device | 0.13 |
| Runtime | 0.13 |
| Behaviour | 0.10 |
| Network | 0.10 |
| Geo | 0.08 |
| Threat | 0.14 |
| Graph | 0.08 |
| Transaction | 0.10 |

Weights sum to 1.0.

```text
component trust = clamp(100 + sum(active signal impacts), 0, 100)
overall trust   = round(sum(component trust × component weight), 2)
confidence      = round(sum(component confidence × component weight), 2)
```

This calculation does not invoke or change LightGBM, Isolation Forest, GraphSAGE, the Trust Engine, or the Decision Engine.

## Signal sources

1. SDK context events update non-threat session posture, for example beneficiary changes or trusted network restoration.
2. Cyber Threat Engine objects update threat trust and the components named by `trust_impact`.
3. Transaction context derives bounded exposure from observed amount and event type.
4. Recovery events remove a matching active signal only when the SDK reports a verified recovery condition.

Signals use stable keys. Repeating the same active threat replaces its current evidence rather than accumulating unlimited deductions.

## Delta contract

Every changed component and changed overall trust creates a delta:

| Field | Meaning |
|---|---|
| `delta_id` | Immutable identifier |
| `session_id`, `passport_id` | Ownership |
| `timestamp` | UTC observation time |
| `event_type` | Triggering event |
| `component` | Component name or `overall` |
| `previous_trust` | Value before the event |
| `current_trust` | Value after the event |
| `difference` | Current minus previous |
| `reason` | Evidence-linked change reason |
| `source` | `SESSION_INTELLIGENCE_ENGINE` |
| `is_recovery` | True when difference is positive |

An event that changes context but not score still creates a timeline snapshot, preserving a complete event sequence.

## Timeline and history

Each snapshot contains timestamp, event, previous overall trust, current overall trust, delta, reason, and a complete passport copy. Supported ranges are:

- `last_minute`;
- `last_hour`;
- `last_day`;
- `custom`, using optional UTC `start` and `end`.

## Recovery

Recovery is event-driven and never time-based fabrication. Examples:

| Recovery event | Cleared evidence |
|---|---|
| `VPN_DISABLED` | VPN network and threat signals |
| `TRUSTED_NETWORK_RESTORED` | Public Wi-Fi signal |
| `BIOMETRIC_VERIFIED` | OTP/password-reset identity signals |
| `KNOWN_DEVICE_VERIFIED` | Matching device/identity threats |
| `RUNTIME_INTEGRITY_RESTORED` | Matching runtime and threat signals |
| `THREAT_CLEARED` | Verified active threat set and its component effects |

Positive deltas are persisted in both `trust_deltas` and `trust_recovery_events`.

## Invariants

- Scores and confidence are always bounded to 0–100.
- One session owns one latest passport and any number of immutable snapshots.
- Passport ID remains stable through the session.
- Component calculations do not depend on another component's calculated score.
- Every persisted passport and snapshot uses the same policy version.
- Closed sessions cannot transition back to an active state.
- The Trust Passport never returns a transaction decision.

