# New Changes — Pulled from GitHub (2026-07-23)

**Author of all changes:** `sanjayrockerz <myteamcreations09@gmail.com>`
**Commits pulled:** `6e3e921` → `81601e9` (previous local HEAD was `b12ec15`)
**Merge type:** clean fast-forward (no history divergence). Two local uncommitted edits (`ml/metrics_report.md`, one icon import in `OperationsCenterPage.jsx`) were stashed, the pull applied, then the stash was reapplied — one trivial conflict in the icon-import list, resolved by keeping upstream's superset list.

| Commit | Date | Subject | Files | Insertions/Deletions |
|---|---|---|---|---|
| `6e3e921` | 2026-07-22 21:26:57 +0530 | feat: add synthetic universe generator, trust engine, pipeline components, and root package.json | 27 | +3724 / -223 |
| `81601e9` | 2026-07-23 00:00:29 +0530 | Finalize reverse‑engineering discovery and SDK integration updates | 29 | +6133 / -974 |
| **Combined (`b12ec15`→`81601e9`)** | | | **42 files** | **+9267 / -607** |

**Scope in one sentence:** your friend took the platform from a single fusion-risk-engine demo (evaluate → verdict → SIEM timeline) and bolted on an entire second product surface — a synthetic "virtual bank" generator, a pre-transaction session/investigation/digital-twin intelligence stack, a SOAR response orchestrator, a quantum-readiness monitor, a mock blockchain evidence ledger, and a mobile "FAT-SDK" developer portal — all still inside the one FastAPI process (no guardrail-forbidden infra introduced).

