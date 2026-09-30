# Existing APK Authentication Audit

Audit date: 2026-09-29

Scope: current working tree of the Fusion Unified Cyber-Fraud Intelligence Platform. The working tree was already dirty before this audit; no application code was changed for this report.

## A. Current Android architecture

- Native Kotlin Android application under `fusion-reference-bank/app`.
- Compose UI, Hilt, Retrofit/Gson, OkHttp, Room, EncryptedSharedPreferences, ZXing Android Embedded.
- Package/namespace/application ID: `com.fusionbank.mobileapp`; debug suffix: `.debug`.
- `FusionBankApp.kt` contains the Hilt application class `FuzenAIBankApp`; the manifest references `.FuzenAIBankApp`.
- Current `NavGraph` starts directly at `home`. `SplashScreen`, `PairingScreen`, and `LoginScreen` exist but are not referenced by the current navigation graph.

## B. Current SDK architecture

`Fusion` is a process-wide singleton. It owns Retrofit, secure storage, device attestation, Room offline queue, SDK session state, banking token state, and `FusionWebSocketManager`. A single OkHttp interceptor chooses the banking token for paths beginning `/banking/`, and the SDK token for all other paths.

## C. Current QR flow

The Operations Center (`DeveloperPlatformPage`) calls `POST {API_BASE}/device/pair` and receives JSON containing `backend`, `ws`, `pairId`, `bootstrapToken`, and `expires`. The complete JSON is sent to a third-party QR image URL (`api.qrserver.com`).

The Android scanner decodes JSON and calls `POST {backend}/device/register` with `pair_id`, `bootstrap_token`, device UUID, Android version, manufacturer, model, SDK version, app version, and fingerprint. The backend stores the one-time record in an in-memory `PairingRegistry`, consumes the token, registers a live device, and mints an SDK-scoped JWT plus a refresh-token-shaped value.

The pairing response is persisted in encrypted preferences. Before the fix, the UI displayed “Redirecting to login…” and offered “Already paired? Go to Login”. The repaired path now starts the authenticated SDK session and waits for WebSocket connection before reporting pairing success; it does not create a banking identity/password session.

## D. Current backend authentication flow

`PlatformSecurityMiddleware` makes `/device/pair` and `/device/register` public. Other protected routes require `Authorization: Bearer <JWT>`, valid HS256 signature, issuer, audience, `nbf`, `exp`, tenant, subject, request ID, and an allowed role.

Platform/dashboard tokens come from `POST /auth/token` using a client ID and secret. Banking identity tokens come from `POST /banking/auth/login` (and canonical aliases under `/auth/*`). Pairing tokens are created by the in-memory registry and are not JWTs.

## E. Current login flow

`LoginViewModel` calls `Fusion.login(email, password)`. Retrofit sends `POST /banking/auth/login` with username/email, password, and device ID. Backend password authentication issues a short-lived access token and rotating refresh token. The SDK then calls `POST /sdk/device`, `POST /sdk/session/start`, starts telemetry, and opens the WebSocket.

This is a separate username/password flow after QR pairing. It contradicts the requested QR-bootstrap flow.

## F. Current device registration flow

There are two registrations:

1. `POST /device/register`: public one-time QR bootstrap; writes only to the in-memory pairing registry and mints an SDK JWT.
2. `POST /sdk/device`: authenticated SDK device registration called during `startSessionInternal`; the backend SDK engine stores the device profile.

Operations Center data is reconstructed from these in-memory registries and SDK sessions. Persistence across process restart is not evidenced.

## G. Current JWT lifecycle

JWTs are custom HS256 tokens created in `api/core_platform/security.py`. Default access TTL is configured by `JWT_TTL_SECONDS` and is 900 seconds in the repository examples. Banking refresh tokens are random opaque values hashed before storage and rotated on refresh. The pairing response also returns `refresh_token`, but `/device/register` does not persist or validate it for refresh; this is not a functional mobile refresh contract.

Android stores access tokens, expiry timestamps, URLs, device ID, and banking refresh token in `EncryptedSharedPreferences`. `ensureValidAccessToken`/`ensureValidBankingToken` source exists, but the current app graph does not invoke the auth bootstrap screens.

## H. Current WebSocket authentication flow

Backend `GET /ws/stream` authenticates from the `Sec-WebSocket-Protocol` header using a protocol value formatted as `Bearer.<JWT>` (or an access-token cookie). It validates tenant and an allowed role, rejects duplicate connection keys with 4409, and sends `connection_ack`.

Android sends the SDK token as `Sec-WebSocket-Protocol: Bearer.<JWT>` and appends `session_id`. It reconnects with linearly increasing delays capped at 30 seconds, with no explicit maximum attempt count or token-expiry stop condition. Browser code uses the same protocol convention.

