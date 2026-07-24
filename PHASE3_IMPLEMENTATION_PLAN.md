# Fusion Risk OS — Phase 3 Implementation Plan

## Purpose and constraints

Phase 3 adds continuous Session Intelligence and a live Trust Passport without replacing any existing engine or API. The implementation will:

- consume the existing SDK event and Cyber Threat Engine outputs;
- calculate nine independent trust components and an overall **trust posture**;
- persist session state, passports, deltas, history, and recovery events;
- publish compatible REST and WebSocket updates to Android and React;
- preserve current ML, risk, threat, decision, dashboard, and developer APIs;
- add no Composite Risk Score, Explainable AI, or Decision Quality Score.

“Overall Trust” is a session-security posture derived only from trust components. It is not a fraud risk score and will not select ALLOW/CHALLENGE/BLOCK decisions.

## Baseline validation

The plan is based on direct source and executable inspection at revision `13d51e0`.

- Android SDK events enter `POST /sdk/event` in `api/main.py`, are recorded by `sdk_engine`, and are independently evaluated by `cyber_threat_engine`.
- Threat objects are in-memory dictionaries indexed by session/device in `api/cyber_threat_engine.py`.
- Existing session endpoints use `SessionTrustPassportEngine` in `api/session_intelligence_engine.py`; that engine returns a large demo-oriented checkpoint model and is not the Phase 3 persistent event-driven passport.
- `GET /sdk/passport` currently reads static values from `sdk_engine`.
- `/ws/stream` replays scripted events and does not publish SDK trust changes.
- Android `FusionWebSocketManager` stores only the last raw WebSocket message; `Fusion` does not parse trust updates.
- React contains a session passport investigation component but no live session registry/dashboard.
- Runtime Neo4j and checked-in ML artifacts are absent. Phase 3 will preserve these boundaries and represent missing graph context as low confidence/unknown, not synthesize graph facts.
- The Android baseline build fails at `app/build.gradle.kts:43`; the repository lacks a Gradle wrapper and launcher resources. Phase 3 Android verification requires a minimal prerequisite build correction, without restructuring prior features.

## Current architecture

```text
Android banking UI
    -> embedded Fusion singleton
       -> REST /sdk/*
       -> WebSocket /ws/stream (fixed server replay)

FastAPI
    -> sdk_engine (sessions, devices, events, SDK policy decisions)
    -> cyber_threat_engine (event-label rules -> threat dictionaries)
    -> existing demo session_engine
    -> risk/trust/investigation engines

React
    -> REST polling and fixed dashboard data
    -> /ws/stream scripted operations replay

Persistence
    -> generic SQLite key/value store for selected evidence/workflows
    -> SDK sessions and threats remain in process memory
```

## Existing event flow

```text
Android action
  -> Fusion.reportEvent()
  -> POST /sdk/event
  -> sdk_engine.ingest_event()
  -> cyber_threat_engine.evaluate_event()
  -> HTTP event ACK
```

The threat result is currently discarded by the route. It does not update session trust or stream to clients.

## Current threat pipeline

```text
SDK event dictionary
  -> nine category evaluators
  -> threat object(s)
  -> in-memory threat store/indexes
  -> GET /threats polling
  -> React Threat Intelligence Dashboard
```

Phase 3 will consume returned threat objects. It will not duplicate or move any threat rules.

## Current session flow

```text
POST /sdk/session/start
  -> sdk_engine.start_session()
  -> static initial trust fields

GET /sdk/passport
  -> sdk_engine.get_trust_passport()
  -> static session values

Separate /session/* APIs
  -> legacy session_engine checkpoint analysis
```

The legacy `/session/*` APIs remain available. New Phase 3 APIs use explicit `/sessions`, `/trust-passport`, `/trust-history`, `/trust-components`, and `/trust/*` contracts.

## Target architecture

```text
SDK session/event/device/network input
  -> existing sdk_engine
  -> existing cyber_threat_engine
  -> SessionIntelligenceEngine
       -> SessionContext reducer
       -> independent TrustComponent calculators
       -> TrustPassport generator
       -> TrustDelta generator
       -> lifecycle reducer
       -> SQLite SessionTrustRepository
       -> TrustUpdateBroker
            -> REST reads
            -> /ws/stream live envelope
            -> Android Fusion StateFlows
            -> React Session Intelligence Dashboard
```

## Trust calculation design

Each component calculator consumes only relevant observed context and threat objects:

