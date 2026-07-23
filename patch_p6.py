import re

def process_file():
    with open('api/session_intelligence_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_identity = """    def _eval_identity_checkpoint(self, user_id: str, data: dict) -> dict:
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

        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9}"""

    new_behavior = """    def _eval_behavior_checkpoint(self, user_id: str, data: dict) -> dict:
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

        return {"score": max(0.0, score), "reasons": reasons, "deviation_index": round(dev_idx, 2)}"""

    new_cyber = """    def _eval_cyber_checkpoint(self, user_id: str, data: dict) -> dict:
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
            
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.85, "threat_category": cat, "mitre_techniques": mitre_tech}"""

    new_graph = """    def _eval_graph_checkpoint(self, user_id: str, data: dict) -> dict:
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
                
        return {"score": max(0.0, score), "reasons": reasons, "confidence": 0.9, "relationship_summary": rel_summary, "mule_ring_distance": -1 if distance == float('inf') else distance}"""

    # We patch the 4 methods.
    
    # 1. replace _eval_identity_checkpoint
    content = re.sub(r'    def _eval_identity_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_device_checkpoint', new_identity + '\n\n    def _eval_device_checkpoint', content, flags=re.DOTALL)
    
    # 2. replace _eval_behavior_checkpoint
    content = re.sub(r'    def _eval_behavior_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_cyber_checkpoint', new_behavior + '\n\n    def _eval_cyber_checkpoint', content, flags=re.DOTALL)
    
    # 3. replace _eval_cyber_checkpoint
    content = re.sub(r'    def _eval_cyber_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_graph_checkpoint', new_cyber + '\n\n    def _eval_graph_checkpoint', content, flags=re.DOTALL)
    
    # 4. replace _eval_graph_checkpoint
    content = re.sub(r'    def _eval_graph_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def get_passport', new_graph + '\n\n    def get_passport', content, flags=re.DOTALL)

    with open('api/session_intelligence_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched checkpoints with continuous math")

if __name__ == "__main__":
    process_file()
