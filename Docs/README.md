# Docs

> Note: Windows filesystems are case-insensitive, so this single `Docs/` directory serves as both
> the `/docs` the build brief asks for (architecture, demo script, metrics, PS2 coverage) and the
> home for the original source briefing materials — there is no separate `docs`/`Docs` split on disk.

## `source/` — original briefing materials (read-only reference)
- `CLAUDE_CODE_PROMPTS.md` — the phase-by-phase Claude Code prompt sequence this build follows.
- `MANUAL_SETUP.md` — the manual checklist (Kaggle token, Neo4j Aura, hackathon registration).
- `finspark_build_roadmap.html` — the 5-day sprint roadmap, scope table, demo script, Q&A prep.
- `Finspark_Hackathon_2026_Unified_Cyber-Fraud_Platform.pdf`, `Unified Cyber-Fraud Platform Research.pdf`,
  `Securing Future Banking Security.pdf` — hackathon problem statement and research dossiers.

## Build docs (this build's deliverables, written as the sprint progresses)
- `architecture.md` + a mermaid diagram distinguishing the built slice from the deck-only
  production layer (Kafka/Flink/K8s/federated learning — never built, always described).
- `demo_script.md` (Day 4 deliverable) — the exact voiceover lines and on-screen T-values for the
  90-second killer demo.
- `ps2_coverage.md` (Day 5 deliverable) — maps each PS2 expected outcome to the exact UI element /
  endpoint that satisfies it.
- Links to `/ml/metrics_report.md` for the honest PR-AUC/F1/confusion-matrix numbers and the
  fusion-uplift headline.

See root `CLAUDE.md` for the mission and scope guardrails.
