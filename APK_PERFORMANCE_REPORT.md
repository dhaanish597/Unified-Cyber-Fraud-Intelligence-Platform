# APK / API Performance Report

Measurement date: 2026-09-29

## Measurement method

Local FastAPI `TestClient`, 20 sequential requests per endpoint, Windows development environment. These are local harness measurements, not production or physical-device latency.

| Endpoint | Min | Median | Max | Samples |
|---|---:|---:|---:|---:|
| `GET /health/live` | 6.90 ms | 8.52 ms | 46.98 ms | 20 |
| `POST /device/pair` | 8.02 ms | 9.25 ms | 13.05 ms | 20 |

## Findings

- Pairing record creation is lightweight and does not perform network or database I/O.
- Android startup initializes encrypted storage, Retrofit, Room, attestation, queue management, and WebSocket state eagerly.
- SDK session startup currently sequences device registration, session creation, WebSocket connection, telemetry initialization, and initial event emission. The sequence is correctness-sensitive; no optimization is applied without device timing evidence.
- Web Operations Center polls device/session data while also using WebSocket streaming. This is potentially redundant but needs event freshness measurements before changing.
- WebSocket reconnect is now bounded to five attempts with exponential delays of 1, 2, 4, 8, and 16 seconds; duplicate scheduled reconnects are suppressed.
- No production, emulator, or physical-device latency measurements are available.

## Recommended next measurements

1. Cold-start and warm-start Android timings from process launch to shell and authenticated home.
2. QR scan-to-`connection_ack` timings across five physical runs.
3. Render API p50/p95 for pairing, device registration, session start, and WebSocket upgrade.
4. Operations Center polling/WebSocket event freshness and duplicate request count.
5. Telemetry batch size, queue flush time, and offline recovery duration.

No latency numbers beyond the local harness above should be used in product or investor material.
