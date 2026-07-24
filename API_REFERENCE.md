# Fusion Risk OS API Reference

Generated from the executable FastAPI route table. Every authenticated REST response includes `X-Request-ID` and `X-Response-Time-Ms`. Pipeline responses additionally contain request, correlation, pipeline, acknowledgement, dependency status, and stage timing fields.

| Method | Route | Authentication | Roles | Consumer | Response | Errors |
|---|---|---|---|---|---|---|
| GET | `/audit/{incident_id}` | Bearer JWT | admin, analyst, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/auth/token` | Public | — | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/banking/auth/login` | Public | — | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/banking/auth/logout` | Bearer JWT | admin, customer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/banking/auth/refresh` | Public | — | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/banking/auth/register` | Public | — | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/banking/notifications` | Bearer JWT | admin, customer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/banking/profile` | Bearer JWT | admin, customer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/burst/analyse` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/device/connected` | Bearer JWT | admin, developer, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/device/pair` | Public | — | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/device/register` | Public | — | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/device/sessions` | Bearer JWT | admin, developer, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/digital_twin/compare` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/digital_twin/update` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/digital_twin/{user_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/digital_twin/{user_id}/history` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/digital_twin/{user_id}/snapshot` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/digital_twin/{user_id}/timeline` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/download/apk` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/download/sdk` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/evaluate/transaction` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/evaluate/transaction/pipeline` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/evaluate/transaction/trust` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/evidence/create` | Bearer JWT | admin, analyst, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/evidence/export` | Bearer JWT | admin, analyst, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/evidence/verify/{evidence_id}` | Bearer JWT | admin, analyst, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/evidence/{evidence_id}` | Bearer JWT | admin, analyst, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/gateway/status` | Bearer JWT | admin, analyst, developer, operator | Payment gateway | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/gateway/webhook` | Public | — | Payment gateway | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/graph/analyze` | Bearer JWT | admin, analyst, developer, operator | Pipeline / dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/graph/topology` | Bearer JWT | admin, analyst, developer, operator | Pipeline / dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/health/live` | Public | — | Operations | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/health/ready` | Public | — | Operations | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/incident/assign` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/incident/{incident_id}` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/investigation/analyse` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/investigation/{case_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/metrics/cost` | Bearer JWT | admin, analyst, developer, operator | Dashboard / QA | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/metrics/evaluate` | Bearer JWT | admin, analyst, developer, operator | Dashboard / QA | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/metrics/threshold_sweep` | Bearer JWT | admin, analyst, developer, operator | Dashboard / QA | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/mule/discover` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/platform/status` | Bearer JWT | admin, analyst, developer, operator | Operations | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/playbook` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/playbook/create` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/quantum/analyze` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/assessment` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/compliance` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/dashboard` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/inventory` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/posture` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/readiness` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/quantum/recommendations` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/quantum/simulate` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/report/cert-in` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/response/execute` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/response/recommend` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/response/rollback` | Bearer JWT | admin, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/scenarios/generate/{scenario_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/scenarios/list` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/apps` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/sdk/device` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/error-codes` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/sdk/event` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/events` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/health` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/sdk/network` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/passport` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sdk/policies` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/sdk/request-decision` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/sdk/session/start` | Bearer JWT | admin, developer, sdk | Android / Fusion SDK | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/session/analyse` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/session/passport/{session_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/session/recalculate` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/session/update` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sessions` | Bearer JWT | admin, analyst, operator, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/sessions/{session_id}` | Bearer JWT | admin, analyst, operator, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| DELETE | `/synthetic/universe/clear` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/synthetic/universe/create_bank` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/export/csv` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/export/json` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/export/parquet` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/export/replay` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/synthetic/universe/generate` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/synthetic/universe/pause` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/preview` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/synthetic/universe/resume` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/synthetic/universe/start_scenario` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/synthetic/universe/stats` | Bearer JWT | admin, developer | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/threats` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/threats/device/{device_id}` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/threats/evaluate` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/threats/session/{session_id}` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/threats/simulate` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/threats/{threat_id}` | Bearer JWT | admin, analyst, developer, operator, sdk | Pipeline / threat dashboard | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/trust-components/{session_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/trust-history/{session_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/trust-passport` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/trust-passport/{session_id}` | Bearer JWT | admin, analyst, developer, operator | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| GET | `/trust/live` | Bearer JWT | admin, analyst, operator, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| POST | `/trust/recalculate` | Bearer JWT | admin, analyst, operator, sdk | Dashboard / operator API | JSON or declared media type | 4xx validation/auth; 5xx sanitized |
| WS | `/ws/stream` | JWT query/header | admin, analyst, developer, operator, sdk | Android / dashboard | connection_ack + pipeline_decision | 4401 auth; 4403 ownership |

## Latency contract

- HTTP wall time: `X-Response-Time-Ms`.
- Pipeline stage times: `timings.normalization_and_ingest_ms`, `threat_engine_ms`, `graph_engine_ms`, `model_or_fallback_ms`, and `total_ms`.
- WebSocket delivery is measured by comparing the pipeline timestamp to client receipt time.

## Error contract

Authentication middleware returns `{"error":{"code":"AUTHORIZATION_FAILED","message":"…","request_id":"…"}}`. Pydantic validation returns HTTP 422. Unavailable model and graph dependencies are represented in successful pipeline responses with explicit status/error fields rather than fabricated values.
