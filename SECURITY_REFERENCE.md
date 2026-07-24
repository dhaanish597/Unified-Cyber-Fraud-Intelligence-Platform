# Security Reference

## Authentication

JWT access tokens use HS256 with issuer, audience, subject, client, roles,
tenant/app scope, issued/not-before/expiry, and unique token ID claims.
Production requires a 32-byte-or-longer secret and configured clients.

Bank passwords use PBKDF2-HMAC-SHA256 with 310,000 iterations and random salts.
Refresh tokens are random 384-bit values; only SHA-256 token hashes are stored.
Refresh is device-bound, expiring, single-use, and rotating. Logout revokes the
current refresh token.

## Authorization

Security middleware protects every path except the documented public set.
Prefix policies enforce SDK, customer, developer, analyst, operator, and admin
roles. App/tenant scopes are enforced when starting SDK sessions. Customer
subjects cannot start, call, or subscribe to another user's SDK session.

## Transport and storage

- Production CORS forbids wildcard origins.
- Android release rejects cleartext and trusts system CAs.
- Dashboard production configuration requires HTTPS and WSS.
- Android tokens/session identifiers use AndroidX encrypted preferences.
- Offline events use application-private Room storage.
- Release client secrets are empty; debug-only credentials are guarded by
  `BuildConfig.DEBUG`.

## Logging and errors

Request logs include method, path, request ID, status, and latency—not
authorization headers, refresh tokens, passwords, webhook signatures, or
payload secrets. Authentication errors use a stable sanitized envelope.

## Operational requirements

Inject secrets through the process environment/secret manager. Do not put
tokens in Vite build variables or Gradle source. Rotate client, JWT, banking,
gateway, Neo4j, and signing credentials independently.

