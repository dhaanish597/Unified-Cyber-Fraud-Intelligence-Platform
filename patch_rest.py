import re

def process_file():
    with open('api/session_intelligence_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_identity = """    def _eval_identity_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 100.0
        reasons = []
        try:
            import api.main
            universe = api.main.cached_universe or {}
            customers = universe.get("customers", [])
            cust = next((c for c in customers if c.get("customer_id") == user_id), None)
        except:
            cust = None

        if cust:
            risk = cust.get("risk_tier", "MEDIUM")
            if risk == "HIGH":
                score -= 30
                reasons.append(f"Synthetic KYC: Risk Tier {risk}")
            elif risk == "MEDIUM":
                score -= 10
                reasons.append(f"Synthetic KYC: Risk Tier {risk}")
            else:
                reasons.append(f"Synthetic KYC: Risk Tier {risk}")
                
            salary = cust.get("annual_salary", 0)
            if salary < 500000:
                score -= 10
                reasons.append(f"Income segment (low)")
            else:
                reasons.append(f"Income segment (high)")
        else:
            from api.digital_twin_engine import get_or_create_digital_twin
            twin = get_or_create_digital_twin(user_id)
            if not twin or not hasattr(twin, "identity") or not twin.identity:
                return {"score": 50.0, "reasons": ["No identity baseline exists. Neutral score."], "confidence": 0.5}
            
            kyc = twin.identity.get("kyc_status", "UNKNOWN")
            if "TIER-3" in kyc:
                reasons.append("KYC: Tier-3 Biometric Verified")
            elif "TIER-2" in kyc:
                score -= 10
                reasons.append("KYC: Tier-2 Document Verified")
            else:
                score -= 30
                reasons.append(f"KYC: {kyc}")

        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9}"""

    new_device = """    def _eval_device_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.sdk_engine import sdk_engine
        
        device_id = data.get("device_id", "dev_9999")
        ip = data.get("ip", "185.15.2.22")
        
        from api.digital_twin_engine import get_or_create_digital_twin
        twin = get_or_create_digital_twin(user_id)
        trusted = [d["device_id"] for d in twin.devices.get("trusted_devices", [])]
        
        is_trusted = device_id in trusted
        
        # We reuse the real risk-deduction math from sdk_engine.register_device
        sdk_res = sdk_engine.register_device(device_id, {"ip": ip})
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
        
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.85}"""

    new_session = """    def _eval_session_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        from api.geo_utils import implied_velocity_kmh, get_coordinates, haversine_km, _parse_time
        import datetime
        
        ip = data.get("ip", "185.15.2.22")
        city = data.get("city")
        curr_geo = get_coordinates(city if city else ip)
        
        twin = get_or_create_digital_twin(user_id)
        home_geo = get_coordinates(twin.locations.get("home_location", {}).get("city", "Mumbai"))
        
        history = twin.locations.get("travel_history", [])
        if history:
            history_sorted = sorted(history, key=lambda x: _parse_time(x.get("timestamp", "2000-01-01 00:00:00")))
            last_travel = history_sorted[-1]
            prev_ts = last_travel.get("timestamp")
            prev_geo = get_coordinates(last_travel.get("city", "Mumbai"))
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
            
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.94}"""

    new_behavior = """    def _eval_behavior_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 100.0
        reasons = []
        dev_idx = 0.0
        try:
            import api.main
            universe = api.main.cached_universe or {}
            accounts = universe.get("accounts", [])
            acc = next((a for a in accounts if a.get("customer_id") == user_id), None)
        except:
            acc = None

        amt = data.get("amount", 0.0)

        if acc:
            avg_txn = acc.get("avg_transaction_value", 5000)
            if amt > avg_txn * 5:
                score -= 40.0
                dev_idx = 5.0
                reasons.append(f"Transaction (INR {amt}) > 5x avg (INR {avg_txn})")
            elif amt > avg_txn * 2:
                score -= 15.0
                dev_idx = 2.0
                reasons.append(f"Transaction (INR {amt}) > 2x avg (INR {avg_txn})")
            else:
                reasons.append(f"Transaction amount normal vs average")
        else:
            from api.digital_twin_engine import get_or_create_digital_twin
            twin = get_or_create_digital_twin(user_id)
            if not twin or not hasattr(twin, "behavior") or not twin.behavior:
                return {"score": 50.0, "reasons": ["No behavior baseline exists. Neutral score."], "deviation_index": 0.0}
                
            avg = twin.behavior.get("avg_transaction_amount", 5500.0)
            std = twin.behavior.get("std_transaction_amount", 1200.0)
            if std == 0: std = 1.0
            z_score = abs(amt - avg) / std
            dev_idx = z_score
            
            if z_score > 3.0:
                score -= 30.0
                reasons.append(f"Transaction Amount matches High Deviation (z={z_score:.1f})")
            else:
                reasons.append(f"Transaction Amount matches baseline (z={z_score:.1f})")

        return {"score": max(0.0, score), "reasons": reasons, "deviation_index": round(dev_idx, 2)}"""

    new_cyber = """    def _eval_cyber_checkpoint(self, user_id: str, data: dict) -> dict:
        score = 100.0
        reasons = []
        mitre_tech = []
        cat = "LOW_RISK"
        
        events = []
        try:
            import api.main
            universe = api.main.cached_universe or {}
            all_events = universe.get("cyber_events", [])
            events = [e for e in all_events if e.get("user_id") == user_id]
        except:
            pass
            
        if not events:
            from api.digital_twin_engine import get_or_create_digital_twin
            twin = get_or_create_digital_twin(user_id)
            if twin and hasattr(twin, "risk"):
                events = twin.risk.get("recent_cyber_events", [])
                
        is_compromised = data.get("cyber_compromise_in_window", False)
        
        if not events and not is_compromised:
            return {"score": 100.0, "reasons": ["No cyber compromise detected in window"], "confidence": 0.9, "threat_category": cat, "mitre_techniques": mitre_tech}
            
        if is_compromised:
            score -= 40.0
            cat = "HIGH_RISK"
            scenario = data.get("scenario_id", "impossible_travel_login")
            mapping = MITRE_ATTACK_MAPPINGS.get(scenario, {"id": "None", "name": "Unknown"})
            technique_id = mapping.get("id", "None")
            if technique_id != "None":
                reasons.append(f"Cyber compromise detected in window [{technique_id}]")
                mitre_tech.append(technique_id)
            else:
                reasons.append("Cyber compromise detected in window")
                
        for ev in events:
            score -= 10.0
            cat = "MEDIUM_RISK" if cat == "LOW_RISK" else cat
            reasons.append(f"Recent cyber event: {ev}")
            
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.85, "threat_category": cat, "mitre_techniques": mitre_tech}"""

    new_graph = """    def _eval_graph_checkpoint(self, user_id: str, data: dict) -> dict:
        try:
            import api.main
            universe = api.main.cached_universe or {}
            graph_topology = universe.get("graph_topology", {})
            nodes = graph_topology.get("nodes", [])
            edges = graph_topology.get("edges", [])
        except ImportError:
            nodes = []
            edges = []
            
        if not nodes:
            return {"score": 50.0, "reasons": ["Graph is empty. Neutral score."], "confidence": 0.5, "relationship_summary": "Empty", "mule_ring_distance": -1}
            
        import networkx as nx
        G = nx.Graph()
        for n in nodes:
            G.add_node(n["id"], **n)
        for e in edges:
            G.add_edge(e["source"], e["target"], **e)
            
        if user_id not in G:
            return {"score": 50.0, "reasons": [f"User {user_id} not in graph. Neutral score."], "confidence": 0.5, "relationship_summary": "Unknown", "mule_ring_distance": -1}
            
        mule_nodes = [n for n, attr in G.nodes(data=True) if attr.get("risk") == "HIGH" or attr.get("type") == "Mule"]
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
        if distance == 1:
            score -= 40.0
            reasons.append("1 hop to a known mule ring")
            rel_summary = "Direct link to Mule"
        elif distance == 2:
            score -= 20.0
            reasons.append("2 hops to a known mule ring")
            rel_summary = "2-hop link to Mule"
        elif distance == 3:
            score -= 10.0
            reasons.append("3 hops to a known mule ring")
            rel_summary = "3-hop link to Mule"
        elif distance != float('inf'):
            reasons.append(f"{distance} hops to known mule ring")
        else:
            reasons.append("No path to known mule ring")
            
        pr = nx.pagerank(G)
        user_pr = pr.get(user_id, 0)
        customers_pr = [p for n, p in pr.items() if G.nodes[n].get("type", "Customer") == "Customer"]
        if customers_pr:
            percentile = sum(1 for p in customers_pr if p < user_pr) / len(customers_pr) * 100
            if percentile > 90:
                score -= 15.0
                reasons.append(f"PageRank top {100-percentile:.1f}% percentile (High Centrality)")
            else:
                reasons.append(f"PageRank percentile: {percentile:.1f}%")
                
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9, "relationship_summary": rel_summary, "mule_ring_distance": -1 if distance == float('inf') else distance}"""

    # We patch all 6 methods.
    
    # 1. replace _eval_identity_checkpoint
    content = re.sub(r'    def _eval_identity_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_device_checkpoint', new_identity + '\n\n    def _eval_device_checkpoint', content, flags=re.DOTALL)
    
    # 2. replace _eval_device_checkpoint
    content = re.sub(r'    def _eval_device_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_session_checkpoint', new_device + '\n\n    def _eval_session_checkpoint', content, flags=re.DOTALL)
    
    # 3. replace _eval_session_checkpoint
    content = re.sub(r'    def _eval_session_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_behavior_checkpoint', new_session + '\n\n    def _eval_behavior_checkpoint', content, flags=re.DOTALL)
    
    # 4. replace _eval_behavior_checkpoint
    content = re.sub(r'    def _eval_behavior_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_cyber_checkpoint', new_behavior + '\n\n    def _eval_cyber_checkpoint', content, flags=re.DOTALL)
    
    # 5. replace _eval_cyber_checkpoint
    content = re.sub(r'    def _eval_cyber_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_graph_checkpoint', new_cyber + '\n\n    def _eval_graph_checkpoint', content, flags=re.DOTALL)
    
    # 6. replace _eval_graph_checkpoint
    content = re.sub(r'    def _eval_graph_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def analyse_session', new_graph + '\n\n    def analyse_session', content, flags=re.DOTALL)

    with open('api/session_intelligence_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched ALL 6 checkpoints in session_intelligence_engine.py with keys")

if __name__ == "__main__":
    process_file()