**Read this first if short on time:** jump to [Summary — Key Issues & Flags](#summary--key-issues--flags) at the bottom. It consolidates every bug, dead-code path, hardcoded/mock-data concern, and CLAUDE.md guardrail flag found across all 42 files.

---

## Table of Contents

1. [Backend — Trust & Intelligence Engines](#part-1-backend--trust--intelligence-engines)
2. [Backend — Orchestration, Quantum Trust & SDK Engines](#part-2-backend--orchestration-quantum-trust--sdk-engines)
3. [Backend — `api/main.py` (Central FastAPI Entrypoint)](#part-3-backend--apimainpy-central-fastapi-entrypoint)
4. [Backend — Synthetic Universe Generator Package](#part-4-backend--synthetic-universe-generator-package)
5. [Frontend — New Trust / Quantum / SDK / Investigation Panels](#part-5-frontend--new-trust--quantum--sdk--investigation-panels)
6. [Frontend — Modified Components](#part-6-frontend--modified-components)
7. [Frontend — Pages (New & Modified)](#part-7-frontend--pages-new--modified)
8. [Summary — Key Issues & Flags](#summary--key-issues--flags)

---

# Part 1: Backend — Trust & Intelligence Engines

*Five brand-new files under `api/`: the customer-facing trust/investigation intelligence stack.*

### `api/trust_engine.py`

- **Status:** New file (246 lines)
- **Purpose:** Produces the "Investigation Trust" evidence bundle (data-quality, stability, graph-reliability, threat-attribution and a composite Investigation Trust Index) for a transaction + risk-engine verdict, and seals it into the ledger service for the XAI/evidence UI.
- **Contents:**
  - `compute_investigation_trust(txn: dict, eval_res: dict = None) -> dict` — the only function in the file (no classes); builds and returns one combined dict via 9 internal steps:
    - Derives `amount` (default `750000.0`), `user_id` (default `"usr_abc"`), `has_cyber` (default `True`), `mule_cluster` (from `txn["dest_mule_cluster_id"]`, or hardcoded `"cluster_alpha"` if `nameDest == "ACC_MULE_NEW"`), and `is_demo` (true when amount/user_id match the canned demo transaction).
    - Sets `composite_score` from `eval_res["score"]` (default `94.0`) and `action` from `eval_res["action"]` (default `"BLOCK"` if score ≥ 75 else `"ALLOW"`).
    - Builds a 10-dimension **Security Data Quality Score (SDQS)** dict (identity_confidence, device_trust, transaction_context, cyber_visibility, graph_coverage, historical_context, behavior_profile_completeness, telemetry_quality, evidence_integrity, audit_readiness), each a hardcoded number branching on `is_demo`/`has_cyber`/`mule_cluster` (e.g. `device_trust = 14 if has_cyber else 94`), then averages them into `overall_sdqs`.
    - Builds an **Evidence Quality Score (EQS)** from a fixed 9-item checklist (Timeline, Cyber SIEM Logs, Transaction History, Graph Snapshot, XAI SHAP Explanation, Counterfactual Sentence, Analyst Notes, Digital Signature, Blockchain Ledger Record) where every item is hardcoded `present: True` except "Analyst Notes"; computes a percentage and a `missing_items` list.
    - Builds a **Decision Stability Index (DSI)** from 4 canned "what-if" sensitivity simulations (±10% amount, location swap Mumbai→Delhi, device-ID mismatch, removing the cyber compromise flag); the 4th simulation hardcodes the score dropping to `61.0` and the action flipping to `"CHALLENGE"`; sets `dsi_score = 96 if action == "BLOCK" else 92`.
    - Builds a **Graph Reliability Index (GRI)** dict (overall_score, known_mule_ring_confidence, pagerank_confidence, community_detection_certainty, historical_node_matches, graph_coverage_percent) with hardcoded values gated on whether `mule_cluster` is set.
    - Selects a **Threat Attribution** multi-class probability dict (Account Takeover, Credential Stuffing, Money Mule Network, SIM Swap, QR Scam, Business Email Compromise, Insider Fraud) from one of 3 hardcoded dicts.
    - Computes the **Investigation Trust Index (ITI)**, a weighted sum: `model_agreement(0.20, fixed 96.0) + graph_confidence(0.15) + cyber_visibility(0.15) + explainability(0.15, fixed 99.0) + evidence_completeness(0.15) + data_quality(0.10) + response_validation(0.10, fixed 100.0)`.
    - Builds a "Why should I trust this?" `decision_trust_report` with a 9-item `reasons[]` list.
    - Calls `ledger_service.create_evidence_record(...)` to obtain an immutable `ledger_record` (SHA-256 hash, HMAC signature, incrementing block height, verification token).
    - Builds a hardcoded `telemetry` dict of fabricated performance numbers (`tps_capacity: 1450`, `inference_ms: 12`, `total_latency_ms: 48`, etc.) — none of these are actually measured.
    - Returns `{iti, sdqs, overall_sdqs, eqs, dsi, gri, threat_attribution, decision_trust_report, ledger_record, telemetry, provenance}`.
- **API surface:** none directly — called from `api/pipeline_engine.py::execute_pipeline`. Also imported directly in `api/main.py` but **never called there — a dead import**.
- **Notable details:**
  - Heavy hardcoded demo defaults throughout (amount `750000.0`, `user_id "usr_abc"`, `device_id "dev_9999"`, `ip "185.15.2.22"`, `nameDest "ACC_MULE_NEW"`, `mule_cluster "cluster_alpha"`).
  - `import json` and `import math` are both unused dead imports.
  - The "telemetry" latency figures are fixed constants presented as if measured — misleading if surfaced to judges as real perf numbers.
  - Depends on `api/ledger_service.py`'s module-level singleton for the SHA-256/HMAC "Hyperledger Fabric"-branded evidence sealing.

### `api/trust_fabric_engine.py`

- **Status:** New file (218 lines)
- **Purpose:** Implements a "regulator-ready" evidence-integrity subsystem — evidence package assembly, SHA-256 sealing, mock digital signatures, an Investigation Trust Index, chain-of-custody logging, and audit-trail/export APIs — backing the `/evidence/*` and `/audit/*` REST endpoints.
- **Contents:**
  - `class TrustFabricEngine`
    - `__init__` — two in-memory dicts: `evidence_store`, `chain_of_custody_logs`. No persistence.
    - `create_evidence_package(data)` — generates IDs (`incident_id`, `evidence_id` via `random.randint(1000,9999)`), assembles a `payload` with hardcoded KYC tier/transaction/device/threat details, computes a **real** `sha256_hash` over the payload, builds a **mock** `digital_signature` (formatted string, not real crypto), a fixed `investigation_trust_index` (`97.8`, `"HIGH_INVESTIGATION_TRUST"`), an 8-step hardcoded `audit_timeline` with **literal fixed date strings** (`"2026-07-22 21:50:0X IST"`, not derived from `datetime.now()`), stores the record, returns it.
    - `get_evidence(evidence_id)` — returns stored package or fabricates a default demo package.
    - `verify_evidence_integrity(evidence_id)` — re-hashes and compares; defaults `is_hash_valid = True` when no `expected_hash` supplied.
    - `get_audit_trail(incident_id)` — returns stored custody log or a synthesized single entry.
    - `export_evidence_bundle(evidence_id, format_type)` — wraps evidence + verification into an export envelope.
  - `trust_fabric = TrustFabricEngine()` — module-level singleton.
- **API surface:** `POST /evidence/create`, `GET /evidence/{evidence_id}`, `GET /evidence/verify/{evidence_id}`, `GET /audit/{incident_id}`, `POST /evidence/export`.
- **Notable details:**
  - Hardcoded secret-free but ID generation uses unseeded `random.randint` — non-deterministic, theoretically collidable.
  - **Bug:** the `audit_timeline`'s hardcoded date strings never reflect the real computed `timestamp` a few lines above — the timeline always shows the same fixed date regardless of actual creation time.
  - "Digital signature"/"HSM Node" are cosmetic strings, not real RSA/ECDSA — no crypto keypair exists.
  - In-memory-only storage — restart loses all evidence/audit history.

### `api/session_intelligence_engine.py`

- **Status:** New file (270 lines)
- **Purpose:** Implements "Pre-Transaction Session Intelligence" — a 6-checkpoint fusion pipeline (identity, device, session, behavior, cyber, graph) issuing a time-boxed "Session Trust Passport" with an ALLOW/CHALLENGE/BLOCK decision before a transaction executes.
- **Contents:**
  - Module-level `MITRE_ATTACK_MAPPINGS` — 7 canned MITRE ATT&CK technique entries (e.g. `impossible_travel_login → T1078.004`, `cookie_theft_reuse → T1539`, `sim_swap_interception → T1111`).
  - `class SessionTrustPassportEngine`
    - `analyse_session(session_data)` — runs 6 checkpoint methods (each individually timed), computes `overall_trust` as a weighted sum (`identity*0.15 + device*0.20 + session*0.20 + behavior*0.15 + cyber*0.15 + graph*0.15`), maps to decision bands (`≥75 ALLOW`, `≥45 CHALLENGE`, else `BLOCK`), with a hard override forcing `BLOCK`/`CRITICAL` if `cyber_res["score"] < 30` or `graph_res["score"] < 30`. Issues a passport with 15-minute expiry.
    - `_eval_identity_checkpoint`, `_eval_device_checkpoint`, `_eval_session_checkpoint`, `_eval_behavior_checkpoint`, `_eval_cyber_checkpoint`, `_eval_graph_checkpoint` — each branches on the same condition (`cyber_compromise_in_window` truthy OR `user_id == "usr_abc"`), returning one of two hardcoded score/reason sets (compromised vs. clean).
    - `get_passport(session_id)` — returns cached passport or synthesizes a default critical-demo one.
    - `update_session(session_id, update_event)` — re-runs analysis merging in the update.
  - `session_engine = SessionTrustPassportEngine()` — module-level singleton.
- **API surface:** `POST /session/analyse`, `GET /session/passport/{session_id}`, `POST /session/update`, `POST /session/recalculate`.
- **Notable details:**
  - The hardcoded demo user `usr_abc` is **unconditionally treated as compromised** across all 6 checkpoints regardless of actual input data.
  - All scores/reasons/MITRE mappings are static per-branch constants — a binary compromised/clean lookup table, not a continuous/model-driven score.

### `api/investigation_intelligence_engine.py`

- **Status:** New file (304 lines)
- **Purpose:** Post-session "Investigation Intelligence" layer — network-level burst-attack detection, graph mule-ring discovery, multi-stage attack-narrative correlation, and decision-quality scoring, rolled into a fusion investigation summary brief.
- **Contents:**
  - `class InvestigationIntelligenceEngine`
    - `detect_burst_attack(user_id, data)` — Module 1: compromised path returns `"CRITICAL"` severity `"SYNCHRONIZED_BOTNET_CREDENTIAL_BURST"` with hardcoded `entity_count: 500`, `velocity_events_per_min: 125.0`, and a 5-signal breakdown table.
    - `discover_mule_ring(user_id, data)` — Module 2: returns a mule ring profile (`ring_confidence: 0.96`, 4-member ring, 5 canned graph patterns) when compromised or a mule cluster is present.
    - `correlate_threat_narrative(user_id, data)` — Module 3: a 5-stage hardcoded attack-chain narrative with fixed timestamps.
    - `calculate_decision_quality(user_id, data)` — Module 4: `decision_quality_score: 96.5`, weighted `explainable_contributions` referencing Cyber SIEM/Neo4j/LightGBM/Isolation Forest — all fixed constants, not live model calls.
    - `generate_fusion_summary(...)` — Module 5: assembles a human-readable brief with `estimated_loss_prevented` and `recommended_response`.
    - `get_cached_investigation(case_id)` — returns cache or synthesizes a default critical-demo result.
  - `investigation_engine = InvestigationIntelligenceEngine()` — module-level singleton.
- **API surface:** `POST /investigation/analyse`, `POST /burst/analyse`, `POST /mule/discover`, `GET /investigation/{case_id}`.
- **Notable details:**
  - Same recurring pattern: every module branches on `cyber_compromise_in_window OR user_id == "usr_abc"`.
  - "Neo4j"/"LightGBM/GraphSAGE/Isolation Forest" mentions are narrative labels on hardcoded numbers, not actual calls into those systems from this file.
  - Attack-chain timestamps are literal hardcoded strings, not derived from real request time.

### `api/digital_twin_engine.py`

- **Status:** New file (294 lines)
- **Purpose:** Maintains a per-customer "Digital Twin" — a continuously-updated in-memory profile (identity, devices, locations, spending habits, behavior, graph position, risk history, predictive forecasts, timeline) used to compute baseline-vs-observed deviation scores.
- **Contents:**
  - `class CustomerDigitalTwin(user_id="usr_abc")` — builds 9 hardcoded profile blocks (identity, devices, locations, transactions_profile, behavior, graph, risk, predictions, timeline), all seeded for the demo persona "Rajesh Kumar."
  - `update_twin(event_data)` — live-updates the twin from a streamed cyber_event or transaction; unconditionally escalates `risk["current_risk"] = 94.0` whenever either sub-condition of a branch is hit.
  - `compare_transaction(txn_data)` — the "Deviation Engine": 6 weighted deviation sub-scores (device/location/amount/merchant/cyber/graph) → `overall_dev_index` → verdict (`CRITICAL_DEVIATION` / `MODERATE_DEVIATION` / `NORMAL`).
  - `get_full_profile()` — returns all 9 profile blocks.
  - Module-level `_TWIN_STORE` cache + `get_or_create_digital_twin(user_id)` factory.
- **API surface:** `GET /digital_twin/{user_id}`, `POST /digital_twin/update`, `POST /digital_twin/compare`, `GET /digital_twin/{user_id}/timeline`, `GET /digital_twin/{user_id}/history`, `GET /digital_twin/{user_id}/snapshot`. Also consumed directly inside the `/ws/stream` WebSocket replay loop for every event.
- **Notable details:**
  - All profile seed data is hardcoded for the single demo persona; any other `user_id` gets a generic near-empty twin.
  - `import math` and `import hashlib` are unused dead imports.
  - Twin state is purely in-memory — restart resets every customer's history/risk trend/timeline.

---

# Part 2: Backend — Orchestration, Quantum Trust & SDK Engines

*Six new files under `api/` plus a new root `package.json`.*

### `api/response_orchestrator_engine.py`

- **Status:** New file (376 lines)
- **Purpose:** SOAR-style response layer recommending/"executing" fraud-response playbooks (freeze account, block device, notify SOC, etc.), tracking them as incidents, supporting rollback — all in-memory, no real integration to any core banking/telco/SMS system.
- **Contents:**
  - `DEFAULT_PLAYBOOKS` — 10 hardcoded playbooks (`PLAYBOOK_ATO`, `PLAYBOOK_MULE`, `PLAYBOOK_CRED_STUFF`, `PLAYBOOK_SIM_SWAP`, `PLAYBOOK_QR_SCAM`, `PLAYBOOK_CORP_FRAUD`, `PLAYBOOK_INSIDER`, `PLAYBOOK_BURST`, `PLAYBOOK_MALWARE`, `PLAYBOOK_SYNTHETIC`), each with trigger conditions, priority, execution order, approval/rollback rules.
  - `class ResponseOrchestrationEngine`
    - `recommend_response(data)` — 6 hardcoded actions if `is_compromised` (same `usr_abc`-always-compromised pattern), else a single `ALLOW` action.
    - `execute_response(request_data)` — fully hardcoded execution trace regardless of input: 7 fabricated steps with sub-millisecond latencies, 3 canned notifications (fixed phone number, webhook, RM name), an 8-event timeline with fixed IST timestamps and a fixed evidence hash prefix.
    - `create_playbook`, `get_playbooks`, `get_incident` (**fabricates data for unknown IDs instead of 404**), `assign_incident`, `rollback_response` (hardcoded confirmation, no real state change).
  - `soar_engine = ResponseOrchestrationEngine()` — module-level singleton.
- **API surface:** `POST /response/recommend`, `POST /response/execute`, `POST /playbook/create`, `GET /playbook`, `GET /incident/{incident_id}`, `POST /incident/assign`, `POST /response/rollback`.
- **Notable details:** nearly all "live" execution data (timestamps, phone numbers, hash prefixes, latencies, analyst names) is hardcoded to match one demo narrative, not derived from actual input.

### `api/quantum_trust_layer.py`

- **Status:** New file (266 lines)
- **Purpose:** The "Quantum Trust Layer" (QTL) — a mock post-quantum-cryptography (PQC) readiness/crypto-agility assessment module, matching CLAUDE.md's "Mini Quantum Risk Monitor" scope item. **No guardrail violation** — this is in-scope.
- **Contents:**
  - `INVENTORY_DATABASE` — 5 hardcoded crypto assets (Core Banking Gateway RSA-2048, SWIFT Node RSA-4096, UPI Gateway ECDSA P-256, HSM Evidence Key Manager ML-KEM-768/Dilithium, Legacy ATM RSA-1024/SHA-1).
  - `class QuantumTrustEngine`
    - `get_readiness_score()` — real formula: `75.0 + (quantum_resistant/total)*20 - (legacy/total)*25 - (expiring_90d/total)*10`, clamped `[10, 98.5]`, mapped to readiness bands.
    - `get_assessment()`, `analyze_asset(asset_id)`, `get_recommendations()`, `get_dashboard_summary()`, `get_compliance_details()`, `simulate_quantum_scenario(scenario_data)` — the simulator carries an explicit disclaimer that it's "an educational architectural simulation... No live cryptographic keys were altered."
  - `quantum_trust = QuantumTrustEngine()` — singleton.
- **API surface:** `GET /quantum/readiness`, `/quantum/inventory`, `/quantum/assessment`, `POST /quantum/analyze`, `GET /quantum/recommendations`, `/quantum/dashboard`, `/quantum/compliance`, `POST /quantum/simulate`.
- **Notable details:** the 5-asset inventory and risk-distribution counts are hardcoded and never reflect a live infrastructure scan — self-declared illustrative only in the simulator's disclaimer, not in the readiness/assessment/recommendation functions.

### `api/pipeline_engine.py`

- **Status:** New file (424 lines)
- **Purpose:** Synthesizes a 16-stage "Real-Time Processing Pipeline" evidence trail for a transaction (ingestion → fusion scoring → SOC dispatch), wrapping the real `risk_engine.evaluate`, `ml.predict` scores, and `trust_engine.compute_investigation_trust`, with a demo-mode fast path for the one canonical hardcoded transaction.
- **Contents:**
  - `execute_pipeline(txn)` — derives identifiers (defaulting to fixed demo values); `is_demo_txn` check (`amount==750000.0 and user_id=="usr_abc"`) **skips all real model calls** and hardcodes `lgbm_prob=0.87`, `composite_score=94.0`, `action="BLOCK"`, etc. Else calls the real `evaluate()`, `tabular_score()`, `anomaly_score()`. Builds 16 `stages_executed` dicts, most with hardcoded "evidence" fields (device trust score, graph traversal counts, fake embedding vector samples) even on the live path; computes a genuine `hashlib.sha256` evidence hash; calls `compute_investigation_trust(...)`.
- **API surface:** `POST /evaluate/transaction/pipeline`, `POST /evaluate/transaction/trust`; also called inside the `/ws/stream` WebSocket handler for every streamed transaction.
- **Notable details:** any real transaction that happens to match `amount=750000.0, user_id="usr_abc"` would silently take the fully mocked demo path instead of running actual models.

### `api/scenario_engine.py`

- **Status:** New file (150 lines)
- **Purpose:** A static library of 12 pre-canned fraud/normal-banking scenario definitions (sample transactions + expected verdict/risk score) for one-click demo scenario selection.
- **Contents:** `SCENARIOS` dict (normal_banking_day, salary_day, upi_fraud, account_takeover, credential_stuffing, sim_swap, qr_scam, known_mule, corporate_payroll_fraud, insider_fraud, atm_cash_out, cross_border_money_laundering); `generate_scenario(scenario_id)` (**silently defaults to `account_takeover` if id unknown**); `get_all_scenarios_list()`.
- **API surface:** `GET /scenarios/list`, `GET /scenarios/generate/{scenario_id}`.
- **Notable details:** `import random` unused; unknown scenario IDs never 404.

### `api/sdk_engine.py`

- **Status:** New file (344 lines)
- **Purpose:** Simulates a mobile "Fusion Adaptive Trust SDK" backend — session lifecycle, device/network/runtime trust scoring, event ingestion, adaptive policy matching, and a real-time decision API — as if a native mobile SDK streamed telemetry into the backend.
- **Contents:**
  - `DEFAULT_POLICIES` — 5 hardcoded adaptive policies whose `trigger` strings are descriptive only (not actually parsed/evaluated — real logic is duplicated separately in `_check_policy_trigger`/`request_decision`, so editing a policy's `trigger` string has zero runtime effect).
  - `class FusionAdaptiveTrustSDKEngine` — `start_session`, `register_device` (real risk-deduction math for root/emulator/Frida/debugger/overlay), `register_network`, `ingest_event`, `_get_risk_modifier`, `_check_policy_trigger`, `request_decision` (ordered if/elif cascade with fixed confidence constants per branch), `get_policies`, `get_trust_passport`, `get_observability` (**`queued_events`/`average_latency_ms` are `random`-generated on every call, not measured**), `get_connected_apps`, `get_live_event_stream`, `get_error_codes`.
- **API surface:** 11 routes (`/sdk/session/start`, `/sdk/device`, `/sdk/network`, `/sdk/event`, `/sdk/request-decision`, `/sdk/policies`, `/sdk/passport`, `/sdk/health`, `/sdk/apps`, `/sdk/events`, `/sdk/error-codes`).
- **Notable details:** `connected_apps` names 3 fictitious apps as demo dressing; no fixed seed anywhere so `/sdk/health` returns different numbers every call.

### `api/ledger_service.py`

- **Status:** New file (113 lines)
- **Purpose:** A simulated "Hyperledger Fabric" blockchain ledger that seals evidence packages with a SHA-256 hash + HMAC "digital signature," an incrementing block height, and a fabricated chain-of-custody trail.
- **Contents:**
  - `class LedgerService(secret_key="FinSpark26_BankOfMaharashtra_QuantumSecretKey")` — **hardcoded secret key checked into source**; `current_block_height` starts at a fixed `48192` every restart; `create_evidence_record` computes a real SHA-256 hash and an HMAC "signature" **explicitly code-commented as "HMAC-SHA256 simulation representing HSM key signature"** yet the field is labeled `digital_signature: f"SIG_RSA4096_..."`; `verify_evidence`, `get_evidence_history`.
- **API surface:** none directly — reached transitively via `trust_engine.py` → `pipeline_engine.py` → `main.py`'s `/evaluate/transaction/pipeline`, `/evaluate/transaction/trust`, and `/ws/stream`.
- **Notable details:** "Hyperledger Fabric v2.5" / "Raft BFT Consensus" are descriptive label strings only — no real blockchain network, peer, or channel exists anywhere; not a guardrail violation (adds no new infra dependency) but reads as more real than it is.

### `package.json` (repo root — new file)

- **Status:** New file (11 lines)
- **Contents:** `name: "unified-cyber-fraud-intelligence-platform"`, no dependencies/devDependencies at all; 4 scripts (`dev`, `build`, `preview`, `start`) that all just delegate to `npm run <script> --prefix web`.
- **Implication:** purely a root-level convenience wrapper around the pre-existing `web/package.json` (which holds the real dependency tree) — lets you run `npm run dev` from the repo root without `cd web` first. No dependency/version conflict risk since this file declares zero dependencies of its own.

---

# Part 3: Backend — `api/main.py` (Central FastAPI Entrypoint)

- **Status:** Modified — **266 lines → 870 lines** (net **+604 / -0** against the pre-pull baseline; every original line, function, and route survives unchanged — nothing was removed).
- **New imports added** (14 new engine-module imports): `pipeline_engine.execute_pipeline`, `trust_engine.compute_investigation_trust` **(dead — never called in this file)**, `scenario_engine` (2 functions), `synthetic_universe.fraud_scenario_engine.generate_bank_universe`, `synthetic_universe.graph_generator.generate_graph_topology`, `synthetic_universe.exporter` (4 functions), `synthetic_universe.bank_model` (`default_bank` **dead**, `get_virtual_bank`, `BANK_REGISTRY` used), `digital_twin_engine.get_or_create_digital_twin`, `session_engine`, `investigation_engine`, `soar_engine`, `trust_fabric`, `quantum_trust`, `sdk_engine`.
  - **`api/ledger_service.py` is not imported into `main.py` at all** — only reachable transitively through `trust_engine`/`pipeline_engine`.
- **New Pydantic request models:** 26 new `BaseModel` classes added (one per new POST endpoint) — no new response models; all responses are raw dicts from the engine singletons.
- **New endpoints added:** route count grew from **4** to **65** — **61 brand-new routes** across 9 feature areas:
  - **Pipeline/Scenario:** `/evaluate/transaction/pipeline`, `/evaluate/transaction/trust`, `/scenarios/list`, `/scenarios/generate/{scenario_id}` (4)
  - **Synthetic Universe:** `/synthetic/universe/create_bank`, `/generate`, `/preview`, `/start_scenario`, `/pause`, `/resume`, `/stats`, `/clear`, `/export/{csv,json,parquet,replay}` (12)
  - **Digital Twin:** `/digital_twin/{user_id}`, `/update`, `/compare`, `/{user_id}/timeline`, `/{user_id}/history`, `/{user_id}/snapshot` (6)
  - **Session Intelligence:** `/session/analyse`, `/passport/{session_id}`, `/update`, `/recalculate` (4)
  - **Investigation Intelligence:** `/investigation/analyse`, `/burst/analyse`, `/mule/discover`, `/investigation/{case_id}` (4)
  - **SOAR Response:** `/response/recommend`, `/execute`, `/rollback`, `/playbook/create`, `/playbook`, `/incident/{incident_id}`, `/incident/assign` (7)
  - **Trust Fabric / Evidence:** `/evidence/create`, `/{evidence_id}`, `/verify/{evidence_id}`, `/audit/{incident_id}`, `/evidence/export` (5)
  - **Quantum Trust Layer:** `/quantum/readiness`, `/inventory`, `/assessment`, `/analyze`, `/recommendations`, `/dashboard`, `/compliance`, `/simulate` (8) — distinct from the pre-existing `/quantum/posture`
  - **FAT-SDK:** `/sdk/session/start`, `/device`, `/network`, `/event`, `/request-decision`, `/policies`, `/passport`, `/health`, `/apps`, `/events`, `/error-codes` (11)
- **Changes to existing endpoints:**
  - `/evaluate/transaction`, `/quantum/posture`, `/report/cert-in` — **all untouched**, byte-for-byte identical to before the pull.
  - **`/ws/stream` (WebSocket replay loop) — meaningfully modified.** For every streamed event it now also: (1) updates the user's digital twin on every event, (2) if the event is a transaction, runs `execute_pipeline()` and streams two **new WS message types** (`pipeline_overview`, then one `pipeline_stage` per stage with a 0.08s delay) before the original per-event delay, (3) widened its `try/except` to also catch bare `Exception` (previously only `WebSocketDisconnect`) and log instead of crash. **Any frontend consumer of `/ws/stream` must now handle these two new message types or will silently ignore them.**
- **Anything removed:** nothing — confirmed +604/-0 against the pre-pull baseline.
- **Notable details:**
  - New route blocks are inserted in three disconnected spots in the file (not grouped consistently) — reads as rushed/copy-pasted rather than organized.
  - Stray extra blank lines inserted in a couple of spots — cosmetic merge debris.
  - Two dead imports (`compute_investigation_trust`, `default_bank`).
  - Two similarly-named but functionally distinct "scenario" systems now coexist: `api/scenario_engine.py` (static canned scenarios, `/scenarios/*`) vs. `api/synthetic_universe/fraud_scenario_engine.py` (procedural generation, `/synthetic/universe/*`) — easy to confuse.
  - No CORS/middleware changes, no app startup/lifecycle changes.
  - Still exactly **one FastAPI process** — all 61 new routes and engine singletons run in-process; **no guardrail violation** (no Kafka/Flink/K8s/Terraform/MLflow/Seldon/federated learning/message broker introduced).

---

# Part 4: Backend — Synthetic Universe Generator Package

*An entire new package, `api/synthetic_universe/` (9 files), that fabricates a full virtual bank from scratch — customers, devices, transactions, cyber events, and a graph — with no real dataset underneath it.*

### `api/synthetic_universe/__init__.py`
- **Status:** New (1 line) — bare package marker (`# api/synthetic_universe package`), no exports/`__all__`. Every consumer imports directly from submodules.

### `api/synthetic_universe/bank_model.py`
- **Status:** New (95 lines; grew from 54 in commit 1)
- **Purpose:** Static reference-data model of fictional banks (branches, ATMs, employees, merchants, payment rails, limits) for realistic-looking IDs.
- **Contents:** `class VirtualBankModel` — 7 branches, 5 ATMs (one deliberately `FLAGGED_RISK`), 5 employees (incl. one `FRAUD_ANALYST` and one `TELLER_PRIVILEGED` used by the insider-fraud scenario), 7 merchants (incl. one `MULE_RING`/`CRITICAL`), 8 payment gateways, 6 hardcoded limits. `BANK_REGISTRY` — 3 fictional banks (`FUSB`/`GLBB`/`APEX`); `default_bank`, `get_virtual_bank(bank_code)`.
- **Notable details:** bank names are entirely fictional (does not impersonate the real sponsor bank). No local RNG seeding — depends on global `random` state.

### `api/synthetic_universe/customer_generator.py`
- **Status:** New (223 lines; grew from 103)
- **Purpose:** Generates full synthetic customer profiles (identity, KYC, accounts, cards, loans, insurance, beneficiaries, behavior habits).
- **Contents:** `generate_random_pan()`, `generate_random_aadhaar()` (fabricate PAN/Aadhaar-shaped strings), `generate_customer_profile(idx, seed)` — hardcoded demo override for `idx==0` (forces `usr_abc`/"Rajesh Kumar"/Mumbai/₹36L salary/KYC Tier-3), `generate_customers_batch(count, seed)`.
- **Notable details:** `import hashlib`/`datetime` are dead imports. Reseeds the **global** `random` module per-customer (`random.seed(seed+idx)`), which mutates process-wide RNG state for anything running afterward.
- **⚠ GUARDRAIL FLAG:** fabricates realistic PAN numbers, Aadhaar numbers, and KYC/biometric verification statuses for 100+ synthetic identities with **no in-file disclaimer that this is fake data** — unlike `data/build_overlay.py`'s mandatory "HONESTY NOTICE" block that CLAUDE.md requires for synthesized data.

### `api/synthetic_universe/cyber_event_generator.py`
- **Status:** New (63 lines; grew from 45)
- **Purpose:** Generates SIEM-style cyber telemetry events (logins, credential attacks, device compromise).
- **Contents:** `CYBER_EVENT_CATALOG` (13 hardcoded event types with fixed `km_from_baseline`), `generate_cyber_event_for_user(user_id, timestamp)` (hardcoded demo path for `usr_abc`), `generate_cyber_telemetry_batch(users, count)`.
- **Notable details:** `timedelta` import unused. The catalog's fixed `km_from_baseline` (e.g. `4500`) is never cross-checked against the real Haversine distance computed elsewhere — the two "distance" numbers can diverge.

### `api/synthetic_universe/device_location_generator.py`
- **Status:** New (92 lines; grew from 66)
- **Purpose:** Generates device fingerprint/trust profiles and geolocation/IP telemetry, including **real** Haversine great-circle distance math.
- **Contents:** `DEVICE_TYPES` (6 classes), `CARRIERS`, `GEO_LOCATIONS` (7 cities incl. Moscow/London pre-labeled "Proxy/VPN"), `calculate_haversine_distance(...)` (genuine formula, Earth radius 6371km), `generate_device_profile(user_id, is_compromised)`, `generate_location_telemetry(city_name, is_proxy, baseline_city)`.
- **Notable details:** real formula-based computation coexists with hardcoded per-city lat/lon constants — legitimate math, fixed input data.

### `api/synthetic_universe/exporter.py`
- **Status:** New (66 lines; grew from 40)
- **Purpose:** Serializes the generated universe into CSV, JSON, WebSocket-replay JSON, or Parquet.
- **Contents:** `export_dataset_csv` (**`isFraud`/`isFlaggedFraud` are both derived purely from `cyber_compromise_in_window`**, not an independent ground-truth flag), `export_dataset_json`, `export_dataset_replay` (fixed per-message `delay`), `export_dataset_parquet_bytes` (graceful pandas/pyarrow fallback to JSON on failure).
- **Notable details:** the only file in the package whose docstring explicitly says "Synthetic."

### `api/synthetic_universe/fraud_scenario_engine.py`
- **Status:** New (175 lines; grew from 82) — **the package's orchestrator**.
- **Purpose:** Defines the demo scenario catalog and assembles the full "Digital Banking Universe" by calling every other generator in sequence.
- **Contents:** `SCENARIO_CATALOG` (12 scenarios with fixed `expected_risk` 15–98), `generate_bank_universe(num_customers, num_txns, seed, bank_code)` — seeds global `random`, calls `get_virtual_bank` → `generate_customers_batch` → per-customer `generate_device_profile`/`generate_location_telemetry` (forcing Moscow/compromised for `usr_abc`) → `generate_transaction_universe` (3% anomaly rate) → `generate_cyber_telemetry_batch` (20% of customer count) → **force-inserts** one fixed cyber event `EVT-CYBER-8819` regardless of what the batch generator produced; truncates customer/account/device/location previews to 50.
- **⚠ GUARDRAIL FLAG:** as the orchestrator producing the entire fabricated universe (PAN/Aadhaar IDs, KYC statuses, a hardcoded "₹7.5L" account-takeover event), its docstrings never state this data is synthetic/non-real — same disclaimer gap as `customer_generator.py`, but here at the top-level entry point.

### `api/synthetic_universe/graph_generator.py`
- **Status:** New (113 lines; grew from 45)
- **Purpose:** Converts the assembled universe into a generic node/edge graph (Customer/Account/Device/IPAddress/City/Merchant/MuleCluster/Fraudster nodes) plus a Cypher sample.
- **Contents:** `generate_graph_topology(universe)` — **the only file in the package with zero imports** (no networkx, no community-detection library).
- **Notable details:** **Bug:** the Cypher sample template hardcodes the label `Customer` for every node type regardless of its actual type.
- **⚠ GUARDRAIL FLAG (most significant one found in this pull):** `graph_properties` returns **fixed, hardcoded** values — `density: 0.048`, `connected_components: 4`, `louvain_modularity: 0.81`, `pagerank_max: 0.0512`, `graph_sage_embedding_dim: 64` — regardless of the actual graph just built, and the file performs **no PageRank, betweenness, Louvain, or GraphSAGE computation whatsoever**. This directly conflicts with two explicit CLAUDE.md requirements: (1) the graph model must actually compute PageRank/betweenness/Louvain centrality, and (2) "metrics honesty is a scoring criterion... every number must be reproducible from the code that produced it." This function presents canned, non-computed centrality/community numbers as if they describe the graph it just built.

### `api/synthetic_universe/transaction_behavior_engine.py`
- **Status:** New (110 lines; grew from 72)
- **Purpose:** Generates individual customer transactions across realistic payment-type distributions, plus the one hardcoded "golden path" fraud transaction tied to the demo narrative.
- **Contents:** `ALL_PAYMENT_TYPES` (18 types), `simulate_customer_transaction(customer, is_anomaly, days_ago)` — hardcoded demo path fixes `amount=750000.0`, `dest_acc="ACC_MULE_NEW"`, `mule_cluster="cluster_alpha"`; otherwise draws from `random.choices` with fixed weights per payment type. `generate_transaction_universe(customers, total_txns, anomaly_pct, seed)`.
- **Notable details:** `import numpy as np` is a dead import. The module-level `anomaly_pct` default (0.02) differs from what the orchestrator actually passes (0.03) — effectively unused.

## Package-level summary

- **Data flow:** `bank_model.py` (static reference data) → `customer_generator.py` (population) → `device_location_generator.py` + `cyber_event_generator.py` + `transaction_behavior_engine.py` (independent per-customer telemetry) → **`fraud_scenario_engine.py`** (orchestrates all of the above into one `universe` dict) → **`graph_generator.py`** (downstream: builds a graph from the universe, with hardcoded fake centrality metrics) and **`exporter.py`** (downstream: serializes to CSV/JSON/Parquet/replay).
- **Overlap with `data/build_overlay.py`:** the pre-existing `data/build_overlay.py` (referenced in CLAUDE.md) anchors to **real PaySim data** and only synthesizes the missing cyber-overlay link, with a mandatory "HONESTY NOTICE" docstring and a fixed seed for reproducibility. This new package instead fabricates **the entire bank end-to-end from nothing** — functionally parallel in purpose (both produce a fraud+cyber-context dataset) but fundamentally different in grounding (real backbone vs. 100% synthetic). **No file in this package carries an equivalent honesty disclaimer** to `build_overlay.py`'s — worth the owner's attention given CLAUDE.md's explicit instruction to "say so explicitly in code comments and to judges. Never present it as real joined bank data."
- **Guardrail tech check:** no Kafka/Flink/K8s/Terraform/MLflow/Seldon/federated learning anywhere in this package.

---

# Part 5: Frontend — New Trust / Quantum / SDK / Investigation Panels

*Nine brand-new React components. Confirmed: none of them import `recharts` or `react-force-graph-2d` — all visualization is hand-built Tailwind divs/bars with `lucide-react` icons.*

### `web/src/components/quantum/QuantumTrustPanel.jsx`
- **Status:** New (429 lines)
- **Purpose:** "Fusion Quantum Trust Layer" dashboard — PQC readiness score, crypto asset inventory, migration recommendations, educational Shor's-algorithm simulator.
- **State:** `readiness`, `assessment`, `inventory`, `recommendations`, `activeTab` (8 tabs declared, only 6 implemented), `loading`, simulator controls (`simSelectedAsset`, `simYear`, `simResult`, `isSimulating`), `searchTerm`.
- **API calls:** `GET /quantum/{readiness,assessment,inventory,recommendations}` (parallel on mount), `POST /quantum/simulate` — all confirmed to exist.
- **Renders:** header stat strip, 8-tab bar, overview/assessment/inventory/migration/simulation/audit content, export buttons.
- **Notable details:** `algorithms` and `compliance` tabs are declared in the tab bar but have **no render block** — selecting either shows blank content. `handleExportReport(format)` always builds a JSON blob regardless of `format` — clicking "Export ... PDF" downloads a file named `.pdf` containing raw JSON. No error/empty state — a failed fetch leaves the component stuck on the loading spinner forever.

### `web/src/components/sdk/FATSDKDeveloperPortal.jsx`
- **Status:** New (623 lines)
- **Purpose:** Stripe-style developer portal for the "Fusion Adaptive Trust SDK" — docs, quick-start code samples, live API explorer, behavior simulator, policy viewer, integration monitor, connected-app registry.
- **State:** `activeTab` (8 tabs), `health`/`apps`/`policies`/`liveEvents`, `loading`, API-Explorer state, SDK-Showcase simulator state, `liveRef` (**declared and attached but never read — dead ref**).
- **API calls:** `GET /sdk/{health,apps,policies,events}` (parallel on mount + polled every 3s), generic API Explorer against a hardcoded 10-endpoint list, `POST /sdk/event` + `POST /sdk/request-decision` for the showcase simulator. All endpoints confirmed to exist.
- **Notable details:** all Kotlin/Gradle code samples reference a fictitious `com.fusion.sdk.Fusion` Android SDK class hierarchy that doesn't exist anywhere in this repo — purely illustrative documentation, not real shippable code.

### `web/src/components/investigation/InvestigationIntelligencePanel.jsx`
- **Status:** New (359 lines)
- **Purpose:** Network-level "Investigation Intelligence Brief" — attack narrative, burst-attack detection, mule-ring discovery, decision-quality scoring, executive summary.
- **Props:** `caseId` (default `'CASE-2026-8942'`), `activeTxn`.
- **API calls:** `POST /investigation/analyse` — confirmed to exist. This is the only network call; no embedded mock response data (unlike several siblings).
- **Notable details:** clean component — fully server-driven, only request-fallback values are hardcoded demo defaults.

### `web/src/components/trust/DecisionStabilityInspector.jsx`
- **Status:** New (91 lines)
- **Purpose:** Perturbation-simulation table showing whether the ALLOW/CHALLENGE/BLOCK decision changes under small feature variations.
- **Props:** `trustData` (returns `null` if absent), `action` (default `'BLOCK'`, **never referenced — dead prop**).
- **Notable details:** pure presentational, no hooks, no API calls. **Currently unreachable in the running app** — imported by `RealTimeProcessingPipeline.jsx` but never actually rendered there, and no other file imports it. As shipped, it never appears on screen.

### `web/src/components/trust/DecisionTrustReport.jsx`
- **Status:** New (102 lines)
- **Purpose:** "Why should I trust this?" defensibility checklist backing a BLOCK/ALLOW verdict.
- **Props:** `trustData` (optional), `action` (default `'BLOCK'`).
- **Notable details:** **Entirely mock data in practice** — defines a large hardcoded fallback report object inline (9 fixed reasons, `confidence_percent: 97`), and since no parent currently passes `trustData` to it anywhere in the codebase, **it only ever shows the hardcoded fallback**. Also currently unreachable in the running app (same import-but-never-rendered pattern as above).

### `web/src/components/trust/InvestigationTrustPanel.jsx`
- **Status:** New (273 lines)
- **Purpose:** Investigation Trust Index (ITI) dashboard combining EQS/GRI/SDQS and a threat-attribution probability distribution.
- **Props:** `trustData` (optional), `action` (default `'BLOCK'`, **dead prop**).
- **State:** `showDetails` — toggles a chevron but **no render block reads it** (dead state, non-functional button).
- **Notable details:** Cards 3 (SDQS) and 4 (Primary Threat Vector) are **hardcoded regardless of props** (always "95.4/100" and "Account Takeover 96%") even when real data is supplied. **Currently unreachable in the running app** (same pattern — imported by `RealTimeProcessingPipeline.jsx` but never rendered).

### `web/src/components/trust/SessionTrustPassportPanel.jsx`
- **Status:** New (235 lines)
- **Purpose:** Shows the outcome of the 6-checkpoint session-trust pipeline — verdict, overall trust %, monitoring level, expiry.
- **Props:** `sessionId` (default `'SESS_9921_CRITICAL'`), `activeTxn`.
- **API calls:** `POST /session/analyse` — confirmed to exist; only network call, no embedded mock data.
- **Notable details:** **Actively wired and used** — rendered in `OperationsCenterPage.jsx`, unlike several trust-panel siblings. Clean implementation.

### `web/src/components/trust/TrustFabricLedgerBadge.jsx`
- **Status:** New (162 lines)
- **Purpose:** Compact clickable badge showing a "Trust Fabric Ledger" (Hyperledger-style) record; opens a modal with full ledger detail + chain-of-custody timeline.
- **Props:** `ledgerRecord` (optional).
- **Notable details:** **Entirely hardcoded fallback data** when no prop supplied (fabricated SHA-256, `"SIG_RSA4096_..."` signature, `block_height: 48193`, an Ethereum-style `transaction_hash` despite claiming Hyperledger Fabric, an 8-step chain-of-custody with fixed timestamps). Its only real usage path (`RealTimeProcessingPipeline` → `FusionLifecyclePipeline` → `OperationsCenterPage`) passes `evaluation?.trust_metrics?.ledger_record`, which **no confirmed `/evaluate/transaction/trust` response actually populates** — meaning this badge almost certainly always displays the fully fabricated mock record in the live app, presented as "VERIFIED"/"Cryptographic Verification PASSED."

### `web/src/components/runtime/RealTimeProcessingPipeline.jsx`
- **Status:** New (368 lines)
- **Purpose:** Renders a "Multi-Checkpoint Pre-Transaction Workflow" — a 10-stage sequential pipeline visualization for a selected sample transaction. Wrapped/re-exported unchanged by `FusionLifecyclePipeline.jsx` (see Part 6), which is what `OperationsCenterPage.jsx` actually renders.
- **Props:** `activeTxn` (only used to match a hardcoded sample by `txn_id`), `evaluation` (only `.trust_metrics?.ledger_record` read), `websocketStages` (**accepted but never referenced anywhere — dead prop**, despite `OperationsCenterPage.jsx` passing real WebSocket-streamed stage data into it).
- **State:** `selectedDataset` (**dead — no UI reads/displays it**), `selectedTxn`, `expandedStageId`, `isPlaying`/`currentStepIndex` (**both fully dead — never read or set beyond initial declaration**, remnants of an apparently unfinished play-through-animation feature).
- **API calls:** **None** — all 10 stages are computed client-side from 3 hardcoded `SAMPLE_TRANSACTIONS`.
- **Notable details:** despite the filename ("Real-Time"), everything shown is static/scripted, keyed only on which of 3 canned sample transactions is selected — not on any live `/evaluate/transaction` result or the real WebSocket pipeline-stage stream the parent page actually sends it. Imports `DecisionTrustReport`, `InvestigationTrustPanel`, `DecisionStabilityInspector` but **renders none of them** — only `TrustFabricLedgerBadge` is actually used. "Total Pipeline Latency: 0.14 ms" is a hardcoded label, not a sum of the (also hardcoded) per-stage times shown.

---

# Part 6: Frontend — Modified Components

### `web/src/App.jsx`
- **Status:** Modified (72 → 77 lines, +5/-0)
- **What changed:** two new routes registered — `analytics` → `<AnalyticsPage />`, `developer` → `<DeveloperPlatformPage />`. No existing routes touched.
- **Why:** wires the two new top-level pages into the router so the new Sidebar links resolve.

### `web/src/components/fabric/DigitalTwinBaseline.jsx`
- **Status:** Modified (60 → 324 lines, +304/-40)
- **What changed:** converted from a fully static hardcoded card into a live, API-backed, 6-tab panel (diffs/identity/devices/graph/predictions/timeline). New `fetchDigitalTwinData()` calls `GET /digital_twin/{userId}` + `POST /digital_twin/compare` in parallel. Old static `twinProfile` object and 3-card layout removed entirely.
- **Notable details:** 6 unused icon imports left over. The `/digital_twin/compare` request body is **hardcoded** to a fixed demo transaction (`amount: 750000.0`, `nameDest: "ACC_MULE_NEW"`) regardless of the actual case being viewed, since the component only receives `userId`, not a real transaction. Failed `comparison` fetches silently fall back to hardcoded `devIndex=88.5`/`CRITICAL_DEVIATION` with no visible error state.

### `web/src/components/fabric/ResponseOrchestrator.jsx`
- **Status:** Modified (102 → 300 lines, +276/-78)
- **What changed:** converted from a client-only simulated 12-step playbook (local `setTimeout` chain) to an API-driven SOAR panel — `fetchSoarRecommendation()` (`POST /response/recommend`), `handleExecutePlaybook` (`POST /response/execute`), new `handleRollback()` (`POST /response/rollback`). Old 12-card step matrix removed; replaced with 3 collapsible module cards.
- **Notable details:** 11 unused icon imports. Comment references "MODULE 3 & 5" but only one module (numbered "3.") actually exists — leftover numbering from an apparently larger unfinished layout. `handleRollback` uses a blocking `window.alert(...)`, inconsistent with the rest of the redesigned UI.

### `web/src/components/fabric/TrustFabric.jsx`
- **Status:** Modified (75 → 297 lines, +269/-47)
- **What changed:** converted from a static hardcoded hash/signature/token display into a full evidence-management panel — `fetchEvidencePackage()` (`POST /evidence/create` → `GET /evidence/verify/{id}`), `handleVerifyIntegrity` (`GET /evidence/verify/{id}`), new `handleExportBundle(format)` (`POST /evidence/export`). Old hardcoded hash/signature/token constants and always-true `isVerified` state removed. New 4-tab layout (integrity/trust_index/custody/export).
- **Notable details:** **Bug (same pattern as the quantum panel's export):** `handleExportBundle` always builds a JSON blob regardless of `format` — the "Download CERT-In PDF Compliance Bundle" and "Export Audit CSV Digest" buttons both download JSON content with a `.pdf`/`.csv` extension, not real PDF/CSV. 8 unused icon imports.

### `web/src/components/investigation/InvestigationWorkbench.jsx`
- **Status:** Modified (329 → 348 lines, +20/-1)
- **What changed:** three new panels inserted into the render tree — `<SessionTrustPassportPanel sessionId="SESS_9921_CRITICAL" .../>`, `<InvestigationIntelligencePanel caseId={caseId} .../>`, `<QuantumTrustPanel />`.
- **Real bug fix bundled in:** `<SimilarIncidentSearch activeCase={activeCaseId} />` → `activeCase={caseId}`. **`activeCaseId` was never defined anywhere in this file** (old or new version) — the previous code would have thrown `ReferenceError: activeCaseId is not defined` the moment this line rendered. This fix is bundled inside an unrelated "add three panels" commit, easy to miss in review.
- **Notable details:** `SessionTrustPassportPanel` gets a hardcoded literal `sessionId` rather than a value derived from the active case.

### `web/src/components/layout/Sidebar.jsx`
- **Status:** Modified (114 → 179 lines, +126/-61)
- **What changed:** flat 11-item nav array replaced with **4 labeled, collapsible categories**: "Pre-Transaction Security" (Mission Overview/Operations Center/Investigation Studio), "Fraud Intelligence" *(new)* (Cyber Analytics *[new route]*/Cases Workqueue/Customer Digital Twin), "Infrastructure & Tools" (Telemetry/Banking/Graph/Lab/Reports/Settings, several relabeled), "Developer Platform" *(new)* (FAT-SDK Platform *[new route]*, badge `NEW`). New `openCategories` state + `toggleCategory` handler.
- **Removed:** the `shortcut` field (`⌥1`, `⌥3`, etc.) from every nav item — **keyboard-shortcut hints are gone entirely, a UI regression** with no replacement affordance.
- **Notable details:** unused `Layers` icon import. Footer stats relabeled from real-sounding values (`SLA Latency: 48ms`, `FPR Budget: 0.48%/0.5%`) to new hardcoded literals (`Pre-Tx Pipeline: 0.14 ms`, `Decision Quality: 96.5% HIGH`) — still not wired to any live state, just renamed mock text.

### `web/src/components/runtime/FusionLifecyclePipeline.jsx`
- **Status:** Modified (89 → 12 lines, +7/-84)
- **What changed:** entire previous implementation (6-stage lifecycle tree built from `activeTxn`/`evaluation`) **deleted wholesale**. File is now a thin wrapper that just forwards `activeTxn`, `evaluation`, and a new `websocketStages` prop straight through to the new `RealTimeProcessingPipeline` component (Part 5).
- **Notable details:** a reviewer looking for the pipeline UI logic will not find it in this file anymore — it all moved to `RealTimeProcessingPipeline.jsx`, which (per Part 5) then ignores the `websocketStages` prop entirely despite `OperationsCenterPage.jsx` populating it from real WebSocket data.

---

# Part 7: Frontend — Pages (New & Modified)

### `web/src/pages/AnalyticsPage.jsx`
- **Status:** New (320 lines)
- **Purpose:** "Cybersecurity Threat Analytics & AI Model Performance" dashboard — threat vectors, fusion-model uplift metrics, geo telemetry, SHAP drivers.
- **API calls:** **None.** Zero fetch/axios calls — every number, table, and chart (`kpis`, `threatVectors`, `modelMetrics`, `hourlyVelocities`, `topOriginGeos`, `shapDrivers`) is a hardcoded local array.
- **Notable details:** `timeRange` toggle and `selectedVector` state are both decorative/dead — switching time range changes nothing. Header badge says "REAL-TIME SIEM TELEMETRY" though nothing is live. "Export CERT-In Report" button just shows a `alert(...)`, doesn't call the real `/report/cert-in` endpoint.
- **⚠ GUARDRAIL FLAG:** displays a specific headline "+38.4% Uplift" and specific PR-AUC/Recall/F1 before/after numbers that **do not correspond to anything in `ml/metrics_report.md`** — presented as if real, reproducible metrics, directly against the spirit of CLAUDE.md's "never hardcode a suspiciously round headline metric... every number must be reproducible from the code that produced it" (that rule is scoped to `ml/metrics_report.md` specifically, but this page publicly displays an equally unsupported headline number).

### `web/src/pages/DeveloperPlatformPage.jsx`
- **Status:** New (11 lines)
- **Purpose:** Thin wrapper page mounting `FATSDKDeveloperPortal` (Part 5) — establishes the `/developer` nav destination.
- **Notable details:** all API calls (`/sdk/*`) and rendering logic live in the child component; cross-checked and all endpoints exist server-side.

### `web/src/pages/CustomersPage.jsx`
- **Status:** Modified (net rewrite, +374/-72)
- **Purpose:** Customer 360 Risk Index — now searchable/filterable with a quick-preview modal.
- **What changed:** new `searchInput`/`activeQuery`/`selectedStatus`/`selectedCustomer` state, `useMemo`-filtered `filteredCustomers`. Customer records expanded with `score`, `ip`, `device`, `kyc`, `lastTxn`, `caseId`; a 5th customer added. New search bar, status pills, quick-search chips, and a "Customer 360 Preview" modal.
- **Real bug fix bundled in:** "View 360 →" now navigates to `/investigation/${c.caseId}` (per-row) instead of a single hardcoded case ID for every row.
- **Notable details:** still 100% local mock data, no backend wiring. 7 unused icon imports. `score` and `lastTxn` fields added to every record but **never rendered anywhere**.

### `web/src/pages/OperationsCenterPage.jsx`
- **Status:** Modified (+180/-155, 411 lines total)
- **Purpose:** Reframed from a generic correlation command center into a "Pre-Transaction Cyber Fraud Prevention Platform" view foregrounding session-trust and investigation-intelligence panels.
- **What changed:** new `websocketStages` state (accumulates real `pipeline_stage` WS messages, reset on `pipeline_overview`) — passed to `FusionLifecyclePipeline`. New `showSecondaryFeeds` toggle hides the raw transaction/SIEM feeds behind a collapsible accordion by default. **Removed:** `filterVerdict`/`searchQuery`/`sortBy` state and the entire transaction-queue filter/search/sort feature (not relocated — deleted outright). Removed the 4-card KPI strip and the old always-visible 3-column layout. Added new `SessionTrustPassportPanel`/`InvestigationIntelligencePanel` sections; `defaultCases` mock array shrunk from 2 entries to 1.
- **Notable details:** `quantumData` and `apiLatency` state are still fetched/computed from real calls but **no longer rendered anywhere** (their only UI consumer, the KPI strip, was deleted) — live network calls now populate dead state. A new hardcoded `"0.14 ms"` string replaces the real `apiLatency` display. Hardcoded copy ("Target Customer: Rajesh Kumar", `sessionId="SESS_9921_CRITICAL"`) will show **stale/wrong info** if a live WS-driven case for a different customer becomes active. A large batch of now-unused icon and component imports (`StatusBadge`, `RiskBadge`, `Table`, `MetricCard`, `EnterpriseBadge`, etc.) was left in from the deleted KPI/filter feature set.

### `web/src/pages/SyntheticLabPage.jsx`
- **Status:** Modified (+237/-56, 274 lines total)
- **Purpose:** Rebuilt from a "Synthetic Attack Harness" parameter-knob demo into a "Fusion Synthetic Banking Universe Generator" driving the new `/synthetic/universe/*` backend.
- **What changed:** old scenario/lead-time/fraud-ratio sliders and fake `setTimeout` status removed; new `numCustomers`/`numTransactions`/`seed` controls, `handleGenerateUniverse()` (`POST /synthetic/universe/generate` — verified param names match backend exactly), `handleDownloadExport(format)` (`GET /synthetic/universe/export/{csv,json}` — verified). New results panel shows customer/account/transaction stats and a "sample" customer table.
- **⚠ Notable / honesty concern:** the old page had an explicit **"Dataset Honesty & Methodology Notice"** panel stating plainly that no real bank/SIEM data is joined and this is a controlled synthetic harness — **this disclosure panel was removed entirely** and not replaced with anything equivalent. The new copy ("Fusion National Bank Engine," "Enterprise virtual digital bank simulator") reads as more real than it is. Also displays a static "Graph Engine Topology: Neo4j Active" label regardless of whether Neo4j is actually configured (CLAUDE.md requires graceful fallback to `networkx` and this UI doesn't reflect that). This is a soft regression against CLAUDE.md's explicit synthetic-data-honesty instruction, though no forbidden technology was introduced.

---

# Summary — Key Issues & Flags

## CLAUDE.md guardrail flags (data/metrics honesty — not "forbidden tech")
No Kafka, Flink, Go microservices, Kubernetes, Terraform, MLflow, Seldon, or federated learning was introduced anywhere in this pull — the "one FastAPI process" hard constraint is intact. The flags below are all about the **"metrics honesty" / "never present synthetic as real" rules**, not infrastructure violations:

1. **`api/synthetic_universe/graph_generator.py`** — returns fixed `louvain_modularity: 0.81`, `pagerank_max: 0.0512`, `graph_sage_embedding_dim: 64`, etc. with **zero actual graph computation** (no networkx/community/GraphSAGE import in the file at all). Directly conflicts with CLAUDE.md's explicit requirement that the graph model compute real PageRank/betweenness/Louvain centrality and that "every number must be reproducible from the code that produced it."
2. **`web/src/pages/AnalyticsPage.jsx`** — displays a headline "+38.4% Uplift" and specific PR-AUC/Recall/F1 before/after numbers with no corresponding computation anywhere and no relation to `ml/metrics_report.md`.
3. **`api/synthetic_universe/customer_generator.py` + `fraud_scenario_engine.py`** — fabricate realistic PAN numbers, Aadhaar numbers, and KYC/biometric statuses for 100+ synthetic identities with no in-code "this is fake" disclaimer, unlike `data/build_overlay.py`'s mandatory HONESTY NOTICE.
4. **`web/src/pages/SyntheticLabPage.jsx`** — the old page's explicit "Dataset Honesty & Methodology Notice" panel was deleted and not replaced, removing the one place that told a viewer this is synthetic, not real bank data.
5. **`api/ledger_service.py` / `TrustFabricLedgerBadge.jsx`** — branded as "Hyperledger Fabric v2.5" / "Raft BFT Consensus" throughout, but it's an in-process SHA-256+HMAC simulation with no real blockchain network anywhere. Not a guardrail violation (adds no new infra), but the branding overstates what it is if it reaches a judge-facing panel.

## Real bugs found (worth fixing regardless of scope)
- **`api/trust_fabric_engine.py`** — `audit_timeline`'s 8 steps are stamped with literal hardcoded date strings instead of the real computed timestamp — always shows the same fixed date.
- **`api/synthetic_universe/graph_generator.py`** — Cypher sample template mislabels every node as `Customer` regardless of actual node type.
- **Three "fake" file-export buttons** across the frontend always produce JSON content regardless of the requested format/extension: `QuantumTrustPanel.jsx` ("Export ... PDF"), `TrustFabric.jsx` ("Download CERT-In PDF" / "Export Audit CSV"). Users will get a `.pdf`/`.csv` file that's actually JSON text.
- **Fixed (bundled into unrelated commits):** `InvestigationWorkbench.jsx` had a genuine `ReferenceError: activeCaseId is not defined` bug that's now fixed; `CustomersPage.jsx`'s "View 360" link used to navigate every row to the same hardcoded case ID, now fixed to use each row's own `caseId`.

## Dead/unreachable code introduced
- `DecisionStabilityInspector.jsx`, `DecisionTrustReport.jsx`, `InvestigationTrustPanel.jsx` — all three are imported by `RealTimeProcessingPipeline.jsx` but **never actually rendered anywhere in the app**, and no other file imports them either. As shipped, these three components can never appear on screen.
- `RealTimeProcessingPipeline.jsx`'s `websocketStages` prop is threaded all the way from `OperationsCenterPage.jsx`'s real WebSocket stream through `FusionLifecyclePipeline.jsx` down to this component — and then never read. The "Real-Time Processing Pipeline" is, in the shipped code, entirely static/scripted from 3 hardcoded sample transactions.
- Several dead state variables: `isPlaying`/`currentStepIndex`/`selectedDataset` in `RealTimeProcessingPipeline.jsx`; `showDetails` in `InvestigationTrustPanel.jsx`; `quantumData`/`apiLatency` in `OperationsCenterPage.jsx` (fetched/computed from real calls but no longer displayed anywhere after the KPI strip was removed).
- Several dead imports (`api/main.py`'s `compute_investigation_trust`/`default_bank`; numerous unused lucide-react icons across `DigitalTwinBaseline.jsx`, `ResponseOrchestrator.jsx`, `TrustFabric.jsx`, `Sidebar.jsx`, `CustomersPage.jsx`, `OperationsCenterPage.jsx`, `SyntheticLabPage.jsx`).
- `api/ledger_service.py` is a new file that's never imported into `api/main.py` directly — only reachable transitively via `trust_engine.py`, which is itself unused as a direct import in `main.py` (only used via `pipeline_engine.py`).

## Removed features (not just refactored)
- `OperationsCenterPage.jsx`'s transaction-queue filter/search/sort UI (`filterVerdict`/`searchQuery`/`sortBy`) was deleted outright, not moved into the new collapsible "secondary feeds" section.
- `Sidebar.jsx`'s keyboard-shortcut hints (`⌥1`, `⌥3`, etc.) were removed with no replacement.
- `SyntheticLabPage.jsx`'s explicit synthetic-data honesty disclosure panel was removed with no replacement.

## Everything is hardcoded around one demo persona
A huge fraction of the new backend logic — across `trust_engine.py`, `session_intelligence_engine.py`, `investigation_intelligence_engine.py`, `response_orchestrator_engine.py`, `digital_twin_engine.py`, and the entire `synthetic_universe` package — branches on the same condition: `user_id == "usr_abc"` (or `cyber_compromise_in_window` truthy) triggers an identical, fully scripted "critical/compromised" response; everything else gets an identical "clean" response. None of this is model-driven or continuously scored — it's a binary lookup table tuned to make one canonical demo scenario (Rajesh Kumar / ₹7.5L transfer / Moscow login / `ACC_MULE_NEW`) look impressive. This is consistent with CLAUDE.md's "vertical slice, demo-first" philosophy, but it means almost none of these new engines would behave sensibly against a different/live transaction today.