- Identity: login, biometric, OTP, credential, SIM, and identity-threat observations.
- Device: device registration, known/new device, root, emulator, integrity, and recovery observations.
- Runtime: debugger, Frida, hooking, overlay/accessibility, tampering, and clean-runtime observations.
- Behaviour: navigation/typing/touch/velocity/beneficiary behavior observations.
- Network: VPN, proxy, TOR, public Wi-Fi, MITM, and removal/trusted-network observations.
- Geo: location observations, impossible travel, GPS spoofing, and baseline-return observations.
- Threat: active threat severity/confidence, resolved/cleared threat observations, and threat count.
- Graph: graph threat objects or verified graph context; unknown graph state carries lower confidence without a fabricated penalty.
- Transaction: transaction amount/velocity/type observations, beneficiary changes, completion, and cancellation.

Calculators are pure, independently tested functions. Rules are declarative typed signal definitions. The engine accumulates bounded signal state, applies time decay, and clamps values to 0–100. Recovery events remove or counteract active negative signals. Confidence is derived from source coverage and freshness rather than a fixed display constant.

Overall Trust is a weighted mean of component values adjusted by component confidence. Weights belong to versioned trust policy configuration and sum to one. No fraud model output or decision verdict participates.

## Session lifecycle

Lifecycle transitions are event-driven:

```text
CREATED -> ACTIVE -> IDLE -> ACTIVE
                   -> SUSPICIOUS -> CHALLENGED -> ACTIVE
                                 -> BLOCKED
any non-closed state -> CLOSED
```

Transitions use observed event/threat state and trust posture. Lifecycle state remains separate from the existing transaction decision engine.

## Files to create

### Backend

- `api/session_intelligence/__init__.py`
- `api/session_intelligence/models.py`
- `api/session_intelligence/policy.py`
- `api/session_intelligence/components.py`
- `api/session_intelligence/repository.py`
- `api/session_intelligence/engine.py`
- `api/session_intelligence/broker.py`
- `api/test_session_intelligence_phase3.py`

### React

- `web/src/pages/SessionIntelligencePage.jsx`
- `web/src/components/session/SessionIntelligenceDashboard.jsx`
- `web/src/components/session/TrustPassportCard.jsx`
- `web/src/components/session/TrustComponentHeatmap.jsx`
- `web/src/components/session/TrustTimelineChart.jsx`

### Android

- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/trust/TrustPassportScreen.kt`

### Documentation

- `SESSION_INTELLIGENCE_ARCHITECTURE.md`
- `TRUST_PASSPORT_SPECIFICATION.md`
- `SESSION_API_REFERENCE.md`
- `TRUST_ENGINE_TEST_REPORT.md`

## Files to modify

### Backend

- `api/main.py` — additive routes; session/trust integration at SDK route boundaries; WebSocket broker integration.
- `api/sdk_engine.py` — preserve existing behavior while exposing session/device lookup facts required by the new layer if necessary.

### React

- `web/src/App.jsx` — add `/sessions` route.
- `web/src/components/layout/Sidebar.jsx` — add Session Intelligence navigation.
- `web/src/components/sdk/FATSDKDeveloperPortal.jsx` — expose live passport/session API status.

### Android

- `sdk/models/SDKModels.kt` — additive Trust Passport, component, delta, and history fields.
- `sdk/network/FusionApiService.kt` — additive history/components/session calls.
- `sdk/network/FusionWebSocketManager.kt` — typed trust-update stream and session subscription.
- `sdk/Fusion.kt` — merge REST bootstrap with WebSocket-driven passport/history StateFlows.
- `ui/components/LiveStatusCard.kt` — show live overall trust/trend/updated time and open detail.
- `ui/navigation/NavGraph.kt` — additive Trust Passport destination.
- `ui/screens/dashboard/DashboardScreen.kt` — navigation entry.
- `app/build.gradle.kts` — minimal baseline Kotlin DSL build correction required for verification.
- launcher resources only if the corrected build reaches and fails resource linking.

## API changes

All changes are additive:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/sessions` | Search/filter live and historical session registry |
| GET | `/sessions/{id}` | Full session context and latest passport |
| GET | `/trust-passport` | Current/default session passport, query by `session_id` |
| GET | `/trust-passport/{session}` | Passport by session |
| GET | `/trust-history/{session}` | Range-filtered snapshots (`last_minute`, `last_hour`, `last_day`, custom) |
| GET | `/trust-components/{session}` | Current components, previous values, differences, trends |
| POST | `/trust/recalculate` | Recalculate from persisted observed context; no synthetic event |
| GET | `/trust/live` | Latest live passport updates for bootstrap/diagnostics |

Compatibility:

- `/sdk/passport` returns the Phase 3 passport plus legacy keys (`composite_trust`, `device_trust`, etc.) so current Android parsing remains valid.
- Existing `/session/*`, `/sdk/*`, `/threats/*`, risk, ML, graph, report, and dashboard APIs remain.
- `/ws/stream` retains existing frame types and adds `trust_passport_update`, `trust_delta`, and `session_state_update`.

## Database changes

