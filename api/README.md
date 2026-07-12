# /api

Single FastAPI process — no microservices.

- `risk_engine.py` (not yet written) — pure Python fusion module: `evaluate(transaction) ->
  {score, action, reasons[]}`, blending tabular score, anomaly score, graph/centrality features, and
  the cyber-context rule (compromise-in-window). Includes a counterfactual recomputation.
- FastAPI app exposing:
  - `POST /evaluate/transaction` — action, score, reasons, SHAP top features, counterfactual sentence.
  - `WebSocket /ws/stream` — replays events from a CSV at demo speed (this is what "streaming" means
    in this repo — no Kafka/Flink).
  - Quantum posture endpoint (TLS cipher-suite classification, HNDL flag).
  - CERT-In incident report endpoint (structured PDF).

See root `CLAUDE.md` for the "one process, no microservices" and streaming-definition rules.
