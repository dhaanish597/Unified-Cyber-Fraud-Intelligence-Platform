import random
from api.synthetic_universe.bank_model import default_bank, get_virtual_bank
from api.synthetic_universe.customer_generator import generate_customers_batch
from api.synthetic_universe.device_location_generator import generate_device_profile, generate_location_telemetry
from api.synthetic_universe.transaction_behavior_engine import generate_transaction_universe
from api.synthetic_universe.cyber_event_generator import generate_cyber_telemetry_batch

SCENARIO_CATALOG = {
    "normal_banking_day": {
        "title": "Normal Banking Day Routine",
        "expected_action": "ALLOW",
        "expected_risk": 15,
        "attack_type": "NONE",
        "attack_narrative": "Standard retail peer-to-peer payments, merchant card swipes, and utility bill clearing across branches."
    },
    "salary_day": {
        "title": "Salary Day High-Volume Transfers",
        "expected_action": "ALLOW",
        "expected_risk": 22,
        "attack_type": "NONE",
        "attack_narrative": "Automated corporate payroll processing disbursing monthly salaries to employee accounts."
    },
    "festival_shopping": {
        "title": "Festival Shopping Surge",
        "expected_action": "ALLOW",
        "expected_risk": 28,
        "attack_type": "NONE",
        "attack_narrative": "Seasonal spike in retail e-commerce transactions and POS card transactions."
    },
    "upi_fraud": {
        "title": "UPI Collect Request Fraud",
        "expected_action": "CHALLENGE",
        "expected_risk": 68,
        "attack_type": "SOCIAL_ENGINEERING",
        "attack_narrative": "Victim tricked into approving a fake cashback refund collect request issued by a fraudster account."
    },
    "account_takeover": {
        "title": "Impossible Travel Account Takeover (ATO)",
        "expected_action": "BLOCK",
        "expected_risk": 94,
        "attack_type": "ACCOUNT_TAKEOVER",
        "attack_narrative": "Foreign IP login from Moscow (4,500 km away) followed 40s later by a ₹7.5L transfer to a newly added mule account."
    },
    "credential_stuffing": {
        "title": "Automated Credential Stuffing Botnet",
        "expected_action": "BLOCK",
        "expected_risk": 91,
        "attack_type": "CREDENTIAL_THEFT",
        "attack_narrative": "500 automated authentication attempts from botnet proxy pool targeting victim internet banking accounts."
    },
    "sim_swap": {
        "title": "SIM Swap Interception Attack",
        "expected_action": "BLOCK",
        "expected_risk": 89,
        "attack_type": "SIM_SWAP",
        "attack_narrative": "Telecom SIM swap performed 10 minutes prior to high-value wire transfer request bypassing SMS OTP."
    },
    "qr_scam": {
        "title": "Malicious Merchant QR Overlay Scam",
        "expected_action": "CHALLENGE",
        "expected_risk": 64,
        "attack_type": "QR_SCAM",
        "attack_narrative": "Physical QR sticker overlay at retail store redirecting merchant payments to an unverified shell account."
    },
    "money_mule": {
        "title": "Known Mule Ring Layering Network",
        "expected_action": "BLOCK",
        "expected_risk": 96,
        "attack_type": "MONEY_MULE",
        "attack_narrative": "Funds rapidly routed through a 14-node mule ring cluster identified via GraphSAGE centrality."
    },
    "payroll_fraud": {
        "title": "Corporate Payroll File Tampering",
        "expected_action": "BLOCK",
        "expected_risk": 93,
        "attack_type": "PAYROLL_FRAUD",
        "attack_narrative": "Batch payroll CSV file modified in transit to replace legitimate employee IFSC/Account entries with shell accounts."
    },
    "insider_fraud": {
        "title": "Bank Employee Insider Privilege Abuse",
        "expected_action": "BLOCK",
        "expected_risk": 95,
        "attack_type": "INSIDER_FRAUD",
        "attack_narrative": "Branch teller overriding daily KYC transaction limits to execute unauthorized off-duty transfer."
    },
    "cross_border": {
        "title": "Cross-Border Money Laundering Pipeline",
        "expected_action": "BLOCK",
        "expected_risk": 98,
        "attack_type": "CROSS_BORDER_LAUNDERING",
        "attack_narrative": "Rapid multi-currency SWIFT wire transfers hop through shell entities in high-risk jurisdictions."
    },
    "synthetic_identity": {
        "title": "Synthetic Identity KYC Fraud",
        "expected_action": "BLOCK",
        "expected_risk": 90,
        "attack_type": "SYNTHETIC_IDENTITY",
        "attack_narrative": "Fabricated KYC identity created using stolen Aadhaar prefix, maxing out credit limit within 48 hours."
    }
}

def generate_bank_universe(
    num_customers: int = 100, 
    num_txns: int = 500, 
    seed: int = 42,
    bank_code: str = "FUSB"
) -> dict:
    """
    Generates an enterprise-scale virtual banking ecosystem for Fusion Risk OS.
    Parts 1 through 11 of Digital Banking Universe.
    """
    random.seed(seed)
    bank_model = get_virtual_bank(bank_code)
    bank_meta = bank_model.to_dict()
    
    # 1. Customer & Account generation
    customers = generate_customers_batch(num_customers, seed=seed)
    
    accounts = []
    cards = []
    loans = []
    for c in customers:
        accounts.extend(c.get("accounts", []))
        cards.extend(c.get("cards", []))
        loans.extend(c.get("loans", []))
        
    # 2. Devices & Geolocation
    devices = [generate_device_profile(c["customer_id"], is_compromised=(c["customer_id"]=="usr_abc")) for c in customers]
    locations = [generate_location_telemetry("Moscow" if c["customer_id"]=="usr_abc" else c["city"], baseline_city=c["city"]) for c in customers]
    
    # 3. Behavioral Transactions Generation
    transactions = generate_transaction_universe(customers, total_txns=num_txns, anomaly_pct=0.03, seed=seed)
    
    # 4. Cyber SIEM Events
    cyber_events = generate_cyber_telemetry_batch(customers, count=max(10, int(num_customers * 0.2)))
    
    # Ensure standard demo events are present for usr_abc
    cyber_events.insert(0, {
        "msg_type": "cyber_event",
        "event_id": "EVT-CYBER-8819",
        "event_type": "impossible_travel_login",
        "user_id": "usr_abc",
        "device_id": "dev_9999",
        "session_id": "SESS_9921_CRITICAL",
        "ip": "185.15.2.22",
        "timestamp": "2026-07-16 10:00:00",
        "severity": "critical",
        "km_from_baseline": 4500,
        "description": "Impossible Travel Login from Moscow, RU 40s prior to ₹7.5L transfer"
    })

    return {
        "bank_metadata": bank_meta,
        "stats": {
            "bank_name": bank_meta["bank_name"],
            "customers_count": len(customers),
            "accounts_count": len(accounts),
            "cards_count": len(cards),
            "loans_count": len(loans),
            "devices_count": len(devices),
            "transactions_count": len(transactions),
            "cyber_events_count": len(cyber_events),
            "branches_count": bank_meta["branches_count"],
            "atm_count": bank_meta["atm_terminals_count"],
            "employees_count": bank_meta["employees_count"]
        },
        "customers": customers[:50], # Sample preview
        "accounts": accounts[:50],
        "devices": devices[:50],
        "locations": locations[:50],
        "transactions": transactions,
        "cyber_events": cyber_events,
        "scenarios_available": SCENARIO_CATALOG
    }

