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
        score = 100.0
        reasons = []
        from api.digital_twin_engine import get_or_create_digital_twin
        import datetime
        twin = get_or_create_digital_twin(user_id)
        
        if not twin or not hasattr(twin, "identity") or not twin.identity:
            return {"score": 50.0, "reasons": ["No baseline exists. Neutral score."], "confidence": 0.5}
            
        kyc = twin.identity.get("kyc_status", "UNKNOWN")
        if "TIER-3" in kyc:
            reasons.append("KYC: Tier-3 Biometric Verified")
        elif "TIER-2" in kyc:
            score -= 10
            reasons.append("KYC: Tier-2 Document Verified")
        else:
            score -= 30
            reasons.append(f"KYC: {kyc}")
            
        # account age in days
        created_at_str = twin.identity.get("created_at", "2020-03-15 09:00:00")
        try:
            created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            age_days = (datetime.datetime.now() - created_at).days
        except:
            age_days = 365
            
        if age_days < 7:
            score -= 20
            reasons.append(f"New Account ({age_days} days)")
        elif age_days < 30:
            score -= 10
            reasons.append(f"Recent Account ({age_days} days)")
        else:
            reasons.append(f"Account age: {age_days} days")
            
        # days since last credential change
        days_since_cred_change = data.get("days_since_credential_change", 90)
        if days_since_cred_change < 1:
            score -= 15
            reasons.append("Credentials changed very recently (< 1 day)")
            
        # prior failed-auth count
        failed_auth_count = data.get("prior_failed_auth_count", twin.identity.get("historical_fraud_count", 0))
        if failed_auth_count > 0:
            score -= (failed_auth_count * 5)
            reasons.append(f"Prior failed auth count: {failed_auth_count}")

        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]

        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9}

    def _eval_device_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.sdk_engine import sdk_engine
        
        device_id = data.get("device_id", "dev_9999")
        ip = data.get("ip", "185.15.2.22")
        
        from api.digital_twin_engine import get_or_create_digital_twin
        twin = get_or_create_digital_twin(user_id)
        trusted = [d["device_id"] for d in twin.devices.get("trusted_devices", [])]
        
        is_trusted = device_id in trusted
        
        # We reuse the real risk-deduction math from sdk_engine.register_device
        sdk_res = sdk_engine.register_device({"device_id": device_id, "ip": ip, **data})
        sdk_score = sdk_res.get("trust_score", 100.0)
        sdk_reasons = sdk_res.get("reasons", [])
        
        score = 100.0
        reasons = []
        if not is_trusted:
            score -= 30.0
            reasons.append("Unrecognized Device")
        else:
            reasons.append("Trusted Device")
            
        score -= (100.0 - sdk_score)
        reasons.extend(sdk_reasons)
        
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.85}

    def _eval_session_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        from api.geo_utils import implied_velocity_kmh, get_coordinates, haversine_km, _parse_time
        import datetime
        
        ip = data.get("ip", "185.15.2.22")
        city = data.get("city")
        curr_geo = get_coordinates(ip if ip else city)
        
        twin = get_or_create_digital_twin(user_id)
        home_geo = get_coordinates(twin.locations.get("home_location", {}).get("city", "Mumbai"))
        
        history = twin.locations.get("travel_history", [])
        if history:
            history_sorted = sorted(history, key=lambda x: _parse_time(x.get("timestamp", "2000-01-01 00:00:00")))
            last_travel = history_sorted[-1]
            prev_ts = last_travel.get("timestamp")
            prev_ip = last_travel.get("ip")
            prev_city = last_travel.get("city", "Mumbai")
            prev_geo = get_coordinates(prev_ip if prev_ip else prev_city)
        else:
            prev_ts = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            prev_geo = home_geo
            
        curr_ts = data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        velocity = implied_velocity_kmh(prev_geo, prev_ts, curr_geo, curr_ts)
        
        score = 100.0
        reasons = []
        
        dist = haversine_km(prev_geo.get("lat", 0), prev_geo.get("lon", 0), curr_geo.get("lat", 0), curr_geo.get("lon", 0))
        t1 = _parse_time(prev_ts)
        t2 = _parse_time(curr_ts)
        mins = max(1, abs((t2 - t1).total_seconds()) / 60.0)
        
        if velocity > 900:
            score -= 85.0
            reasons.append(f"Impossible Travel Event ({prev_geo.get('city', 'Unknown')} to {curr_geo.get('city', 'Unknown')} in {int(mins)} min = {velocity:,.0f} km/h implied velocity)")
        else:
            reasons.append(f"Normal Travel Velocity ({velocity:,.0f} km/h)")
            
        session_age = data.get("session_age_minutes", 10)
        if session_age < 1:
            score -= 10.0
            reasons.append(f"Session just started ({session_age} min)")
        else:
            reasons.append(f"Session age mature ({session_age} min)")
            
        token_seen = data.get("token_previously_seen", True)
        if not token_seen:
            score -= 20.0
            reasons.append("New Session Token")
        else:
            reasons.append("Token previously seen")
            
        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.94}

    def _eval_behavior_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 100.0
        reasons = []
        dev_idx = 0.0
        
        from api.digital_twin_engine import get_or_create_digital_twin
        twin = get_or_create_digital_twin(user_id)
        if not twin or not hasattr(twin, "behavior") or not twin.behavior:
            return {"score": 50.0, "reasons": ["No baseline exists. Neutral score."], "deviation_index": 0.0}
            
        # continuous z-score of the session's behavioral features against the user's digital twin baseline
        session_age = data.get("session_age_minutes", 10.0)
        avg_session = twin.behavior.get("avg_session_duration_sec", 240) / 60.0
        
        # default std deviation if not provided
        std = 2.0
        
        z_score = abs(session_age - avg_session) / std
        dev_idx = z_score
        
        score -= min(30.0, z_score * 5.0) # continuous deduction
        reasons.append(f"Session Behavior Z-Score: {z_score:.2f}")

        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]

        return {"score": max(0.0, score), "reasons": reasons, "deviation_index": round(dev_idx, 2)}

    def _eval_cyber_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 100.0
        reasons = []
        mitre_tech = []
        cat = "LOW_RISK"
        
        import datetime
        now = datetime.datetime.now()
        
        # fetch actual cyber events
        events = data.get("recent_cyber_events", [])
        if not events:
            try:
                import api.main
                universe = api.main.cached_universe or {}
                all_events = universe.get("cyber_events", [])
                events = [e for e in all_events if e.get("user_id") == user_id]
            except:
                pass
            
        scenario = data.get("scenario_id", "")
        mapping = MITRE_ATTACK_MAPPINGS.get(scenario, {"id": "None", "name": "Unknown"})
        technique_id = mapping.get("id", "None")
            
        if not events and not data.get("cyber_compromise_in_window"):
            return {"score": 100.0, "reasons": ["No cyber compromise detected in window"], "confidence": 0.9, "threat_category": cat, "mitre_techniques": mitre_tech}
            
        if data.get("cyber_compromise_in_window"):
            score -= 40.0
            cat = "HIGH_RISK"
            if technique_id != "None":
                reasons.append(f"Active cyber compromise [{technique_id}]")
                mitre_tech.append(technique_id)
            else:
                reasons.append("Active cyber compromise in window")
                
        # Time decay for past events
        for ev in events:
            ev_ts_str = ev.get("timestamp", (now - datetime.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"))
            severity = str(ev.get("severity", "MEDIUM")).upper()
            try:
                ev_ts = datetime.datetime.strptime(ev_ts_str, "%Y-%m-%d %H:%M:%S")
            except:
                ev_ts = now - datetime.timedelta(hours=24)
                
            hours_ago = max(0, (now - ev_ts).total_seconds() / 3600.0)
            decay_factor = max(0.1, 1.0 - (hours_ago / 72.0))
            
            sev_weight = 30.0 if severity == "CRITICAL" else (20.0 if severity == "HIGH" else 10.0)
            deduction = sev_weight * decay_factor
            score -= deduction
            
            if severity in ["HIGH", "CRITICAL"]: cat = "HIGH_RISK"
            elif cat == "LOW_RISK": cat = "MEDIUM_RISK"
            
            reasons.append(f"Past Event: {ev.get('event_type', 'Unknown')} (Decay: {decay_factor:.2f})")
            
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None" and technique_id not in mitre_tech:
            mitre_tech.append(technique_id)
            reasons = [r + f" [{technique_id}]" for r in reasons]
            
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.85, "threat_category": cat, "mitre_techniques": mitre_tech}

    def _eval_graph_checkpoint(self, user_id: str, data: dict) -> dict:
        try:
            import api.main
            universe = api.main.cached_universe or {}
            graph_topology = universe.get("graph_topology", {})
            nodes = graph_topology.get("nodes", data.get("graph_nodes", []))
            edges = graph_topology.get("edges", data.get("graph_edges", []))
        except ImportError:
            nodes = data.get("graph_nodes", [])
            edges = data.get("graph_edges", [])
            
        scenario = data.get("scenario_id", "")
            
        if not nodes:
            reasons = ["Graph is empty. Neutral score."]
            if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
                reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            return {"score": 50.0, "reasons": reasons, "confidence": 0.5, "relationship_summary": "Empty", "mule_ring_distance": -1}
            
        import networkx as nx
        G = nx.Graph()
        for n in nodes:
            G.add_node(n["id"], **n)
        for e in edges:
            G.add_edge(e["source"], e["target"], **e)
            
        if user_id not in G:
            reasons = [f"User {user_id} not in graph. Neutral score."]
            if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
                reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            return {"score": 50.0, "reasons": reasons, "confidence": 0.5, "relationship_summary": "Unknown", "mule_ring_distance": -1}
            
        mule_nodes = [n for n, attr in G.nodes(data=True) if str(attr.get("risk", "")).upper() == "HIGH" or "mule" in str(attr.get("type", "")).lower()]
        distance = float('inf')
        for m in mule_nodes:
            try:
                d = nx.shortest_path_length(G, user_id, m)
                distance = min(distance, d)
            except nx.NetworkXNoPath:
                pass
                
        score = 100.0
        reasons = []
        rel_summary = "Normal"
        
        if distance != float('inf'):
            # continuous deduction based on distance
            dist_deduction = max(0, 50 - (distance * 10))
            score -= dist_deduction
            reasons.append(f"{distance} hops to known mule ring")
            rel_summary = f"{distance}-hop link to Mule"
        else:
            reasons.append("No path to known mule ring")
            
        pr = nx.pagerank(G)
        user_pr = pr.get(user_id, 0)
        customers_pr = [p for n, p in pr.items() if str(G.nodes[n].get("type", "Customer")).lower() == "customer"]
        if customers_pr:
            percentile = sum(1 for p in customers_pr if p <= user_pr) / len(customers_pr) * 100
            # continuous deduction based on percentile centrality
            score -= (percentile / 100.0) * 15.0
            reasons.append(f"PageRank Centrality: {percentile:.1f}th percentile")
                
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
                
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9, "relationship_summary": rel_summary, "mule_ring_distance": -1 if distance == float('inf') else distance}

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
