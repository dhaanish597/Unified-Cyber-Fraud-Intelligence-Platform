# Fusion Risk OS Production Integration Plan

## Scope and completion rule

This plan completes and validates the existing Android application, Fusion SDK,
FastAPI platform, threat engine, graph/model runtimes, and React dashboard as one
executable platform. It does not implement or extend Session Intelligence, Trust
Passport, Composite Risk, Explainable AI, Decision Quality Score, Response
Orchestrator, Investigation Workbench, or Executive Dashboard.

The production path is:

```text
Android banking action
  -> Fusion SDK authenticated request
  -> FastAPI normalization
  -> cyber threat evaluation
  -> Neo4j graph observation and queries
  -> available ML inference (or explicit ModelUnavailable)
  -> authoritative decision policy
  -> authenticated REST response
  -> authenticated WebSocket event
  -> Android and dashboard consumers
```

An external dependency is never represented as executed unless it really ran.
Neo4j, trained model, GraphSAGE, signing, HTTPS, and WSS checks therefore have
separate configured and unconfigured validation outcomes.

## Architecture

### Android and SDK

- The banking UI owns presentation only.
- `Fusion` is the sole API gateway and owns authentication, token refresh,
  session restoration, request metadata, offline delivery, retry, and WebSocket
  reconnect.
- A single decision request represents a transfer. The UI does not send a
  duplicate telemetry event or make local risk decisions.
- Encrypted storage contains refresh/access-token metadata, user/session IDs,
  and no client secret in release builds.

### Backend

- FastAPI remains a single process.
- Security middleware authenticates every non-public REST route. Route policies
  enforce SDK, dashboard, operator, analyst, developer, and admin roles.
- Banking authentication issues short-lived JWT access tokens and rotating,
  revocable refresh tokens. SDK machine credentials remain development-only.
- The authoritative pipeline produces one typed result containing request,
  correlation, session, acknowledgement, graph, model, decision, and timing
  evidence.
- One broadcast broker distributes completed pipeline results. WebSocket
  clients can filter by session and receive only authorized live events.

### Graph and ML

- Neo4j is selected only when credentials exist and connectivity succeeds.
  Queries persist observations and detect shared devices, shared beneficiaries,
  mule candidates, circular transfers, and fraud-ring candidates.
- NetworkX remains a documented development fallback and is never reported as
  Neo4j execution.
- LightGBM/XGBoost and Isolation Forest load versioned artifacts and report
  artifact hashes. Missing/failed artifacts return `ModelUnavailable` with null
  scores and probabilities.
- GraphSAGE executes only with a compatible versioned artifact; otherwise its
  status is explicitly unavailable. No graph/model confidence is fabricated.

### Dashboard

- Authentication completes before rendering or API/WebSocket activity.
- A shared authenticated client handles token refresh and errors.
- The threat view consumes live pipeline broadcasts and derives latency and
  confidence from observed responses only.
- Production API and WSS origins are build-time configuration requirements.

## Current gaps

1. Gradle wrapper scripts/JAR/properties are absent and no system Gradle exists.
2. Android login accepts any nonblank username and starts a security session;
   it has no banking login, logout endpoint, refresh, expiry, profile, or
   reliable persistent-session recovery.
3. Android transfer sends both an event and a decision request, duplicating the
   authoritative pipeline.
4. SDK requests do not consistently carry request/correlation IDs, retry keys,
   backend ACK metadata, or token-expiry handling.
5. Release Android and dashboard URLs are placeholders. Release signing cannot
   be validated without external signing properties.
6. The backend has JWT access tokens but no refresh-token lifecycle or banking
   identity endpoints.
7. WebSocket authentication exists, but the live stream is coupled to Phase 3
   trust updates rather than completed authoritative pipeline results.
8. Model artifacts and GraphSAGE artifacts are absent. Runtime fallback is
   honest but uses `FALLBACK` rather than the required explicit
   `ModelUnavailable` contract.
9. Neo4j is not configured locally. Current Neo4j queries omit fraud-ring
   detection and health/query evidence.
10. The dashboard has hard-coded latency/confidence values and a large number of
    direct fetch calls. Some requests can run before authentication completes.
11. The React production build succeeds but emits a 1.03 MB chunk warning.
12. Backend compilation succeeds; tests are 18/19. The sole failure belongs to
    prohibited Phase 3 Session Intelligence and is recorded, not expanded.
13. There is no executable platform E2E/failure harness, endpoint inventory,
    production configuration validator, or consolidated documentation.

## Dependency graph

```text
configuration validation
  +-> REST/JWT/refresh security
  |    +-> banking auth/profile
  |    +-> SDK authenticated client
  |    +-> dashboard authenticated client
  |    `-> WebSocket authorization
  +-> graph runtime ----> pipeline
  +-> model runtime ----> pipeline
  +-> threat engine ----> pipeline
  `-> pipeline broker --> REST response
                      +-> WebSocket
                      +-> Android decision state
                      `-> dashboard live state

