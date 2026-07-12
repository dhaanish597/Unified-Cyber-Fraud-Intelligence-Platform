# Unified Cyber-Fraud Intelligence Platform — FinSpark'26 (Bank of Maharashtra, PS2)

**Prototype due:** 16 Jul 2026. **Today:** 12 Jul 2026 (Day 1 of the 5-day sprint). **Finale:** COEP Pune, 25–26 Jul 2026.

## Mission (the one sentence we win on)

> "A SIEM sees the stolen login. A fraud engine sees the transfer. Neither sees they're the same
> attack 40 seconds apart. Our platform fuses them into one graph and blocks the transfer while
> it's still in flight."

## What we are building

A single-machine, demo-able **vertical slice** of a Unified Cyber-Fraud Intelligence Platform for a
bank. It fuses (a) a tabular fraud model, (b) a graph model, and (c) a cyber-context rule into one
fusion risk engine that returns **ALLOW / CHALLENGE / BLOCK** with human-readable reasons, shown on
a dark "single pane of glass" SOC dashboard.

We are judged on whether one fused, explainable, quantum-aware demo convinces a room of bankers and
security leaders — not on a 12-month enterprise platform. Build the slice that produces the 90-second
demo (see `docs/demo_script.md` once written); keep the rest of the architecture in the deck as vision.

## Hard scope rules — guardrails, do not violate

### BUILD (must run live, in this repo)
- Fusion overlay data generator (`/data/build_overlay.py`) — the core, defensible innovation.
- Tabular fraud model: XGBoost/LightGBM + SMOTE (training split only).
- Graph model: GraphSAGE embeddings (PyTorch Geometric, on Elliptic) + centrality (PageRank,
  betweenness, Louvain community) on the account/device/IP graph.
- Anomaly model: Isolation Forest for zero-day / unseen-pattern scoring.
- Fusion risk engine that blends all of the above into a score + ALLOW/CHALLENGE/BLOCK + reasons[].
- FastAPI service: `POST /evaluate/transaction` + WebSocket replay stream + report + quantum endpoints.
  **One process. No microservices.**
- React dashboard: SIEM timeline, transaction ledger, fused score + verdict badge, XAI panel
  (SHAP + counterfactual sentence), threat graph visualizer.
- Mini Quantum Risk Monitor (TLS cipher-suite posture, HNDL flag).
- One-click CERT-In incident PDF report.

### DO NOT BUILD (deck/vision only — never write this code)
Kafka, Flink, Go microservices, Kubernetes, Terraform, MLflow, Seldon, federated learning.
**If you think we need any of these, stop and tell the user instead of building it.**

### Definitions that matter
- **"Streaming"** = a Python script that replays events from a CSV over a WebSocket at demo speed.
  There is no real message broker anywhere in this repo.
- **Graph store**: Neo4j Aura Free if a connection string is present in `.env`; otherwise fall back
  to `networkx` in-memory. Code must detect the absence of credentials and degrade gracefully —
  never hard-fail because Neo4j isn't configured.
- **Metrics honesty is a scoring criterion.** Never report plain accuracy on the imbalanced fraud
  set (fraud is ~0.13% of PaySim — a do-nothing model scores ~99.8% "accuracy" and that number is
  meaningless). Always report **PR-AUC, F1, recall at a fixed low false-positive rate** (e.g. 0.5%),
  and a **confusion matrix**. The headline number is the **fusion uplift**: recall on cyber-preceded
  frauds, tabular-only baseline vs. the fused engine, at the same FPR.
- Never hardcode a suspiciously round headline metric (e.g. "99.4% accuracy"). Every number in
  `ml/metrics_report.md` must be reproducible from the code that produced it.

## Tech stack

- **ML/graph:** Python 3.11+ (3.13 available locally), pandas, scikit-learn, xgboost, lightgbm,
  imbalanced-learn (SMOTE), PyTorch Geometric (GraphSAGE), shap, Isolation Forest.
- **Backend:** one FastAPI process — `POST /evaluate/transaction`, WebSocket stream, CERT-In report
  endpoint, quantum posture endpoint. No microservices.
- **Frontend:** React + Vite + Tailwind; graph viz via `react-force-graph-2d`; charts via `recharts`;
  dark SOC theme (red = BLOCK, amber = CHALLENGE, green = ALLOW).
- **Graph store:** Neo4j Aura Free if `.env` has creds, else `networkx` in-memory fallback.

## Repo layout

```
/data   — download.py (Kaggle pulls) + build_overlay.py (the fusion overlay generator) + raw/processed data (gitignored)
/ml     — feature engineering, training, saved models (gitignored binaries), metrics_report.md
/graph  — schema, GraphSAGE training, centrality computation, embedding export
/api    — FastAPI app, risk_engine.py, XAI (SHAP), CERT-In report generator
/web    — React + Vite + Tailwind dashboard
/Docs   — architecture diagram, demo_script.md, metrics, PS2 coverage checklist, PLUS the
          original source briefing materials under Docs/source/ (see Docs/README.md)
```

> Naming note: this repo lives on a case-insensitive Windows filesystem, so `docs` and `Docs` are
> the same directory on disk. The brief's `/docs` and the pre-existing `/Docs` (source PDFs) are
> unified as `/Docs`, with source material moved to `Docs/source/`. Always write build docs
> (architecture, demo script, metrics, PS2 coverage) directly under `Docs/`, not `Docs/source/`.

## Datasets

- **PaySim** (`ealaxi/paysim1`) — transaction backbone; fraud concentrated in TRANSFER + CASH_OUT.
- **IEEE-CIS Fraud** (`ieee-fraud-detection`, competition dataset) — real device/identity features.
- **Elliptic Bitcoin** (`ellipticco/elliptic-data-set`) — graph model (GraphSAGE) training.
- **UNSW-NB15** — cyber-intrusion patterns for the injected compromise events; not always API-pullable,
  may need to be dropped into `/data/raw` manually by the user. CICIDS2017 is an acceptable substitute.

The fusion overlay (linking a user's cyber events to their fraud transactions) does not exist in any
public dataset — that gap is the market gap. We synthesize it as a **controlled evaluation harness**
and say so explicitly in code comments and to judges. Never present it as real joined bank data.

## Working agreement for this build

- One phase at a time. Commit between phases with a clear message.
- Never let a broken phase roll into the next — run it end to end and confirm before moving on.
- If Neo4j Aura setup eats time: skip it, use the `networkx` fallback — this is explicitly allowed.
- If GraphSAGE training is slow: use precomputed Elliptic embeddings + networkx centrality; skip
  live GNN training in the demo path.
- If PaySim is unwieldy: sample it (e.g. 1–2M rows) — the demo doesn't need all 6.3M rows.
- Anything that doesn't make the 90-second demo more convincing belongs in the deck's "describe"
  column, not in this codebase.
- Do not download datasets, train models, log into external services, or deploy anything without
  being asked — those are explicit, separate steps.
