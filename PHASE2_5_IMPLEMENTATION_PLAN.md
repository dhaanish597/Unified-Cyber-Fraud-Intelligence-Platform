# Fusion Risk OS — Phase 2.5 Implementation Plan

## Purpose and scope boundary

Phase 2.5 stabilizes the current repository as one connected platform. It does not add Session Intelligence, Trust Passport, Composite Risk, Explainable AI, or Decision Quality Score features. Phase 3 code already present at baseline revision `7f80343` is treated as protected compatibility surface: shared authentication, transport, persistence, and event-pipeline changes may integrate with it, but its product scope will not be expanded.

The implementation remains one FastAPI process as required by `CLAUDE.md`. Neo4j is preferred when configured; a real in-memory NetworkX repository is the documented, explicit fallback. Missing ML artifacts must result in an honest fallback result, never simulated inference.

## Baseline evidence

The plan is based on direct source inspection and baseline execution at revision `7f80343`.

- FastAPI imports successfully and exposes 88 routes.
- React production build succeeds.
- Android debug APK exists from the previous phase.
- Baseline Android release APK/AAB are not produced; release is configured with the debug signing key.
- Baseline backend tests produced 12 passes and one performance failure: a 30-sample trust recalculation p95 reached 61.64 ms against the 50 ms target.
- `ml/models/` and `data/processed/entity_graph_features.json` are absent.
- No Neo4j environment configuration is present and no Python runtime code imports `GraphDatabase`.
- `JWT_SECRET` is present in the current environment, but no endpoint consumes or validates it.
- No SDK API credential or Android production signing configuration is present.
- `LEDGER_SIGNING_KEY` is absent; the ledger generates an ephemeral key at import.

## Current architecture

```text
Android UI
  -> Fusion singleton
     -> Retrofit /sdk/* (HTTP)
     -> OkHttp /ws/stream (WS)
     -> local Room retry queue

React
  -> direct unauthenticated REST calls
  -> direct unauthenticated WebSockets

FastAPI main.py
  -> multiple direct endpoint handlers
  -> sdk_engine rule/decision path
  -> cyber_threat_engine rule path
  -> Phase 3 session_intelligence path
  -> pipeline_engine transaction path
       -> risk_engine
          -> LightGBM/XGBoost loader
          -> Isolation Forest loader
          -> static JSON graph lookup
       -> trust_engine demo metrics
  -> independent investigation/response/quantum/demo engines

Persistence
  -> SQLite key/value store
  -> Phase 3 SQLite trust tables
  -> most SDK/threat state held in process memory

Graph
  -> offline NetworkX build script
  -> offline GraphSAGE training script
  -> no runtime Neo4j client/repository
```

## Detected problems

### Platform integration

1. `api/main.py` imports `execute_pipeline` twice and calls engines independently from many routes.
2. `/sdk/event` and `/sdk/request-decision` have parallel orchestration rather than one authoritative pipeline service.
3. SDK decisions are local rules in `sdk_engine.request_decision`; transaction decisions use a separate `risk_engine`.
4. The WebSocket unscoped path executes a scripted demo pipeline rather than publishing only authoritative pipeline results.
5. Gateway ingestion calls `execute_pipeline` directly and bypasses shared authentication/session validation.

### ML

1. Runtime model artifacts are absent.
2. `risk_engine.evaluate()` raises `FileNotFoundError`; there is no typed availability response.
3. `pipeline_engine` labels stages as LightGBM, Isolation Forest, GraphSAGE, Neo4j, and SHAP even when those systems did not execute.
4. Model versions are hardcoded in provenance instead of loaded from metadata.
5. Docker copies `ml/models/`, which fails or produces a nonfunctional image when artifacts are not provisioned.

### Graph

1. No runtime Neo4j repository exists.
2. The current graph stage reads a static JSON lookup and supplies default centrality values.
3. Shared-device, shared-beneficiary, circular-transfer, mule, and fraud-ring queries are not implemented against a live repository.
4. React substitutes a fabricated graph when API graph data is absent.
5. Graph threat rules accept event labels and emit invented PageRank/betweenness evidence.

### Threat integrity

1. Threat store is seeded with demo threats at process startup.
2. Confidence is fixed by rule and evidence strings contain measurements not present in the event.
3. Detection latency adds random milliseconds.
4. Campaign latency and confidence are hardcoded.
5. Graph threats claim GraphSAGE/centrality evidence without querying graph intelligence.

### Trust and decision integrity

1. `/evaluate/transaction` has a demo transaction override with fixed score, SHAP values, and counterfactual.
2. `pipeline_engine` fills missing identities, accounts, IPs, cyber flags, graph clusters, SHAP impacts, and stage evidence with suspicious demo values.
3. Legacy `session_intelligence_engine`, `trust_engine`, `digital_twin_engine`, `sdk_engine`, response, and quantum modules contain synthetic scores/confidence.
4. `sdk_engine.start_session` exposes hardcoded trust values.
5. `sdk_engine.request_decision` accepts caller-supplied trust and returns hardcoded confidence.

