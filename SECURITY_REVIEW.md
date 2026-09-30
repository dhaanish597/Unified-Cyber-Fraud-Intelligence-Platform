# Security Review

## Controls implemented

- No passwords, OTPs, UPI PINs, CVVs, banking credentials, or raw keystrokes are collected.
- QR payloads are length-limited, parsed locally on Android, and validated server-side.
- No arbitrary URL is fetched or launched by the backend SafeCheck implementation.
- Tenant for public SafeCheck requests is derived from server configuration; client input cannot select a tenant.
- Authenticated Operations Center assessment listing is tenant-scoped by JWT-derived tenant.
- Reports are input-validated, tenant-scoped, deduplicated, rate-limited, and initially unverified.
- Internal events hash payment identifiers and omit report descriptions/evidence.
- Existing JWT, CORS, encrypted Android storage, and WebSocket security were reused.

## Risks and limitations

- The initial rate limiter is process-local and must move to a shared store for multi-instance production deployment.
- Community report status transitions and reviewer audit tooling are not yet implemented.
- URL reputation is intentionally not queried; adding it requires SSRF protections, DNS rebinding defenses, private-address blocking, timeouts, response-size limits, and no redirects to internal networks.
- The pairing and SafeCheck stores currently rely on the existing SQLite/process-local architecture.
- Production CORS, TLS, release signing, and deployed secrets require external verification.

## Security conclusion

SafeCheck is an intelligence/warning feature, not a payment processor. No production-readiness or regulatory-certification claim is made.
