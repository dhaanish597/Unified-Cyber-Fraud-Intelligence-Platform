# Phase 1 Implementation Plan — Fusion Reference Banking APK & Fusion Adaptive Trust SDK Integration

## 1. Executive Summary & Purpose

This document outlines the detailed architecture, engineering specification, API contracts, execution roadmap, risk matrix, and validation criteria for **Phase 1: Official Android Reference Banking Application (`fusion-reference-bank`) and Fusion Adaptive Trust SDK (FAT-SDK) Integration**.

The reference banking application is a production-grade Android application built with **Modern Kotlin, Jetpack Compose, Material 3, MVVM Architecture, Hilt Dependency Injection, Retrofit, OkHttp WebSockets, Coroutines, StateFlow, and Jetpack Security**. It serves as the official reference implementation for financial institutions integrating Fusion Risk OS.

**Core Directive:**
- **Zero modification** to existing backend services (`api/`), decision engines, Trust Passport, Developer Portal, or React Dashboard (`web/`).
- **Live backend communication:** All authentication, device registration, event streaming, decision requests, policy sync, and WebSockets interact directly with the running FastAPI backend (`http://<host>:8001`).
- **Real-time telemetry:** Every user flow (login, navigation, transfer, beneficiary addition, QR payment, bill payment, logout) streams telemetry directly into Fusion Risk OS.

---

## 2. Current Architecture & System Inspection

Following an exhaustive audit of the existing repository:

### 2.1 Existing Backend System Components (`/api`)
1. **SDK Engine (`api/sdk_engine.py`)**: Manages SDK sessions, device profiles, runtime integrity attestation, network trust, event ingestion, adaptive policy engine, and Trust Passport sync.
2. **Session Intelligence Engine (`api/session_intelligence_engine.py`)**: Executes the 6-checkpoint pre-transaction pipeline (Identity, Device, Session, Behavior, Cyber Threat, Graph) and issues Session Trust Passports.
3. **Risk Engine (`api/risk_engine.py`)**: Fuses tabular fraud models (XGBoost), graph models (GraphSAGE/centrality), and cyber threat context to evaluate transaction requests.
4. **WebSocket Stream (`api/main.py: /ws/stream`)**: Pushes real-time transaction streams, pipeline stage execution updates, and SOC timeline events.
5. **Trust Fabric & Quantum Layer (`api/trust_fabric_engine.py`, `api/quantum_trust_layer.py`)**: Handles quantum-safe cipher posture, zero-trust token issuance, and SOC alert orchestration.

### 2.2 Endpoint Contracts

| Method | Path | Description | Payload / Query |
| :--- | :--- | :--- | :--- |
| `POST` | `/sdk/session/start` | Starts FAT-SDK session & returns session trust state | `{ app_id, tenant_id, sdk_version, user_id, device_id, environment }` |
| `POST` | `/sdk/device` | Registers device posture & security integrity checks | `{ device_id, model, manufacturer, android_version, security_patch, screen_lock_enabled, root_detected, emulator_detected, frida_detected, debugger_attached, overlay_detected, timezone, locale }` |
| `POST` | `/sdk/network` | Registers network environment & VPN/proxy telemetry | `{ session_id, network_type, carrier, vpn_detected, proxy_detected, roaming, wifi_vs_cellular }` |
| `POST` | `/sdk/event` | Ingests real-time behavioral telemetry event | `{ session_id, device_id, event_type, amount, composite_trust, sdk_version }` |
| `POST` | `/sdk/request-decision` | Requests real-time policy & risk decision for action | `{ session_id, event_type, amount, composite_trust, vpn_detected, root_detected, runtime_trust }` |
| `GET` | `/sdk/policies` | Fetches active adaptive security policies | None |
| `GET` | `/sdk/passport` | Retrieves real-time Session Trust Passport | `?session_id=<SDK_SESS_ID>` |
| `GET` | `/sdk/health` | Fetches SDK health & latency metrics | None |
| `WS` | `/ws/stream` | Persistent WebSocket for real-time events & decisions | WebSocket binary/JSON stream |

---

## 3. Reference Banking Application Architecture (`fusion-reference-bank`)

