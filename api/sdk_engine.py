import time
import datetime
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
        self.ingestion_latencies: List[float] = []
        self.policies: List[dict] = DEFAULT_POLICIES
        self.policy_version: str = "1.0.3"
        self.connected_apps: List[dict] = []

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
            "device_id": data.get("device_id") or f"DEV_{uuid.uuid4().hex[:8].upper()}",
            "environment": data.get("environment", "PRODUCTION"),
            "started_at": ts,
            "status": "ACTIVE",
            "policy_version": self.policy_version,
            "composite_trust_score": None,
            "device_trust": None,
            "session_trust": None,
            "behaviour_trust": None,
            "network_trust": None,
            "runtime_trust": None,
            "trust_status": "PENDING_AUTHORITATIVE_EVIDENCE",
        }
        self.sdk_sessions[session_id] = session
        app = next(
            (item for item in self.connected_apps if item["app_id"] == session["app_id"]),
            None,
        )
        if app is None:
            app = {
                "app_id": session["app_id"],
                "name": session["app_id"],
                "platform": "Android",
                "sdk_version": session["sdk_version"],
                "status": "CONNECTED",
                "last_heartbeat": ts,
                "events_today": 0,
                "trust_sessions": 0,
            }
            self.connected_apps.append(app)
        app["last_heartbeat"] = ts
        app["trust_sessions"] += 1
        return session

    # MODULE 2 & 3: Device Intelligence & Runtime Integrity
    def register_device(self, data: dict) -> dict:
        device_id = data.get("device_id") or f"DEV_{uuid.uuid4().hex[:8].upper()}"
        root_detected = data.get("root_detected", False)
        emulator = data.get("emulator_detected", False)
        frida_detected = data.get("frida_detected", False)
        debugger = data.get("debugger_attached", False)
        overlay = data.get("overlay_detected", False)

        device_profile = {
            "device_id": device_id,
            "model": data.get("model"),
            "manufacturer": data.get("manufacturer"),
            "android_version": data.get("android_version"),
            "security_patch": data.get("security_patch"),
            "app_version": data.get("app_version"),
            "fingerprint": hashlib.sha256(device_id.encode()).hexdigest()[:32],
            "screen_lock_enabled": data.get("screen_lock_enabled"),
            "root_detected": root_detected,
            "emulator_detected": emulator,
            "play_integrity_status": "NOT_EVALUATED",
            "frida_detected": frida_detected,
            "debugger_attached": debugger,
            "overlay_detected": overlay,
            "timezone": data.get("timezone"),
            "locale": data.get("locale"),
            "device_trust_score": None,
            "runtime_trust_score": None,
            "trust_status": "PENDING_AUTHORITATIVE_EVIDENCE",
            "registered_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

        self.device_profiles[device_id] = device_profile
        return device_profile

    # MODULE 6: Network Intelligence
    def register_network(self, data: dict) -> dict:
        vpn_detected = data.get("vpn_detected", False)
        proxy_detected = data.get("proxy_detected", False)
        return {
            "network_type": data.get("network_type"),
            "carrier": data.get("carrier"),
            "asn": data.get("asn"),
            "vpn_detected": vpn_detected,
            "proxy_detected": proxy_detected,
            "roaming": data.get("roaming", False),
            "wifi_vs_cellular": data.get("wifi_vs_cellular"),
            "network_trust_score": None,
            "trust_status": "PENDING_AUTHORITATIVE_EVIDENCE",
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
            "policy_triggered": self._check_policy_trigger(event),
            "sdk_version": event.get("sdk_version", "FAT-SDK v2.4.1"),
            "ingestion_latency_ms": round((time.perf_counter() - t0) * 1000.0, 2)
        }
        self.event_log.append(enriched_event)
        if len(self.event_log) > 500:
            self.event_log = self.event_log[-500:]
        latency = enriched_event["ingestion_latency_ms"]
        self.ingestion_latencies = (self.ingestion_latencies + [latency])[-500:]
        session = self.sdk_sessions.get(enriched_event["session_id"])
        if session:
            app = next(
                (item for item in self.connected_apps if item["app_id"] == session["app_id"]),
                None,
            )
            if app:
                app["events_today"] += 1
                app["last_heartbeat"] = enriched_event["timestamp"]
        return enriched_event

    def _check_policy_trigger(self, event: dict) -> str | None:
        event_type = event.get("event_type", "")
        amount = float(event.get("amount", 0))
        if amount > 50000 and event_type == "TRANSFER_INITIATED":
            return "POL_001"
        if event_type == "OVERLAY_DETECTED":
            return "POL_002"
        return None

    # MODULE 9: Adaptive Policies
    def get_policies(self) -> dict:
        return {"policies": self.policies, "policy_version": self.policy_version}

    # MODULE 11: Trust Passport Sync
    def get_trust_passport(self, session_id: str) -> dict:
        session = self.sdk_sessions.get(session_id, {})
        return {
            "session_id": session_id,
            "composite_trust": session.get("composite_trust_score"),
            "device_trust": session.get("device_trust"),
            "session_trust": session.get("session_trust"),
            "behaviour_trust": session.get("behaviour_trust"),
            "network_trust": session.get("network_trust"),
            "runtime_trust": session.get("runtime_trust"),
            "trust_status": "UNAVAILABLE" if not session else session.get("trust_status"),
            "policy_version": self.policy_version,
            "sync_timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        }

    # MODULE 18: Observability / SDK Health
    def get_observability(self) -> dict:
        total_events = len(self.event_log)
        active_sessions = sum(1 for s in self.sdk_sessions.values() if s.get("status") == "ACTIVE")
        average_latency = (
            round(sum(self.ingestion_latencies) / len(self.ingestion_latencies), 3)
            if self.ingestion_latencies
            else None
        )
        return {
            "sdk_health": "HEALTHY" if active_sessions else "IDLE",
            "connection_status": "CONNECTED" if active_sessions else "NO_ACTIVE_CLIENTS",
            "active_sessions": active_sessions,
            "queued_events": None,
            "total_events_processed": total_events,
            "average_latency_ms": average_latency,
            "dropped_events": 0,
            "policy_version": self.policy_version,
            "trust_sync_status": "AVAILABLE" if active_sessions else "NO_ACTIVE_SESSIONS",
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