Additive SQLite tables:

- `session_registry`
  - session identity, user, lifecycle state, device/location, threat count, last activity, created/closed times, serialized observed context.
- `trust_passports`
  - one current passport per session, version, component values/confidence, trend, timestamps.
- `trust_snapshots`
  - append-only passport snapshots indexed by session and timestamp.
- `trust_deltas`
  - component/overall previous/current/delta/reason/event/source rows.
- `trust_recovery_events`
  - positive deltas and recovery reason/source.

Indexes cover session/time, user/state, and snapshot range reads. Schema creation is idempotent. No existing table is altered or dropped.

## React changes

The Session Intelligence Dashboard will provide:

- live/historical session registry with state, trust, threat count, activity, device, and location;
- search and state/trend/component filters;
- selected Trust Passport card;
- nine-component current/previous/difference/trend heatmap;
- trust timeline chart and delta feed;
- history-range controls;
- recovery-event feed;
- REST bootstrap plus WebSocket updates;
- explicit loading, empty, reconnecting, and error states.

No risk score, SHAP/XAI, or DQS widgets will be added.

## Android changes

- Subscribe `/ws/stream?session_id=<active session>` after session creation.
- Parse trust update envelopes into typed StateFlows.
- Bootstrap passport/history from REST once; subsequent changes arrive by WebSocket.
- Expose overall trust, component breakdown, trend, last update, history/deltas, connection state, and measured backend latency.
- Add a Trust Passport detail screen without replacing existing banking/simulator navigation.
- Simulator events continue through `Fusion.reportEvent`; backend updates propagate back through WebSocket. The Android UI will not locally mutate trust.

## Testing strategy

### Unit

- each component calculator: negative signals, clear/recovery signals, clamp, decay, unknown input;
- overall trust and confidence;
- lifecycle transition reducer;
- delta/reason generation;
- serialization and legacy compatibility.

### Repository

- idempotent schema initialization;
- current passport upsert;
- ordered history/range filtering;
- session registry search/filter;
- restart persistence;
- concurrent writes.

### Integration/API

- session start creates registry/passport;
- every SDK event creates snapshot/delta;
- threat output affects relevant components;
- recovery raises trust and creates recovery record;
- all required REST APIs;
- existing SDK and threat APIs remain compatible;
- multiple concurrent sessions remain isolated.

### WebSocket

- trust update envelope after SDK event;
- session filter;
- reconnect/bootstrap behavior;
- propagation timing.

### Android/React

- React production build and component behavior tests where feasible;
- Android compile, typed JSON parsing, StateFlow update, navigation;
- manual end-to-end simulator verification recorded in test report.

### Performance

- trust recalculation p50/p95/p99 across representative events, target p95 <50 ms;
- WebSocket route-to-client propagation target p95 <200 ms;
- 1,000 active-session creation/update benchmark with bounded memory and isolated state.

## Rollback strategy

1. Revert commits in reverse dependency order: Android, React, WebSocket/API integration, engine/persistence.
2. Existing APIs remain callable throughout because Phase 3 routes are additive and `/sdk/passport` keeps legacy fields.
3. Stop invoking `session_intelligence` from SDK routes to restore the prior event path.
4. Leave additive SQLite tables in place during rollback; they are inert and preserve evidence. A separate reviewed migration can archive/drop them later.
5. Restore the prior `/ws/stream` handler if broker integration causes a regression.
6. No ML artifact, model, graph training, threat rule, or risk-engine rollback is required.

## Dependency graph and implementation order

```text
models + policy
      |
      v
pure component calculators
      |
      v
repository <---- engine ----> broker
                     |
                     v
          SDK/threat route integration
                     |
          +----------+-----------+
          v                      v
        REST                 WebSocket
          |                      |
          +----------+-----------+
                     |
            +--------+--------+
            v                 v
          React             Android
```

Implementation order:

1. Typed models, versioned policy, pure component calculators.
2. Additive SQLite repository.
3. Session engine and lifecycle/delta/recovery behavior.
4. SDK/threat route integration.
5. REST APIs and compatible `/sdk/passport`.
6. WebSocket broker.
7. React dashboard.
8. Android live synchronization and UI.
9. Unit/integration/performance verification.
10. Final architecture/spec/API/test documentation.

## Internal plan validation

The plan is valid against the repository because:

- it consumes `cyber_threat_engine.evaluate_event()` results rather than duplicating detection;
- it adds route families and preserves all current paths;
- it does not import or modify ML models;
- it separates trust posture from risk decisions;
- it uses one trust calculation service for REST, SDK, WebSocket, Android, and React;
- it uses additive persistence and reversible integration points;
- it handles absent graph/ML evidence as unknown rather than fabricating it;
- it defines executable compatibility and performance tests before UI claims are accepted.