### 3.1 Tech Stack & Guidelines
- **Language**: Kotlin 1.9+ (Modern idiomatic Kotlin)
- **UI Framework**: Jetpack Compose + Material Design 3 (Dark & Light Theme support)
- **Architecture Pattern**: MVVM (Model-View-ViewModel) + Repository Pattern + Clean Architecture
- **Dependency Injection**: Hilt / Dagger
- **Asynchronous Flow**: Kotlin Coroutines + `StateFlow` / `SharedFlow`
- **Networking**: Retrofit 2 + OkHttp 4 (with WebSocket listener & logging interceptors)
- **Security & Storage**: Jetpack Security (`EncryptedSharedPreferences`), Certificate Pinning, Network Security Config, ProGuard optimization rules
- **Offline Event Queue**: Room Database / Encrypted Persistent Queue with network status listener & automatic retry sync

---

### 3.2 Application Flow & Navigation Map

```
[Splash Screen]
       │
       ▼
[Secure Login Screen] ──(Authentication + Fusion.startSession() + WS Connect)──► [Home Dashboard]
                                                                                       │
         ┌───────────────────┬───────────────────┬───────────────────┬─────────────────┼──────────────────┐
         │                   │                   │                   │                 │                  │
         ▼                   ▼                   ▼                   ▼                 ▼                  ▼
[Accounts Screen]   [Transfer Screen]   [Beneficiary Screen]  [QR Payment]   [Bill Payment]   [Profile Screen]
                             │                   │                   │                 │                  │
                    (Request Decision)   (Report Event)      (Report Event)    (Report Event)             │
                             │                   │                   │                 │                  │
                             └───────────────────┴───────────────────┴─────────────────┴──────────────────┘
                                                                                       │
                                                                                       ▼
                                                                                [Logout Flow]
                                                                          (Fusion.endSession() + Clear Storage)
```

---

### 3.3 Embedded Fusion Adaptive Trust SDK (`com.fusionbank.sdk`)

The SDK component will be structured clean and isolated inside `com.fusionbank.sdk`, wrapping all communication with Fusion Risk OS:

```kotlin
object Fusion {
    fun initialize(config: FusionConfig)
    fun startSession(userId: String, onResult: (Result<SessionState>) -> Unit)
    fun reportEvent(eventType: String, amount: Double = 0.0, extra: Map<String, Any> = emptyMap())
    fun requestDecision(actionType: String, amount: Double = 0.0, callback: (DecisionResult) -> Unit)
    fun getTrustPassport(): StateFlow<TrustPassport?>
    fun endSession()
    fun shutdown()
}
```

#### Event Telemetry Mapping:
- **LOGIN**: `SESSION_STARTED` & `USER_LOGIN`
- **HOME DASHBOARD**: `HOME_VISITED`
- **TRANSFER**: `TRANSFER_INITIATED` (Triggers `/sdk/request-decision`)
- **BENEFICIARY**: `BENEFICIARY_ADDED`
- **QR PAYMENT**: `QR_PAYMENT`
- **BILL PAYMENT**: `BILL_PAYMENT`
- **LOGOUT**: `SESSION_ENDED`

---

### 3.4 Persistent Live Status Card UI Component

Every primary view features the **Fusion Adaptive Trust Status Bar / Card**, displaying:
- **Connection Status**: Green Dot (Connected) / Yellow Dot (Syncing) / Red Dot (Offline/Disconnected)
- **SDK Version**: `FAT-SDK v2.4.1`
- **Session ID**: Active session string (e.g. `SDK_SESS_A1B2C3D4`)
- **Trust Passport Status**: Composite Trust Score (e.g., `82.0` - `ALLOW`)
- **Active Policy Version**: `v1.0.3`
- **Latency & Last Sync Time**: `12ms | Just now`

---

## 4. Files to be Created & Modified

### 4.1 Existing System Modifications
- **Zero modifications** to existing `api/` Python code, `web/` React frontend, `ml/` models, or `data/`.

### 4.2 New Files to be Created (`fusion-reference-bank/`)

