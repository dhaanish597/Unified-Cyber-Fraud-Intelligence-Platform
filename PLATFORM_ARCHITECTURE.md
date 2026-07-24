# Fusion Risk OS Platform Architecture

## Executable production slice

```text
Android banking UI
  -> Fusion SDK (encrypted auth/session state, request identity, queue, WSS)
  -> FastAPI security middleware
  -> AuthoritativePlatformPipeline
       1. normalize and acknowledge
       2. cyber threat rules
       3. Neo4j or explicit NetworkX fallback
       4. versioned model inference or ModelUnavailable policy
       5. authoritative decision adapter
  -> authenticated REST decision
  -> PlatformEventBroker
  -> authenticated WebSocket
       +-> Android session
       `-> React threat dashboard
```

FastAPI is one process. There is no Kafka, microservice, or hidden second
decision path. The Android transfer UI calls only `Fusion.requestDecision`;
the SDK owns every backend interaction.

## Component ownership

| Component | Responsibility | Authoritative state |
|---|---|---|
| Android UI | Banking presentation and user intent | Compose state only |
| Fusion SDK | Authentication, session, request IDs, retries, WSS | Encrypted preferences + Room queue |
| FastAPI middleware | JWT validation and role enforcement | Signed token claims |
| Banking auth | Password verification and refresh rotation | SQLite hashed records |
| Threat engine | Deterministic evidence-backed findings | In-process bounded indexes |
| Graph runtime | Observations and graph queries | Neo4j; NetworkX is marked fallback |
| Model runtime | Artifact validation and inference | `ml/models` metadata/artifacts |
| Decision adapter | Final action selection | Versioned deterministic policy |
| Event broker | Completed pipeline fan-out/reconnect history | Bounded process-local history |
| React dashboard | Live operational presentation | Backend responses only |

## Trust boundaries

- Public: liveness/readiness, client-token issue, banking login/refresh, and the
  signature-validated payment webhook.
- Authenticated: every other REST route.
- WebSocket: JWT required before accept. Customer JWTs may subscribe only to
  sessions owned by their subject.
- Release Android uses system certificate validation and rejects cleartext.
- Production dashboard startup requires HTTPS/WSS and a runtime token.

## Persistence and restart behavior

Bank users and hashed refresh tokens use the existing SQLite key/value store.
Offline SDK telemetry uses Room. Access tokens are short lived; refresh tokens
rotate on every use and are revoked on logout. SDK server-side sessions and the
WebSocket broker are process-local, so clients create a new SDK session after a
backend restart using their persistent banking refresh token.

## Explicit degraded states

- Missing/failed models: `ModelUnavailable`, null scores/probabilities, policy
  fallback.
- Missing/failed Neo4j: `NETWORKX_FALLBACK` or `FAILED`; never labelled Neo4j.
- Missing GraphSAGE: `UNAVAILABLE/GRAPHSAGE_ARTIFACT_NOT_CONFIGURED`.
- No calibrated threat probability: confidence is null.

