# FinSpark'26 — Claude Code Build Prompts

**Project:** Unified Cyber-Fraud Intelligence Platform (Bank of Maharashtra, PS2)
**Goal:** ship a working *vertical slice* that proves cyber-fraud fusion catches an in-flight fraud each silo would miss.
**Prototype due:** 16 Jul 2026.

---

## How to use this file

1. Do the one-time steps in `MANUAL_SETUP.md` **first** (datasets, Kaggle key, Neo4j, tools). Claude Code can't do those.
2. Open a terminal in an empty project folder and run `claude`.
3. Paste **Prompt 0** first. Let it finish, review the diff, commit.
4. Then paste **one phase prompt per sprint day**, in order. Review + commit after each.
5. Golden rule for driving Claude Code here: **one phase at a time, commit between phases, and push back the moment it starts building Kafka/Flink/Kubernetes.** Those are deck-only.

> Tip: after each phase, tell Claude Code `commit this with a clear message` and `run it end to end and show me the output` before moving on. Never let a broken phase roll into the next.

---

## PROMPT 0 — Bootstrap the repo + the mission file

```
You are helping me build a hackathon prototype in 5 days. Before writing any code, read this brief carefully and create a CLAUDE.md at the repo root capturing it, so you keep the constraints in mind for the whole build.

MISSION (the one sentence we win on):
"A SIEM sees the stolen login. A fraud engine sees the transfer. Neither sees they're the same attack 40 seconds apart. Our platform fuses them into one graph and blocks the transfer while it's still in flight."

WHAT WE ARE BUILDING: a single-machine, demo-able vertical slice of a Unified Cyber-Fraud Intelligence Platform for a bank. It fuses (a) a tabular fraud model, (b) a graph model, and (c) a cyber-context rule into one risk engine that returns ALLOW / CHALLENGE / BLOCK with human-readable reasons, shown on a dark "single pane of glass" SOC dashboard.

HARD SCOPE RULES (write these into CLAUDE.md as guardrails):
- BUILD (must run live): fusion overlay data generator; tabular fraud model (XGBoost/LightGBM + SMOTE); graph model (GraphSAGE embeddings + centrality); anomaly model (Isolation Forest); fusion risk engine; FastAPI service with /evaluate + WebSocket replay; React dashboard with SIEM timeline + ledger + fused score + XAI panel + threat graph; mini Quantum Risk Monitor; one-click CERT-In incident PDF.
- DO NOT BUILD (deck/vision only, never write this code): Kafka, Flink, Go microservices, Kubernetes, Terraform, MLflow, Seldon, federated learning. If you think we need any of these, stop and tell me instead of building it.
- "Streaming" = a Python script that replays events from a CSV over a WebSocket at demo speed. No real message broker.
- Metrics honesty is a scoring criterion: never report accuracy on the imbalanced set. Always PR-AUC, F1, recall at a fixed low false-positive rate, and a confusion matrix.

TECH STACK:
- ML/graph: Python 3.11+, pandas, scikit-learn, xgboost + lightgbm, imbalanced-learn (SMOTE), PyTorch Geometric (GraphSAGE), shap, Isolation Forest.
- Backend: one FastAPI process (POST /evaluate/transaction, WebSocket for the stream, report + quantum endpoints). No microservices.
- Frontend: React + Vite + Tailwind; graph viz via react-force-graph-2d; charts via recharts; dark SOC theme (red/amber/green severity).
- Graph store: Neo4j Aura Free if a connection string is in .env, otherwise fall back to networkx in-memory. Detect and degrade gracefully.

TASKS FOR THIS PROMPT (bootstrap only — no models yet):
1. Create CLAUDE.md with the mission, scope rules, and stack above.
2. Scaffold this monorepo layout with placeholder READMEs in each:
   /data (download + fusion overlay generator), /ml (training + saved models + metrics),
   /graph (schema, GraphSAGE, embedding export), /api (FastAPI, risk engine, XAI, CERT-In),
   /web (React dashboard), /docs (architecture, demo script, metrics).
3. Create a Python virtual environment setup, a requirements.txt with the ML/API deps pinned to known-good recent versions, and a .env.example with placeholders for NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD (no real secrets).
4. Write /data/download.py: a script that pulls PaySim, IEEE-CIS, and Elliptic via the Kaggle API into /data/raw, and reads a local UNSW-NB15 CSV if present. Assume `kaggle` CLI is configured; print clear instructions if it isn't. Do NOT hardcode or ask me for my Kaggle token.
5. Add a .gitignore that excludes /data/raw, /data/processed, model binaries, node_modules, .env, and venvs.
6. Initialize git and make the first commit.

Do not download data or train anything yet. Stop after the scaffold and show me the tree.
```

