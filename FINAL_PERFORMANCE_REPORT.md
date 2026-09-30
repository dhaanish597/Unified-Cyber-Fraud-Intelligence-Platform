# Final Performance Report

Date: 2026-09-30

## Measured locally

Harness: local FastAPI `TestClient`, 20 sequential requests, Windows development environment. These are not production or device measurements.

| Endpoint | Min | Median | Max | Samples |
|---|---:|---:|---:|---:|
| `GET /health/live` | 6.90 ms | 8.52 ms | 46.98 ms | 20 |
| `POST /device/pair` | 8.02 ms | 9.25 ms | 13.05 ms | 20 |

## Source findings

- SDK startup initializes storage, Room, attestation, queue, and WebSocket state eagerly.
- Session startup sequences device registration, session creation, WebSocket connection, telemetry setup, and initial event emission for correctness.
- Operations Center combines polling with WebSocket updates; freshness and duplicate-request measurements are still required before changing it.
- WebSocket reconnect is bounded to five attempts with 1/2/4/8/16 second delays.
- QR scanning now has a bounded 30-second capture window and does not send duplicate callbacks within the debounce window.

## Required device/deployment measurements

- Cold/warm Android startup.
- Camera-open and scan detection latency.
- Scan-to-assessment latency.
- Scan-to-WebSocket `connection_ack` latency.
- Render p50/p95 for registration/session/analysis.
- Operations Center event freshness.
- Offline queue flush and reconnect duration.

No unmeasured production latency is claimed.
