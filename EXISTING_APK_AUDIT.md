98790p-[p09876# EXISTING APK / SDK / BACKEND AUDIT

Audit scope: current working tree, Android source, SDK, FastAPI backend, Vercel web client, deployment configuration, and checked-in tests. Existing unrelated working-tree changes were preserved.

## Architecture and current data flow

- Android: Kotlin/Compose app in `fusion-reference-bank/app`; Hilt, Retrofit/OkHttp, Room, EncryptedSharedPreferences, ZXing.
- SDK: singleton `Fusion` owns API, tokens, device attestation, offline queue, telemetry, session lifecycle, and WebSocket manager.
- Backend: FastAPI `api/main.py`, platform security middleware, JWT/role/tenant enforcement, SDK engine, event brokers, risk/session engines, and in-memory pairing/device/session registries.
- Web: Vite/React Operations Center in `web/src`; Vercel serverless `/api/token` keeps dashboard client secret server-side and obtains a platform JWT from the Render API.
- Deployment: Render runs the FastAPI service; Vercel serves the dashboard and token proxy.

## Authentication/session flow

Dashboard `POST /auth/token` obtains a short-lived platform JWT. Banking login uses `POST /banking/auth/login` and rotating refresh tokens. SDK calls use `Authorization: Bearer <JWT>`. JWT validation checks HS256 signature, issuer, audience, `nbf`, `exp`, subject, tenant, request ID, and role. WebSocket authentication uses `Sec-WebSocket-Protocol: Bearer.<JWT>`.

## QR pairing flow

`POST /device/pair` creates a five-minute in-memory, one-time bootstrap record. The QR contains backend URL, WebSocket URL, pair ID, bootstrap token, tenant ID, environment, and expiry. Android posts device metadata to `POST /device/register`; the backend validates token, expiry, replay state, and tenant, then issues a tenant-scoped SDK JWT. The repaired Android path starts the SDK session and waits for authenticated WebSocket connection before declaring pairing success.

## API contracts and Operations Center integration

- `POST /device/pair`: QR bootstrap creation.
- `POST /device/register`: one-time device bootstrap and SDK credential issuance.
- `POST /sdk/device`: authenticated device profile registration.
- `POST /sdk/session/start`: authenticated tenant/app-scoped SDK session.
- `POST /sdk/event`, `/sdk/network`, `/sdk/telemetry`: authenticated telemetry/event ingestion.
- `GET /device/connected`, `GET /device/sessions`: Operations Center device/session views.
- `/ws/stream`: authenticated event/trust stream with connection acknowledgement and heartbeat handling.

The backend event brokers and SDK/session engines feed Operations Center views; pairing/device/session state is process-local and is lost on backend restart.

## Current failures and stale configuration

1. Backend pytest collection is blocked in this environment by FastAPI 0.115.12 / Starlette 1.7.0 incompatibility: `APIRouter` construction raises `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'`.
2. No physical-device, deployed HTTP trace, or five-run QR/WebSocket trace exists, so live status codes and latency are unknown.
3. The prior source path required manual banking login after QR pairing; the repaired path now supports QR bootstrap to SDK session, but physical verification is still pending.
4. WebSocket reconnect is capped by delay but has no explicit maximum retry count or token-expiry-specific stop state.
5. Pairing/device/session registries are in memory, so restart durability and multi-instance correctness are not established.
6. The repository contains checked-in demo endpoint properties; they now target the Render API/WSS host, but deployment values must still be verified externally.

## Security risks

- QR tokens are short-lived and single-use, but the pairing registry is process-local.
- No passwords, OTPs, PINs, CVVs, or raw keystrokes are used by the SafeCheck design or existing SDK telemetry path.
- Android token storage uses encrypted preferences; release builds do not embed development client credentials.
- Dashboard secret remains server-side in Vercel `/api/token.js`.
- Any future URL reputation fetch must enforce SSRF protections, DNS/IP filtering, timeouts, and no arbitrary URL execution.
- CORS is explicit in source; deployed origin alignment remains unverified.

## Performance observations

- Android startup initializes SDK, encrypted storage, database, attestation, queue, and state collectors eagerly.
- SDK session startup performs device registration, session start, WebSocket connect, telemetry setup, and initial event emission sequentially.
- Operations Center refreshes device/session data on a polling interval while also maintaining a WebSocket.
- No representative latency measurements are available; optimization must wait for a runnable backend/device loop.

## Minimal recommended fixes

- Repair/pin the Python dependency set so backend tests collect.
- Add regression tests at the QR exchange -> session -> WebSocket seam.
- Bound WebSocket retry count and expose reconnect/session-expired states.
- Decide whether pairing/device/session state needs durable shared storage before multi-instance deployment.
- Verify deployed Render/Vercel environment values and CORS from a real trace.
- Implement SafeCheck as a separate risk/reporting surface that reuses existing auth, tenant, event, and Operations Center contracts without changing them.

## Audit conclusion

The existing architecture is reusable. SafeCheck should be added as deterministic QR parsing, evidence-based risk scoring, community reports, and sanitized internal events. Production readiness is not established until backend tests, API contracts, Android tests, and physical QR pairing are runnable and passing.
