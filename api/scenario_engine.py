import random
from datetime import datetime, timedelta

SCENARIOS = {
    "normal_banking_day": {
        "id": "normal_banking_day",
        "title": "Normal Banking Day Routine",
        "description": "Clean retail transactions, peer-to-peer payments, and routine merchant purchases.",
        "expected_action": "ALLOW",
        "expected_risk": 15,
        "sample_txns": [
            {"txn_id": "TXN-NORM-001", "user_id": "usr_retail_101", "amount": 1250.0, "type": "PAYMENT", "nameOrig": "ACC_RTL_101", "nameDest": "ACC_MERCHANT_44", "ip": "49.207.18.9", "device_id": "dev_normal_01", "cyber_compromise_in_window": False, "dest_mule_cluster_id": None},
            {"txn_id": "TXN-NORM-002", "user_id": "usr_retail_102", "amount": 3500.0, "type": "TRANSFER", "nameOrig": "ACC_RTL_102", "nameDest": "ACC_FRIEND_22", "ip": "103.22.45.10", "device_id": "dev_normal_02", "cyber_compromise_in_window": False, "dest_mule_cluster_id": None}
        ]
    },
    "salary_day": {
        "id": "salary_day",
        "title": "Salary Day High-Volume Processing",
        "description": "Mass automated corporate payroll transfers and routine utility bill payments.",
        "expected_action": "ALLOW",
        "expected_risk": 22,
        "sample_txns": [
            {"txn_id": "TXN-SALARY-101", "user_id": "usr_emp_881", "amount": 125000.0, "type": "TRANSFER", "nameOrig": "ACC_CORP_PAYROLL", "nameDest": "ACC_EMP_881", "ip": "14.142.36.2", "device_id": "dev_payroll_srv", "cyber_compromise_in_window": False, "dest_mule_cluster_id": None}
        ]
    },
    "upi_fraud": {
        "id": "upi_fraud",
        "title": "UPI Collect Request Fraud",
        "description": "Phishing collect request disguised as cashback refund targeting vulnerable users.",
        "expected_action": "CHALLENGE",
        "expected_risk": 68,
        "sample_txns": [
            {"txn_id": "TXN-UPI-301", "user_id": "usr_victim_09", "amount": 49999.0, "type": "TRANSFER", "nameOrig": "ACC_VICTIM_09", "nameDest": "ACC_UPI_PHISH", "ip": "117.201.8.44", "device_id": "dev_victim_09", "cyber_compromise_in_window": False, "dest_mule_cluster_id": "cluster_phish"}
        ]
    },
    "account_takeover": {
        "id": "account_takeover",
        "title": "Impossible Travel Account Takeover (ATO)",
        "description": "Foreign IP login 4,500 km away followed 40 seconds later by full balance drain.",
        "expected_action": "BLOCK",
        "expected_risk": 94,
        "sample_txns": [
            {"txn_id": "TXN-81293", "user_id": "usr_abc", "amount": 750000.0, "type": "TRANSFER", "nameOrig": "ACC_ABC_123", "nameDest": "ACC_MULE_NEW", "ip": "185.15.2.22", "device_id": "dev_9999", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_alpha"}
        ]
    },
    "credential_stuffing": {
        "id": "credential_stuffing",
        "title": "Automated Credential Stuffing Attack",
        "description": "500 failed login attempts from botnet proxy pool followed by compromised transfer.",
        "expected_action": "BLOCK",
        "expected_risk": 91,
        "sample_txns": [
            {"txn_id": "TXN-STUFF-501", "user_id": "usr_stuffed_12", "amount": 320000.0, "type": "TRANSFER", "nameOrig": "ACC_STUFF_12", "nameDest": "ACC_BOT_MULE", "ip": "194.26.29.110", "device_id": "dev_botnet_88", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_botnet"}
        ]
    },
    "sim_swap": {
        "id": "sim_swap",
        "title": "SIM Swap Interception Attack",
        "description": "Telco SIM porting event 10 mins prior to OTP bypass and transfer destination change.",
        "expected_action": "BLOCK",
        "expected_risk": 89,
        "sample_txns": [
            {"txn_id": "TXN-SIM-601", "user_id": "usr_sim_44", "amount": 450000.0, "type": "TRANSFER", "nameOrig": "ACC_SIM_44", "nameDest": "ACC_EXFIL_88", "ip": "27.56.12.90", "device_id": "dev_new_imei", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_sim_mule"}
        ]
    },
    "qr_scam": {
        "id": "qr_scam",
        "title": "Malicious Merchant QR Overlay Scam",
        "description": "Tampered QR code redirecting funds to malicious shell merchant account.",
        "expected_action": "CHALLENGE",
        "expected_risk": 64,
        "sample_txns": [
            {"txn_id": "TXN-QR-701", "user_id": "usr_qr_88", "amount": 15000.0, "type": "PAYMENT", "nameOrig": "ACC_QR_88", "nameDest": "ACC_FAKE_QR", "ip": "49.36.14.88", "device_id": "dev_qr_88", "cyber_compromise_in_window": False, "dest_mule_cluster_id": None}
        ]
    },
    "known_mule": {
        "id": "known_mule",
        "title": "Known Mule Ring Layering Network",
        "description": "Funds routed through a dense 14-node mule ring identified via GraphSAGE PageRank.",
        "expected_action": "BLOCK",
        "expected_risk": 96,
        "sample_txns": [
            {"txn_id": "TXN-MULE-801", "user_id": "usr_ring_01", "amount": 890000.0, "type": "TRANSFER", "nameOrig": "ACC_RING_01", "nameDest": "ACC_MULE_HUB", "ip": "103.88.22.11", "device_id": "dev_mule_ring", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_alpha"}
        ]
    },
    "corporate_payroll_fraud": {
        "id": "corporate_payroll_fraud",
        "title": "Corporate Payroll File Tampering",
        "description": "Unauthorized alteration of beneficiary IBAN accounts in batch payroll upload.",
        "expected_action": "BLOCK",
        "expected_risk": 93,
        "sample_txns": [
            {"txn_id": "TXN-PAYROLL-901", "user_id": "usr_hr_manager", "amount": 2500000.0, "type": "TRANSFER", "nameOrig": "ACC_CORP_MAIN", "nameDest": "ACC_SHELL_OFFSHORE", "ip": "115.240.88.19", "device_id": "dev_hr_tampered", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_offshore"}
        ]
    },
    "insider_fraud": {
        "id": "insider_fraud",
        "title": "Bank Employee Insider Privilege Abuse",
        "description": "Internal override of KYC limits and high-risk transfer during off-duty hours.",
        "expected_action": "BLOCK",
        "expected_risk": 95,
        "sample_txns": [
            {"txn_id": "TXN-INSIDER-950", "user_id": "usr_teller_402", "amount": 5000000.0, "type": "TRANSFER", "nameOrig": "ACC_HIGH_NET", "nameDest": "ACC_GHOST_101", "ip": "10.4.88.14", "device_id": "dev_internal_term", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_ghost"}
        ]
    },
    "atm_cash_out": {
        "id": "atm_cash_out",
        "title": "Synchronized ATM Cash-Out Ring",
        "description": "Simultaneous debit card withdrawal attempts across 5 physical ATM terminals.",
        "expected_action": "BLOCK",
        "expected_risk": 92,
        "sample_txns": [
            {"txn_id": "TXN-ATM-980", "user_id": "usr_xyz", "amount": 1200000.0, "type": "CASH_OUT", "nameOrig": "ACC_XYZ_992", "nameDest": "ACC_ATM_404", "ip": "103.45.12.8", "device_id": "dev_8812", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_beta"}
        ]
    },
    "cross_border_money_laundering": {
        "id": "cross_border_money_laundering",
        "title": "Cross-Border Money Laundering Pipeline",
        "description": "Rapid multi-hop wire transfer routing through shell corporations across jurisdictions.",
        "expected_action": "BLOCK",
        "expected_risk": 98,
        "sample_txns": [
            {"txn_id": "TXN-LAUNDER-999", "user_id": "usr_shell_co", "amount": 15000000.0, "type": "TRANSFER", "nameOrig": "ACC_SHELL_IN", "nameDest": "ACC_OFFSHORE_KYC_ZERO", "ip": "185.220.101.5", "device_id": "dev_tor_node", "cyber_compromise_in_window": True, "dest_mule_cluster_id": "cluster_global_ring"}
        ]
    }
}

def generate_scenario(scenario_id: str) -> dict:
    """Returns scenario configuration and generated payload."""
    scenario = SCENARIOS.get(scenario_id, SCENARIOS["account_takeover"])
    return {
        "scenario_id": scenario["id"],
        "title": scenario["title"],
        "description": scenario["description"],
        "expected_action": scenario["expected_action"],
        "expected_risk": scenario["expected_risk"],
        "transactions": scenario["sample_txns"]
    }

def get_all_scenarios_list() -> list:
    """Returns metadata for all 12 scenarios."""
    return [
        {
            "id": v["id"],
            "title": v["title"],
            "description": v["description"],
            "expected_action": v["expected_action"],
            "expected_risk": v["expected_risk"]
        } for v in SCENARIOS.values()
    ]
