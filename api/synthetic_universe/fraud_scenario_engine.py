import random
from api.synthetic_universe.bank_model import default_bank
from api.synthetic_universe.customer_generator import generate_customers_batch
from api.synthetic_universe.device_location_generator import generate_device_profile, generate_location_telemetry
from api.synthetic_universe.transaction_behavior_engine import generate_transaction_universe
from api.synthetic_universe.cyber_event_generator import generate_cyber_telemetry_batch

SCENARIO_CATALOG = {
    "normal_banking_day": {"title": "Normal Banking Day Routine", "expected_action": "ALLOW", "expected_risk": 15},
    "salary_day": {"title": "Salary Day High-Volume Transfers", "expected_action": "ALLOW", "expected_risk": 22},
    "festival_shopping": {"title": "Festival Shopping Surge", "expected_action": "ALLOW", "expected_risk": 28},
    "upi_fraud": {"title": "UPI Collect Request Fraud", "expected_action": "CHALLENGE", "expected_risk": 68},
    "account_takeover": {"title": "Impossible Travel Account Takeover (ATO)", "expected_action": "BLOCK", "expected_risk": 94},
    "credential_stuffing": {"title": "Automated Credential Stuffing Botnet", "expected_action": "BLOCK", "expected_risk": 91},
    "sim_swap": {"title": "SIM Swap Interception Attack", "expected_action": "BLOCK", "expected_risk": 89},
    "qr_scam": {"title": "Malicious Merchant QR Overlay Scam", "expected_action": "CHALLENGE", "expected_risk": 64},
    "money_mule": {"title": "Known Mule Ring Layering Network", "expected_action": "BLOCK", "expected_risk": 96},
    "payroll_fraud": {"title": "Corporate Payroll File Tampering", "expected_action": "BLOCK", "expected_risk": 93},
    "insider_fraud": {"title": "Bank Employee Insider Privilege Abuse", "expected_action": "BLOCK", "expected_risk": 95},
    "cross_border": {"title": "Cross-Border Money Laundering Pipeline", "expected_action": "BLOCK", "expected_risk": 98}
}

def generate_bank_universe(num_customers: int = 100, num_txns: int = 500, seed: int = 42) -> dict:
    """
    Generates an enterprise-scale virtual banking ecosystem for Fusion National Bank.
    """
    random.seed(seed)
    
    # 1. Bank metadata
    bank_meta = default_bank.to_dict()
    
    # 2. Customer & Account generation
    customers = generate_customers_batch(num_customers)
    
    # Extract total accounts
    accounts = []
    for c in customers:
        accounts.extend(c["accounts"])
        
    # 3. Devices & Geolocation
    devices = [generate_device_profile(c["customer_id"], is_compromised=(c["customer_id"]=="usr_abc")) for c in customers]
    locations = [generate_location_telemetry("Moscow" if c["customer_id"]=="usr_abc" else c["city"]) for c in customers]
    
    # 4. Behavioral Transactions Generation
    transactions = generate_transaction_universe(customers, total_txns=num_txns, anomaly_pct=0.03)
    
    # 5. Cyber SIEM Events
    cyber_events = generate_cyber_telemetry_batch(customers, count=max(10, int(num_customers * 0.2)))
    
    # Ensure standard demo events are present
    cyber_events.insert(0, {
        "msg_type": "cyber_event",
        "event_id": "EVT-CYBER-8819",
        "event_type": "impossible_travel_login",
        "user_id": "usr_abc",
        "device_id": "dev_9999",
        "ip": "185.15.2.22",
        "timestamp": "2026-07-16 10:00:00",
        "severity": "critical",
        "km_from_baseline": 4500,
        "description": "Impossible Travel Login from Moscow, RU 40s prior to ₹7.5L transfer"
    })

    return {
        "bank_name": "Fusion National Bank",
        "stats": {
            "customers_count": len(customers),
            "accounts_count": len(accounts),
            "devices_count": len(devices),
            "transactions_count": len(transactions),
            "cyber_events_count": len(cyber_events),
            "branches_count": bank_meta["branches"],
            "atm_count": bank_meta["atm_terminals"]
        },
        "customers": customers[:50], # Sample preview
        "accounts": accounts[:50],
        "devices": devices[:50],
        "locations": locations[:50],
        "transactions": transactions,
        "cyber_events": cyber_events,
        "scenarios_available": list(SCENARIO_CATALOG.keys())
    }
