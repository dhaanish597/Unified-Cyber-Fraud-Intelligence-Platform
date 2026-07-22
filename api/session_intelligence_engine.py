import time
import datetime
import random
from typing import Dict, List, Any

# MITRE ATT&CK Mappings for Cyber Checkpoint
MITRE_ATTACK_MAPPINGS = {
    "impossible_travel_login": {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "tactic": "Initial Access"},
    "credential_stuffing_surge": {"id": "T1110.004", "name": "Brute Force: Credential Stuffing", "tactic": "Credential Access"},
    "sim_swap_interception": {"id": "T1111", "name": "Multi-Factor Authentication Interception", "tactic": "Credential Access"},
    "cookie_theft_reuse": {"id": "T1539", "name": "Steal Web Session Cookie", "tactic": "Credential Access"},
    "vpn_proxy_login": {"id": "T1090.003", "name": "Proxy: Multi-hop Proxy", "tactic": "Command and Control"},
    "rooted_device_access": {"id": "T1406", "name": "Obfuscated Files or Information: Root/Jailbreak", "tactic": "Defense Evasion"},
    "malware_detected": {"id": "T1417", "name": "Input Capture: Keylogging / Overlay", "tactic": "Credential Access"}
}

class SessionTrustPassportEngine:
    """
    Pre-Transaction Session Intelligence Engine for Fusion Risk OS.
    Executes a 6-checkpoint pre-transaction evaluation before any financial action.
    Outputs a Session Trust Passport.
    """
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    def analyse_session(self, session_data: dict) -> dict:
        """
        Executes the 6-Checkpoint Pre-Transaction Pipeline sequentially.
        """
        t_total_start = time.perf_counter()
        session_id = session_data.get("session_id", f"SESS_{random.randint(10000, 99999)}")
        user_id = session_data.get("user_id", "usr_abc")

        # CHECKPOINT 1: Identity Intelligence
        t0 = time.perf_counter()
        identity_res = self._eval_identity_checkpoint(user_id, session_data)
        t_identity = (time.perf_counter() - t0) * 1000.0

        # CHECKPOINT 2: Device Intelligence
        t0 = time.perf_counter()
        device_res = self._eval_device_checkpoint(user_id, session_data)
        t_device = (time.perf_counter() - t0) * 1000.0

        # CHECKPOINT 3: Session Intelligence
        t0 = time.perf_counter()
        session_res = self._eval_session_checkpoint(user_id, session_data)
        t_session = (time.perf_counter() - t0) * 1000.0

        # CHECKPOINT 4: Behavior Intelligence
        t0 = time.perf_counter()
        behavior_res = self._eval_behavior_checkpoint(user_id, session_data)
        t_behavior = (time.perf_counter() - t0) * 1000.0

        # CHECKPOINT 5: Cyber Threat Intelligence
        t0 = time.perf_counter()
        cyber_res = self._eval_cyber_checkpoint(user_id, session_data)
        t_cyber = (time.perf_counter() - t0) * 1000.0

        # CHECKPOINT 6: Graph Intelligence
        t0 = time.perf_counter()
        graph_res = self._eval_graph_checkpoint(user_id, session_data)
        t_graph = (time.perf_counter() - t0) * 1000.0

        # FUSION & PASSPORT GENERATION
        t0 = time.perf_counter()
        
        # Calculate Weighted Overall Trust Score (0 to 100)
        overall_trust = round(
            (identity_res["score"] * 0.15) +
            (device_res["score"] * 0.20) +
            (session_res["score"] * 0.20) +
            (behavior_res["score"] * 0.15) +
            (cyber_res["score"] * 0.15) +
            (graph_res["score"] * 0.15),
            1
        )

        if overall_trust >= 75.0:
            decision = "ALLOW"
            monitoring_level = "LOW"
        elif overall_trust >= 45.0:
            decision = "CHALLENGE"
            monitoring_level = "MEDIUM" if overall_trust >= 60 else "HIGH"
        else:
            decision = "BLOCK"
            monitoring_level = "CRITICAL"

        if cyber_res["score"] < 30.0 or graph_res["score"] < 30.0:
            decision = "BLOCK"
            monitoring_level = "CRITICAL"

        t_fusion = (time.perf_counter() - t0) * 1000.0
        t_total = (time.perf_counter() - t_total_start) * 1000.0

        # Issue Session Trust Passport
        now = datetime.datetime.now()
        expiry = (now + datetime.timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S IST")

        passport = {
            "session_id": session_id,
            "user_id": user_id,
            "issued_at": now.strftime("%Y-%m-%d %H:%M:%S IST"),
            "expiry": expiry,
            "decision": decision,
            "overall_trust": overall_trust,
            "monitoring_level": monitoring_level,
            "checkpoints": {
                "checkpoint_1_identity": {
                    "name": "Identity Intelligence",
                    "score": identity_res["score"],
                    "confidence": identity_res["confidence"],
                    "reasons": identity_res["reasons"],
                    "execution_time_ms": round(t_identity, 2)
                },
                "checkpoint_2_device": {
                    "name": "Device Intelligence",
                    "score": device_res["score"],
                    "confidence": device_res["confidence"],
                    "reasons": device_res["reasons"],
                    "execution_time_ms": round(t_device, 2)
                },
                "checkpoint_3_session": {
                    "name": "Session Intelligence",
                    "score": session_res["score"],
                    "confidence": 0.94,
                    "reasons": session_res["reasons"],
                    "execution_time_ms": round(t_session, 2)
                },
                "checkpoint_4_behavior": {
                    "name": "Behavior Intelligence",
                    "score": behavior_res["score"],
                    "deviation_index": behavior_res["deviation_index"],
                    "reasons": behavior_res["reasons"],
                    "execution_time_ms": round(t_behavior, 2)
                },
                "checkpoint_5_cyber": {
                    "name": "Cyber Threat Intelligence",
                    "score": cyber_res["score"],
                    "threat_confidence": cyber_res["confidence"],
                    "threat_category": cyber_res["threat_category"],
                    "mitre_techniques": cyber_res["mitre_techniques"],
                    "reasons": cyber_res["reasons"],
                    "execution_time_ms": round(t_cyber, 2)
                },
                "checkpoint_6_graph": {
                    "name": "Graph Intelligence",
                    "score": graph_res["score"],
                    "confidence": graph_res["confidence"],
                    "relationship_summary": graph_res["relationship_summary"],
                    "mule_ring_distance": graph_res["mule_ring_distance"],
                    "reasons": graph_res["reasons"],
                    "execution_time_ms": round(t_graph, 2)
                }
            },
            "performance_metrics": {
                "identity_engine_ms": round(t_identity, 2),
                "device_engine_ms": round(t_device, 2),
                "session_engine_ms": round(t_session, 2),
                "behavior_engine_ms": round(t_behavior, 2),
                "cyber_engine_ms": round(t_cyber, 2),
                "graph_engine_ms": round(t_graph, 2),
                "fusion_engine_ms": round(t_fusion, 2),
                "total_latency_ms": round(t_total, 2)
            }
        }

        self.active_sessions[session_id] = passport
        return passport

    def _eval_identity_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 95.0
        reasons = ["KYC Verified (Tier-3 Biometric)", "Account Age > 3 Years"]
        if user_id == "usr_abc":
            score = 88.0
            reasons.append("High-Value Corporate Segment Customer")
        return {"score": score, "confidence": 0.98, "reasons": reasons}

    def _eval_device_checkpoint(self, user_id: str, data: dict) -> dict:
        is_compromised = data.get("cyber_compromise_in_window", False) or user_id == "usr_abc"
        if is_compromised:
            return {
                "score": 25.0,
                "confidence": 0.94,
                "reasons": ["Unregistered Device Fingerprint (dev_9999)", "Proxy / VPN Traffic Detected", "SIM Swap Check Flagged"]
            }
        return {
            "score": 96.0,
            "confidence": 0.96,
            "reasons": ["Known Primary Device (iPhone 15 Pro)", "No Root/Jailbreak Detected", "Device Trust Score 0.98"]
        }

    def _eval_session_checkpoint(self, user_id: str, data: dict) -> dict:
        ip = data.get("ip", "185.15.2.22")
        is_compromised = data.get("cyber_compromise_in_window", False) or user_id == "usr_abc"
        if is_compromised or ip == "185.15.2.22":
            return {
                "score": 15.0,
                "reasons": ["Impossible Travel Event (Moscow, RU 4,500 km away)", "JWT Token Replayed over Commercial VPN", "MFA Token Out of Sync"]
            }
        return {
            "score": 94.0,
            "reasons": ["Valid JWT Token & Session Cookie", "Biometric MFA Verified", "Login Location within Home Baseline (Mumbai)"]
        }

    def _eval_behavior_checkpoint(self, user_id: str, data: dict) -> dict:
        is_compromised = data.get("cyber_compromise_in_window", False) or user_id == "usr_abc"
        if is_compromised:
            return {
                "score": 30.0,
                "deviation_index": 82.5,
                "reasons": ["Off-Hours Login (02:00 AM IST vs Baseline 09:00-21:00)", "Anomalous Spend Amount (₹7.5L vs Normal ₹50K)", "Unseen Beneficiary Target"]
            }
        return {
            "score": 92.0,
            "deviation_index": 8.0,
            "reasons": ["Login within Preferred Hours (10:00 IST)", "Normal Spending Envelope", "Known Beneficiary Target"]
        }

    def _eval_cyber_checkpoint(self, user_id: str, data: dict) -> dict:
        is_compromised = data.get("cyber_compromise_in_window", False) or user_id == "usr_abc"
        if is_compromised:
            return {
                "score": 10.0,
                "confidence": 0.98,
                "threat_category": "CRITICAL_THREAT",
                "mitre_techniques": [
                    MITRE_ATTACK_MAPPINGS["impossible_travel_login"],
                    MITRE_ATTACK_MAPPINGS["cookie_theft_reuse"]
                ],
                "reasons": ["Known Malicious ASN (AS49505 OOO Baxet)", "Impossible Travel 40s Prior to Transfer Request", "Dark Web Credential Spill Alert"]
            }
        return {
            "score": 98.0,
            "confidence": 0.99,
            "threat_category": "CLEAN",
            "mitre_techniques": [],
            "reasons": ["Clean IP Reputation (Jio Fiber AS55836)", "No Active Threat Feeds Flagged"]
        }

    def _eval_graph_checkpoint(self, user_id: str, data: dict) -> dict:
        mule_cluster = data.get("dest_mule_cluster_id")
        is_compromised = data.get("cyber_compromise_in_window", False) or user_id == "usr_abc"
        if is_compromised or mule_cluster:
            return {
                "score": 12.0,
                "confidence": 0.96,
                "mule_ring_distance": 1,
                "relationship_summary": f"Direct 1-Hop Transfer Link to Mule Ring Cluster '{mule_cluster or 'alpha'}'",
                "reasons": ["Destination Account is a Known Mule Node", "GraphSAGE PageRank Centrality Spike (0.0450)", "Belongs to Active Fraud Ring Alpha"]
            }
        return {
            "score": 95.0,
            "confidence": 0.95,
            "mule_ring_distance": 5,
            "relationship_summary": "Clean Graph Neighborhood (5 Hops from Known Mule Rings)",
            "reasons": ["Low Node Betweenness Centrality", "Verified Beneficiary History"]
        }

    def get_passport(self, session_id: str) -> dict:
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        # Generate default active passport for demo session
        return self.analyse_session({"session_id": session_id, "user_id": "usr_abc", "cyber_compromise_in_window": True})

    def update_session(self, session_id: str, update_event: dict) -> dict:
        passport = self.get_passport(session_id)
        # Recalculate passport with new live event
        return self.analyse_session({**update_event, "session_id": session_id, "user_id": passport.get("user_id", "usr_abc")})

session_engine = SessionTrustPassportEngine()
