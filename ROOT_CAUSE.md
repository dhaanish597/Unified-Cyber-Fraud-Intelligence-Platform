# Root Cause

## Confirmed from source

The QR path is only a device/SDK bootstrap. `POST /device/register` mints an SDK token, but the Android UI then explicitly redirects to a separate username/password login. The banking access token is therefore absent until the user performs manual login, and the authenticated SDK session/WebSocket cannot be created from QR pairing alone.

The current `NavGraph` starts at `home` and does not reference `SplashScreen`, `PairingScreen`, or `LoginScreen`, so the intended authentication state machine is not the active application entry path.

## Contributing configuration risk

The checked-in debug Gradle properties set `FUSION_DEBUG_BASE_URL` and `FUSION_BASE_URL` to `https://crypto-fraud-intelligence-self.vercel.app/`, while the Vercel web token proxy and web production fallback target `https://risk-engine-api-o2kl.onrender.com`. Pairing can override this at runtime, but a fresh APK before pairing and any QR generated with a stale frontend/API value can target the wrong service.

## Test blocker

Backend pytest collection currently fails before tests run: installed FastAPI/Starlette rejects `APIRouter(on_startup=...)` in `api/core_platform/banking_auth.py:328`. This is an environment/framework compatibility failure, not evidence that pairing tests pass.

## Fix applied

The Android path now treats QR pairing as the SDK authentication bootstrap: it persists the returned scoped JWT, starts the backend SDK session, waits for WebSocket `CONNECTED`, and only then reports pairing success. The app entry graph now restores that paired session or presents the QR screen.

## Not claimed

No production HTTP status/body or physical-device run was available. A specific live 401/403 root cause remains unproven until a trace is captured.
