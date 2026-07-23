import re

def process_file():
    with open('api/session_intelligence_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_mitre = """# MITRE ATT&CK Mappings for Cyber Checkpoint
MITRE_ATTACK_MAPPINGS = {
    "impossible_travel_login": {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "tactic": "Initial Access"},
    "credential_stuffing_surge": {"id": "T1110.004", "name": "Brute Force: Credential Stuffing", "tactic": "Credential Access"},
    "sim_swap_interception": {"id": "T1111", "name": "Multi-Factor Authentication Interception", "tactic": "Credential Access"},
    "cookie_theft_reuse": {"id": "T1539", "name": "Steal Web Session Cookie", "tactic": "Credential Access"},
    "vpn_proxy_login": {"id": "T1090.003", "name": "Proxy: Multi-hop Proxy", "tactic": "Command and Control"},
    "rooted_device_access": {"id": "T1406", "name": "Obfuscated Files or Information: Root/Jailbreak", "tactic": "Defense Evasion"},
    "malware_detected": {"id": "T1417", "name": "Input Capture: Keylogging / Overlay", "tactic": "Credential Access"},
    "known_mule": {"id": "T1566", "name": "Phishing", "tactic": "Initial Access"},
    "insider_fraud": {"id": "T1078.002", "name": "Valid Accounts: Domain Accounts", "tactic": "Initial Access"},
    "cross_border_money_laundering": {"id": "T1567", "name": "Exfiltration Over Web Service", "tactic": "Exfiltration"},
    "corporate_payroll_fraud": {"id": "T1565.001", "name": "Data Manipulation: Stored Data Manipulation", "tactic": "Impact"},
    "atm_cash_out": {"id": "T1499", "name": "Endpoint Denial of Service", "tactic": "Impact"},
    "qr_scam": {"id": "T1204", "name": "User Execution", "tactic": "Execution"},
    "normal_banking_day": {"id": "None", "name": "Normal", "tactic": "None"},
    "salary_day": {"id": "None", "name": "Normal", "tactic": "None"},
    "account_takeover": {"id": "T1078.004", "name": "Valid Accounts: Cloud Accounts", "tactic": "Initial Access"},
    "upi_fraud": {"id": "T1566", "name": "Phishing", "tactic": "Initial Access"}
}"""

    content = re.sub(r'# MITRE ATT&CK Mappings for Cyber Checkpoint.*?\}', new_mitre, content, flags=re.DOTALL)

    checkpoints_code = """    def _eval_identity_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        import datetime
        twin = get_or_create_digital_twin(user_id)
        
        kyc = twin.identity.get("kyc_status", "")
        created_at_str = twin.identity.get("created_at", "2020-01-01 00:00:00")
        try:
            created_at = datetime.datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
        except:
            created_at = datetime.datetime.now()
        age_days = (datetime.datetime.now() - created_at).days
        
        days_since_cred = data.get("days_since_credential_change", 90)
        failed_auth = data.get("prior_failed_auth_count", 0)
        
        score = 100.0
        reasons = []
        if "TIER-3" in kyc or "BIOMETRIC" in kyc:
            reasons.append("KYC Verified (Tier-3 Biometric)")
        else:
            score -= 20.0
            reasons.append(f"KYC Status: {kyc}")
            
        if age_days > 365:
            reasons.append(f"Account Age Mature ({age_days} days)")
        else:
            score -= 10.0
            reasons.append(f"New Account ({age_days} days)")
            
        if days_since_cred < 2:
            score -= 30.0
            reasons.append(f"Recent Credential Change ({days_since_cred} days)")
            
        if failed_auth > 2:
            score -= 40.0
            reasons.append(f"High Failed Auth Count ({failed_auth})")
            
        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {"score": max(0.0, score), "confidence": 0.98, "reasons": reasons}

    def _eval_device_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        from api.sdk_engine import sdk_engine
        
        device_id = data.get("device_id", "dev_unknown")
        twin = get_or_create_digital_twin(user_id)
        known_devices = [d["device_id"] for d in twin.devices.get("trusted_devices", [])]
        
        score = 100.0
        reasons = []
        if device_id in known_devices:
            reasons.append(f"Known Primary Device ({device_id})")
        else:
            score -= 40.0
            reasons.append(f"Unregistered Device Fingerprint ({device_id})")
            
        device_profile = sdk_engine.register_device(data)
        device_trust = device_profile.get("device_trust_score", 100.0)
        score = min(score, device_trust)
        
        if device_profile.get("root_detected"):
            reasons.append("Root/Jailbreak Detected")
        if device_profile.get("emulator_detected"):
            reasons.append("Emulator Detected")
        if device_profile.get("frida_detected"):
            reasons.append("Frida Detected")
            
        if not (device_profile.get("root_detected") or device_profile.get("emulator_detected") or device_profile.get("frida_detected")):
            reasons.append(f"Device Trust Score {device_profile.get('device_trust_score', 100.0)}")
            
        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {
            "score": score,
            "confidence": 0.96,
            "reasons": reasons
        }

    def _eval_session_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        from api.geo_utils import implied_velocity_kmh, get_coordinates, haversine_km, _parse_time
        import datetime
        
        ip = data.get("ip", "185.15.2.22")
        city = data.get("city")
        curr_geo = get_coordinates(city if city else ip)
        
        twin = get_or_create_digital_twin(user_id)
        home_geo = get_coordinates(twin.locations.get("home_location", {}).get("city", "Mumbai"))
        prev_ts = "2026-07-23 09:00:00"
        if twin.locations.get("travel_history"):
            last_travel = twin.locations["travel_history"][-1]
            prev_ts = last_travel.get("timestamp", prev_ts)
            home_geo = get_coordinates(last_travel.get("city", "Mumbai"))
        
        curr_ts = data.get("timestamp", datetime.datetime.now())
        
        velocity = implied_velocity_kmh(home_geo, prev_ts, curr_geo, curr_ts)
        
        score = 100.0
        reasons = []
        
        dist = haversine_km(home_geo.get("lat", 0), home_geo.get("lon", 0), curr_geo.get("lat", 0), curr_geo.get("lon", 0))
        t1 = _parse_time(prev_ts)
        t2 = _parse_time(curr_ts)
        mins = max(1, abs((t2 - t1).total_seconds()) / 60.0)
        
        if velocity > 900:
            score -= 85.0
            reasons.append(f"Impossible Travel Event ({home_geo.get('city', 'Unknown')} to {curr_geo.get('city', 'Unknown')} in {int(mins)} min = {velocity:,.0f} km/h implied velocity)")
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
            
        score = max(0.0, score)
        return {
            "score": score,
            "reasons": reasons
        }

    def _eval_behavior_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        twin = get_or_create_digital_twin(user_id)
        
        scenario = data.get("scenario_id", "")
        
        if not hasattr(twin, 'behavior') or not twin.behavior:
            reasons = ["No digital twin baseline exists for behavior"]
            if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
                reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            return {
                "score": 50.0,
                "deviation_index": 50.0,
                "reasons": reasons
            }
            
        score = 100.0
        reasons = []
        dev = 0.0
        
        amount = float(data.get("amount", 0))
        mean_spend = 5000.0 # twin.behavior might not have this, default to 5000
        std_spend = 1000.0
        
        if std_spend > 0:
            z_score = abs(amount - mean_spend) / std_spend
            if z_score > 3:
                score -= 30.0
                dev += 30.0
                reasons.append(f"Anomalous Spend Amount (z={z_score:.1f}, {amount} vs mean {mean_spend})")
            else:
                reasons.append("Normal Spending Envelope")
        
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {
            "score": max(0.0, score),
            "deviation_index": dev,
            "reasons": reasons or ["Matches behavior baseline"]
        }

    def _eval_cyber_checkpoint(self, user_id: str, data: dict) -> dict:
        events = data.get("cyber_events", [])
        if data.get("cyber_compromise_in_window"):
            events.append({"type": "impossible_travel_login", "severity": "HIGH", "age_hours": 0.1})
            events.append({"type": "cookie_theft_reuse", "severity": "CRITICAL", "age_hours": 0.5})
            
        score = 100.0
        reasons = []
        mitre_tech = []
        threat_category = "CLEAN"
        scenario = data.get("scenario_id", "")
        
        if not events:
            reasons = ["No Active Threat Feeds Flagged"]
            if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
                reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            return {
                "score": 98.0,
                "confidence": 0.99,
                "threat_category": "CLEAN",
                "mitre_techniques": [],
                "reasons": reasons
            }
            
        for ev in events:
            sev = ev.get("severity", "MEDIUM")
            age = ev.get("age_hours", 1.0)
            weight = 30.0 if sev == "CRITICAL" else 20.0 if sev == "HIGH" else 10.0
            decay = max(0.1, 1.0 / (1.0 + age))
            score -= weight * decay
            
            ev_type = ev.get("type", "unknown")
            reasons.append(f"Cyber Event: {ev_type} (sev={sev}, {age:.1f}h ago)")
            if ev_type in MITRE_ATTACK_MAPPINGS:
                mitre_tech.append(MITRE_ATTACK_MAPPINGS[ev_type])
                
        if score < 50.0:
            threat_category = "CRITICAL_THREAT"
        elif score < 80.0:
            threat_category = "ELEVATED_RISK"
            
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {
            "score": max(0.0, score),
            "confidence": 0.98,
            "threat_category": threat_category,
            "mitre_techniques": mitre_tech,
            "reasons": reasons
        }

    def _eval_graph_checkpoint(self, user_id: str, data: dict) -> dict:
        import networkx as nx
        scenario = data.get("scenario_id", "")
        nodes = data.get("graph_nodes", [])
        edges = data.get("graph_edges", [])
        
        if not nodes and not edges:
            reasons = ["Graph is empty, returning neutral score"]
            if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
                reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            return {
                "score": 50.0,
                "confidence": 0.5,
                "relationship_summary": "Graph empty",
                "mule_ring_distance": -1,
                "reasons": reasons
            }
            
        G = nx.DiGraph()
        for n in nodes:
            G.add_node(n["id"], **n)
        for e in edges:
            G.add_edge(e["source"], e["target"])
            
        score = 100.0
        reasons = []
        distance = 5
        
        try:
            pr = nx.pagerank(G)
            user_pr = pr.get(user_id, 0.0)
            mules = [n for n, d in G.nodes(data=True) if str(d.get("risk", "")).upper() == "CRITICAL" or "mule" in str(d.get("type", "")).lower()]
            if mules and G.has_node(user_id):
                shortest = float('inf')
                for m in mules:
                    try:
                        d = nx.shortest_path_length(G, source=user_id, target=m)
                        if d < shortest: shortest = d
                    except:
                        pass
                    try:
                        d = nx.shortest_path_length(G, source=m, target=user_id)
                        if d < shortest: shortest = d
                    except:
                        pass
                
                if shortest < float('inf'):
                    distance = shortest
                    if distance <= 2:
                        score -= 50.0
                        reasons.append(f"Direct {distance}-Hop Transfer Link to Mule Ring")
                    else:
                        score -= 10.0
                        reasons.append(f"{distance} hops from Mule Ring")
                else:
                    reasons.append("No path to known Mule Rings")
            else:
                reasons.append("No known Mule nodes in graph")
                
            reasons.append(f"PageRank Score: {user_pr:.4f}")
        except Exception as e:
            reasons.append(f"Graph analysis failed: {str(e)}")
            
        if data.get("cyber_compromise_in_window"):
            score -= 40.0
            reasons.append("Known Compromised Graph Node")
            
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        return {
            "score": max(0.0, score),
            "confidence": 0.95,
            "mule_ring_distance": distance,
            "relationship_summary": reasons[0] if reasons else "Clean Graph",
            "reasons": reasons
        }"""

    content = re.sub(r'    def _eval_identity_checkpoint.*?def get_passport', checkpoints_code + '\n\n    def get_passport', content, flags=re.DOTALL)

    with open('api/session_intelligence_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched session_intelligence_engine.py")

if __name__ == "__main__":
    process_file()