---

## PROMPT 1 — Day 0 (Jul 11): the fusion overlay generator ★

> This is the day's real deliverable. If only one thing works today, it's this.

```
Now build the fusion overlay generator — the core innovation. No public dataset links a user's cyber/login events to their fraud transactions; that gap IS the market gap, so we synthesize the link as a controlled evaluation harness.

Write /data/build_overlay.py that does the following and is fully reproducible (fixed random seed, config at top):

1. Load PaySim from /data/raw. Keep it manageable (sample if needed) and focus on TRANSFER + CASH_OUT rows where fraud concentrates. Preserve the isFraud label.
2. Assign each transaction a synthetic user_id, device_id, and ip. Deliberately SHARE some devices/IPs across a small set of users to create mule-ring structure (e.g. ~6-account clusters sharing a device).
3. Generate a per-user cyber event log (fused_events.csv): mostly normal logins, plus injected compromise sequences inspired by UNSW-NB15 attack patterns — impossible-travel login, new-device + MFA-cookie reuse, credential-stuffing success. Each event has: timestamp, user_id, device_id, ip, event_type, geo (lat/lon or km-from-baseline), severity.
4. For a chosen slice of the FRAUD transactions, place a compromise event 30–120 seconds BEFORE the fraudulent transfer. Leave the rest of the frauds without a preceding cyber signal (so fusion uplift is measurable, not universal).
5. Emit a fused label / feature: for every transaction, compute `cyber_compromise_in_window` = True if a compromise event for that user fired within a configurable pre-window (default 300s) before the transaction.
6. Output to /data/processed: transactions.csv (with user/device/ip + the cyber-context feature) and fused_events.csv (the SIEM feed). Also write a small overlay_report.md summarizing: how many frauds are cyber-preceded, mule cluster count, event-type distribution.

Then write a tiny sanity check that prints, for the tabular label alone vs. tabular+cyber-context, how separable the cyber-preceded frauds are — this previews the "fusion uplift" story.

Keep everything honest and documented: a comment block at the top must state plainly that this is a synthetic correlation harness, not real joined bank data. Commit when green.
```

---

## PROMPT 2 — Day 1 (Jul 12): tabular + anomaly models, honest metrics

```
Build the tabular fraud model and the anomaly model on /data/processed/transactions.csv. All work goes in /ml.

1. Feature engineering (/ml/features.py): velocity (txns per user per time window), balance deltas (orig/dest before-after), time-since-last-txn per user, log-scaled amount, transaction-type encoding. Keep the cyber-context feature available but ALSO train a "tabular-only baseline" that excludes it, so we can measure fusion uplift later.
2. Train/test split that is time-aware or at least user-disjoint to avoid leakage. Apply SMOTE to the TRAINING SPLIT ONLY — never the test set.
3. Train an XGBoost and a LightGBM classifier; pick the stronger by PR-AUC. Save the model to /ml/models.
4. Train an Isolation Forest for zero-day / unseen-pattern scoring; save it. Expose a function that returns an anomaly score for a transaction.
5. Produce /ml/metrics_report.md: PR-AUC, F1, recall at a FIXED low FPR (e.g. 0.5%), and the confusion matrix — for the model. Include one paragraph I can read aloud to defend each number. Explicitly note why accuracy is meaningless on a ~0.13% fraud rate.
6. Save a reusable /ml/predict.py exposing: tabular_score(txn) and anomaly_score(txn), loading the saved models.

No dashboards, no API yet. End with the metrics_report.md printed and models saved. Commit.
```

