# Fusion Risk OS — Session Intelligence Architecture

## Scope

Phase 3 adds continuous session-security posture evaluation. It does not implement a Composite Risk Score, Explainable AI, Decision Quality Score, or a new decision policy. Existing SDK, threat, decision, and ML paths remain in place.

## Deployed architecture

```text
Android banking app                          React enterprise dashboard
  Fusion SDK                                  Session Intelligence page
    REST /sdk/*                                  REST /sessions + /trust-*
    WS /ws/stream?session_id=...                 WS /ws/stream?session_id=...
             \                                  /
              +---------- FastAPI -------------+
                            |
             +--------------+----------------+
             |                               |
       Existing SDK Engine             Existing Cyber Threat Engine
       event ACK / decision            taxonomy / evidence / campaign
             |                               |
             +-------- threat objects -------+
                            |
                 SessionIntelligenceEngine
                   deterministic reducer
                            |
             +--------------+---------------+
             |                              |
       Trust Component Engine          Lifecycle Engine
       9 independent components        session state
             |                              |
             +--------- Trust Passport -----+
                            |
               delta + snapshot + recovery
                            |
                  SessionTrustRepository
                    additive SQLite tables
                            |
                   TrustUpdateBroker
                   WebSocket fan-out
```

There is no Phase 3 runtime dependency on Neo4j, GraphSAGE, LightGBM, or Isolation Forest. Existing model code is untouched. Graph trust remains independently represented with reduced confidence until graph evidence is supplied.

## Runtime event sequence

```text
1. Android sends POST /sdk/event.
2. sdk_engine ingests the event and creates the existing ACK.
3. cyber_threat_engine evaluates the same event once.
4. Returned threat objects are passed to SessionIntelligenceEngine.
5. The reducer loads persisted SessionContext.
6. Context facts, threat impacts, and verified recovery events update active signals.
7. Each trust component recalculates independently.
8. Trust Passport, component deltas, overall delta, timeline snapshot,
   lifecycle state, and recovery rows are committed atomically.
9. The unchanged SDK event ACK returns.
10. TrustUpdateBroker publishes the update to session-scoped WebSocket clients.
```

Threat detection is not duplicated. `SessionIntelligenceEngine` consumes the existing threat object's `severity`, `confidence`, `detection_source`, and `trust_impact`.

## Modules and responsibilities

| Module | Responsibility |
|---|---|
| `api/session_intelligence/models.py` | Strict session, component, passport, delta, snapshot, registry, and update contracts |
| `api/session_intelligence/policy.py` | Versioned weights, context signals, threat impact mapping, lifecycle thresholds, recovery mapping |
| `api/session_intelligence/components.py` | Independent component scoring, confidence, trend, and overall trust posture |
| `api/session_intelligence/engine.py` | Event reducer, lifecycle, delta, history, recovery, and recalculation orchestration |
| `api/session_intelligence/repository.py` | Thread-safe additive SQLite persistence |
| `api/session_intelligence/broker.py` | Bounded process-local WebSocket fan-out and recent update cache |
| `api/main.py` | Compatible SDK integration and Phase 3 REST/WebSocket surface |
| `web/src/components/session/` | Live registry, passport, heatmap, timeline, delta, recovery, and history UI |
| `fusion-reference-bank/.../sdk/Fusion.kt` | Android state flows, REST synchronization, and parsed live passport updates |
| `fusion-reference-bank/.../TrustPassportScreen.kt` | Android passport, components, trend, delta, history, latency, and stream UI |

## Session state model

Every session persists:

- identity: session ID and user ID;
- device: current device ID and supplied attestation facts;
- runtime, behavior, network, geo, transaction: observed SDK facts and active signals;
- threat: active threat objects summarized by source keys;
- graph: independent component and evidence coverage;
- history: event count, last event, timestamps, snapshots, and deltas;
- lifecycle: `CREATED`, `ACTIVE`, `IDLE`, `SUSPICIOUS`, `CHALLENGED`, `BLOCKED`, or `CLOSED`.

Explicit lifecycle events take precedence. Otherwise, trust below 70 is suspicious and trust below 30 is blocked. A closed session remains closed.

## Persistence

Phase 3 creates only additive SQLite objects:

| Table | Key | Content |
|---|---|---|
| `session_registry` | `session_id` | Active state, current trust, confidence, context, device, location, threat count |
| `trust_passports` | `session_id` | Latest versioned Trust Passport |
| `trust_snapshots` | `snapshot_id` | Event-by-event immutable timeline/history snapshot |
| `trust_deltas` | `delta_id` | Component and overall before/after change |
| `trust_recovery_events` | `delta_id` | Positive trust deltas caused by verified recovery |

SQLite WAL mode and a repository lock provide safe concurrent access inside one application process. This architecture supports the requested 1,000-session registry target. For multi-instance horizontal deployment, replace the repository and broker implementations through the existing service boundary with shared SQL and pub/sub infrastructure.

## Live delivery and reconnect

- A WebSocket with `session_id` receives a current passport bootstrap and future updates for only that session.
- Android reconnects with bounded backoff from 2 to 30 seconds and retains its session filter.
- React reconnects after 1.5 seconds and reloads REST history on session/range changes.
- Queue size is bounded at 100 updates per subscriber; the oldest item is discarded for a slow client.
- Existing unscoped WebSocket clients retain the legacy operations replay before entering live mode.

## Compatibility

- Existing endpoints are not removed or renamed.
- Existing SDK responses remain unchanged.
- `GET /sdk/passport` returns the Phase 3 passport when available, including legacy aliases required by the existing Android SDK.
- The existing decision result is returned unchanged; Phase 3 does not convert trust into a decision.
- Existing Cyber Threat Engine objects and dashboards remain available.

## Failure boundaries

- SQLite transaction failure prevents a partial passport/timeline write.
- A WebSocket delivery failure does not roll back persisted trust.
- WebSocket clients recover current state through bootstrap after reconnect.
- Unsupported legacy pipeline/model failures are reported as a `pipeline_error` frame rather than terminating the live stream.
- Offline Android events continue through the existing Room queue and update trust when the backend acknowledges them.

## Rollback

1. Revert the Phase 3 logical commits in reverse order.
2. Keep additive tables; older code ignores them.
3. If data removal is required, export the five Phase 3 tables, stop application writers, then drop only those tables.
4. Restore the previous `/sdk/passport` and `/ws/stream` handlers.
5. Rebuild React and Android from the prior revision.