Gradle wrapper -> Android compile -> APK/AAB -> package measurements
Backend tests + React build + integration harness -> final audit
```

## Execution order

1. Add contract tests for auth lifecycle, pipeline metadata, model-unavailable
   behavior, WebSocket authorization/broadcast, graph queries, and failures.
2. Add secure banking authentication, refresh rotation, revocation, profile,
   logout, request identity, and sanitized structured errors.
3. Decouple pipeline WebSocket broadcasts from prohibited Phase 3 trust state.
4. Complete pipeline request/correlation/ACK/timing contracts and failure
   semantics.
5. Complete Neo4j repository queries/health evidence and versioned model/runtime
   status.
6. Complete Android wrapper/build configuration, SDK auth/session/offline
   recovery, and banking UI integration; eliminate duplicate transfer calls.
7. Centralize dashboard auth/API/WebSocket consumption and remove synthetic
   metrics from production views.
8. Add endpoint inventory and automated E2E/failure/security/performance checks.
9. Run compile, tests, Android debug/release/AAB, React build, integration tests,
   security validation, and performance measurements.
10. Generate runtime/reference/deployment documentation and a fresh final audit.

## Files to modify

- `.env.example`, `.gitignore`, `requirements.txt`, `pytest.ini`, `README.md`
- `api/main.py`
- `api/platform/config.py`, `security.py`, `pipeline.py`, `model_runtime.py`,
  `graph_runtime.py`, `observability.py`
- `api/sdk_engine.py` and focused backend tests
- `fusion-reference-bank/build.gradle.kts`, `app/build.gradle.kts`,
  `gradle.properties`, `README.md`
- Android manifest/network security, SDK models/API/client/queue/storage/socket,
  application initialization, login/transfer/profile/navigation view models and
  screens
- `web/src/main.jsx`, `platformAuth.js`, `App.jsx`, threat/runtime consumers,
  and `vite.config.js`

## Files to create

- Gradle wrapper scripts and `gradle/wrapper/*`
- Backend auth/pipeline broadcast modules and production-validation helpers
- Focused integration, failure, security, and performance tests
- `scripts/validate_production.ps1` and endpoint-inventory generator
- `PLATFORM_ARCHITECTURE.md`
- `PIPELINE_REFERENCE.md`
- `API_REFERENCE.md`
- `SDK_REFERENCE.md`
- `ML_RUNTIME.md`
- `GRAPH_RUNTIME.md`
- `SECURITY_REFERENCE.md`
- `DEPLOYMENT_GUIDE.md`
- `FINAL_PRODUCTION_READINESS_REPORT.md`

## Testing plan

### Static and build

- Python `compileall`
- FastAPI import/OpenAPI generation
- React `vite build`
- Gradle wrapper verification, lint, unit tests, debug APK, release APK, and
  release AAB

### Contract and security

- Public/private route inventory and JWT role matrix
- Invalid, expired, malformed, and wrong-role access tokens
- Refresh rotation, replay rejection, expiry, and logout revocation
- WebSocket missing/expired/wrong-role tokens
- Secret/config validation and response/log redaction

### End to end

- Banking login -> SDK session -> transfer -> threat -> graph -> ML or explicit
  unavailable -> decision -> REST ACK -> WebSocket update.
- Assert request ID, correlation ID, session ID, pipeline ID, timings, backend
  ACK, decision source, graph backend, and model status at every boundary.

### Failure and recovery

- Network loss/offline queue, retry idempotency, expired access token, refresh,
  reconnect, multiple sessions, backend restart, Neo4j unavailable, missing
  model, and malformed input.
- No crash, no fabricated score, no duplicated pipeline execution.

### Performance

- Measure backend total, threat, graph, model, and WebSocket delivery latency
  distributions from real timestamps.
- Record cold import/start, process memory/CPU, reconnect/queue recovery, and
  generated APK/AAB sizes where the local toolchain permits execution.

## Rollback plan

- Changes are grouped by backend contract, Android SDK, dashboard client, tests,
  and documentation so each group can be reverted independently.
- Existing database files and user-generated audit/log artifacts are not
  modified or deleted.
- New security configuration is environment-driven; development credentials
  remain confined to debug/development modes.
- The NetworkX and policy fallback paths remain available for development, with
  explicit degraded/unavailable status, if Neo4j or models fail.
- If a contract migration cannot be completed atomically, compatibility fields
  remain nullable for one release while all new clients use the authoritative
  fields.

## Risk assessment

| Risk | Impact | Control |
|---|---:|---|
| No Neo4j credentials/service | High | Run repository contract tests and report runtime gate as unvalidated; never claim Neo4j execution |
| No trained model/GraphSAGE artifacts | High | Explicit `ModelUnavailable`/GraphSAGE unavailable status with null scores |
| No Android SDK/Gradle cache/network | High | Add reproducible wrapper and distinguish source failure from toolchain unavailability |
| No release keystore | Medium | Validate unsigned/minified release and AAB; make signed artifact a documented external credential gate |
| Broad legacy/Phase 3 surface | High | Do not extend it; route production completion through isolated platform modules |
| Auth contract migration | High | Add lifecycle and role tests before client migration |
| In-memory refresh/session state | High | Persist hashed tokens and sessions in SQLite for restart/revocation tests |
| React bundle size | Medium | Route-level lazy loading and explicit chunking |
| Dirty worktree/database WAL | Medium | Preserve all pre-existing files and avoid database-destructive operations |

## Internal validation

The plan is internally consistent with the repository constraints:

- It preserves the required single FastAPI process and existing NetworkX
  development fallback.
- It introduces no prohibited roadmap capability.
- It makes production claims conditional on executable evidence.
- Security/auth changes precede client integration.
- Pipeline contract changes precede E2E validation.
- External credentials are treated as deployment gates, never mocked.
- Rollback boundaries match the implementation groups.

Implementation may begin after this validation.
