# Deployment Guide

## Prerequisites

- Python 3.11+ and dependencies from `requirements.txt`
- Node.js/npm matching the lockfile
- JDK 17+ and Android SDK; repository Gradle wrapper is included
- Neo4j 5.x credentials for a production-ready graph gate
- Versioned trained model artifacts for an available ML gate
- TLS certificates/reverse proxy and an Android release keystore

## Backend

Copy `.env.example` to a secret-managed environment and replace every example.
Production startup requires security mode, JWT secret, clients, banking users,
and CORS origins. Then:

```powershell
python -m uvicorn api.main:app --host 127.0.0.1 --port 8001
```

Terminate TLS at a production reverse proxy or load balancer and forward
WebSocket upgrades. Readiness is intentionally degraded until both models and
Neo4j are available.

## Dashboard

Set `VITE_API_BASE` to the public HTTPS API before `npm run build`. Provide the
short-lived dashboard token at runtime as
`window.__FUSION_CONFIG__.accessToken`; do not compile it into the bundle.
Serve `web/dist` over HTTPS with SPA fallback.

## Android

Provide release URLs and signing properties through environment/Gradle
properties:

```powershell
.\gradlew.bat bundleRelease `
  -PFUSION_BASE_URL=https://api.bank.example/ `
  -PFUSION_WS_URL=wss://api.bank.example/ws/stream `
  -PFUSION_RELEASE_STORE_FILE=C:\secure\release.jks `
  -PFUSION_RELEASE_STORE_PASSWORD=... `
  -PFUSION_RELEASE_KEY_ALIAS=... `
  -PFUSION_RELEASE_KEY_PASSWORD=...
```

The unsigned release path can validate compilation/minification, but store
submission requires a real keystore and verification with `jarsigner`.

## Validation

Run `scripts/validate_production.ps1`. It compiles Python, regenerates the API
inventory, runs backend tests/performance measurements, builds React, and runs
the Android debug/release/AAB matrix. Run device/emulator instrumentation for
network loss, process death, certificate failure, reconnect, and Room recovery
before a production rollout.

## Rollback

Keep the previous backend image, dashboard assets, and signed AAB. Database
changes are additive key/value collections. Revert the application version
while retaining refresh/user records; clients will establish fresh SDK
sessions after reconnect.

