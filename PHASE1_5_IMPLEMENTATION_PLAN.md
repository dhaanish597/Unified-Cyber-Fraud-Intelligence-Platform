# Implementation Plan — Phase 1.5: Cyber Attack Simulator (Demo Control Panel)

## 1. Executive Summary & Purpose

Phase 1.5 adds an enterprise-grade **Cyber Attack Simulator ("Demo Control Panel")** inside the **Fusion Reference Banking APK (`fusion-reference-bank`)**.

This is **NOT** a debug screen or fake admin panel. It is an enterprise security testing tool designed for live demonstrations to banking executives and security leaders. It allows presenters to simulate realistic mobile threats, device compromises, runtime tampering, overlay attacks, network anomalies, session hijacks, and full attack campaigns.

**Core Principle:**
- Every simulation **MUST** use the official embedded **Fusion SDK** (`Fusion.reportEvent()`, `Fusion.requestDecision()`, `Fusion.registerDevice()`, `Fusion.registerNetwork()`, `Fusion.getTrustPassport()`).
- **NO** bypassed SDK calls. **NO** mocked dashboard state. **NO** fake calculations. All telemetry flows live:
  `APK -> Fusion SDK -> FastAPI Backend -> Session Intelligence -> Threat Correlation -> Trust Passport -> Decision Engine -> React Dashboard & App`.

---

## 2. Trigger & Hidden Access Mechanism

To ensure Demo Mode is never accessible during normal user operation:
- **Logo Secret Tap:** Tapping the Bank Logo 7 times in succession (in `TopAppBar`, `SplashScreen`, or `LoginScreen`).
- **Version Long-Press:** Long-pressing the app version string on the `ProfileScreen` for > 2 seconds.
- **Activation Notification:** Displays a styled banner / snackbar: `"Fusion Demo Mode Enabled"` and navigates directly to `Destinations.SIMULATOR`.

---

## 3. UI Layout & Component Specification (`SimulatorScreen.kt`)

The Cyber Attack Simulator is organized into 15 professional sections styled with Material 3 Dark Theme:

1. **Connection & System Health**: Displays Fusion Connection State (Green/Yellow/Red), SDK Version (`FAT-SDK v2.4.1`), Backend Health, Active Session ID, WebSocket State, and Live Latency.
2. **Device Security Controls**: Toggles for Rooted Device, Magisk Installed, Bootloader Unlocked, USB Debugging Enabled, Developer Options Enabled, Unknown Sources Enabled, Emulator, App Integrity Failure.
3. **Runtime Integrity Controls**: Toggles for Debugger Attached, Frida Detected, Xposed, Runtime Hooking, Memory Tampering, Code Injection, Native Library Modified, Certificate Pinning Failure.
4. **Overlay Attack Controls**: Toggles for Overlay Attack, Accessibility Abuse, Screen Recording, Screenshot Attempt, Tap Injection, Click Hijacking.
5. **Network Threat Controls**: Toggles for VPN Enabled, TOR, Proxy, Public WiFi, MITM Simulation, SSL Downgrade, IP Reputation Low.
6. **Session Attack Triggers**: Triggers for Session Hijack, Concurrent Login, Session Replay, Token Theft, Cookie Manipulation.
7. **Behaviour Simulation**: Sliders for Typing Speed, Touch Pressure, Navigation Speed, Transaction Urgency. Toggles for Robotic Behaviour, Unusual Navigation, Very Fast Transfer, Repeated OTP Attempts.
8. **Location Intelligence Triggers**: Triggers for Impossible Travel, Country Change, GPS Spoof, Location Disabled.
9. **Device Fingerprint Triggers**: Triggers for New Device, Fingerprint Changed, OS Updated, SIM Changed.
10. **Transaction Simulator**: Buttons for ₹500, ₹5,000, ₹50,000, ₹5,00,000 transfers + Multiple Transfers, Rapid Transfers, Beneficiary Added, QR Payment, Bill Payment, Card Payment.
11. **Threat Campaigns & Scenario Library**: One-click attack campaigns:
    - `Normal Customer`
    - `Account Takeover`
    - `Compromised Device`
    - `Insider Threat`
    - `Money Mule`
    - `Social Engineering`
    - `Malware Infection`
    - `QR Fraud`
    - `SIM Swap`
    - `Credential Stuffing`
12. **Live Event Stream**: Real-time log showing Timestamp, Generated Event, SDK Status, API status, WebSocket status, Backend ACK, and Latency.
13. **Trust Passport Preview**: Real-time breakdown of Identity, Device, Runtime, Behaviour, Network, Session, Graph, and Overall Trust scores.
14. **Decision Preview**: Real-time display of latest decision (`ALLOW`, `REQUIRE_BIOMETRIC`, `REQUIRE_OTP`, `REQUIRE_FACE_AUTHENTICATION`, `BLOCK_TRANSACTION`, `TERMINATE_SESSION`), confidence %, reason codes, and recommended action.
15. **Developer Logs**: Expandable JSON viewer for raw API requests, responses, and WebSocket frames.

---

## 4. Proposed File Changes

### [NEW] Component: Cyber Attack Simulator Module (`com.fusionbank.mobileapp.ui.screens.simulator`)

- [NEW] [SimulatorViewModel.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/simulator/SimulatorViewModel.kt) — State management, attack campaign orchestrator, SDK event dispatching
- [NEW] [SimulatorScreen.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/simulator/SimulatorScreen.kt) — 15-section Material 3 Dark theme UI
- [NEW] [DemoScenarioLibrary.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/simulator/DemoScenarioLibrary.kt) — Pre-defined campaign scenarios

### [MODIFY] Existing Files
- [MODIFY] [NavGraph.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/navigation/NavGraph.kt) — Add `Destinations.SIMULATOR` route.
- [MODIFY] [LiveStatusCard.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/components/LiveStatusCard.kt) — Add 7-tap gesture trigger on shield logo to launch Demo Mode.
- [MODIFY] [ProfileScreen.kt](file:///c:/Users/motis/Downloads/fastapi/Unified-Cyber-Fraud-Intelligence-Platform/fusion-reference-bank/app/src/main/java/com/fusionbank/mobileapp/ui/screens/profile/ProfileScreen.kt) — Add long-press trigger on SDK Version string to launch Demo Mode.

---

## 5. Verification Plan

1. **Hidden Activation Verification:**
   - Tap app logo 7 times -> confirm toast `"Fusion Demo Mode Enabled"` -> confirm screen opens `Cyber Attack Simulator`.
   - Long press version string in Profile -> confirm activation.
2. **SDK Telemetry Verification:**
   - Click `"Overlay Attack"` -> verify event `OVERLAY_DETECTED` sent via `Fusion.reportEvent()` -> verify backend `/sdk/event` response received with ACK.
   - Click `"Account Takeover"` campaign -> verify sequence of events (`IMPOSSIBLE_TRAVEL`, `NEW_DEVICE`, `VPN_ENABLED`, `TRANSFER_INITIATED`) dispatched through SDK.
   - Submit decision request -> verify decision preview card updates live with decision (`BLOCK_TRANSACTION` / `REQUIRE_BIOMETRIC`).
3. **Dashboard Realtime Sync:**
   - Verify events and decisions stream live over `/ws/stream` and appear on the React SOC Dashboard.
