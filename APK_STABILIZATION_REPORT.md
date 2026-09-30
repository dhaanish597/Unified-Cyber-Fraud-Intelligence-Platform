# APK Stabilization Report

## Completed

- QR pairing now carries tenant/environment binding and preserves compatibility for older clients that omit the tenant field.
- Android pairing persists the scoped SDK JWT, starts the SDK session, and waits for WebSocket `CONNECTED` before reporting success.
- App entry navigation restores a valid paired SDK session or presents pairing instead of opening the authenticated home blindly.
- Android demo URLs target the Render API/WSS host rather than the Vercel static dashboard host.
- WebSocket reconnect uses bounded exponential backoff: five attempts at 1/2/4/8/16 seconds, with duplicate scheduled jobs suppressed.
- Backend dependency pins now include compatible Starlette for the FastAPI pin.

## Verification

- Full backend suite: 40 passed.
- SafeCheck backend suite: 7 passed.
- Python syntax checks: passed.
- Android debug APK build: passed.
- Web production build: passed.
- Real-camera SafeCheck hardening build: passed; physical camera behavior remains unverified.

## Not verified

- Physical Android QR scan and WebSocket handshake.
- Render/Vercel deployed environment values.
- Five-run physical reliability test.
- Release signing build.

The APK is not declared production-ready until those external gates pass.