### Authentication and authorization

1. Every REST endpoint is anonymous except gateway HMAC.
2. WebSockets are anonymous.
3. No JWT issuer, verifier, role policy, SDK API key policy, or session ownership validation exists.
4. CORS allows every origin while credentials are enabled.
5. React and Android do not attach authorization.
6. Login starts a session without authenticating credentials.

### Android and transport

1. Production defaults use cleartext HTTP/WS.
2. Network security trusts user-installed certificates and permits cleartext globally.
3. Release is signed with the debug key.
4. `SecureStorage` silently falls back to plaintext preferences.
5. Device attestation reports placeholder Frida/overlay results and fixed screen-lock state.
6. Room queue retry has no attempt count, exponential backoff, dead-letter state, or uniqueness/idempotency key.
7. The project has no checked-in Gradle wrapper.

### Operations and code quality

1. No structured logging, request correlation, centralized error envelope, readiness check, or dependency status endpoint.
2. Metrics endpoints can fail with missing models and some SDK health values are random.
3. SQLite locations are inconsistent and `.gitignore` is malformed with UTF-16/NUL content.
4. Deployment manifests contain no required secret/dependency health validation.
5. Tests do not cover authentication, graph fallback, model fallback, authoritative routing, or secure WebSockets.

## Target architecture

```text
Android / React / Gateway
       |
       | HTTPS/WSS + JWT or SDK credential
       v
FastAPI security middleware
       |
       v
AuthoritativePlatformPipeline
  1. validate identity/session
  2. normalize event/transaction
  3. persist SDK event and idempotency state
  4. CyberThreatEngine (evidence-derived rules only)
  5. GraphIntelligenceRepository
       -> Neo4j when healthy
       -> explicit NetworkX fallback when unavailable
  6. ModelRuntime
       -> loaded versioned artifacts
       -> explicit deterministic policy fallback when unavailable
  7. existing Decision Engine policy evaluation
  8. persist outcome/audit metadata
  9. publish one result envelope
       -> REST response
       -> WebSocket subscribers
       -> React
       -> Android SDK
```

Phase 3 session state may consume the authoritative threat result after step 4, but Phase 2.5 will not add new trust behavior.

## Dependency graph

```text
security configuration
  -> REST middleware
  -> WebSocket authentication
  -> React auth client
  -> Android auth interceptor

event normalizer
  -> threat engine
  -> graph repository
  -> model runtime
  -> decision adapter
  -> pipeline result
  -> audit persistence
  -> WebSocket broker

graph repository interface
  -> Neo4j implementation
  -> NetworkX implementation
  -> graph tests

model runtime interface
  -> artifact manifest/loader
  -> explicit fallback
  -> health/readiness
  -> pipeline evidence

Android build configuration
  -> secure release URLs
  -> release signing
  -> certificate pinning
  -> debug-only localhost cleartext
```

## Broken integrations and resolution

| Broken integration | Resolution |
|---|---|
| SDK event → separate threat/session calls | One platform pipeline method used by all SDK event routes |
| SDK decision → local caller-trust rules | Decision adapter consumes authoritative pipeline context and server-owned session |
| Transaction API → hard failure without models | Typed `MODEL` or `POLICY_FALLBACK` inference result |
| Pipeline → static graph defaults | Repository query result with backend/status/evidence |
| Threat engine → invented evidence | Evidence builders use only fields present in normalized telemetry |
| Graph threats → event-label claim | Graph findings generated only from repository query evidence |
| REST/WS → anonymous access | Central JWT/API-key policy and session ownership |
| Android/React → no credentials | Shared token acquisition/storage and request/WS authorization |
| WebSocket → demo replay | Authoritative event envelopes; demo replay isolated to explicit development mode |
| Health → random values | Measured counters and dependency readiness |

## Implementation strategy

### 1. Platform contracts

Create typed normalized event, graph result, inference result, decision result, pipeline result, dependency status, and error contracts. Every optional subsystem records:

- `status`: `EXECUTED`, `FALLBACK`, `UNAVAILABLE`, or `FAILED`;
- implementation/model/backend name;
- version when known;
- measured latency;
- evidence actually used;
- error code without secret leakage.

### 2. Authentication

Add a standard-library HS256 JWT verifier/issuer with short-lived tokens, issuer/audience validation, roles, and constant-time signature verification. Add:

