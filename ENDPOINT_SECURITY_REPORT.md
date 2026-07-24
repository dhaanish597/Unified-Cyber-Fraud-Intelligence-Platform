# Endpoint Security Report

Audit date: July 24, 2026

## Security Model

Primary enforcement file:

- `api/platform/security.py`

Public endpoints:

- `POST /auth/token`
- `GET /health/live`
- `GET /health/ready`
- `POST /gateway/webhook`

All other HTTP routes require bearer authentication.

WebSocket:

- `WS /ws/stream` requires an access token by header or query string

## Route Role Policies

| Route family | Allowed roles |
| --- | --- |
| `/sdk/` | `sdk`, `developer`, `admin` |
| `/synthetic/` | `developer`, `admin` |
| `/response/` | `operator`, `admin` |
| `/playbook` | `operator`, `admin` |
| `/incident/` | `operator`, `admin` |
| `/evidence/` | `analyst`, `operator`, `admin` |
| `/audit/` | `analyst`, `operator`, `admin` |
| `/trust/` | `analyst`, `operator`, `sdk`, `admin` |
| `/sessions` | `analyst`, `operator`, `sdk`, `admin` |
| `/threats` | `analyst`, `operator`, `developer`, `sdk`, `admin` |
| `/graph/` | `analyst`, `operator`, `developer`, `admin` |
| `/platform/` | `analyst`, `operator`, `developer`, `admin` |
| all other non-public routes | `analyst`, `operator`, `developer`, `admin` |

## Token Model

Token issuance:

- HS256 JWT
- issuer enforced
- audience enforced
- `iat`, `nbf`, `exp`, `jti` included
- role claims required

Production requirements:

- strong `JWT_SECRET`
- explicit `FUSION_AUTH_CLIENTS_JSON`
- non-wildcard `CORS_ORIGINS`

## Endpoint Inventory Summary

### Public

| Endpoint | Auth | Notes |
| --- | --- | --- |
| `POST /auth/token` | none | client credential bootstrap |
| `GET /health/live` | none | liveness |
| `GET /health/ready` | none | readiness |
| `POST /gateway/webhook` | HMAC signature | bypasses bearer auth by design, signature verified before processing |

### SDK and session transport

| Endpoint | Auth | Notes |
| --- | --- | --- |
| `POST /sdk/session/start` | bearer | SDK session bootstrap |
| `POST /sdk/device` | bearer | device posture ingest |
| `POST /sdk/network` | bearer | network posture ingest |
| `POST /sdk/event` | bearer | event ingest |
| `POST /sdk/request-decision` | bearer | authoritative pipeline decision request |
| `GET /sdk/passport` | bearer | actual passport only |
| `GET /sdk/events` | bearer | session event access |
| `GET /sdk/apps` | bearer | developer/app access |
| `GET /sdk/policies` | bearer | policy surface |
| `GET /sdk/error-codes` | bearer | SDK diagnostics |
| `GET /sdk/health` | bearer | SDK health |
| `GET /sessions` | bearer | live registry |
| `GET /sessions/{session_id}` | bearer | session details |
| `GET /trust-passport` | bearer | collection view |
| `GET /trust-passport/{session_id}` | bearer | single session passport |
| `GET /trust-components/{session_id}` | bearer | component breakdown |
| `GET /trust-history/{session_id}` | bearer | session trust history |
| `POST /trust/recalculate` | bearer | recalculation |
| `GET /trust/live` | bearer | current trust state |
| `WS /ws/stream` | bearer/query token | live stream |

### Threat, graph, platform, and operations

Representative protected endpoints:

- `/threats*`
- `/graph/analyze`
- `/platform/status`
- `/response/*`
- `/playbook*`
- `/incident/*`
- `/evidence/*`
- `/audit/*`
- `/synthetic/universe/*`

These are all behind bearer auth and role enforcement.

## Validation Performed

Verified by automated tests:

- unauthenticated non-public route returns `401`
- insufficient role returns `403`
- authenticated SDK pipeline remains usable
- invalid gateway signature returns `401`

Evidence:

- `api/test_platform_stabilization.py`

## Residual Risks

1. Dashboard production auth is still token-bootstrap based, not full interactive operator auth.
2. WebSocket browser fallback can use query-string tokens, which is practical but not the ideal long-term transport pattern.
3. Legacy route surface remains large, which increases future hardening effort.

## Conclusion

Endpoint protection is substantially better than the pre-stabilization state and is no longer the main blocker for production readiness. The remaining blockers are operational completeness: real ML artifacts, Neo4j-backed graph runtime, production Android release posture, and end-user authentication maturity.