---

## PROMPT 3 — Day 2 (Jul 13): graph model + the fusion risk engine

> By end of today, **all ML is done.** Everything after is what judges see.

```
Two deliverables today: the graph model, and the fusion risk engine that ties everything together.

GRAPH (/graph):
1. Load the Elliptic Bitcoin dataset and train a GraphSAGE model in PyTorch Geometric to produce node embeddings and licit/illicit classification. Save embeddings + a short metrics note. GraphSAGE is inductive — note in comments that new nodes get embeddings without full retraining (we'll cite this in Q&A).
2. Separately, build the account/device/IP graph from /data/processed (Neo4j Aura if .env has creds, else networkx). Compute centrality features per entity: PageRank, betweenness, and Louvain community id. Export a lookup: entity -> {centrality features, community, mule_cluster_flag}.

FUSION RISK ENGINE (/api/risk_engine.py — pure Python module, no web yet):
3. Implement evaluate(transaction) -> {score 0-100, action, reasons[]} where:
   - score blends: tabular_score, anomaly_score, graph/centrality features for the txn's entities, and the cyber-context rule (compromise_in_window) with a meaningful weight.
   - action thresholds: ALLOW / CHALLENGE / BLOCK.
   - reasons[] are human-readable strings ("Login IP 2,000 km from baseline 40s prior", "Beneficiary shares device with 6 flagged accounts").
4. Add a counterfactual: recompute the score with the cyber-context set to False and return the alternate action, so the engine can say "with no prior cyber compromise, score = 61 -> CHALLENGE, not BLOCK."
5. Compute and save the FUSION UPLIFT metric into /ml/metrics_report.md: recall on cyber-preceded frauds for the tabular-only baseline vs. the full fused engine, at the SAME false-positive rate. This delta is our headline number.

Run the engine over a batch of transactions to prove it works, print a few sample verdicts + reasons, and confirm the uplift number is positive. Commit.
```

**⚠ Also today, 7:00–8:00 PM: Mentoring Session 2.** Bring these three questions (from the roadmap):
1. Is a synthetic cyber-fraud correlation overlay acceptable as our evaluation harness?
2. Which compliance hook impresses the jury most — CERT-In auto-report or DPDP consent?
3. For the finale: live demo or recorded?

---

## PROMPT 4 — Day 3 (Jul 14): API + dashboard + XAI (the single pane of glass)