- explicit `/auth/token` development/enterprise bootstrap driven by configured credentials;
- JWT for dashboard/developer APIs;
- SDK client credential exchange followed by a scoped SDK token;
- role policy: `analyst`, `operator`, `developer`, `sdk`, `admin`;
- session ownership checks for SDK/user-scoped routes;
- WebSocket token validation before acceptance;
- gateway webhook retains HMAC and is excluded from JWT only for the signed webhook path;
- `/health/live` remains public; `/health/ready` exposes no secrets.

Production startup fails if secure mode is enabled without strong secrets. Tests use isolated secrets.

### 3. Model runtime

Wrap existing `ml.predict` in an availability-aware service. Validate metadata and artifact checksums/version. When artifacts are absent:

- do not return model probabilities, SHAP, or model confidence;
- use a named `POLICY_FALLBACK` based only on observable deterministic rules;
- identify fallback reasons and reduced capability;
- expose readiness as degraded, not healthy.

No model will be trained or downloaded in this phase.

### 4. Graph runtime

Create a `GraphIntelligenceRepository` interface with:

- Neo4j implementation using parameterized Cypher and connectivity verification;
- NetworkX fallback populated only from observed events/transactions;
- upsert transaction/device/beneficiary relations;
- query methods for shared devices, shared beneficiaries, circular transfers, mule indicators, and fraud-ring communities;
- explicit backend and evidence fields.

If Neo4j credentials are absent, NetworkX executes real queries and reports `backend=NETWORKX_FALLBACK`; it never labels results as Neo4j.

### 5. Threat integrity

Remove production threat seeding and random latency. Rule confidence becomes evidence coverage:

```text
confidence = verified required indicators / total required indicators
```

Event labels alone may select a rule but cannot fabricate low-level evidence. Each threat carries observed evidence, missing evidence, confidence basis, and measured latency. Campaign confidence derives from correlated distinct findings and their evidence coverage.

### 6. Authoritative pipeline

Introduce one application service called by SDK event, SDK decision, transaction evaluation, gateway, and explicit threat evaluation routes. Existing endpoints remain but become adapters. The service owns normalization, dependency calls, decision, persistence, and publication. Duplicate demo bypasses are removed or restricted to explicit development scenario endpoints.

### 7. Trust placeholders

- Remove hardcoded trust from SDK session responses.
- Where Phase 3 has a real persisted passport, expose it.
- Otherwise return `null`/`UNAVAILABLE` with evidence status, not a plausible number.
- Disable or clearly mark legacy synthetic trust endpoints as development-only; do not build new trust logic.
- Remove fixed decision confidence and distinguish policy certainty from statistical confidence.

### 8. Android

- Add checked-in Gradle wrapper.
- Build-type URLs: localhost HTTP/WS only in debug; HTTPS/WSS required in release.
- Release signing loaded from environment/local untracked properties; release build must fail safely without credentials rather than use debug signing.
- Add JWT/API-token interceptor and authenticated WebSocket query/header.
- Remove plaintext preference fallback.
- Configure certificate pinning through production configuration.
- Add queue retry metadata, exponential scheduling policy, idempotency key, and safe logs.
- Validate debug APK, signed release APK, and signed release AAB. Because signing credentials are absent at baseline, create an ephemeral test keystore only for build verification outside Git; production packaging remains credential-gated.

### 9. React

No redesign. Add one centralized authenticated API/WebSocket client and migrate direct calls. Display dependency/fallback status already returned by APIs. Remove fabricated graph default data; render an explicit unavailable/empty state.

### 10. Observability and errors

Add request ID middleware, structured JSON logging, measured counters, consistent error envelopes, dependency health, and startup validation. Never log request bodies, passwords, tokens, API keys, or sensitive banking fields.

## Execution order

1. Commit this validated plan.
2. Add platform contracts, configuration, security, and tests.
3. Add model runtime with explicit fallback and health tests.
4. Add graph repository, Neo4j/NetworkX implementations, queries, and tests.
5. Refactor threat confidence/evidence and remove production seeds.
6. Add authoritative pipeline and migrate backend adapters.
7. Harden WebSocket publication/authentication.
8. Migrate React to centralized authenticated transport without redesign.
9. Harden Android SDK/configuration/storage/queue/signing and add wrapper/tests.
10. Remove/disable remaining fabricated production paths and dead duplicates.
11. Run performance, security, startup, integration, and build validation.
12. Produce implementation report and a fresh audit.

## Risk analysis

| Risk | Impact | Mitigation |
|---|---|---|
| Broad authentication breaks existing clients | High | Compatibility test matrix; migrate React/Android in same change; configurable development bootstrap |
| Missing model artifacts block transaction decisions | High | Explicit policy fallback; degraded readiness; never claim ML |
| No Neo4j service available for validation | High | Real NetworkX fallback plus Neo4j unit tests with fake driver; readiness reports fallback |
| Refactoring route orchestration changes responses | High | Preserve endpoint schemas where honest; contract tests before/after |
| Removing fake defaults empties dashboards | Medium | Explicit empty/unavailable states without UI redesign |
| SQLite contention misses latency target | Medium | Batch/connection reuse, WAL, indexes, performance tests |
| Release signing unavailable | Medium | External ephemeral verification keystore; production build remains secret-gated |
| Phase 3 regression | High | Existing Phase 3 tests remain mandatory; no new Phase 3 behavior |

