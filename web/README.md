# /web

React + Vite + Tailwind dashboard — the dark "single pane of glass" SOC UI.

Planned layout:
- KPI header: TPS ticker, threat level, ₹ intercepted / 24h.
- Three-column live view: SIEM timeline (left), transaction ledger (right), fused score + verdict
  badge (center, color-coded ALLOW=green / CHALLENGE=amber / BLOCK=red).
- Threat Graph Visualizer (`react-force-graph-2d`): click a mule node to expand linked
  devices/IPs/destination accounts.
- XAI panel: SHAP top features (bar list) + a single prominent counterfactual sentence.
- Quantum tab: posture gauge (% quantum-vulnerable) + HNDL alert row.
- Connects to `/ws/stream` on the API so the whole view animates from the replay stream.

Not yet scaffolded with Vite — that happens when frontend work starts (Day 3 of the sprint).
