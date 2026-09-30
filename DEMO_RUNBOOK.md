# Demo Runbook (Current State)

This runbook is intentionally marked not-ready for the requested QR-bootstrap demo. It documents the verified current path and the checks required before claiming readiness.

## Current source-backed path

1. Deploy backend with valid production JWT, banking-user, SDK-client, tenant, CORS, and database settings.
2. Deploy web with `FUSION_API_BASE` pointing to the backend and dashboard client credentials configured only in Vercel.
3. Open Developer Platform and verify the visible `API_BASE` resolves to the backend, not the Vercel static host.
4. Generate a five-minute QR.
5. Scan it with the updated APK. Pairing now performs SDK session creation and waits for authenticated WebSocket connection before showing success.
6. Verify `/sdk/device`, `/sdk/session/start`, WebSocket `connection_ack`, device/session rows, and live events.

## Required pre-demo gates

- Fix and test QR-to-authenticated-session bootstrap.
- Add the pairing/auth screens to the active navigation state machine.
- Verify Android release URLs are the production backend and WSS endpoint.
- Repair the backend test environment and run the pairing regression suite.
- Run expiry, replay, wrong tenant/environment, invalid token, network interruption, retry, logout, relogin, and existing-session cases.
- Run the physical flow five times and record status, latency, and failure point.

## Do not claim

Do not claim the APK is fixed or demo-ready until the physical QR -> authentication -> device registration -> session -> WebSocket -> authenticated home flow succeeds end to end.
