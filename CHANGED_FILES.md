# Changed Files

Application changes after the audit:

- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/sdk/Fusion.kt`: QR pairing now completes SDK session creation and waits for authenticated WebSocket connection; added QR-paired session restore.
- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/navigation/NavGraph.kt`: active entry point now restores a paired session or shows QR pairing before home.
- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/pairing/PairingScreen.kt`: success copy reflects secure session establishment.
- `fusion-reference-bank/gradle.properties`: checked-in demo endpoints now target the Render API/WSS service instead of the Vercel dashboard host.
- `api/core_platform/pairing.py`, `api/main.py`, and `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/sdk/models/SDKModels.kt`: QR payload/registration now carries and validates tenant/environment binding.
- `requirements.txt`, `requirements-render.txt`: pin a FastAPI-compatible Starlette version for the current test/runtime contract.
- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/sdk/network/FusionWebSocketManager.kt`: bounded exponential reconnect with duplicate-job prevention.
- `api/safecheck.py`, `api/core_platform/security.py`, `api/main.py`, `api/test_safecheck.py`: deterministic SafeCheck analysis, privacy-minimized reporting, tenant-scoped assessments, events, and tests.
- `fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/sdk/Fusion.kt`, `.../FusionApiService.kt`, `.../SDKModels.kt`, `.../ui/screens/safecheck/SafeCheckScreen.kt`, `.../ui/navigation/NavGraph.kt`: SafeCheck SDK contract, QR scan/result/report UI, and navigation.
- `web/src/pages/OperationsCenterPage.jsx`: displays sanitized SafeCheck assessment events using the existing Operations Center WebSocket.
- `web/package.json`, `web/package-lock.json`: update React Router to patched `7.18.4`; production dependency audit is clean.
- `fusion-reference-bank/app/src/main/AndroidManifest.xml` and `.../ui/screens/safecheck/SafeCheckScreen.kt`: explicit camera permission, real scanner permission recovery, timeout, duplicate debounce, payload guard, review-before-analysis, and safe QR UX.
- `api/safecheck.py` and `api/test_safecheck.py`: Unicode normalization, unsupported-scheme rejection, duplicate-parameter signal, and regression tests.

Created audit artifacts:

- `EXISTING_APK_AUTH_AUDIT.md`
- `ROOT_CAUSE.md`
- `AUTH_FLOW_DIAGRAM.md`
- `CHANGED_FILES.md`
- `TEST_RESULTS.md`
- `SECURITY_NOTES.md`
- `DEMO_RUNBOOK.md`
- `EXISTING_APK_AUDIT.md`
- `APK_PERFORMANCE_REPORT.md`
- `APK_STABILIZATION_REPORT.md`
- `SAFE_CHECK_IMPLEMENTATION_REPORT.md`
- `SECURITY_REVIEW.md`
- `COMMERCIAL_MODEL.md`
- `FINAL_SYSTEM_AUDIT.md`
- `FINAL_VERIFICATION_REPORT.md`
- `FINAL_SECURITY_REVIEW.md`
- `FINAL_PERFORMANCE_REPORT.md`
- `FINAL_API_CONTRACT.md`
- `FINAL_ANDROID_RELEASE_CHECKLIST.md`
- `FINAL_DEMO_RUNBOOK.md`
