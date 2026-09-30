# Security Notes

- QR payload contains the one-time bootstrap token plus tenant/environment binding. It is acceptable only while short-lived, single-use, and free of passwords or long-lived secrets. The registry remains in-memory and must be persisted or deliberately bounded for production.
- `/device/register` is intentionally public, but must remain strictly scoped to the one-time credential and must not become a general device-registration bypass.
- JWT validation is strict in source: HS256, issuer, audience, expiry, tenant, subject, request ID, and role checks. Do not weaken these checks to mask 401/403 errors.
- Dashboard client secret is kept in Vercel server-side `api/token.js`; it is not referenced by Android source. Verify Vercel environment configuration and rotate any secret ever exposed in a browser bundle.
- Android stores tokens in `EncryptedSharedPreferences`, but the pairing response’s refresh token is not currently integrated into a functioning pairing refresh lifecycle.
- WebSocket auth uses a bearer token in the subprotocol. Avoid logging the full subprotocol/token; current WebSocket logging should be reviewed before demo capture.
- CORS is explicit and wildcard-free in production source. Confirm deployed `CORS_ORIGINS` includes the actual Vercel origin and no stale hostname.
- Checked-in debug properties include cleartext local-development guidance and a Vercel hostname. Release build validation requires HTTPS/WSS, but production URL ownership still needs correction/verification.
- In-memory pairing records, devices, sessions, and duplicate-connection state are lost on backend restart and are unsuitable for durable production pairing without a persistence decision.
