import time
import datetime
import random
import hashlib
import uuid
from typing import Dict, List, Any

# SDK DEFAULT ADAPTIVE POLICIES
DEFAULT_POLICIES = [
    {
        "id": "POL_001",
        "name": "High-Value Transfer Biometric Requirement",
        "trigger": "transfer_amount > 50000",
        "action": "REQUIRE_BIOMETRIC",
        "priority": "HIGH",
        "active": True,
        "version": "1.0.3"
    },
    {
        "id": "POL_002",
        "name": "Rooted Device Block Policy",
        "trigger": "device_root_detected == true",
        "action": "BLOCK_SESSION",
        "priority": "CRITICAL",
        "active": True,
        "version": "1.0.3"
    },
    {
        "id": "POL_003",
        "name": "VPN Challenge Policy",
        "trigger": "vpn_detected == true AND transfer_amount > 10000",
        "action": "REQUIRE_OTP",
        "priority": "MEDIUM",
        "active": True,
        "version": "1.0.3"
    },
    {
        "id": "POL_004",
        "name": "Runtime Tamper Session Termination",
        "trigger": "runtime_trust_score < 30",
        "action": "TERMINATE_SESSION",
        "priority": "CRITICAL",
        "active": True,
        "version": "1.0.3"
    },
    {
        "id": "POL_005",
        "name": "Session Idle Re-Authentication",
        "trigger": "idle_time_seconds > 600",
        "action": "REQUIRE_FACE_AUTHENTICATION",
        "priority": "MEDIUM",
        "active": True,
        "version": "1.0.3"
    }
]

# SDK ERROR CODES
ERROR_CODES = {
    "SDK_001": "Invalid API Key",
    "SDK_002": "Session Not Found",
    "SDK_003": "Invalid Event Type",
    "SDK_004": "Trust Passport Expired",
    "SDK_005": "Device Attestation Failed",
    "SDK_006": "Policy Engine Unavailable",
    "SDK_007": "Event Queue Full",
    "SDK_008": "Runtime Integrity Failure",
    "SDK_009": "Network Trust Degraded",
    "SDK_010": "Decision Timeout"
}

