# Final API Contract

Date: 2026-09-30

## Pairing/session

- `POST /device/pair`: creates a short-lived tenant/environment-bound pairing credential for the Operations Center.
- `POST /device/register`: consumes the one-time pairing credential and returns device ID, access/session credentials, expiry, backend URL, WSS URL, tenant, and environment.
- `POST /sdk/device`: authenticated device registration.
- `POST /sdk/session/start`: authenticated SDK session creation.
- WebSocket `/ws/stream`: authenticated with the existing `Sec-WebSocket-Protocol: Bearer.<JWT>` mechanism.

## SafeCheck

### `POST /risk/qr/analyze`

Request:

```json
{
  "qr_payload": "upi://pay?pa=merchant@bank&pn=Encoded%20Name&am=500&cu=INR",
  "application_id": "com.fusionbank.mobileapp",
  "client_version": "1.0.1"
}
```

Response uses the existing camelCase client contract:

```json
{
  "riskScore": 18,
  "confidence": 82,
  "riskLevel": "LOW",
  "qrType": "UPI",
  "parsedDetails": {},
  "signals": [],
  "recommendation": "Verify the recipient name and amount before paying.",
  "assessmentId": "ASC_...",
  "assessedAt": "2026-09-30T00:00:00Z",
  "reportCount": 0
}
```

Risk levels are `LOW`, `MEDIUM`, `HIGH`, and `UNKNOWN`; the Android UI presents `MEDIUM` as `ELEVATED` without changing the wire contract. A score is never produced for an unknown QR type. Encoded names are not independently verified.

### `POST /reports/payment-identifier`

Accepts an identifier, category, description, and optional evidence. Reports begin as `UNVERIFIED`; duplicate reports return `409`, and the process-local source limiter returns `429` after the configured threshold. Free-form text is sanitized before storage.

### `GET /risk/qr/assessments`

Authenticated and tenant-scoped. Returns recent assessment records for the Operations Center.

## Event contracts

- `QR_RISK_ASSESSMENT`: assessment ID, tenant, QR type, score, level, confidence, signal codes, report count, timestamp.
- `COMMUNITY_RISK_REPORT`: report ID, tenant, category, identifier hash, status, timestamp.

Neither event contains passwords, payment secrets, report free text, or raw QR payloads.
