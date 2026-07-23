# Fusion Reference Banking Application (`fusion-reference-bank`)
## Fusion Adaptive Trust SDK (FAT-SDK) Production Reference Integration

Welcome to the official **Fusion Reference Banking Application**. This repository contains a production-ready, modern Kotlin Android application demonstrating how financial institutions integrate with **Fusion Risk OS** via the embedded **Fusion Adaptive Trust SDK (FAT-SDK)**.

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    FUSION REFERENCE BANKING APPLICATION (APK)                   │
│                                                                                 │
│  ┌────────────────────┐   ┌───────────────────────────┐   ┌──────────────────┐  │
│  │   Jetpack Compose  │   │     Hilt ViewModel Layer  │   │  Room DB Offline │  │
│  │  Material 3 Views  │◄──┼──►  (StateFlow / Coroutines)  │◄─►│    Event Queue   │  │
│  └─────────┬──────────┘   └─────────────┬─────────────┘   └──────────────────┘  │
│            │                            │                                       │
│            └────────────────────────────┼───────────────────────────────────────┤
│                                         ▼                                       │
│                      ┌────────────────────────────────────┐                     │
│                      │   FUSION ADAPTIVE TRUST SDK (FAT)  │                     │
│                      │  - Device Attestation Engine       │                     │
│                      │  - Network Security Monitor        │                     │
│                      │  - Encrypted Storage (AES-256)     │                     │
│                      └─────────────────┬──────────────────┘                     │
└────────────────────────────────────────┼────────────────────────────────────────┘
                                         │  HTTP / REST API & WebSocket Stream
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             FUSION RISK OS BACKEND                              │
│                                                                                 │
│  ┌───────────────────────┐   ┌─────────────────────────┐   ┌─────────────────┐  │
│  │  Session Intelligence  │   │  Trust Passport Engine  │   │ Decision Engine │  │
│  │  (/sdk/session/start)  │   │     (/sdk/passport)     │   │(/sdk/decision)  │  │
│  └───────────────────────┘   └─────────────────────────┘   └─────────────────┘  │
│                                                                                 │
│  ┌───────────────────────┐   ┌─────────────────────────┐   ┌─────────────────┐  │
│  │  Graph Intelligence   │   │ Threat Correlation SOC  │   │ Developer Portal│  │
│  │   (Mule Cluster Detection)│  │ (WebSocket Stream Stream) │   │ & React Dashboard│ │
│  └───────────────────────┘   └─────────────────────────┘   └─────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Telemetry & Integration Sequence Diagram

```
User App                  Fusion SDK                  FastAPI Backend                SOC Dashboard
   │                           │                             │                             │
   │─── Login Request ────────►│                             │                             │
   │                           │─── POST /sdk/device ───────►│                             │
   │                           │─── POST /sdk/session/start ►│                             │
   │                           │◄── Session ID & Trust ──────│                             │
   │                           │─── Connect /ws/stream ─────►│                             │
   │◄── Navigation (Home) ─────│                             │                             │
   │                           │─── POST /sdk/event ────────►│─── Stream Event Timeline ──►│
   │                           │   (HOME_VISITED)            │                             │
   │─── Perform Transfer ─────►│                             │                             │
   │                           │─── POST /sdk/request-dec ──►│                             │
   │                           │◄── Decision: ALLOW / BLOCK ─│                             │
   │◄── Show Result Dialog ────│                             │                             │
```

---

## 3. Endpoints & API Mapping

| Action | Telemetry / Endpoint | Method | Payload / Request Data |
| :--- | :--- | :--- | :--- |
| **App Splash / Launch** | Security Attestation Scan | Local | Root, Emulator, Frida, Debugger Checks |
| **Login** | `/sdk/session/start` | `POST` | `{ app_id, tenant_id, sdk_version, user_id, device_id, environment }` |
| **Device Attestation** | `/sdk/device` | `POST` | `{ device_id, model, manufacturer, android_version, security_patch, root_detected, emulator_detected, ... }` |
| **Network Attestation** | `/sdk/network` | `POST` | `{ session_id, network_type, carrier, vpn_detected, proxy_detected, roaming }` |
| **Home Navigation** | `/sdk/event` | `POST` | `{ session_id, device_id, event_type: "HOME_VISITED" }` |
| **Fund Transfer** | `/sdk/request-decision` | `POST` | `{ session_id, event_type: "TRANSFER_INITIATED", amount, composite_trust }` |
| **Add Beneficiary** | `/sdk/event` | `POST` | `{ session_id, device_id, event_type: "BENEFICIARY_ADDED" }` |
| **QR Merchant Pay** | `/sdk/event` | `POST` | `{ session_id, device_id, event_type: "QR_PAYMENT", amount }` |
| **Utility Bill Pay** | `/sdk/event` | `POST` | `{ session_id, device_id, event_type: "BILL_PAYMENT", amount }` |
| **Realtime Stream** | `/ws/stream` | `WS` | Continuous bidirectional WebSocket telemetry & pipeline updates |
| **Session Termination**| `/sdk/event` | `POST` | `{ event_type: "SESSION_ENDED" }` + WS Disconnect + Clear Storage |

---

## 4. Setup & Build Guide

### Prerequisites
- JDK 17+ (Java 21 supported)
- Android Studio Hedgehog / Iguana / Jellyfish or Gradle 8.2+

### Building Debug & Release Binaries

```bash
# Navigate to the reference bank directory
cd fusion-reference-bank

# Build Debug APK
./gradlew assembleDebug

# Build Release APK
./gradlew assembleRelease

# Build Android App Bundle (AAB)
./gradlew bundleRelease
```

The compiled APK outputs will be generated in:
- Debug APK: `app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `app/build/outputs/apk/release/app-release.apk`
- Release AAB: `app/build/outputs/bundle/release/app-release.aab`