class FusionAdaptiveTrustSDKEngine:
    """
    Fusion Adaptive Trust SDK Engine (FAT-SDK) — Backend Platform Layer.
    Manages SDK sessions, device profiles, runtime integrity, behavioural intelligence,
    network trust, event streaming, adaptive policy engine, and real-time Trust Passport sync.
    """
    def __init__(self):
        self.sdk_sessions: Dict[str, dict] = {}
        self.device_profiles: Dict[str, dict] = {}
        self.event_log: List[dict] = []
        self.policies: List[dict] = DEFAULT_POLICIES
        self.policy_version: str = "1.0.3"
        self.connected_apps: List[dict] = [
            {
                "app_id": "com.fusionbank.mobileapp",
                "name": "Fusion National Bank Mobile",
                "platform": "Android 14",
                "sdk_version": "FAT-SDK v2.4.1",
                "status": "CONNECTED",
                "last_heartbeat": "2026-07-22 22:09:40 IST",
                "events_today": 1482,
                "trust_sessions": 94
            },
            {
                "app_id": "com.glbbank.android",
                "name": "Global Bank Enterprise App",
                "platform": "Android 13",
                "sdk_version": "FAT-SDK v2.4.1",
                "status": "CONNECTED",
                "last_heartbeat": "2026-07-22 22:08:12 IST",
                "events_today": 892,
                "trust_sessions": 57
            },
            {
                "app_id": "com.apexbank.retail",
                "name": "Apex Retail Banking App",
                "platform": "iOS 17.4",
                "sdk_version": "FAT-SDK v2.4.1",
                "status": "DEGRADED_LATENCY",
                "last_heartbeat": "2026-07-22 22:07:55 IST",
                "events_today": 234,
                "trust_sessions": 21
            }
        ]

    # MODULE 1: SDK Session Management
    def start_session(self, data: dict) -> dict:
        session_id = f"SDK_SESS_{uuid.uuid4().hex[:16].upper()}"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        session = {
            "session_id": session_id,
            "app_id": data.get("app_id", "com.fusionbank.mobileapp"),
            "tenant_id": data.get("tenant_id", "TENANT_FUSB_001"),
            "sdk_version": data.get("sdk_version", "FAT-SDK v2.4.1"),
            "user_id": data.get("user_id", "usr_sdk_demo"),
            "device_id": data.get("device_id", f"DEV_{random.randint(10000, 99999)}"),
            "environment": data.get("environment", "PRODUCTION"),
            "started_at": ts,
            "status": "ACTIVE",
            "policy_version": self.policy_version,
            "composite_trust_score": 82.0,
            "device_trust": 88.0,
            "session_trust": 85.0,
            "behaviour_trust": 79.0,
            "network_trust": 91.0,
            "runtime_trust": 94.0
        }
        self.sdk_sessions[session_id] = session
        return session

    # MODULE 2 & 3: Device Intelligence & Runtime Integrity
    def register_device(self, data: dict) -> dict:
        device_id = data.get("device_id", f"DEV_{random.randint(10000, 99999)}")
        root_detected = data.get("root_detected", False)
        emulator = data.get("emulator_detected", False)
        frida_detected = data.get("frida_detected", False)
        debugger = data.get("debugger_attached", False)
        overlay = data.get("overlay_detected", False)

        # Risk score calculation
        risk_deductions = (
            (30 if root_detected else 0) +
            (25 if emulator else 0) +
            (40 if frida_detected else 0) +
            (20 if debugger else 0) +
            (15 if overlay else 0)
        )
        device_trust = max(10.0, 100.0 - risk_deductions)
        runtime_trust = max(5.0, 100.0 - (20 if frida_detected else 0) - (10 if debugger else 0))

        device_profile = {
            "device_id": device_id,
            "model": data.get("model", "Samsung Galaxy S24"),
            "manufacturer": data.get("manufacturer", "Samsung"),
            "android_version": data.get("android_version", "14"),
            "security_patch": data.get("security_patch", "2026-07-01"),
            "app_version": data.get("app_version", "5.2.1"),
            "fingerprint": hashlib.sha256(device_id.encode()).hexdigest()[:32],
            "screen_lock_enabled": data.get("screen_lock_enabled", True),
            "root_detected": root_detected,
            "emulator_detected": emulator,
            "play_integrity_status": "MEETS_DEVICE_INTEGRITY" if not root_detected else "FAILS_BASIC_INTEGRITY",
            "frida_detected": frida_detected,
            "debugger_attached": debugger,
            "overlay_detected": overlay,
            "timezone": data.get("timezone", "Asia/Kolkata"),
            "locale": data.get("locale", "en_IN"),
            "device_trust_score": round(device_trust, 1),
            "runtime_trust_score": round(runtime_trust, 1),
            "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

        self.device_profiles[device_id] = device_profile
        return device_profile

    # MODULE 6: Network Intelligence
    def register_network(self, data: dict) -> dict:
        vpn_detected = data.get("vpn_detected", False)
        proxy_detected = data.get("proxy_detected", False)
        network_trust = 100.0 - (15 if vpn_detected else 0) - (20 if proxy_detected else 0)
        return {
            "network_type": data.get("network_type", "CELLULAR_5G"),
            "carrier": data.get("carrier", "Jio"),
            "asn": data.get("asn", "AS55836"),
            "vpn_detected": vpn_detected,
            "proxy_detected": proxy_detected,
            "roaming": data.get("roaming", False),
            "wifi_vs_cellular": data.get("wifi_vs_cellular", "CELLULAR"),
            "network_trust_score": round(max(20.0, network_trust), 1),
            "assessed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

    # MODULE 7: Event Engine
    def ingest_event(self, event: dict) -> dict:
        t0 = time.perf_counter()
        event_id = f"EVT_{uuid.uuid4().hex[:12].upper()}"
        enriched_event = {
            "event_id": event_id,
            "session_id": event.get("session_id", "SDK_SESS_DEMO"),
            "device_id": event.get("device_id", "DEV_DEMO"),
            "event_type": event.get("event_type", "UNKNOWN"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "trust_metadata": {
                "composite_trust": event.get("composite_trust", 82.0),
                "event_risk_modifier": self._get_risk_modifier(event.get("event_type", "")),
                "policy_triggered": self._check_policy_trigger(event)
            },
            "sdk_version": event.get("sdk_version", "FAT-SDK v2.4.1"),
            "ingestion_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2)
        }
        self.event_log.append(enriched_event)
        if len(self.event_log) > 500:
            self.event_log = self.event_log[-500:]
        return enriched_event

    def _get_risk_modifier(self, event_type: str) -> float:
        modifiers = {
            "BENEFICIARY_ADDED": -8.0,
            "TRANSFER_INITIATED": -5.0,
            "OVERLAY_DETECTED": -25.0,
            "RUNTIME_THREAT": -30.0,
            "VPN_ENABLED": -10.0,
            "USER_LOGIN": 0.0,
            "QR_SCAN": -3.0,
        }
        return modifiers.get(event_type, 0.0)

    def _check_policy_trigger(self, event: dict) -> str | None:
        event_type = event.get("event_type", "")
        amount = float(event.get("amount", 0))
        if amount > 50000 and event_type == "TRANSFER_INITIATED":
            return "POL_001"
        if event_type == "OVERLAY_DETECTED":
            return "POL_002"
        return None

    # MODULE 10: Decision API
    def request_decision(self, data: dict) -> dict:
        t0 = time.perf_counter()
        session_id = data.get("session_id", "SDK_SESS_DEMO")
        amount = float(data.get("amount", 0))
        event_type = data.get("event_type", "TRANSFER")
        composite_trust = float(data.get("composite_trust", 82.0))
        vpn = data.get("vpn_detected", False)
        root = data.get("root_detected", False)
        runtime_trust = float(data.get("runtime_trust", 94.0))

        if root:
            decision = "BLOCK_TRANSACTION"
            reason_codes = ["DEVICE_ROOT_DETECTED", "PLAY_INTEGRITY_FAILED"]
            confidence = 99.0
        elif runtime_trust < 30:
            decision = "TERMINATE_SESSION"
            reason_codes = ["RUNTIME_INTEGRITY_FAILURE", "FRIDA_INSTRUMENTATION_DETECTED"]
            confidence = 97.0
        elif amount > 50000 and composite_trust < 75:
            decision = "REQUIRE_FACE_AUTHENTICATION"
            reason_codes = ["HIGH_VALUE_TRANSFER", "BELOW_TRUST_THRESHOLD"]
            confidence = 91.0
        elif amount > 50000:
            decision = "REQUIRE_BIOMETRIC"
            reason_codes = ["HIGH_VALUE_TRANSFER_POL_001"]
            confidence = 88.0
        elif vpn and amount > 10000:
            decision = "REQUIRE_OTP"
            reason_codes = ["VPN_DETECTED_POL_003", "ELEVATED_NETWORK_RISK"]
            confidence = 84.0
        elif composite_trust >= 80:
            decision = "ALLOW"
            reason_codes = ["COMPOSITE_TRUST_ACCEPTABLE", "NO_POLICY_VIOLATIONS"]
            confidence = 92.0
        else:
            decision = "HOLD_TRANSACTION"
            reason_codes = ["TRUST_BELOW_THRESHOLD", "MANUAL_REVIEW_REQUIRED"]
            confidence = 77.0

        return {
            "decision_id": f"DEC_{uuid.uuid4().hex[:12].upper()}",
            "session_id": session_id,
            "decision": decision,
            "confidence": confidence,
            "reason_codes": reason_codes,
            "recommended_action": f"Apply {decision.replace('_', ' ').title()} for event: {event_type}",
            "policy_version": self.policy_version,
            "decision_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2)
        }

    # MODULE 9: Adaptive Policies
    def get_policies(self) -> dict:
        return {"policies": self.policies, "policy_version": self.policy_version}

    # MODULE 11: Trust Passport Sync
    def get_trust_passport(self, session_id: str) -> dict:
        session = self.sdk_sessions.get(session_id, {})
        return {
            "session_id": session_id,
            "composite_trust": session.get("composite_trust_score", 82.0),
            "device_trust": session.get("device_trust", 88.0),
            "session_trust": session.get("session_trust", 85.0),
            "behaviour_trust": session.get("behaviour_trust", 79.0),
            "network_trust": session.get("network_trust", 91.0),
            "runtime_trust": session.get("runtime_trust", 94.0),
            "policy_version": self.policy_version,
            "sync_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

    # MODULE 18: Observability / SDK Health
    def get_observability(self) -> dict:
        total_events = len(self.event_log)
        active_sessions = sum(1 for s in self.sdk_sessions.values() if s.get("status") == "ACTIVE")
        return {
            "sdk_health": "HEALTHY",
            "connection_status": "CONNECTED",
            "active_sessions": active_sessions or 3,
            "queued_events": random.randint(0, 5),
            "total_events_processed": total_events,
            "average_latency_ms": round(random.uniform(0.8, 2.4), 2),
            "dropped_events": 0,
            "policy_version": self.policy_version,
            "trust_sync_status": "SYNCHRONIZED",
            "connected_apps": len(self.connected_apps),
            "assessed_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

    def get_connected_apps(self) -> List[dict]:
        return self.connected_apps

    def get_live_event_stream(self) -> List[dict]:
        return self.event_log[-20:][::-1]

    def get_error_codes(self) -> dict:
        return ERROR_CODES

sdk_engine = FusionAdaptiveTrustSDKEngine()