```
fusion-reference-bank/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── proguard-rules.pro
├── app/
│   ├── build.gradle.kts
│   ├── proguard-rules.pro
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── res/
│       │   │   ├── xml/network_security_config.xml
│       │   │   ├── values/colors.xml, strings.xml, themes.xml
│       │   │   └── drawable/
│       │   └── java/com/fusionbank/mobileapp/
│       │       ├── FusionBankApp.kt
│       │       ├── di/ (AppModule, NetworkModule, DatabaseModule)
│       │       ├── sdk/ (Fusion SDK Layer)
│       │       │   ├── Fusion.kt
│       │       │   ├── FusionConfig.kt
│       │       │   ├── models/ (SDKSession, DeviceProfile, NetworkProfile, SDKEvent, TrustDecision, TrustPassport)
│       │       │   ├── network/ (FusionApiService, FusionWebSocketManager)
│       │       │   ├── queue/ (OfflineEventQueueManager, EventEntity, EventDao, AppDatabase)
│       │       │   └── security/ (DeviceAttestationEngine, SecureStorage)
│       │       ├── data/ (Repositories & Data Sources)
│       │       ├── ui/
│       │       │   ├── theme/ (Theme.kt, Color.kt, Type.kt)
│       │       │   ├── components/ (LiveStatusCard.kt, ActionButton.kt, TopAppBar.kt)
│       │       │   ├── screens/
│       │       │   │   ├── splash/SplashScreen.kt
│       │       │   │   ├── login/LoginScreen.kt, LoginViewModel.kt
│       │       │   │   ├── dashboard/DashboardScreen.kt, DashboardViewModel.kt
│       │       │   │   ├── accounts/AccountsScreen.kt
│       │       │   │   ├── transfer/TransferScreen.kt, TransferViewModel.kt
│       │       │   │   ├── beneficiary/BeneficiaryScreen.kt, BeneficiaryViewModel.kt
│       │       │   │   ├── qr/QrPaymentScreen.kt, QrViewModel.kt
│       │       │   │   ├── bill/BillPaymentScreen.kt, BillViewModel.kt
│       │       │   │   └── profile/ProfileScreen.kt, ProfileViewModel.kt
│       │       │   └── navigation/NavGraph.kt
│       └── test/ & androidTest/
```

---

## 5. Execution Roadmap

1. **Phase 1.1: Project Skeleton Initialization**: Setup Gradle project structure, dependencies (Hilt, Jetpack Compose, Retrofit, OkHttp, Room, Security).
2. **Phase 1.2: Fusion SDK Core Engine (`com.fusionbank.sdk`)**: Build device attestation scanner, secure storage, model definitions, and API client.
3. **Phase 1.3: Networking & WebSocket Infrastructure**: Implement Retrofit services for `/sdk/*` endpoints and OkHttp WebSocket client for `/ws/stream` with exponential reconnect logic.
4. **Phase 1.4: Offline Storage & Resilient Event Queue**: Build Room DB offline queue that caches unsent events when offline and flushes them automatically upon network restoration.
5. **Phase 1.5: UI Layer Implementation (Material 3 Jetpack Compose)**: Implement all 9 application screens with dark/light theme support and the persistent Live Status Card.
6. **Phase 1.6: Build Verification & Deliverables**: Verify Kotlin compilation, build Debug APK, Release APK, AAB bundle, generate architectural diagrams and README guides.

---

## 6. Risk Analysis & Mitigation

| Risk Category | Potential Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Backend Unavailability** | App unable to perform live API calls | SDK fallback to local offline event queue & graceful retry states |
| **WebSocket Connection Drop** | Loss of real-time Trust Passport stream | Automatic reconnect with exponential backoff & heartbeat pinging |
| **Security / Tampering Risk** | Hardcoded credentials or insecure storage | Jetpack EncryptedSharedPreferences, Certificate Pinning, zero secrets in source |
| **Data Integrity in Offline Queue** | Out-of-order events during sync | Monotonic millisecond timestamps & transactional queue processing |

---

## 7. Rollback & Recovery Strategy

- **Isolated Directory**: All new code is self-contained within `fusion-reference-bank/` and `PHASE1_IMPLEMENTATION_PLAN.md`.
- **Zero Impact on Root Code**: If rollback is necessary, removing `fusion-reference-bank/` completely restores the repository to its exact prior state.
