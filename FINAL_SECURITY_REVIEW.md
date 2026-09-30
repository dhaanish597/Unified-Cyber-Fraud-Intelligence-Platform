# Final Security Review

Date: 2026-09-30

## Verified controls

- Real QR contents are treated as untrusted input.
- Android rejects oversized payloads and unsupported/dangerous URI schemes before analysis.
- Backend enforces payload length, URI scheme, Unicode normalization, field parsing, and duplicate UPI-parameter signaling.
- SafeCheck never opens URLs, launches UPI intents, or executes payments.
- No passwords, OTPs, UPI PINs, CVVs, banking credentials, or raw keystrokes are collected by the new flow.
- Public SafeCheck tenant context is server-derived; client payload cannot select an arbitrary tenant.
- Authenticated assessment listing is JWT/tenant scoped.
- Pairing remains short-lived, tenant-bound, environment-bound, and single-use.
- Android session credentials use existing encrypted storage.
- Report descriptions/evidence are redacted for obvious secret terms/values before persistence; internal events hash identifiers and omit free-form content.
- No private-key/API-key pattern matches were found by the repository heuristic scan.
- Production web dependency audit (`npm audit --omit=dev --audit-level=high`) reports zero vulnerabilities after updating React Router to `7.18.4`.

## Remaining risks

- Pairing/session state and report rate limiting are process-local or SQLite-backed; multi-instance production requires shared durable state and shared rate limiting.
- Deployment CORS, TLS, JWT issuer/audience/signing configuration, and release secrets are not verified from this workspace.
- The existing repository contains adjacent synthetic/demo and RRR fixture paths; those must remain clearly isolated from public fraud claims.
- URL reputation is not queried. Any future lookup requires SSRF protections, DNS rebinding defenses, private-address blocking, timeouts, redirect controls, and response-size limits.
- Camera behavior still needs physical-device verification.
- The full development dependency audit still reports Vite/Vitest/transitive build-tool vulnerabilities; fixing those requires major-version toolchain changes and is a separate compatibility task. `pip_audit` is unavailable in the environment.

No banking certification, regulatory approval, real fraud-prevention guarantee, or payment-processing claim is made.
