# Session Intelligence API Reference

Base URL examples use `http://localhost:8001`. The current repository does not add a new authentication scheme; deployments must apply the platform gateway/authentication policy before public exposure.

## REST endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/sessions` | Search/filter the live and historical session registry |
| GET | `/sessions/{session_id}` | Full current session, passport, deltas, and recovery |
| GET | `/trust-passport` | Latest passport, or passport selected by query |
| GET | `/trust-passport/{session_id}` | Passport for one session |
| GET | `/trust-history/{session_id}` | Timeline/history range |
| GET | `/trust-components/{session_id}` | Components, delta history, and recovery events |
| POST | `/trust/recalculate` | Recalculate from persisted active signals |
| GET | `/trust/live` | Recent live update envelopes |
| WS | `/ws/stream?session_id=...` | Bootstrap and live session-scoped passport updates |

## GET `/sessions`

Query parameters:

| Name | Type | Default | Notes |
|---|---|---|---|
| `state` | lifecycle enum | — | Case-insensitive |
| `search` | string | — | Session, user, or device substring |
| `include_closed` | boolean | `true` | Ignored when an explicit state is supplied |
| `limit` | integer | `200` | Repository clamps to 1–1000 |

Response:

```json
{
  "sessions": [{
    "session_id": "SDK_SESS_123",
    "user_id": "user_42",
    "trust": 84.1,
    "confidence": 49.7,
    "threat_count": 2,
    "last_activity": "2026-07-24T12:00:00Z",
    "current_state": "ACTIVE",
    "current_device": "DEV_42",
    "location": "Mumbai",
    "created_at": "2026-07-24T11:30:00Z",
    "closed_at": null,
    "trust_trend": "DECLINING"
  }],
  "count": 1
}
```

Invalid state returns 422.

## GET `/sessions/{session_id}`

Returns:

```json
{
  "session": { "session_id": "SDK_SESS_123", "lifecycle": "ACTIVE" },
  "passport": { "session_id": "SDK_SESS_123", "overall_trust": 84.1 },
  "deltas": [],
  "recovery_events": []
}
```

Returns 404 when the session does not exist.

## GET `/trust-passport`

Optional query: `session_id`.

- With `session_id`, returns that passport.
- Without it, returns the most recently updated passport.
- Returns 404 when no matching passport exists.

## GET `/trust-passport/{session_id}`

Returns the Trust Passport contract defined in `TRUST_PASSPORT_SPECIFICATION.md`, plus SDK compatibility aliases. Returns 404 when absent.

## GET `/trust-history/{session_id}`

Query parameters:

| Name | Type | Default |
|---|---|---|
| `range` | `last_minute`, `last_hour`, `last_day`, `custom` | `last_hour` |
| `start` | ISO-8601 datetime | — |
| `end` | ISO-8601 datetime | — |
| `limit` | integer | `1000`, clamped to 1–5000 |

Response:

```json
{
  "session_id": "SDK_SESS_123",
  "range": "last_hour",
  "snapshots": [{
    "snapshot_id": "SNAP_123",
    "timestamp": "2026-07-24T12:00:00Z",
    "event_type": "VPN_ENABLED",
    "previous_trust": 100.0,
    "current_trust": 95.0,
    "delta": -5.0,
    "reason": "HIGH threat observed: Anonymizing Network / VPN Tunnel Active",
    "passport": {}
  }],
  "count": 1
}
```

## GET `/trust-components/{session_id}`

Returns current overall trust, confidence, trend, all nine component objects, persisted deltas, and recovery events. Returns 404 when absent.

## POST `/trust/recalculate`

Request:

```json
{ "session_id": "SDK_SESS_123" }
```

Recalculates from persisted active signals. It does not rerun threat detection, call ML models, or make a decision.

Response is a WebSocket-compatible update envelope. Returns 404 for an unknown session.

## GET `/trust/live`

Query parameters: optional `session_id`, `limit` (1–100).

Returns the process-local recent update cache:

```json
{ "updates": [], "count": 0 }
```

Use the WebSocket for continuous delivery.

## WebSocket `/ws/stream`

Session-aware clients connect to:

```text
ws://localhost:8001/ws/stream?session_id=SDK_SESS_123
```

The first frame is a current bootstrap when a passport exists:

```json
{
  "msg_type": "trust_passport_update",
  "session_id": "SDK_SESS_123",
  "event_type": "TRUST_BOOTSTRAP",
  "passport": {},
  "deltas": []
}
```

Subsequent frames include:

```json
{
  "msg_type": "trust_passport_update",
  "session_id": "SDK_SESS_123",
  "event_type": "OVERLAY_DETECTED",
  "passport": {},
  "deltas": [],
  "snapshot": {},
  "processing_time_ms": 3.4
}
```

Send text `ping` or JSON `{"type":"ping"}` to receive `{"msg_type":"pong"}`.

Unscoped clients retain the previous dashboard replay for compatibility and then receive live updates for all sessions.

Developer tooling can bypass the legacy replay and receive all session updates immediately:

```text
ws://localhost:8001/ws/stream?stream=trust
```

## SDK integration points

These existing endpoints now update session intelligence without changing their response contracts:

| Endpoint | Integration |
|---|---|
| `POST /sdk/session/start` | Creates registry/context/passport and publishes initial update |
| `POST /sdk/network` | Evaluates threat objects, updates network/session trust, publishes |
| `POST /sdk/event` | Evaluates threats once, reduces state, persists, publishes |
| `POST /sdk/request-decision` | Preserves decision response and updates the session from the event |
| `GET /sdk/passport` | Returns Phase 3 passport when present; legacy fallback otherwise |
