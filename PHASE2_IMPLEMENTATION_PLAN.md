# Phase 2 Implementation Plan — Enterprise Cyber Threat Intelligence Engine

## 1. Executive Summary & Architecture Overview

Phase 2 builds the **Enterprise Cyber Threat Intelligence Engine** for **Fusion Risk OS**. 

While Phase 1 established the Android Reference Banking Application (`fusion-reference-bank`), embedded Fusion Adaptive Trust SDK (`FAT-SDK`), live FastAPI backend, and Cyber Attack Simulator, Phase 2 implements the automated backend intelligence pipeline that converts raw incoming SDK events into structured, evidence-backed, correlated **Cyber Threat Objects**.

### 1.1 Enterprise Threat Processing Pipeline

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│  SDK / Simulator│────►│  Event Normalizer   │────►│ Threat Detection     │
│  Event Payload  │     │  & Schema Evaluator │     │ Engine (9 Categories)│
└─────────────────┘     └─────────────────────┘     └──────────┬───────────┘
                                                               │
┌─────────────────┐     ┌─────────────────────┐                ▼
│ Realtime SOC    │◄────│ WebSocket Broadcast │◄────┌──────────────────────┐
│ React Dashboard │     │    (/ws/stream)     │     │ Threat Correlation   │
└─────────────────┘     └─────────────────────┘     │ & Evidence Engine    │
                                                    └──────────┬───────────┘
                                                               │
                                                               ▼
                                                    ┌──────────────────────┐
                                                    │ Structured Threat    │
                                                    │ Object & Store       │
                                                    └──────────────────────┘
