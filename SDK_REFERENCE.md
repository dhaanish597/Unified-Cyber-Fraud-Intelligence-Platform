# Fusion Android SDK Reference

## Host integration

`FusionBankApp` initializes the singleton with build-specific HTTPS/WSS
endpoints. Release builds contain no development client credentials. The host
application authenticates only through:

```kotlin
Fusion.login(username, password) { result -> ... }
Fusion.restoreSession { result -> ... }
Fusion.requestDecision(
    eventType = "TRANSFER_INITIATED",
    amount = amount,
    beneficiaryId = beneficiaryId,
) { result -> ... }
Fusion.logout { result -> ... }
```

The banking UI does not call Retrofit or make local fraud decisions.

## Session lifecycle

Login verifies credentials on the backend, stores rotating tokens in encrypted
preferences, registers the observed device, starts an SDK session, verifies the
backend ACK, and opens the authenticated session-scoped WebSocket. Splash
recovery rotates the refresh token and creates a fresh SDK session. Logout
revokes the refresh token, closes WSS, and clears session credentials while
preserving the stable device ID.

## Request evidence

Every event/decision has a UUID-derived request and correlation ID. Decision
responses require `backend_ack=true` and include pipeline ID, dependency status,
stage timings, and nullable model confidence. Room persists telemetry request
and correlation IDs so retries retain their idempotency key.

## Offline and reconnect behavior

Telemetry events are queued chronologically in Room after network failure.
Successful WebSocket reconnect triggers queue flushing. Failed items remain
pending and stop the flush to preserve order. Financial decisions are not
executed later from an offline queue.

## Build commands

```powershell
cd fusion-reference-bank
.\gradlew.bat testDebugUnitTest assembleDebug
.\gradlew.bat assembleRelease bundleRelease lintRelease
```

Release configuration accepts `FUSION_BASE_URL`, `FUSION_WS_URL`, and the four
`FUSION_RELEASE_*` signing properties. URLs must use HTTPS/WSS.

