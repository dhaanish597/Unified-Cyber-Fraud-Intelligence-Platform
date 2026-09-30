# Test Results

Audit/implementation date: 2026-09-30

| Check | Result | Evidence |
|---|---|---|
| Full backend pytest suite | PASS | `python -m pytest -q`: 40 passed |
| SafeCheck tests | PASS | `python -m pytest -q api/test_safecheck.py`: 7 passed |
| Python syntax | PASS | `python -m py_compile api/safecheck.py api/main.py api/core_platform/pairing.py` |
| Web production build | PASS | `npm run build`: Vite transformed 3163 modules |
| Android debug build | PASS | `fusion-reference-bank\\gradlew.bat :app:assembleDebug`: BUILD SUCCESSFUL after real-camera hardening |
| Pairing tenant/replay smoke test | PASS | Wrong tenant rejected; valid token single-use |
| Score reproducibility | PASS | Same UPI payload produced same score/confidence/signals |
| Report duplicate/rate limit | PASS | Duplicate 409; sixth source report 429 |
| Android unit tests | NO-SOURCE | `:app:testDebugUnitTest` completed successfully; no Android unit test sources were found |
| Android integration tests | NOT RUN | Requires emulator/device harness |
| API contract tests | PARTIAL | Backend endpoint tests pass; deployed contract not verified |
| E2E browser tests | NOT RUN | Existing Playwright suite does not cover SafeCheck |
| Physical QR/WebSocket flow | NOT RUN | No connected device/emulator or deployed trace |
| Security scan | NOT RUN | No repository security scanner configured |
| Production web dependency audit | PASS | `npm audit --omit=dev --audit-level=high`: 0 vulnerabilities |
| Development dependency audit | BLOCKED/PARTIAL | `npm audit` reports Vite/Vitest/transitive findings; `pip_audit` is not installed |

Warnings remain for deprecated FastAPI startup hooks, reportlab, and the legacy `google.generativeai` package. They did not fail the suite.

Production readiness is not declared.
