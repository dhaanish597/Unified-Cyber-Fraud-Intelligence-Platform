import time
import datetime
import hashlib
import os
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
        self.attack_chains: Dict[str, List[dict]] = {}
        self.recovery_events: Dict[str, List[dict]] = {}
        self.telemetry_history: Dict[str, List[dict]] = {}

    # MODULE 1: SDK Session Management
    def start_session(self, data: dict) -> dict:
        session_id = f"SDK_SESS_{uuid.uuid4().hex[:16].upper()}"
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST")
        session = {
            "session_id": session_id,
            "app_id": data.get("app_id") or os.getenv("FUSION_DEFAULT_APP_ID", "com.fusionbank.mobileapp"),
            "tenant_id": data.get("tenant_id") or os.getenv("FUSION_DEFAULT_TENANT_ID", "TENANT_FUSB_001"),
            "sdk_version": data.get("sdk_version", "FAT-SDK v2.4.1"),
            "user_id": data.get("user_id", "usr_sdk_demo"),
            "device_id": data.get("device_id") or f"DEV_{uuid.uuid4().hex[:8].upper()}",
            "environment": data.get("environment", "PRODUCTION"),
            "started_at": ts,
            "status": "ACTIVE",
            "policy_version": self.policy_version,
            "composite_trust_score": 95.0,
            "device_trust": 95.0,
            "session_trust": 95.0,
            "behaviour_trust": 95.0,
            "network_trust": 95.0,
            "runtime_trust": 95.0,
            "trust_status": "HEALTHY",
        }
        self.sdk_sessions[session_id] = session
        self.attack_chains[session_id] = []
        self.recovery_events[session_id] = []
        self.telemetry_history[session_id] = []
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

    def process_telemetry(self, data: dict) -> dict:
        session_id = data.get("session_id")
        session = self.sdk_sessions.get(session_id)
        if not session:
            session = self.start_session({"session_id": session_id, "user_id": "usr_sdk_demo", "device_id": data.get("device_id")})
            
        history = self.telemetry_history.setdefault(session_id, [])
        history.append(data)
        if len(history) > 100:
            history.pop(0)
            
        is_vpn = data.get("vpn_active", False)
        is_proxy = data.get("proxy_active", False)
        is_root = data.get("root_detected", False)
        is_debugger = data.get("debugger_attached", False)
        is_frida = data.get("frida_detected", False)
        is_magisk = data.get("magisk_detected", False)
        is_emulator = data.get("emulator_detected", False)
        is_accessibility = data.get("accessibility_active", False)
        is_overlay = data.get("overlay_active", False)
        is_mitm = data.get("mitm_active", False)
        is_ssl_pinning_broken = not data.get("ssl_pinning_ok", True)
        is_signature_broken = not data.get("app_signature_ok", True)
        is_tampered = data.get("apk_tampered", False)
        is_screen_capture = data.get("screen_capture_active", False)
        is_dev_options = data.get("developer_options_active", False)
        
        chain = self.attack_chains.setdefault(session_id, [])
        active_events = [e["event"] for e in chain]
        
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        if is_vpn and "VPN Enabled" not in active_events:
            chain.append({"time": now_str, "event": "VPN Enabled", "severity": "MEDIUM"})
        if is_emulator and "Emulator Detected" not in active_events:
            chain.append({"time": now_str, "event": "Emulator Detected", "severity": "HIGH"})
        if is_root and "Root Access Enabled" not in active_events:
            chain.append({"time": now_str, "event": "Root Access Enabled", "severity": "CRITICAL"})
        if is_magisk and "Magisk Manager Active" not in active_events:
            chain.append({"time": now_str, "event": "Magisk Manager Active", "severity": "CRITICAL"})
        if is_frida and "Frida Hook Tool Detected" not in active_events:
            chain.append({"time": now_str, "event": "Frida Hook Tool Detected", "severity": "CRITICAL"})
        if is_debugger and "Debugger Attached" not in active_events:
            chain.append({"time": now_str, "event": "Debugger Attached", "severity": "HIGH"})
        if is_accessibility and "Accessibility Service Exploited" not in active_events:
            chain.append({"time": now_str, "event": "Accessibility Service Exploited", "severity": "HIGH"})
        if is_overlay and "Overlay Window Active" not in active_events:
            chain.append({"time": now_str, "event": "Overlay Window Active", "severity": "HIGH"})
        if is_mitm and "MITM Attack Suspected" not in active_events:
            chain.append({"time": now_str, "event": "MITM Attack Suspected", "severity": "CRITICAL"})
        if is_ssl_pinning_broken and "SSL Pinning Integrity Fault" not in active_events:
            chain.append({"time": now_str, "event": "SSL Pinning Integrity Fault", "severity": "HIGH"})
        if is_signature_broken and "App Signature Mismatch" not in active_events:
            chain.append({"time": now_str, "event": "App Signature Mismatch", "severity": "CRITICAL"})
        if is_tampered and "APK Tampering Flagged" not in active_events:
            chain.append({"time": now_str, "event": "APK Tampering Flagged", "severity": "CRITICAL"})
        if is_screen_capture and "Screen Recording Detected" not in active_events:
            chain.append({"time": now_str, "event": "Screen Recording Detected", "severity": "MEDIUM"})
        if is_dev_options and "Developer Options Active" not in active_events:
            chain.append({"time": now_str, "event": "Developer Options Active", "severity": "LOW"})
            
        device_trust = 95.0
        network_trust = 95.0
        runtime_trust = 95.0
        
        if is_root or is_magisk:
            device_trust -= 30
        if is_emulator:
            device_trust -= 20
        if is_vpn:
            network_trust -= 20
        if is_proxy:
            network_trust -= 15
        if is_frida or is_debugger:
            runtime_trust -= 35
        if is_tampered or is_signature_broken:
            runtime_trust -= 40
        if is_overlay or is_accessibility:
            runtime_trust -= 20
            
        active_threat_count = sum([is_vpn, is_root or is_magisk, is_frida or is_debugger, is_overlay or is_accessibility])
        correlation_penalty = 0
        if active_threat_count >= 2:
            correlation_penalty = 15 * (active_threat_count - 1)
            
        session_trust = 95.0 - (95.0 - device_trust) - (95.0 - network_trust) - (95.0 - runtime_trust) - correlation_penalty
        
        recovery = self.recovery_events.get(session_id, [])
        has_biometric_recovered = any(r["event"] == "Biometric Verified" for r in recovery)
        
        if has_biometric_recovered:
            session_trust += 40
            
        device_trust = max(10.0, min(100.0, device_trust))
        network_trust = max(10.0, min(100.0, network_trust))
        runtime_trust = max(10.0, min(100.0, runtime_trust))
        session_trust = max(10.0, min(100.0, session_trust))
        
        session["device_trust"] = device_trust
        session["network_trust"] = network_trust
        session["runtime_trust"] = runtime_trust
        session["composite_trust_score"] = session_trust
        
        if session_trust >= 80:
            session["trust_status"] = "HEALTHY"
        elif session_trust >= 50:
            session["trust_status"] = "SUSPICIOUS"
        elif session_trust >= 30:
            session["trust_status"] = "CHALLENGED"
        else:
            session["trust_status"] = "BLOCKED"
            
        return session

    def recover_session(self, session_id: str, action: str) -> dict:
        session = self.sdk_sessions.get(session_id)
        if not session:
            return {"status": "ERROR", "message": "Session not found"}
            
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        recovery = self.recovery_events.setdefault(session_id, [])
        
        if action == "biometric":
            recovery.append({"time": now_str, "event": "Biometric Verified"})
            chain = self.attack_chains.setdefault(session_id, [])
            chain.append({"time": now_str, "event": "Biometric Verified - Trust Restored", "severity": "RECOVERY"})
            
            session["composite_trust_score"] = min(95.0, session.get("composite_trust_score", 95.0) + 40.0)
            if session["composite_trust_score"] >= 80:
                session["trust_status"] = "HEALTHY"
                
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
        event_id = event.get("event_id") or f"EVT_{uuid.uuid4().hex[:12].upper()}"
        enriched_event = {
            "event_id": event_id,
            "session_id": event.get("session_id", "SDK_SESS_DEMO"),
            "device_id": event.get("device_id", "DEV_DEMO"),
            "event_type": event.get("event_type", "UNKNOWN"),
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "policy_triggered": self._check_policy_trigger(event),
            "sdk_version": event.get("sdk_version", "FAT-SDK v2.4.1"),
            "request_id": event.get("request_id"),
            "correlation_id": event.get("correlation_id"),
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

class BehavioralBiometricsEngine:
    def __init__(self):
        # session_id -> list of samples
        self.buffers: Dict[str, List[dict]] = {}

    def add_sample(self, session_id: str, sample: dict) -> float:
        if session_id not in self.buffers:
            self.buffers[session_id] = []
        self.buffers[session_id].append(sample)
        if len(self.buffers[session_id]) > 200:
            self.buffers[session_id].pop(0)

        # Compute scoring
        typing_score = self.compute_typing_rhythm_score(session_id)
        touch_score = self.compute_touch_pressure_score(session_id)
        motion_score = self.compute_motion_score(session_id)

        # Weighted average
        # If any channel is None (not collected), distribute weights to others
        weights = {"typing": 0.4, "touch": 0.35, "motion": 0.25}
        total_weight = 0.0
        weighted_sum = 0.0

        if typing_score is not None:
            weighted_sum += typing_score * weights["typing"]
            total_weight += weights["typing"]
        if touch_score is not None:
            weighted_sum += touch_score * weights["touch"]
            total_weight += weights["touch"]
        if motion_score is not None:
            weighted_sum += motion_score * weights["motion"]
            total_weight += weights["motion"]

        if total_weight > 0:
            combined_score = weighted_sum / total_weight
        else:
            combined_score = 1.0  # default when no biometrics received yet

        return round(combined_score, 2)

    def compute_typing_rhythm_score(self, session_id: str) -> float | None:
        samples = [s.get("typing_rhythm") for s in self.buffers[session_id] if s.get("typing_rhythm")]
        if not samples:
            return None
        
        latest = samples[-1]
        if latest.get("is_calibrating", True):
            return 1.0
        
        std_dev = latest.get("std_dev_inter_key_interval_ms", 0.0)
        mean_int = latest.get("mean_inter_key_interval_ms", 0.0)
        
        if mean_int <= 0:
            return 1.0
        
        # Coefficient of variation = std_dev / mean
        cv = std_dev / mean_int
        
        # If cv is extremely small (< 0.05), it indicates script/bot automation
        if cv < 0.05:
            return 0.1
        # If cv is between 0.1 and 0.4, it's very natural human rhythm
        elif 0.1 <= cv <= 0.4:
            return 1.0
        # If cv is between 0.05 and 0.1 or 0.4 and 0.6, scale down
        elif 0.05 <= cv < 0.1:
            return round((cv - 0.05) / 0.05 * 0.9 + 0.1, 2)
        elif 0.4 < cv <= 0.7:
            return round(1.0 - (cv - 0.4) / 0.3 * 0.5, 2)
        else:
            return 0.5

    def compute_touch_pressure_score(self, session_id: str) -> float | None:
        samples = [s.get("touch_pressure") for s in self.buffers[session_id] if s.get("touch_pressure")]
        if not samples:
            return None
        
        latest = samples[-1]
        if latest.get("is_calibrating", True):
            return 1.0
            
        std_dev = latest.get("std_dev_pressure", 0.0)
        mean_p = latest.get("mean_pressure", 0.0)
        
        if std_dev < 0.001:
            return 0.1  # Bot touch pressure signature
        
        if 0.1 <= mean_p <= 0.9:
            return 1.0
        return 0.7

    def compute_motion_score(self, session_id: str) -> float | None:
        samples = [s.get("motion_signature") for s in self.buffers[session_id] if s.get("motion_signature")]
        if not samples:
            return None
            
        latest = samples[-1]
        if latest.get("is_calibrating", True):
            return 1.0
            
        std_x = latest.get("accel_std_x", 0.0)
        std_y = latest.get("accel_std_y", 0.0)
        std_z = latest.get("accel_std_z", 0.0)
        
        total_motion_std = std_x + std_y + std_z
        
        if total_motion_std < 0.01:
            return 0.2
        elif total_motion_std > 20.0:
            return 0.4
            
        return 1.0

sdk_engine = FusionAdaptiveTrustSDKEngine()
behavioral_engine = BehavioralBiometricsEngine()