> ML is frozen. Tonight is frontend, **not** model debugging. (MSME hackathon also submits today — that's why ML was front-loaded.)

```
Wire the engine to a FastAPI service and build the React dashboard. This is the part judges actually see, so make it crisp.

BACKEND (/api):
1. FastAPI app exposing:
   - POST /evaluate/transaction -> action, score, reasons[], SHAP top features, counterfactual sentence.
   - WebSocket /ws/stream -> replays events from a CSV (transactions + interleaved cyber events) at demo speed, emitting typed messages the UI can render on a SIEM timeline and a ledger.
2. Compute SHAP values for the tabular model per decision and return the top contributing features with signed impact.
3. CORS open for local dev. Keep it ONE process.

FRONTEND (/web) — React + Vite + Tailwind, dark SOC theme:
4. KPI header: TPS ticker, threat level, ₹ intercepted / 24h.
5. Three-column live view: SIEM timeline (left), transaction ledger (right), fused score + verdict badge (center, big, color-coded ALLOW/CHALLENGE/BLOCK).
6. Threat Graph Visualizer (react-force-graph-2d): click a mule node -> expand linked devices / IPs / destination accounts.
7. XAI panel: SHAP top features as a small bar list + the single counterfactual sentence rendered prominently.
8. Connect to the WebSocket so the whole view animates from the replay stream.

Get one full transaction to flow: replay -> /evaluate -> verdict + reasons + SHAP + counterfactual on screen. End with the app running locally (give me the two commands to start api and web). Commit.
```

---

## PROMPT 5 — Day 4 (Jul 15): quantum monitor + CERT-In report + the killer demo

```
Add the two "banker wow" features and script the 90-second demo.

QUANTUM RISK MONITOR (/api + /web):
1. Backend endpoint /quantum/posture: given TLS handshake records (use a small bundled sample CSV of cipher suites), classify each as quantum-vulnerable (RSA / plain ECDHE) vs hybrid/PQC (ML-KEM). Return the % vulnerable and flag any "long-lived sensitive data over vulnerable cipher" as a Harvest-Now-Decrypt-Later (HNDL) risk.
2. Frontend "Quantum" tab: a posture gauge (% quantum-vulnerable) + an HNDL alert row.

CERT-In REPORT (/api):
3. POST /report/cert-in: given an incident id, generate a structured incident PDF (reportlab or weasyprint) with timestamp, affected user, the fused reasons, and a note that it's within the 6-hour CERT-In reporting mandate. Wire a one-click "Generate CERT-In report" button in the UI that downloads it.

THE KILLER DEMO (/docs/demo_script.md + a scripted replay CSV):
4. Build the demo replay dataset so this exact sequence fires on one keypress:
   T-0:00 calm, dashboard green.
   T+0:00 SIEM: impossible-travel login + new device for usr_abc.
   T+0:40 same user starts a ₹7,50,000 UPI transfer to a brand-new beneficiary.
   T+0:41 FUSION -> BLOCK, score jumps to ~94, threat graph auto-expands the 6-account mule cluster.
   T+0:55 XAI + counterfactual ("with no prior cyber compromise, score = 61 -> CHALLENGE").
   T+1:10 one-click CERT-In report.
   T+1:25 quantum tab shows this session used ECDHE, flagged HNDL.
5. Write /docs/demo_script.md with the exact voiceover lines and the on-screen T-values.

Run the full scripted scenario end to end and confirm every beat lands. Commit.
```

**Also today (manual):** record a steady 3-minute screen-capture demo video with voiceover as your safety net.

---

## PROMPT 6 — Day 5 (Jul 16): README, polish, submission prep

```
Final hardening pass — no new features.

1. Write a top-level README.md: one-paragraph pitch, the architecture diagram (generate a clean mermaid diagram in /docs showing the built slice vs. the deck-only production layer), and copy-paste "how to run" instructions (data -> overlay -> train -> api -> web).
2. Generate a /docs/ps2_coverage.md that maps each PS2 expected outcome to the exact UI element / endpoint that satisfies it (this becomes a deck slide).
3. Clean the repo: remove dead code, ensure .env is gitignored and no secrets are committed, confirm requirements install from clean, confirm `npm install && npm run dev` works from scratch.
4. Verify the metrics_report.md has the fusion-uplift headline number and honest PR-AUC/F1/confusion matrix, linkable from the deck.
5. (Optional) Add deploy config: a Dockerfile or render.yaml for the API and instructions to deploy /web to Vercel. Do NOT deploy for me or enter any credentials — just prepare the config and tell me the exact commands to run.

Print a final submission checklist and confirm everything runs from a clean clone. Commit and tag v1.0.
```

---

## Working notes for driving Claude Code

- **Commit between every phase.** If a phase goes sideways, `git reset` is your friend.
- **If it stalls on data size:** tell it to sample PaySim (e.g. 1–2M rows) — the demo doesn't need all 6.3M.
- **If Neo4j Aura setup eats time:** say `skip Neo4j, use the networkx fallback` — the roadmap explicitly allows this.
- **If GraphSAGE training is slow:** say `use precomputed Elliptic embeddings and networkx centrality; skip live GNN training in the demo path`.
- **Keep it honest:** if Claude Code ever writes a hardcoded "99.4%" or accuracy headline, stop it. Your metrics must be defensible line-by-line.
- **Protect the demo:** anything that doesn't make the 90-second demo more convincing goes in the deck's "describe" column, not the codebase.
