# Fusion SafeCheck Implementation Report

## APIs

- `POST /risk/qr/analyze`
- `POST /reports/payment-identifier`
- `GET /risk/qr/assessments` (authenticated Operations Center view)

## Supported QR types

- UPI payloads: payee address, encoded name, amount, currency, note, and non-sensitive metadata.
- HTTP/HTTPS URLs: scheme, host, and structure signals only. SafeCheck does not fetch or execute URLs.
- Unknown/unsupported payloads: explicit `UNKNOWN` assessment with no fabricated score.

## Risk model

Scores are deterministic and built from explicit signals: payload validity, missing/malformed fields, URL structure, suspicious URL attributes, and tenant-scoped community report status. `confidence` is separate from `riskScore`. Unsupported payloads return `riskScore: null` and `riskLevel: UNKNOWN`.

## Community reports

Reports are stored as `UNVERIFIED`, deduplicated by tenant/identifier/category, rate-limited per source address, and emitted as sanitized `COMMUNITY_RISK_REPORT` events. The implementation does not publicly label individuals or assert criminality.

## Fusion integration

Assessments emit `QR_RISK_ASSESSMENT` events containing only assessment ID, tenant, QR type, score, confidence, signal codes, and report count. Operations Center displays recent sanitized assessment cards and receives live events on the existing WebSocket.

## Android

SafeCheck reuses the existing ZXing scanner and Fusion SDK Retrofit transport. The result UI explicitly states that encoded payee names are not independently verified and includes a report form. No payment execution path was added.

## Remaining work

- Add persistent distributed rate limiting if public traffic leaves the single-instance demo deployment.
- Add external reputation provider only behind an SSRF-safe, privacy-reviewed service boundary.
- Add moderation tooling for transitioning reports through `UNDER_REVIEW`, `CORROBORATED`, and `CONFIRMED`.