## Rollback strategy

- Use logical commits by subsystem.
- Each route remains an adapter; the authoritative pipeline can be disabled through a temporary rollback flag during deployment.
- Authentication enforcement supports `FUSION_SECURITY_MODE=development` only for local validation; production mode cannot be bypassed.
- Graph backend selection is configuration-driven; Neo4j can fall back to NetworkX without code rollback.
- Model runtime automatically moves to explicit policy fallback when artifact validation fails.
- Database changes are additive; export new tables before any removal.
- Android transport/signing changes are isolated by build type.
- Revert commits in reverse execution order; never delete user data during rollback.

## Performance targets

| Measure | Target |
|---|---:|
| Backend import/startup | <3 s excluding external dependency timeout |
| SDK event pipeline p95 | <100 ms with local NetworkX/fallback |
| Threat evaluation p95 | <50 ms |
| Graph query p95 | <50 ms NetworkX; <100 ms Neo4j |
| Model inference p95 | <50 ms when loaded |
| Policy fallback p95 | <10 ms |
| WebSocket process propagation p95 | <200 ms |
| SQLite queue enqueue p95 | <20 ms |
| Android cold start | <2.5 s on reference device/emulator |
| WebSocket reconnect | exponential 1–30 s with jitter |
| 1,000 active sessions | no cross-session contamination or errors |

## Security targets

- All non-health REST routes authenticated.
- All WebSockets authenticated before acceptance.
- JWT: HS256, minimum 256-bit secret, issuer/audience/expiry/jti/role validation.
- SDK tokens scoped to app, tenant, user, device, and session.
- Gateway webhook HMAC verified before persistence or execution.
- Production CORS allowlist; no wildcard with credentials.
- HTTPS/WSS only in Android release.
- No user CA trust or cleartext in release.
- No debug signing in release.
- Encrypted Android storage with fail-closed initialization.
- No BODY logging or secrets/PII in logs.
- Stable configured ledger signing key in production.
- Parameterized Cypher only.

## Validation checklist

### Backend

- [ ] Backend imports and starts with no model/Neo4j credentials.
- [ ] Readiness reports degraded dependencies honestly.
- [ ] Every production route has a security policy.
- [ ] SDK event, decision, transaction, gateway, and threat routes use one pipeline.
- [ ] Existing response compatibility tests pass.
- [ ] No demo transaction override remains in production routes.

### ML and graph

- [ ] Loaded models report artifact names and versions.
- [ ] Missing models report `POLICY_FALLBACK`; probabilities are null.
- [ ] Neo4j connectivity and parameterized query tests pass.
- [ ] NetworkX fallback executes real shared-device/beneficiary/cycle/ring queries.
- [ ] Graph UI has no fabricated default graph.

### Threat and trust integrity

- [ ] No startup threat seeding in production.
- [ ] No random latency/confidence.
- [ ] Evidence is derived from received telemetry or graph query results.
- [ ] Missing trust is unavailable, not a plausible default.
- [ ] Prohibited Phase 3+/XAI/DQS features are not added.

### Clients and transport

- [ ] React production build passes with authenticated client.
- [ ] Android debug APK builds.
- [ ] Android release APK and AAB build with external verification signing.
- [ ] Release manifest/network config rejects cleartext.
- [ ] REST and WebSocket credentials are attached and refreshed safely.
- [ ] Offline queue ordering, idempotency, retry, and reconnect tests pass.

### Final

- [ ] Full pytest suite passes.
- [ ] Android unit tests pass.
- [ ] React build passes.
- [ ] Backend startup and health probes pass.
- [ ] Performance targets are measured, not estimated.
- [ ] `PHASE2_5_IMPLEMENTATION_REPORT.md` is complete.
- [ ] Fresh `PRODUCTION_READINESS_AUDIT.md` is complete.
- [ ] Final readiness conclusion is evidence-based.

## Internal validation

The plan was checked against these constraints:

1. It uses one FastAPI process and does not introduce prohibited infrastructure from `CLAUDE.md`.
2. It does not train/download models or require unavailable Neo4j credentials.
3. It preserves endpoint compatibility through adapters.
4. It makes missing ML/graph capability explicit instead of simulating execution.
5. It does not implement new Session Intelligence, Trust Passport, Composite Risk, XAI, or DQS scope.
6. It orders security/client migrations together to avoid a permanently broken intermediate platform.
7. It provides reversible, additive changes and measurable completion criteria.

The plan is internally valid and implementation may begin.

