# Final Android Release Checklist

## Verified in workspace

- [x] Existing package namespace/application ID preserved: `com.fusionbank.mobileapp`.
- [x] Debug APK assembles successfully.
- [x] Release build requires HTTPS API and WSS WebSocket properties.
- [x] Release build clears debug client credentials.
- [x] Camera permission is declared explicitly.
- [x] Real JourneyApps ZXing scanner dependency is used.
- [x] QR payload length/scheme guards are present.
- [x] Review-before-analysis is present.
- [x] No automatic URL opening or UPI intent execution.
- [x] Pairing/session restoration path remains guarded by backend session/WebSocket confirmation.
- [x] WebSocket reconnect is bounded.

## Must be completed before release/demo sign-off

- [ ] Supply and verify release signing configuration.
- [ ] Install the release APK on a physical Android device.
- [ ] Verify camera permission grant/deny/settings recovery.
- [ ] Verify low-light, rotation, pause/resume, timeout, and duplicate scan behavior.
- [ ] Verify deployed Render API/WSS and Vercel Operations Center.
- [ ] Complete five pairing runs and record status/latency/failure point.
- [ ] Complete SafeCheck real QR scan and event propagation.
- [ ] Complete session close/reopen/expiry/network recovery tests.
- [ ] Run formal dependency/security scanning.

Release readiness is pending the unchecked gates.
