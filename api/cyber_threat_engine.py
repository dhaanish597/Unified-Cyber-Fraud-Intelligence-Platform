import time
import datetime
import uuid
from typing import Dict, List, Any, Optional

class CyberThreatEngine:
    """
    Enterprise Cyber Threat Intelligence Engine for Fusion Risk OS (Phase 2).
    Evaluates incoming SDK telemetry against a 9-category enterprise taxonomy,
    collects granular evidence, calculates dynamic confidence scores (0-100%),
    correlates isolated threats into multi-stage attack campaigns, and outputs
    structured threat objects for live SOC monitoring.
    """

    def __init__(self):
        self.threat_store: Dict[str, dict] = {}
        self.session_threat_index: Dict[str, List[str]] = {}
        self.device_threat_index: Dict[str, List[str]] = {}
        self.historical_threats: List[dict] = []
        

    def evaluate_event(self, event_data: dict) -> List[dict]:
        """
        Main entry point: Ingests raw SDK event payload and evaluates threat rules (<100ms).
        Returns a list of generated / updated Threat Objects.
        """
        t0 = time.perf_counter()
        session_id = event_data.get("session_id", "SDK_SESS_DEMO")
        device_id = event_data.get("device_id", "DEV_12345")
        user_id = event_data.get("user_id", "usr_sdk_demo")
        event_type = event_data.get("event_type", "UNKNOWN")
        amount = float(event_data.get("amount", 0.0))
        
        detected_threats = []

        # Category Evaluator Dispatch
        dev_threats = self._eval_device_threats(event_data)
        run_threats = self._eval_runtime_threats(event_data)
        ovr_threats = self._eval_overlay_threats(event_data)
        net_threats = self._eval_network_threats(event_data)
        ses_threats = self._eval_session_threats(event_data)
        beh_threats = self._eval_behaviour_threats(event_data)
        idn_threats = self._eval_identity_threats(event_data)
        txn_threats = self._eval_transaction_threats(event_data)
        grp_threats = self._eval_graph_threats(event_data)

        raw_threats = (dev_threats + run_threats + ovr_threats + net_threats + 
                       ses_threats + beh_threats + idn_threats + txn_threats + grp_threats)

        for item in raw_threats:
            threat_obj = self._build_threat_object(
                item, session_id, device_id, user_id, t0, event_data
            )
            self._save_threat(threat_obj)
            detected_threats.append(threat_obj)

        # Multi-Threat Campaign Correlation
        correlated_campaigns = self._correlate_campaigns(session_id, device_id, t0)
        for campaign in correlated_campaigns:
            self._save_threat(campaign)
            detected_threats.append(campaign)

        return detected_threats

    # CATEGORY 1: Device Threats
    def _eval_device_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        root = data.get("root_detected", False) or event_type in ["ROOT_DETECTED", "MAGISK_DETECTED"]
        emu = data.get("emulator_detected", False) or event_type == "EMULATOR_DETECTED"
        bootloader = event_type == "BOOTLOADER_UNLOCKED"

        if root:
            threats.append({
                "threat_name": "Rooted Operating System / SU Binary Detected",
                "threat_category": "Device Threats",
                "severity": "CRITICAL",
                "evidence": [
                    "su binary found at /system/xbin/su",
                    "Magisk hide daemon detected in memory",
                    "OS integrity state: UNTRUSTED_ROOTED"
                ],
                "detection_source": "FAT-SDK Device Attestation Engine",
                "trust_impact": {"device_trust": -35.0, "runtime_trust": -20.0},
                "recommended_action": "BLOCK_TRANSACTION"
            })

        if emu:
            threats.append({
                "threat_name": "Android Hardware Emulator Execution",
                "threat_category": "Device Threats",
                "severity": "HIGH",
                "evidence": [
                    "Build fingerprint: generic/google_sdk/x86",
                    "QEMU hypervisor driver present (/dev/qemu_pipe)",
                    "Sensor hardware polling returned null response"
                ],
                "detection_source": "FAT-SDK Hardware Classifier",
                "trust_impact": {"device_trust": -25.0},
                "recommended_action": "REQUIRE_BIOMETRIC"
            })
        return threats

    # CATEGORY 2: Runtime Threats
    def _eval_runtime_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        frida = data.get("frida_detected", False) or event_type in ["FRIDA_DETECTED", "RUNTIME_HOOK_DETECTED"]
        debugger = data.get("debugger_attached", False) or event_type == "DEBUGGER_ATTACHED"

        if frida:
            threats.append({
                "threat_name": "Frida Dynamic Instrumentation Framework Active",
                "threat_category": "Runtime Threats",
                "severity": "CRITICAL",
                "evidence": [
                    "TCP port 27042 listening (Frida RPC Server)",
                    "In-memory library hook detected: frida-agent.so",
                    "Method hooking detected on java.security.Signature"
                ],
                "detection_source": "FAT-SDK Runtime Integrity Guard",
                "trust_impact": {"runtime_trust": -45.0, "device_trust": -20.0},
                "recommended_action": "TERMINATE_SESSION"
            })

        if debugger:
            threats.append({
                "threat_name": "Active Debugger Attached to Banking Process",
                "threat_category": "Runtime Threats",
                "severity": "HIGH",
                "evidence": [
                    "android.os.Debug.isDebuggerConnected() returned TRUE",
                    "TracerPid in /proc/self/status is non-zero (PID 4821)",
                    "JDWP thread actively listening on ADB port"
                ],
                "detection_source": "FAT-SDK Anti-Debugging Engine",
                "trust_impact": {"runtime_trust": -30.0},
                "recommended_action": "REQUIRE_OTP"
            })
        return threats

    # CATEGORY 3: Overlay Attacks
    def _eval_overlay_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        overlay = data.get("overlay_detected", False) or event_type in ["OVERLAY_DETECTED", "ACCESSIBILITY_ABUSE", "ACCESSIBILITY_OVERLAY_ACTIVE"]

        if overlay:
            threats.append({
                "threat_name": "Malicious Window Overlay & Accessibility Service Abuse",
                "threat_category": "Overlay Attacks",
                "severity": "CRITICAL",
                "evidence": [
                    "Accessibility Service active: com.malware.overlay.service",
                    "SYSTEM_ALERT_WINDOW active over payment composables",
                    "Screen capture flags overridden by external window"
                ],
                "detection_source": "FAT-SDK Screen Protection Guard",
                "trust_impact": {"behaviour_trust": -30.0, "runtime_trust": -35.0},
                "recommended_action": "TERMINATE_SESSION"
            })
        return threats

    # CATEGORY 4: Network Threats
    def _eval_network_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        vpn = data.get("vpn_detected", False) or event_type in ["VPN_ENABLED", "PROXY_DETECTED", "TOR_NODE_DETECTED"]

        if vpn:
            threats.append({
                "threat_name": "Anonymizing Network / VPN Tunnel Active",
                "threat_category": "Network Threats",
                "severity": "MEDIUM",
                "evidence": [
                    "Network interface tun0 active (10.8.0.2)",
                    "ASN changed to AS14061 (DigitalOcean / VPN Provider)",
                    "DNS server mismatch with local ISP carrier"
                ],
                "detection_source": "FAT-SDK Network Intelligence Monitor",
                "trust_impact": {"network_trust": -25.0},
                "recommended_action": "REQUIRE_OTP"
            })
        return threats

    # CATEGORY 5: Session Threats
    def _eval_session_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        if event_type in ["SESSION_HIJACK_ATTEMPT", "CONCURRENT_LOGIN", "SESSION_REPLAY"]:
            threats.append({
                "threat_name": "Session Hijack & Concurrent IP Access Anomaly",
                "threat_category": "Session Threats",
                "severity": "HIGH",
                "evidence": [
                    "Active IP 1: 49.37.12.89 (Mumbai, India)",
                    "Active IP 2: 185.220.101.4 (Frankfurt, Germany)",
                    "TLS Session ID reuse within 3 seconds window"
                ],
                "detection_source": "Fusion Pre-Transaction Session Intelligence",
                "trust_impact": {"session_trust": -35.0},
                "recommended_action": "TERMINATE_SESSION"
            })
        return threats

    # CATEGORY 6: Behaviour Threats
    def _eval_behaviour_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        if event_type in ["ROBOTIC_BEHAVIOUR", "HIGH_VELOCITY_NAVIGATION", "RAPID_TRANSFER_SEQUENCE"]:
            threats.append({
                "threat_name": "Automated Scripting & Robotic Touch Biometrics",
                "threat_category": "Behaviour Threats",
                "severity": "HIGH",
                "evidence": [
                    "Touch pressure variance: 0.000 (Human average > 0.12)",
                    "Tap interval standard deviation: 0.02ms (Robotic precision)",
                    "Linear swipe trajectory with zero micro-tremor"
                ],
                "detection_source": "Fusion Behavioral Biometrics Engine",
                "trust_impact": {"behaviour_trust": -40.0},
                "recommended_action": "REQUIRE_FACE_AUTHENTICATION"
            })
        return threats

    # CATEGORY 7: Identity Threats
    def _eval_identity_threats(self, data: dict) -> List[dict]:
        threats = []
        event_type = data.get("event_type", "")
        if event_type in ["IMPOSSIBLE_TRAVEL", "NEW_DEVICE_DETECTED", "SIM_CARD_CHANGED"]:
            threats.append({
                "threat_name": "Impossible Travel & Geofence Anomaly",
                "threat_category": "Identity Threats",
                "severity": "CRITICAL",
                "evidence": [
                    "Location t0 (22:45 IST): Delhi, India (IP 122.160.1.4)",
                    "Location t1 (22:49 IST): London, UK (IP 81.2.69.142)",
                    "Calculated velocity: 1,450 km/h (Exceeds commercial aircraft bounds)"
                ],
                "detection_source": "Fusion Identity Intelligence Engine",
                "trust_impact": {"identity_trust": -40.0, "session_trust": -30.0},
                "recommended_action": "BLOCK_TRANSACTION"
            })
        return threats

    # CATEGORY 8: Transaction Threats
    def _eval_transaction_threats(self, data: dict) -> List[dict]:
        threats = []
        amount = float(data.get("amount", 0.0))
        event_type = data.get("event_type", "")

        if amount > 50000 or event_type in ["HIGH_VALUE_TRANSFER", "VELOCITY_SURGE"]:
            threats.append({
                "threat_name": "High-Value Velocity Surge Transaction Risk",
                "threat_category": "Transaction Threats",
                "severity": "HIGH" if amount < 200000 else "CRITICAL",
                "evidence": [
                    f"Requested Amount: ₹{amount:,.2f}",
                    "User 30-day baseline average: ₹12,400.00",
                    "Cumulative 1-hour velocity: 3 transfers (Total ₹{amount:,.2f})"
                ],
                "detection_source": "Fusion Anomaly & Risk Evaluation Engine",
                "trust_impact": {"session_trust": -20.0},
                "recommended_action": "REQUIRE_BIOMETRIC" if amount < 200000 else "REQUIRE_FACE_AUTHENTICATION"
            })
        return threats

    # CATEGORY 9: Graph Threats
    def _eval_graph_threats(self, data: dict) -> List[dict]:
        threats = []
        graph_findings = data.get("_graph_findings") or []
        for finding in graph_findings:
            finding_type = finding.get("finding_type")
            if finding_type not in {
                "SHARED_DEVICE",
                "SHARED_BENEFICIARY",
                "CIRCULAR_TRANSFER",
                "FRAUD_RING_CANDIDATE",
            }:
                continue
            threats.append({
                "threat_name": f"Graph Intelligence Finding: {finding_type}",
                "threat_category": "Graph Threats",
                "severity": finding.get("severity", "HIGH"),
                "evidence": finding.get("evidence", []),
                "detection_source": f"Fusion Graph Intelligence ({data.get('_graph_backend', 'UNKNOWN')})",
                "trust_impact": {"graph_trust": -50.0},
                "recommended_action": "BLOCK_TRANSACTION"
            })
        return threats

    # Threat Object Builder & Model
    def _build_threat_object(
        self,
        item: dict,
        session_id: str,
        device_id: str,
        user_id: str,
        t0: float,
        event_data: dict,
    ) -> dict:
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 3)
        threat_id = f"THR_{uuid.uuid4().hex[:8].upper()}"
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        observed_evidence = []
        for key, value in event_data.items():
            if key.startswith("_") or key in {"composite_trust", "sdk_version"}:
                continue
            if value is True or key in {
                "event_type",
                "device_id",
                "session_id",
                "user_id",
                "network_type",
                "carrier",
            }:
                observed_evidence.append({"field": key, "observed_value": value})
        if float(event_data.get("amount", 0.0) or 0.0) > 0:
            observed_evidence.append(
                {"field": "amount", "observed_value": float(event_data["amount"])}
            )
        if item["threat_category"] == "Graph Threats":
            observed_evidence = list(item.get("evidence") or [])
        direct_indicators = [
            evidence
            for evidence in observed_evidence
            if evidence.get("field") not in {"event_type", "device_id", "session_id", "user_id"}
        ]
        confidence = 100.0 if direct_indicators else None
        confidence_explanation = (
            f"{len(direct_indicators)} direct telemetry indicator(s) supported the rule."
            if direct_indicators
            else "Not available: only an event classification was supplied."
        )
        
        return {
            "threat_id": threat_id,
            "threat_name": item["threat_name"],
            "threat_category": item["threat_category"],
            "severity": item["severity"],
            "confidence": confidence,
            "confidence_explanation": confidence_explanation,
            "confidence_basis": {
                "method": "OBSERVED_EVIDENCE_COVERAGE",
                "direct_indicator_count": len(direct_indicators),
                "event_label_present": bool(event_data.get("event_type")),
            },
            "evidence": observed_evidence,
            "session_id": session_id,
            "device_id": device_id,
            "user_id": user_id,
            "timestamp": ts,
            "detection_source": item["detection_source"],
            "trust_impact": item["trust_impact"],
            "recommended_action": item["recommended_action"],
            "status": "ACTIVE",
            "detection_latency_ms": latency_ms
        }

    def _correlate_campaigns(
        self, session_id: str, device_id: str, t0: float
    ) -> List[dict]:
        """
        Correlates multiple active threats into high-level attack campaign objects.
        """
        session_threats = self.session_threat_index.get(session_id, [])
        threat_objs = [self.threat_store[tid] for tid in session_threats if tid in self.threat_store]
        
        categories = {t["threat_category"] for t in threat_objs}
        campaigns = []

        # Campaign Rule 1: Account Takeover
        if "Identity Threats" in categories and "Network Threats" in categories:
            existing = any(
                threat.get("threat_category") == "Campaign Correlation"
                and threat.get("threat_name") == "ACCOUNT TAKEOVER CAMPAIGN"
                for threat in threat_objs
            )
            if existing:
                return campaigns
            inputs = [
                threat
                for threat in threat_objs
                if threat["threat_category"] in {"Identity Threats", "Network Threats"}
            ]
            measured_confidences = [
                float(threat["confidence"])
                for threat in inputs
                if threat.get("confidence") is not None
            ]
            confidence = (
                round(sum(measured_confidences) / len(measured_confidences), 2)
                if measured_confidences
                else None
            )
            campaigns.append({
                "threat_id": f"CAMPAIGN_{uuid.uuid4().hex[:8].upper()}",
                "threat_name": "ACCOUNT TAKEOVER CAMPAIGN",
                "threat_category": "Campaign Correlation",
                "severity": "CRITICAL",
                "confidence": confidence,
                "confidence_explanation": (
                    "Arithmetic mean of correlated findings with measured confidence."
                    if measured_confidences
                    else "Not available: correlated findings had no measured confidence."
                ),
                "confidence_basis": {
                    "method": "MEAN_CORRELATED_FINDING_CONFIDENCE",
                    "input_threat_ids": [threat["threat_id"] for threat in inputs],
                },
                "evidence": [
                    {
                        "threat_id": threat["threat_id"],
                        "category": threat["threat_category"],
                        "confidence": threat["confidence"],
                    }
                    for threat in inputs
                ],
                "session_id": session_id,
                "device_id": device_id,
                "user_id": inputs[0].get("user_id", "unknown"),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "detection_source": "Fusion Multi-Threat Correlation Engine",
                "trust_impact": {"overall_trust": -60.0},
                "recommended_action": "BLOCK_TRANSACTION",
                "status": "ACTIVE",
                "detection_latency_ms": round((time.perf_counter() - t0) * 1000.0, 3),
            })
        return campaigns

    def _save_threat(self, threat: dict):
        tid = threat["threat_id"]
        sid = threat["session_id"]
        did = threat["device_id"]
        
        self.threat_store[tid] = threat
        self.session_threat_index.setdefault(sid, []).append(tid)
        self.device_threat_index.setdefault(did, []).append(tid)
        self.historical_threats.append(threat)
        if len(self.historical_threats) > 1000:
            self.historical_threats = self.historical_threats[-1000:]

    def get_all_threats(self, status: Optional[str] = None, category: Optional[str] = None, severity: Optional[str] = None) -> List[dict]:
        res = list(self.threat_store.values())
        if status:
            res = [t for t in res if t.get("status") == status]
        if category:
            res = [t for t in res if t.get("threat_category") == category]
        if severity:
            res = [t for t in res if t.get("severity") == severity]
        return res[::-1]

    def get_threat_by_id(self, threat_id: str) -> Optional[dict]:
        return self.threat_store.get(threat_id)

    def get_threats_by_session(self, session_id: str) -> List[dict]:
        tids = self.session_threat_index.get(session_id, [])
        return [self.threat_store[t] for t in tids if t in self.threat_store]

    def get_threats_by_device(self, device_id: str) -> List[dict]:
        tids = self.device_threat_index.get(device_id, [])
        return [self.threat_store[t] for t in tids if t in self.threat_store]

# Singleton Instance
cyber_threat_engine = CyberThreatEngine()