```

---

## 2. Current Event Flow vs. Phase 2 Enhanced Threat Flow

### Current Event Flow (Phase 1)
1. APK / Simulator emits `/sdk/event` or `/sdk/device` or `/sdk/network`.
2. `api/sdk_engine.py` receives request, appends simple event dictionary to in-memory `event_log`.
3. `api/main.py` streams generic event frame over `/ws/stream`.

### Enhanced Cyber Threat Flow (Phase 2)
1. SDK Event arrives via HTTP POST (`/sdk/event`, `/sdk/device`, `/sdk/network`, `/sdk/request-decision`, or `/threats/evaluate`).
2. **Normalization Engine**: Standardizes raw telemetry into canonical attributes (IP, ASN, device flags, timestamps, user session).
3. **Threat Detection Engine**: Evaluates 9 Enterprise Threat Categories against detection rules and historical baselines.
4. **Threat Correlation Engine**: Groups isolated threat signals into high-level attack campaigns (e.g. `Account Takeover`, `Social Engineering / Remote Control`, `Money Mule Ring`, `Malware Campaign`).
5. **Evidence & Confidence Engine**: Generates granular evidence arrays (e.g. `["ASN Changed to AS14061 (DigitalOcean)", "Known Commercial VPN IP", "Country Mismatch IN -> US"]`) and calculates dynamic confidence scores (0–100%) with explicit rationale.
6. **Trust Impact & Action Recommendation**: Determines trust deductions per domain and emits standardized recommendations (`ALLOW`, `REQUIRE_BIOMETRIC`, `REQUIRE_OTP`, `REQUIRE_FACE_AUTHENTICATION`, `BLOCK_TRANSACTION`, `TERMINATE_SESSION`).
7. **Realtime Broadcast & Storage**: Persists threat objects in SQLite/In-memory store and streams `{ msg_type: "cyber_threat", data: threat_obj }` via WebSocket to the React Dashboard.

---

## 3. Enterprise Threat Taxonomy (9 Categories)

| Category | Threats Included | Detection Logic & Attributes |
| :--- | :--- | :--- |
| **1. Device Threats** | Root, Magisk, Bootloader Unlocked, Unknown Sources, Emulator, Integrity Failure, OS Tampering, Fingerprint Change | Scans Play Integrity status, su binaries, build fingerprint anomalies, bootloader state |
| **2. Runtime Threats** | Debugger Attached, Frida, Xposed, Hooking, Memory Modification, Code Injection, Cert Pinning Failure, Native Lib Tampering | Inspects ptrace, memory maps, Frida default ports, runtime class hook detection |
| **3. Overlay Attacks** | Accessibility Abuse, Overlay Windows, Tapjacking, Screen Capture, Click Injection, Remote Control | Detects system window flags, active accessibility service overlays, screen recording APIs |
| **4. Network Threats** | VPN, TOR, Proxy, MITM, SSL Downgrade, IP Reputation Low, ASN Change, Public Wi-Fi | Evaluates network interfaces, known proxy/VPN ASNs, SSL handshake cipher posture |
| **5. Session Threats** | Session Replay, Concurrent Login, Session Hijack, Session Extension, Token Theft, Cookie Manipulation | Compares user-agent hashes, concurrent IP locations, session token issuance bounds |
| **6. Behaviour Threats** | Fast Typing, Robotic Touch, Rapid Navigation, Rapid Transfers, Multiple OTP, Beneficiary Abuse | Analyzes touch pressure variance, inter-tap delays, navigation velocity, OTP retry surges |
| **7. Identity Threats** | Credential Stuffing, Impossible Travel, Device Change, SIM Change, Location Spoofing, Identity Mismatch | Velocity checks on geofence bounds, SIM IMSI changes, impossible speed (>900 km/h) |
| **8. Transaction Threats**| Large Amount, Velocity Surge, Rapid Transfers, QR Abuse, Bill Fraud, Beneficiary Risk | High-value thresholds (>₹50,000), transfer frequency within 60s windows, mule accounts |
| **9. Graph Threats** | Money Mule, Shared Device, Shared Beneficiary, Circular Transfers, Fraud Ring | GraphSAGE / NetworkX node centrality, shared device-user degree count > 5 |

---

## 4. Structured Threat Object Model

Each detected threat is output as a strongly typed, structured enterprise JSON object:

```json
{
  "threat_id": "THR_89201A4F",
  "threat_name": "Active Accessibility & Window Overlay Hijacking",
  "threat_category": "Overlay Attacks",
  "severity": "CRITICAL",
  "confidence": 96.5,
  "confidence_explanation": "Detected active Accessibility Service overlay combined with unknown window overlay during transfer flow.",
  "evidence": [
    "Accessibility Service status: ENABLED (package: com.malware.remote.access)",
    "System Window Overlay detected over payment composables",
    "Screen capture flag disabled by external package"
  ],
  "session_id": "SDK_SESS_99182A",
  "device_id": "DEV_S24_9812",
  "user_id": "usr_sdk_demo",
  "timestamp": "2026-07-23 23:15:04 IST",
  "detection_source": "FAT-SDK Runtime Integrity & Overlay Guard",
  "trust_impact": {
    "device_trust": -30.0,
    "runtime_trust": -40.0,
    "behaviour_trust": -15.0
  },
  "recommended_action": "TERMINATE_SESSION",
  "status": "ACTIVE",
  "campaign_correlation": "Social Engineering / Remote Control Campaign"
}
```

---

## 5. Proposed File Changes

### 5.1 Backend Changes (`/api`)

#### [NEW] `api/cyber_threat_engine.py`
- Implements `CyberThreatEngine` class.
- Evaluates raw event payloads against the 9-category taxonomy.
- Performs threat correlation into composite attack campaigns.
- Calculates dynamic confidence scores, evidence arrays, and trust impact.
- Manages active and historical threat data store.

#### [MODIFY] `api/main.py`
- Register new `/threats` API routes:
  - `GET /threats` — List active/historical threats with filter & search support.
  - `GET /threats/{id}` — Get detailed threat object by ID.
  - `GET /threats/session/{session_id}` — Get threats for a specific session.
  - `GET /threats/device/{device_id}` — Get threats for a specific device.
  - `POST /threats/evaluate` — Ingest SDK event and evaluate threat taxonomy (<100ms).
  - `POST /threats/simulate` — Trigger threat simulation payload.
- Update `/sdk/event`, `/sdk/device`, `/sdk/network`, `/sdk/request-decision` to automatically invoke `CyberThreatEngine` and stream `{ msg_type: "cyber_threat" }` frames via WebSockets.

---

### 5.2 Frontend React Changes (`/web`)

#### [NEW] `web/src/pages/CyberThreatIntelligencePage.jsx`
- Main container page for Cyber Threat Intelligence.

#### [NEW] `web/src/components/threat/ThreatIntelligenceDashboard.jsx`
- Dedicated enterprise Threat Intelligence UI containing:
  1. **Threat Summary Cards**: Active Threats, Resolved Threats, Avg Detection Time (<100ms), Threats by Category, Threats by Severity, Confidence Distribution.
  2. **Interactive Filters & Search**: Search by name, session, device, evidence text. Filter by Severity, Category, Status, Time range.
  3. **Active Threats Table**: Displays Threat Name, Category, Severity Badge, Confidence %, Evidence Count, Timestamp, Status, Actions.
  4. **Threat Timeline Component**: Visual step-by-step timeline (`Time -> Threat -> Evidence -> Correlation -> Backend Action`).
  5. **Threat Details Modal**: Deep-dive modal showing complete evidence list, raw SDK payload, trust impact breakdown, and recommended response.
  6. **Threat Campaign Correlation View**: Highlights correlated attack patterns (`Account Takeover`, `Social Engineering`, `Money Mule Ring`).

#### [MODIFY] `web/src/App.jsx` & `web/src/components/layout/Sidebar.jsx`
- Add `/threats` route under "Fraud Intelligence" navigation section in Sidebar with `NEW` badge.

---

## 6. Execution Roadmap

1. **Phase 2.1: Core Backend Threat Engine (`api/cyber_threat_engine.py`)**: Implement 9-category taxonomy evaluators, evidence generator, confidence calculator, and correlation engine.
2. **Phase 2.2: FastAPI Threat APIs & WebSocket Integration (`api/main.py`)**: Add `/threats` REST endpoints and integrate threat broadcasting into `/ws/stream`.
3. **Phase 2.3: Frontend Threat Intelligence Dashboard (`web/src/...`)**: Build `CyberThreatIntelligencePage`, `ThreatIntelligenceDashboard`, filters, timeline, and detail modal.
4. **Phase 2.4: Simulator & Realtime Integration Verification**: Verify that triggering events in the Android APK / Cyber Attack Simulator immediately generates structured threats, broadcasts over WebSockets (<200ms), and updates the dashboard in real time.

---

## 7. Testing & Verification Strategy

- **Automated API Tests**: Unit tests in `api/test_cyber_threat_engine.py` verifying each of the 9 taxonomy rules, evidence generation, and confidence calculations.
- **End-to-End WebSocket Test**: Trigger Simulator event (`Overlay Attack`) -> verify `/sdk/event` triggers backend detection (<100ms) -> verify WebSocket frame received -> verify React Dashboard updates live.
- **Deduplication Check**: Ensure consecutive identical heartbeat events do not flood the system with duplicate alerts.

---

## 8. Rollback Strategy

- All Phase 2 additions are modular and isolated in `api/cyber_threat_engine.py` and `web/src/components/threat/`.
- Existing risk engines (`risk_engine.py`, `sdk_engine.py`) remain functional.
- If rollback is needed, removing `cyber_threat_engine.py` and reverting `main.py` routing restores the system to Phase 1 state without breaking core banking or SDK functionality.