## I. Current tenant propagation

Tenant is carried in JWT claim `tenant_id`, Android `BuildConfig.TENANT_ID`, `FusionConfig.tenantId`, and `sdk/session/start.tenant_id`. Backend rejects tenant mismatch with 403. The repaired QR payload includes `tenantId` and `environment`; `/device/register` requires the tenant and rejects a different-tenant credential before consuming it.

## J. Current Vercel -> backend configuration

The web client resolves `VITE_API_BASE`, then `window.__FUSION_CONFIG__.apiBase`, then local development localhost or the hardcoded Render URL `https://risk-engine-api-o2kl.onrender.com`.

The Vercel serverless `/api/token` proxy resolves `FUSION_API_BASE` with the same Render fallback and keeps `FUSION_DASHBOARD_CLIENT_SECRET` server-side. This is the correct secret-boundary design in source.

`DeveloperPlatformPage` uses the web API base for `POST /device/pair` and, in production, defaults the mobile backend URL to the same API base.

## K. Current Render/backend configuration

`render.yaml` deploys `api.main:app` as `risk-engine-api`, with production JWT, CORS, client, banking-user, tenant, and database settings supplied as Render environment variables. Source `.env` has `CORS_ORIGINS=https://web-three-nu-82.vercel.app`; this is not proof that the deployed Render value matches the actual Vercel hostname.

## L-R. Exact failure point and request evidence

No physical-device trace, HAR, Logcat capture, or deployed response was present in the repository, so an observed production status/body cannot honestly be claimed. The source-level failure is deterministic:

1. QR scan succeeds.
2. Android sends `POST {QR.backend}/device/register` with JSON bootstrap/device data. This can return 200 and an SDK token.
3. Pairing UI intentionally transitions to a separate password login, rather than authenticated mobile home.
4. Only after `POST /banking/auth/login` does Android call protected SDK endpoints and WebSocket.

Relevant request contracts:

| Request | Headers | Expected/possible result |
|---|---|---|
| Web `POST /device/pair` | `Authorization: Bearer <dashboard JWT>`, JSON | 200 pairing JSON; 401/403 if dashboard token/bootstrap fails |
| Android `POST /device/register` | JSON; no bearer required | 200 SDK credentials; 401 invalid/expired/reused QR; 503 if no tenant-scoped SDK client |
| Android `POST /banking/auth/login` | JSON; no bearer required | 200 banking token; 401 bad credentials/configuration |
| Android `POST /sdk/device` | `Authorization: Bearer <SDK JWT>` | protected SDK registration |
| Android `POST /sdk/session/start` | `Authorization: Bearer <SDK JWT>` | 403 on tenant/app mismatch; 401 invalid/expired token |
| Android WebSocket `/ws/stream?session_id=...` | `Sec-WebSocket-Protocol: Bearer.<SDK JWT>` | 101 + `connection_ack`; 4401/4403/4409 on auth/duplicate failure |

The exact code path that produces the reported “manual login after scan” behavior is `PairingScreen.kt` (`Redirecting to login…`) plus `Fusion.pair()` returning only `PairingRegistrationResponse`; no banking session is created by pairing.

## S. Failure classification

- Primary: authentication contract / flow integration.
- Secondary: Android navigation integration (auth screens exist but are not in `NavGraph`).
- Secondary: deployment/configuration risk (the checked-in debug properties previously pointed at the Vercel frontend hostname, while Vercel’s API proxy and web fallback point to Render; the properties are now corrected).
- Secondary: test environment dependency mismatch (backend tests cannot collect).
- Not proven: a particular live 401, 403, CORS, WebSocket, tenant, or deployment response, because no deployed trace is available.

## T. Minimal safe fix recommendation

Do not rewrite JWT or WebSocket security. First define one server-backed pairing exchange that consumes the one-time credential and returns the authenticated mobile session required by the existing SDK. Reuse the existing JWT claims, secure storage, device registration, and WebSocket protocol. Wire `NavGraph` to an explicit backend-driven state machine: restore valid session -> authenticated; otherwise pairing -> pairing exchange -> device/session registration -> connected; use password login only as an explicit fallback if product requirements retain it. Pin the production Android API/WS URLs to the actual Render service, not the Vercel static frontend, and verify deployed CORS values. Add tests at the pairing-to-session seam before implementation.

## Unknowns requiring external verification

- Actual production Render URL and deployed environment values.
- Whether Vercel’s current deployment has the `api/token` environment variables configured.
- Physical APK installed on a device and its Logcat/network trace.
- Five-run physical QR -> session -> WebSocket success rate.
- Whether a process restart is acceptable given in-memory pairing/device/session registries.
