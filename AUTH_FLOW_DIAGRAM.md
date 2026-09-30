# Current and Target Authentication Flow

## Current implementation

```text
Vercel Operations Center
  -> POST /device/pair
  -> QR JSON {backend, ws, pairId, bootstrapToken, tenantId, environment, expires}
  -> Android scans QR
  -> POST /device/register (public, one-time bootstrap)
  -> SDK JWT stored
  -> UI redirects to manual login
  -> POST /banking/auth/login
  -> banking JWT + refresh token
  -> POST /sdk/device
  -> POST /sdk/session/start
  -> WebSocket /ws/stream with Sec-WebSocket-Protocol: Bearer.<JWT>
```

## Required production-demo flow

```text
Vercel Operations Center
  -> POST /device/pair
  -> short-lived one-time QR credential
  -> Android scans and validates environment/expiry/shape
  -> POST pairing exchange over HTTPS
  -> backend consumes credential atomically and creates mobile session
  -> short-lived access token + refresh/session credentials
  -> encrypted Android storage
  -> authenticated device registration
  -> authenticated SDK session start
  -> authenticated WebSocket with existing protocol
  -> backend-driven CONNECTED state
  -> authenticated mobile home + Operations Center activity
```

The target flow must never mark the UI authenticated before the exchange, device registration, session start, and WebSocket acknowledgement succeed.
