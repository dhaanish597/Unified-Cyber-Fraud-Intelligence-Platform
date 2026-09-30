# Fusion Final System Audit

Audit date: 2026-09-30

Scope: current working tree, Android application and SDK, FastAPI backend, Vercel web client, SafeCheck, QR pairing, telemetry, synthetic transaction, and report paths. Existing unrelated working-tree changes were preserved.

## Existing architecture

- Android application: Kotlin/Compose under `fusion-reference-bank/app`, application ID `com.fusionbank.mobileapp`, debug suffix `.debug`.
- SDK: singleton `Fusion` owns Retrofit/OkHttp transport, encrypted token storage, device attestation, session lifecycle, telemetry, offline queue, and `FusionWebSocketManager`.
- Backend: FastAPI in `api/main.py`, platform security middleware, JWT validation, tenant/role authorization, SQLite-backed generic store, pairing registry, event broker, telemetry/risk pipeline, synthetic universe, and report endpoints.
- Web: React/Vite Operations Center in `web/src`; deployment uses Vercel for the dashboard and Render for the API/WebSocket service.
- QR library: JourneyApps ZXing Android Embedded `4.3.0`. The current SafeCheck screen uses its real `ScanContract`; it is not a mocked payload generator.

## Current working flows

### Pairing and session

Operations Center creates a short-lived, one-time pairing record. The QR includes backend/WSS endpoints, pair ID, bootstrap token, tenant, environment, and expiry. Android validates the payload, calls `/device/register`, persists the scoped SDK JWT in encrypted storage, registers the device/session, opens the authenticated WebSocket using `Bearer.<JWT>`, and only then transitions past the pairing gate.

### SafeCheck

The current Android SafeCheck screen launches the JourneyApps camera scanner, submits the decoded payload to `POST /risk/qr/analyze`, renders parsed details/signals/risk/confidence, and can submit `POST /reports/payment-identifier`. The backend stores tenant-scoped assessments and emits `QR_RISK_ASSESSMENT`; the Operations Center consumes assessment events and can query `GET /risk/qr/assessments`.

### Synthetic transaction and telemetry

The existing transfer/synthetic paths use `Fusion.reportEvent`, SDK telemetry, the platform event broker, and the existing transaction/risk pipeline. They do not execute UPI or bank transfers. Existing UI surfaces label synthetic/development data in several places.

### Reports

The web Reports page reads backend report data, caches the last successful result in session storage, retries, and provides empty/error states. The backend includes existing incident/report paths plus the RRR report path. Some RRR repository fixtures are explicitly mock/demo data and are not evidence of a real investigation.

## Current broken or incomplete flows

1. SafeCheck has a real camera intent, but the app manifest does not explicitly declare `CAMERA`, and the screen has no explicit permission-denied/permanently-denied UI or settings recovery path.
2. A decoded QR is analyzed immediately. There is no review step between capture and backend analysis, so the user cannot inspect parsed details before analysis.
3. The Android screen does not apply a client-side payload length/scheme guard or duplicate-scan debounce before sending untrusted data to the backend.
4. Camera lifecycle behavior is delegated to the external scanner activity; explicit timeout, cancellation, and camera-unavailable messages are not surfaced by the SafeCheck UI.
5. Backend pairing/device/session registries are process-local. Restart durability and multi-instance deployment correctness are not established.
6. No connected Android device/emulator, deployed Render trace, Vercel trace, or five-run QR/WebSocket evidence is present in the repository.
7. Android unit test sources and physical/integration test harnesses for camera and pairing are absent.

## Security findings

- Pairing credentials are short-lived and single-use, with tenant/environment validation. Replay is rejected in the current backend seam tests.
- JWT validation checks signature and platform claims; WebSocket authentication uses a subprotocol token. Deployed issuer/audience configuration remains externally unverified.
- Android release configuration requires HTTPS/WSS and does not embed development client credentials. Debug-only credentials are intentionally build-generated and must not be used for release.
- SafeCheck does not execute URLs, launch UPI intents, or perform payment operations. URL reputation is explicitly not queried, avoiding an SSRF path.
- Public report text is server-sanitized for obvious OTP/PIN/CVV/password/credential values, but users must still be warned not to submit secrets.
- The SQLite store is tenant-aware for SafeCheck records. Existing unrelated report/fixture paths require separate review before any public exposure.

## Duplicated or adjacent functionality

- There are multiple report domains: existing transaction/CERT-In reports and RRR investigation reports. They should not be conflated with SafeCheck community reports.
- There are multiple QR surfaces: pairing QR generation and payment QR/SafeCheck scanning. They use different contracts and must remain separate.
- WebSocket consumers exist across Operations Center, threat/intelligence surfaces, and SDK portal code. The Android SDK keeps one connection manager; no second Android SafeCheck socket should be introduced.

## Environment dependencies

- Android debug properties currently point to the Render API/WSS host. Release URLs must be supplied through `FUSION_BASE_URL` and `FUSION_WS_URL`.
- Vercel `VITE_API_BASE`, server-side dashboard token configuration, Render CORS, JWT issuer/audience/signing configuration, and WebSocket routing must be checked in the deployed environments.
- Pairing/session state currently depends on the lifetime of the backend process.

## Exact files requiring changes for this hardening pass

- `fusion-reference-bank/app/src/main/AndroidManifest.xml`: explicit camera permission.
- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/safecheck/SafeCheckScreen.kt`: permission lifecycle, capture validation/debounce, review-before-analysis, timeout/cancel/error states.
- `api/safecheck.py` and `api/test_safecheck.py`: preserve and extend the stable SafeCheck contract and input/security regression coverage where needed.
- `FINAL_*` documentation: record evidence and unverified deployment/physical gates.

## Acceptance tests

- Android build and unit task complete.
- Camera permission granted opens the real scanner; denied permission shows a retry path; permanently denied permission offers app settings.
- Valid UPI QR is decoded, previewed, parsed, and analyzed only after user confirmation.
- URL, malformed, unsupported, oversized, and dangerous-scheme payloads are rejected or classified without external execution.
- Duplicate scan callbacks do not create duplicate analyses.
- Pairing accepts a valid tenant-bound QR, rejects expiry/replay/wrong tenant, persists the session, registers once, and authenticates the WebSocket.
- Expired/invalid JWT and unauthenticated tenant/API/WebSocket calls are rejected.
- SafeCheck score/confidence are reproducible and tenant-scoped.
- Reports redact obvious secrets, reject duplicates, rate-limit abuse, and expose review status.
- Synthetic transaction remains explicitly non-financial and generates telemetry.
- Operations Center receives SafeCheck/session/telemetry events without manual refresh.
- Backend tests, web tests/build, Android build, static/secret checks, deployed acceptance, and physical five-run acceptance are recorded separately as VERIFIED, PARTIALLY VERIFIED, or NOT VERIFIED.

## Audit conclusion

The existing architecture is reusable. The smallest safe implementation is to harden the existing JourneyApps scanner and SafeCheck screen, keep backend parsing authoritative, preserve existing pairing/WebSocket contracts, and document the deployment/device gates instead of simulating them.
