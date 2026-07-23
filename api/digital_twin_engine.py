import datetime

from typing import Dict, List, Any

class CustomerDigitalTwin:
    """
    Customer Digital Twin Engine for Fusion Risk OS.
    Maintains a continuously evolving single source of truth for a customer's identity,
    devices, locations, transaction habits, graph centrality, risk history, and predictive profile.
    """
    def __init__(self, user_id: str = "usr_abc"):
        self.user_id = user_id
        
        # PART 2: IDENTITY PROFILE
        self.identity = {
            "customer_id": user_id,
            "full_name": "Rajesh Kumar" if user_id == "usr_abc" else f"Customer {user_id}",
            "kyc_status": "VERIFIED TIER-3 (BIOMETRIC)",
            "occupation": "Software Principal Engineer",
            "annual_salary": 3600000.0,
            "risk_tier": "HIGH" if user_id == "usr_abc" else "LOW",
            "relationship_manager": "RM_ANKIT_SHARMA",
            "primary_account": "ACC_ABC_123" if user_id == "usr_abc" else f"ACC_{user_id.upper()}",
            "account_types": ["SAVINGS", "SALARY", "CREDIT_PLATINUM"],
            "historical_fraud_count": 0,
            "trust_level": 94.5, # 0.0 to 100.0
            "created_at": "2020-03-15 09:00:00"
        }

        # PART 3: DEVICE PROFILE
        self.devices = {
            "trusted_devices": [
                {"device_id": "dev_9999", "name": "iPhone 15 Pro", "os": "iOS 17.5.1", "browser": "Safari Mobile", "fingerprint": "FP_a1b2c3d4e5", "trust_score": 0.98, "is_rooted": False},
                {"device_id": "dev_1103", "name": "MacBook Pro M3", "os": "macOS Sonoma 14.5", "browser": "Chrome Desktop", "fingerprint": "FP_f6g7h8i9j0", "trust_score": 0.96, "is_rooted": False}
            ],
            "new_devices": [],
            "compromised_devices": [],
            "browser_history": ["Chrome Desktop", "Safari Mobile", "Edge Desktop"],
            "os_history": ["iOS 17.5.1", "macOS Sonoma 14.5"],
            "sim_history": ["+91 98200 12345 (Jio 5G)"],
            "imei_history": ["356789012345678", "864201928374651"],
            "device_trust_score": 0.97,
            "root_detection_flag": False
        }

        # PART 4: LOCATION PROFILE
        self.locations = {
            "trusted_cities": ["Mumbai", "Pune"],
            "home_location": {"city": "Mumbai", "state": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777},
            "office_location": {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0880, "lon": 72.8890},
            "travel_history": [
                {"city": "Mumbai", "timestamp": "2026-07-15 18:30:00", "is_home": True},
                {"city": "Pune", "timestamp": "2026-06-20 11:00:00", "is_home": False}
            ],
            "foreign_countries_visited": [],
            "geo_velocity_kmh": 12.5,
            "impossible_travel_events": [],
            "vpn_usage_count": 0
        }

        # PART 5: TRANSACTION PROFILE
        self.transactions_profile = {
            "avg_daily_spend": 3200.0,
            "avg_monthly_spend": 85000.0,
            "normal_amount_range": {"min": 200.0, "max": 50000.0},
            "max_historical_single_tx": 125000.0,
            "transfer_frequency_per_week": 4.5,
            "merchant_preferences": ["Amazon Retail", "Swiggy", "Indian Oil", "Supermarket Hub"],
            "preferred_beneficiaries": ["ACC_BENEF_101", "ACC_BENEF_202", "ACC_FRIEND_99"],
            "salary_pattern": {"credited_day": 1, "avg_salary": 300000.0},
            "emi_pattern": {"emi_day": 5, "avg_emi": 45000.0},
            "utility_pattern": {"bill_day": 10, "avg_utility": 4500.0},
            "cash_withdrawal_pattern": {"frequency_days": 15, "avg_cash": 10000.0}
        }

        # PART 6: BEHAVIOR PROFILE
        self.behavior = {
            "preferred_login_hours": [8, 9, 10, 11, 14, 15, 19, 20, 21],
            "avg_session_duration_sec": 240,
            "weekend_spending_ratio": 0.35,
            "night_activity_ratio": 0.02, # 12 AM to 5 AM activity ratio
            "holiday_behavior_score": 0.88,
            "behavior_drift_index": 0.04 # Low drift
        }

        # PART 7: GRAPH PROFILE
        self.graph = {
            "neighborhood_size": 28,
            "community_id": "COMMUNITY_WEST_RETAIL_12",
            "distance_to_known_mule_ring": 5, # Safe distance
            "pagerank_score": 0.0042,
            "betweenness_centrality": 0.0015,
            "risk_neighbors_count": 0,
            "fraud_cluster_membership": None
        }

        # PART 8: RISK PROFILE
        self.risk = {
            "current_risk": 15.0, # Normal
            "historical_risk": [12.0, 14.0, 15.0, 18.0, 15.0],
            "risk_trend": "STABLE",
            "average_risk": 14.8,
            "peak_risk": 22.0,
            "recovered_cases_count": 0,
            "blocked_cases_count": 0,
            "false_positives_count": 0
        }

        # PART 11: PREDICTIVE ENGINE FORECASTS
        self.predictions = {
            "predicted_next_login": "2026-07-23 09:15:00 IST",
            "predicted_next_amount_range": "INR 500.00 – INR 4,500.00",
            "likely_merchant": "Swiggy Food Delivery",
            "likely_device": "iPhone 15 Pro (dev_9999)",
            "likely_location": "Mumbai, Maharashtra",
            "expected_daily_spend": 3200.0,
            "expected_weekly_spend": 22400.0
        }

        # PART 12: CHRONOLOGICAL TIMELINE
        self.timeline = [
            {"timestamp": "2020-03-15 09:00:00", "event_type": "ACCOUNT_CREATED", "title": "Account Opened", "description": "Primary Savings Account ACC_ABC_123 opened at Nariman Point Branch."},
            {"timestamp": "2020-03-16 10:15:00", "event_type": "DEVICE_ADDED", "title": "Primary Device Registered", "description": "iPhone 15 Pro (dev_9999) bound to mobile banking app."},
            {"timestamp": "2021-06-01 14:00:00", "event_type": "BENEFICIARY_ADDED", "title": "Trusted Beneficiary Added", "description": "ACC_BENEF_101 added with biometric MFA authorization."},
            {"timestamp": "2026-07-15 18:30:00", "event_type": "ROUTINE_TRANSACTION", "title": "Merchant Payment", "description": "₹1,250 spent at Swiggy via UPI_GATEWAY."}
        ]

    def update_twin(self, event_data: dict) -> dict:
        """
        Updates the Digital Twin dynamically from live streaming events.
        Part 1 & Part 15 of Customer Digital Twin Engine.
        """
        msg_type = event_data.get("msg_type", "transaction")
        timestamp = event_data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if msg_type == "cyber_event":
            evt_type = event_data.get("event_type", "unknown")
            severity = event_data.get("severity", "medium")
            ip = event_data.get("ip", "185.15.2.22")
            km = event_data.get("km_from_baseline", 0)

            # Update Location Profile if impossible travel
            if km > 1000 or "impossible_travel" in evt_type:
                self.locations["impossible_travel_events"].append({
                    "timestamp": timestamp,
                    "ip": ip,
                    "location": "Moscow, RU",
                    "km_from_home": km
                })
                self.locations["vpn_usage_count"] += 1
                self.locations["travel_history"].insert(0, {"city": "Moscow", "timestamp": timestamp, "is_home": False})

            # Update Device Profile if compromised
            if "rooted" in evt_type or severity == "critical":
                self.devices["device_trust_score"] = 0.12
                self.devices["root_detection_flag"] = True
                self.devices["compromised_devices"].append({
                    "device_id": event_data.get("device_id", "dev_9999"),
                    "ip": ip,
                    "flagged_at": timestamp
                })

            # Update Risk Profile
            self.risk["current_risk"] = 94.0
            self.risk["risk_trend"] = "ESCALATING"
            self.risk["historical_risk"].append(94.0)

            # Append to Timeline
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

            # Update Graph Profile if mule cluster detected
            if event_data.get("dest_mule_cluster_id"):
                self.graph["distance_to_known_mule_ring"] = 1 # Direct 1-hop link to mule
                self.graph["risk_neighbors_count"] += 1
                self.graph["fraud_cluster_membership"] = event_data["dest_mule_cluster_id"]

            if is_compromised or amount > 500000.0:
                self.risk["current_risk"] = 94.0
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
        """
        Part 9: DIGITAL TWIN COMPARISON & Part 10: DEVIATION ENGINE.
        Compares expected customer baseline vs. observed incoming transaction.
        """
        obs_amount = float(txn_data.get("amount", 0.0))
        obs_device = txn_data.get("device_id", "dev_9999")
        obs_ip = txn_data.get("ip", "185.15.2.22")
        obs_dest = txn_data.get("nameDest", "")
        obs_cyber = txn_data.get("cyber_compromise_in_window", False)
        obs_mule = txn_data.get("dest_mule_cluster_id")

        # 1. Device Deviation (0 to 100)
        trusted_dev_ids = [d["device_id"] for d in self.devices["trusted_devices"]]
        device_diff = obs_device not in trusted_dev_ids or self.devices["root_detection_flag"]
        device_dev_score = 95.0 if device_diff else 5.0

        # 2. Location Deviation
        location_diff = obs_ip == "185.15.2.22" or obs_cyber
        location_dev_score = 98.0 if location_diff else 4.0

        # 3. Amount Deviation
        amount_diff = obs_amount > self.transactions_profile["normal_amount_range"]["max"]
        amount_dev_score = min(100.0, (obs_amount / 50000.0) * 20.0) if amount_diff else 8.0

        # 4. Merchant/Beneficiary Deviation
        dest_diff = obs_dest not in self.transactions_profile["preferred_beneficiaries"]
        merchant_dev_score = 85.0 if obs_mule else (60.0 if dest_diff else 5.0)

        # 5. Cyber & Graph Deviation
        cyber_dev_score = 99.0 if obs_cyber else 2.0
        graph_dev_score = 96.0 if obs_mule else 5.0

        # 6. Overall Deviation Index (Weighted average)
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
            "overall_deviation_index": overall_dev_index, # 0.0 to 100.0
            "verdict": "CRITICAL_DEVIATION" if overall_dev_index > 75.0 else ("MODERATE_DEVIATION" if overall_dev_index > 40.0 else "NORMAL"),
            "deviations_breakdown": {
                "device_deviation": device_dev_score,
                "location_deviation": location_dev_score,
                "transaction_amount_deviation": amount_dev_score,
                "beneficiary_deviation": merchant_dev_score,
                "cyber_telemetry_deviation": cyber_dev_score,
                "graph_mule_ring_deviation": graph_dev_score
            },
            "comparison_diffs": {
                "device_difference": "UNTRUSTED / PROXY DEVICE (dev_9999 from Moscow IP)" if device_diff else "MATCHES_REGISTERED_IPHONE",
                "location_difference": "IMPOSSIBLE TRAVEL (Moscow, RU vs Home Mumbai)" if location_diff else "HOME_GEOLOCATION_MATCH",
                "amount_difference": f"ANOMALOUS SPIKE (INR {obs_amount:,.2f} vs Max Normal INR 50,000.00)" if amount_diff else "WITHIN_EXPECTED_RANGE",
                "beneficiary_difference": f"UNSEEN MULE RECIPIENT ({obs_dest} linked to {obs_mule})" if obs_mule else "KNOWN_BENEFICIARY",
                "velocity_difference": "BURST VELOCITY (Transfer 40s after foreign login)",
                "behavior_difference": "OFF-HOURS CRITICAL BALANCE DRAIN ATTEMPT"
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
            "timeline": self.timeline
        }

# Global in-memory Digital Twin Store
_TWIN_STORE: Dict[str, CustomerDigitalTwin] = {}

def get_or_create_digital_twin(user_id: str = "usr_abc") -> CustomerDigitalTwin:
    if user_id not in _TWIN_STORE:
        _TWIN_STORE[user_id] = CustomerDigitalTwin(user_id)
    return _TWIN_STORE[user_id]
