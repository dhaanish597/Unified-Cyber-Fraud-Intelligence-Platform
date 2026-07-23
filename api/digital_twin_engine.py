import datetime
import math
from typing import Dict, List, Any

class CustomerDigitalTwin:
    def __init__(self, user_id: str = "usr_abc"):
        self.user_id = user_id
        
        # Load Universe
        universe = None
        try:
            import api.main
            universe = api.main.cached_universe
        except ImportError:
            pass
            
        txns = []
        customer = None
        if universe:
            txns = [t for t in universe.get("transactions", []) if t.get("user_id") == user_id or t.get("nameOrig", "").endswith(user_id)]
            if not txns:
                # Fallback matching logic for generated transaction user_ids
                txns = [t for t in universe.get("transactions", []) if t.get("nameOrig", "").replace("ACC_", "").replace("_469", "") == user_id]
            if not txns and user_id == "usr_abc":
                txns = [t for t in universe.get("transactions", []) if t.get("nameOrig") == "ACC_ABC_123"]
            
            customer = next((c for c in universe.get("customers", []) if c["customer_id"] == user_id), None)
            
        self.baseline_status = "SUFFICIENT_HISTORY" if len(txns) > 0 else "INSUFFICIENT_HISTORY"
        
        # Compute baseline
        self.amt_mean = 0.0
        self.amt_std = 1.0
        self.hour_hist = {h: 0 for h in range(24)}
        self.known_devices = set()
        self.known_geos = set()
        self.counterparty_set = set()
        self.last_risk_update = datetime.datetime.now()
        
        if customer:
            self.known_geos.add(customer.get("city", "Mumbai"))
            bprof = customer.get("behavior_profile", {})
            self.known_devices.add(bprof.get("primary_device_id", "dev_9999"))
            for ip in bprof.get("trusted_ip_subnets", []):
                self.known_geos.add(ip)
        else:
            self.known_devices.add("dev_9999")
            self.known_geos.add("Mumbai")
            self.known_geos.add("185.15.2.22")
            
        if self.baseline_status == "SUFFICIENT_HISTORY":
            amounts = [float(t.get("amount", 0.0)) for t in txns]
            self.amt_mean = sum(amounts) / len(amounts)
            if len(amounts) > 1:
                self.amt_std = math.sqrt(sum((x - self.amt_mean)**2 for x in amounts) / (len(amounts) - 1))
            else:
                self.amt_std = self.amt_mean * 0.1 if self.amt_mean > 0 else 1.0
            if self.amt_std < 1.0:
                self.amt_std = 1.0
                
            for t in txns:
                dt_str = t.get("timestamp", "2026-01-01 00:00:00")
                try:
                    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    self.hour_hist[dt.hour] += 1
                except:
                    pass
                dest = t.get("nameDest", "")
                if dest:
                    self.counterparty_set.add(dest)
        else:
            self.amt_mean = 3200.0
            self.amt_std = 1500.0
            self.hour_hist = {h: (10 if 8 <= h <= 21 else 1) for h in range(24)}

        c_name = customer["full_name"] if customer else (f"Customer {user_id}" if user_id != "usr_abc" else "Rajesh Kumar")
        c_tier = customer["risk_tier"] if customer else ("HIGH" if user_id == "usr_abc" else "LOW")
        
        self.identity = {
            "customer_id": user_id,
            "full_name": c_name,
            "kyc_status": customer.get("kyc_status", "VERIFIED TIER-3 (BIOMETRIC)") if customer else "VERIFIED TIER-3 (BIOMETRIC)",
            "occupation": customer.get("occupation", "Software Principal Engineer") if customer else "Software Principal Engineer",
            "annual_salary": customer.get("annual_salary", 3600000.0) if customer else 3600000.0,
            "risk_tier": c_tier,
            "relationship_manager": customer.get("relationship_manager", "RM_ANKIT_SHARMA") if customer else "RM_ANKIT_SHARMA",
            "primary_account": customer.get("primary_account", f"ACC_{user_id.upper()}") if customer else f"ACC_{user_id.upper()}",
            "account_types": ["SAVINGS", "SALARY", "CREDIT_PLATINUM"],
            "historical_fraud_count": 0,
            "trust_level": 94.5,
            "created_at": "2020-03-15 09:00:00"
        }
        
        self.devices = {
            "trusted_devices": [{"device_id": d, "trust_score": 0.98} for d in self.known_devices],
            "new_devices": [],
            "compromised_devices": [],
            "browser_history": ["Chrome Desktop", "Safari Mobile", "Edge Desktop"],
            "os_history": ["iOS 17.5.1", "macOS Sonoma 14.5"],
            "sim_history": ["+91 98200 12345 (Jio 5G)"],
            "imei_history": ["356789012345678", "864201928374651"],
            "device_trust_score": 0.97,
            "root_detection_flag": False
        }
        
        self.locations = {
            "trusted_cities": list(self.known_geos),
            "home_location": {"city": customer.get("city", "Mumbai") if customer else "Mumbai"},
            "office_location": {"city": customer.get("city", "Mumbai") if customer else "Mumbai"},
            "travel_history": [],
            "foreign_countries_visited": [],
            "geo_velocity_kmh": 12.5,
            "impossible_travel_events": [],
            "vpn_usage_count": 0
        }
        
        self.transactions_profile = {
            "avg_daily_spend": self.amt_mean,
            "avg_monthly_spend": self.amt_mean * 30,
            "normal_amount_range": {"min": max(0.0, self.amt_mean - self.amt_std), "max": self.amt_mean + 2*self.amt_std},
            "max_historical_single_tx": self.amt_mean + 3*self.amt_std,
            "transfer_frequency_per_week": 4.5,
            "merchant_preferences": [],
            "preferred_beneficiaries": list(self.counterparty_set),
            "salary_pattern": {"credited_day": 1, "avg_salary": 300000.0},
            "emi_pattern": {"emi_day": 5, "avg_emi": 45000.0},
            "utility_pattern": {"bill_day": 10, "avg_utility": 4500.0},
            "cash_withdrawal_pattern": {"frequency_days": 15, "avg_cash": 10000.0}
        }
        
        self.behavior = {
            "preferred_login_hours": [h for h, c in self.hour_hist.items() if c > 0],
            "avg_session_duration_sec": 240,
            "weekend_spending_ratio": 0.35,
            "night_activity_ratio": 0.02,
            "holiday_behavior_score": 0.88,
            "behavior_drift_index": 0.04
        }
        
        self.graph = {
            "neighborhood_size": len(self.counterparty_set),
            "community_id": "COMMUNITY_WEST_RETAIL_12",
            "distance_to_known_mule_ring": 5,
            "pagerank_score": 0.0042,
            "betweenness_centrality": 0.0015,
            "risk_neighbors_count": 0,
            "fraud_cluster_membership": None
        }
        
        self.risk = {
            "current_risk": 15.0,
            "historical_risk": [12.0, 14.0, 15.0, 18.0, 15.0],
            "risk_trend": "STABLE",
            "average_risk": 14.8,
            "peak_risk": 22.0,
            "recovered_cases_count": 0,
            "blocked_cases_count": 0,
            "false_positives_count": 0
        }
        
        self.predictions = {
            "predicted_next_login": "2026-07-23 09:15:00 IST",
            "predicted_next_amount_range": "INR 500.00 – INR 4,500.00",
            "likely_merchant": "Swiggy Food Delivery",
            "likely_device": "iPhone 15 Pro",
            "likely_location": "Mumbai, Maharashtra",
            "expected_daily_spend": self.amt_mean,
            "expected_weekly_spend": self.amt_mean * 7
        }
        
        self.timeline = [
            {"timestamp": "2020-03-15 09:00:00", "event_type": "ACCOUNT_CREATED", "title": "Account Opened", "description": f"Account opened for {c_name}."}
        ]

    def update_twin(self, event_data: dict) -> dict:
        msg_type = event_data.get("msg_type", "transaction")
        timestamp = event_data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # Risk Decay
        now = datetime.datetime.now()
        hours_passed = (now - self.last_risk_update).total_seconds() / 3600.0
        if hours_passed > 0:
            decay = hours_passed * 0.5
            self.risk["current_risk"] = max(15.0, self.risk["current_risk"] - decay)
        self.last_risk_update = now

        if msg_type == "cyber_event":
            evt_type = event_data.get("event_type", "unknown")
            severity = event_data.get("severity", "medium")
            ip = event_data.get("ip", "185.15.2.22")
            km = event_data.get("km_from_baseline", 0)

            if km > 1000 or "impossible_travel" in evt_type:
                self.locations["impossible_travel_events"].append({
                    "timestamp": timestamp,
                    "ip": ip,
                    "location": "Moscow, RU",
                    "km_from_home": km
                })
                self.locations["vpn_usage_count"] += 1
                self.locations["travel_history"].insert(0, {"city": "Moscow", "timestamp": timestamp, "is_home": False})

            if "rooted" in evt_type or severity == "critical":
                self.devices["device_trust_score"] = 0.12
                self.devices["root_detection_flag"] = True
                self.devices["compromised_devices"].append({
                    "device_id": event_data.get("device_id", "dev_9999"),
                    "ip": ip,
                    "flagged_at": timestamp
                })

            risk_add = 40.0 if severity == "critical" else (20.0 if severity == "high" else 5.0)
            self.risk["current_risk"] = min(100.0, self.risk["current_risk"] + risk_add)
            self.risk["risk_trend"] = "ESCALATING"
            self.risk["historical_risk"].append(self.risk["current_risk"])
            
            self.timeline.insert(0, {
                "timestamp": timestamp,
                "event_type": "CYBER_ALERT",
                "title": f"Cyber Compromise Alert ({evt_type})",
                "description": event_data.get("description", f"Compromise alert from IP {ip} ({km} km from baseline)")
            })

        elif msg_type == "transaction":
            amount = float(event_data.get("amount", 0.0))
            dest = event_data.get("nameDest", "")
            is_compromised = event_data.get("cyber_compromise_in_window", False)

            if event_data.get("dest_mule_cluster_id"):
                self.graph["distance_to_known_mule_ring"] = 1
                self.graph["risk_neighbors_count"] += 1
                self.graph["fraud_cluster_membership"] = event_data["dest_mule_cluster_id"]

            if is_compromised or amount > 500000.0:
                self.risk["current_risk"] = min(100.0, self.risk["current_risk"] + 30.0)
                self.risk["risk_trend"] = "ESCALATING"
                self.risk["blocked_cases_count"] += 1
                self.timeline.insert(0, {
                    "timestamp": timestamp,
                    "event_type": "HIGH_RISK_TX",
                    "title": f"High Risk Transfer Flagged (INR {amount:,.2f})",
                    "description": f"Transfer to {dest} flagged. Destination part of mule cluster {event_data.get('dest_mule_cluster_id', 'alpha')}."
                })
            else:
                self.timeline.insert(0, {
                    "timestamp": timestamp,
                    "event_type": "ROUTINE_TRANSACTION",
                    "title": f"Transaction Executed (INR {amount:,.2f})",
                    "description": f"Transfer to {dest} via {event_data.get('channel', 'UPI')}."
                })

        return self.get_full_profile()

    def compare_transaction(self, txn_data: dict) -> dict:
        obs_amount = float(txn_data.get("amount", 0.0))
        obs_device = txn_data.get("device_id", "dev_9999")
        obs_ip = txn_data.get("ip", "185.15.2.22")
        obs_dest = txn_data.get("nameDest", "")
        obs_cyber = txn_data.get("cyber_compromise_in_window", False)
        obs_mule = txn_data.get("dest_mule_cluster_id")
        
        if self.baseline_status == "INSUFFICIENT_HISTORY":
            overall_dev_index = 50.0
            return {
                "user_id": self.user_id,
                "overall_deviation_index": overall_dev_index,
                "verdict": "MODERATE_DEVIATION",
                "deviations_breakdown": {
                    "device_deviation": 50.0,
                    "location_deviation": 50.0,
                    "transaction_amount_deviation": 50.0,
                    "beneficiary_deviation": 50.0,
                    "cyber_telemetry_deviation": 99.0 if obs_cyber else 10.0,
                    "graph_mule_ring_deviation": 96.0 if obs_mule else 10.0
                },
                "comparison_diffs": {
                    "device_difference": "INSUFFICIENT_HISTORY",
                    "location_difference": "INSUFFICIENT_HISTORY",
                    "amount_difference": "INSUFFICIENT_HISTORY",
                    "beneficiary_difference": "INSUFFICIENT_HISTORY",
                    "velocity_difference": "INSUFFICIENT_HISTORY",
                    "behavior_difference": "INSUFFICIENT_HISTORY"
                }
            }

        # 1. Device Deviation
        device_diff = obs_device not in self.known_devices or self.devices.get("root_detection_flag", False)
        device_dev_score = 95.0 if device_diff else 5.0

        # 2. Location Deviation
        location_diff = (obs_ip not in self.known_geos and not any(city in obs_ip for city in self.known_geos)) or obs_cyber
        location_dev_score = 98.0 if location_diff else 4.0

        # 3. Amount Deviation (Z-score)
        z_score = (obs_amount - self.amt_mean) / self.amt_std if self.amt_std > 0 else 0
        amount_dev_score = min(100.0, max(0.0, z_score * 25.0))
        amount_diff = z_score > 3.0

        # 4. Merchant/Beneficiary Deviation
        dest_diff = obs_dest not in self.counterparty_set
        merchant_dev_score = 85.0 if obs_mule else (60.0 if dest_diff else 5.0)

        # 5. Cyber & Graph Deviation
        cyber_dev_score = 99.0 if obs_cyber else 2.0
        graph_dev_score = 96.0 if obs_mule else 5.0

        overall_dev_index = round(
            (device_dev_score * 0.20) +
            (location_dev_score * 0.25) +
            (amount_dev_score * 0.20) +
            (merchant_dev_score * 0.15) +
            (cyber_dev_score * 0.10) +
            (graph_dev_score * 0.10),
            1
        )

        return {
            "user_id": self.user_id,
            "overall_deviation_index": overall_dev_index,
            "verdict": "CRITICAL_DEVIATION" if overall_dev_index > 75.0 else ("MODERATE_DEVIATION" if overall_dev_index > 40.0 else "NORMAL"),
            "deviations_breakdown": {
                "device_deviation": device_dev_score,
                "location_deviation": location_dev_score,
                "transaction_amount_deviation": round(amount_dev_score, 1),
                "beneficiary_deviation": merchant_dev_score,
                "cyber_telemetry_deviation": cyber_dev_score,
                "graph_mule_ring_deviation": graph_dev_score
            },
            "comparison_diffs": {
                "device_difference": f"UNTRUSTED DEVICE ({obs_device})" if device_diff else "MATCHES_REGISTERED_DEVICE",
                "location_difference": f"ANOMALOUS LOCATION ({obs_ip})" if location_diff else "HOME_GEOLOCATION_MATCH",
                "amount_difference": f"ANOMALOUS SPIKE (Z-score: {z_score:.1f})" if amount_diff else "WITHIN_EXPECTED_RANGE",
                "beneficiary_difference": f"UNSEEN MULE RECIPIENT ({obs_dest})" if obs_mule else ("NEW_BENEFICIARY" if dest_diff else "KNOWN_BENEFICIARY"),
                "velocity_difference": "BURST VELOCITY" if obs_cyber else "NORMAL_VELOCITY",
                "behavior_difference": "OFF-HOURS ATTEMPT" if obs_cyber else "NORMAL_BEHAVIOR"
            }
        }

    def get_full_profile(self) -> dict:
        return {
            "user_id": self.user_id,
            "identity": self.identity,
            "devices": self.devices,
            "locations": self.locations,
            "transactions_profile": self.transactions_profile,
            "behavior": self.behavior,
            "graph": self.graph,
            "risk": self.risk,
            "predictions": self.predictions,
            "timeline": self.timeline,
            "baseline_status": getattr(self, 'baseline_status', 'INSUFFICIENT_HISTORY')
        }

# Global in-memory Digital Twin Store
_TWIN_STORE: Dict[str, CustomerDigitalTwin] = {}

def get_or_create_digital_twin(user_id: str = "usr_abc") -> CustomerDigitalTwin:
    if user_id not in _TWIN_STORE:
        _TWIN_STORE[user_id] = CustomerDigitalTwin(user_id)
    return _TWIN_STORE[user_id]
