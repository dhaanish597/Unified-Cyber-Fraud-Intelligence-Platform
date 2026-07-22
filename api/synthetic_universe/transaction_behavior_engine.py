import random
import numpy as np
from datetime import datetime, timedelta

ALL_PAYMENT_TYPES = [
    "UPI", "NEFT", "RTGS", "IMPS", "ATM_WITHDRAWAL", "CASH_DEPOSIT", 
    "CARD_SWIPE", "POS", "ONLINE_SHOPPING", "FUEL", "FOOD", "BILLS", 
    "SALARY_CREDIT", "LOAN_EMI", "INSURANCE", "MERCHANT_PAYMENT", "REFUND", "TRANSFER"
]

def simulate_customer_transaction(customer: dict, is_anomaly: bool = False, days_ago: int = 0) -> dict:
    """
    Simulates a transaction driven by Part 7 customer habits and Part 6 payment channels.
    Preserves exact demo values for usr_abc / txn_demo_999.
    """
    user_id = customer["customer_id"]
    salary = customer.get("annual_salary", 1200000)
    orig_acc = customer["primary_account"]
    habits = customer.get("behavior_profile", {})
    
    # Generate timestamp according to preferred login hours or random
    pref_hours = habits.get("preferred_login_hours", [9, 10, 11, 14, 15, 19, 20])
    hour = random.choice(pref_hours) if not is_anomaly else 2 # 2 AM off-hours for anomaly
    dt = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))
    dt = dt.replace(hour=hour)
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

    # DEMO SHORTCUT / ANOMALY CONDITION
    if is_anomaly or (user_id == "usr_abc" and days_ago == 0):
        amount = 750000.0
        txn_type = "TRANSFER"
        dest_acc = "ACC_MULE_NEW"
        channel = "UPI_EXPRESS"
        cyber_flag = True
        mule_cluster = "cluster_alpha"
        channel_risk = 0.94
    else:
        cyber_flag = False
        mule_cluster = None
        txn_type = random.choices(
            ["UPI", "CARD_SWIPE", "ONLINE_SHOPPING", "FOOD", "FUEL", "TRANSFER", "BILLS", "ATM_WITHDRAWAL", "NEFT"],
            weights=[0.35, 0.20, 0.15, 0.10, 0.08, 0.05, 0.04, 0.02, 0.01]
        )[0]
        channel = f"{txn_type}_GATEWAY"
        channel_risk = 0.05

        if txn_type in ["UPI", "TRANSFER"]:
            amount = float(round(random.uniform(200.0, min(80000.0, salary * 0.05)), 2))
            dest_acc = f"ACC_BENEF_{random.randint(100, 999)}"
        elif txn_type in ["CARD_SWIPE", "POS", "ONLINE_SHOPPING", "FOOD", "FUEL"]:
            amount = float(round(random.uniform(150.0, 8500.0), 2))
            dest_acc = f"ACC_MERCHANT_{random.randint(10, 99)}"
        elif txn_type == "BILLS":
            amount = float(round(random.uniform(500.0, 15000.0), 2))
            dest_acc = "ACC_UTILITY_BOARD_01"
        elif txn_type == "ATM_WITHDRAWAL":
            amount = float(round(random.choice([500, 1000, 2000, 5000, 10000, 20000]), 2))
            dest_acc = "ACC_ATM_404"
        elif txn_type == "NEFT":
            amount = float(round(random.uniform(50000.0, 500000.0), 2))
            dest_acc = f"ACC_CORP_VENDOR_{random.randint(10, 99)}"
        else:
            amount = float(round(random.uniform(500.0, 10000.0), 2))
            dest_acc = f"ACC_GENERIC_{random.randint(100, 999)}"

    txn_id = f"txn_syn_{abs(hash(user_id + str(amount) + timestamp)) % 900000 + 100000}"
    if user_id == "usr_abc" and is_anomaly:
        txn_id = "txn_demo_999"

    old_bal = round(amount * random.uniform(1.2, 3.5), 2)
    new_bal = 0.0 if is_anomaly else round(old_bal - amount, 2)

    return {
        "txn_id": txn_id,
        "step": random.randint(1, 744),
        "timestamp": timestamp,
        "user_id": user_id,
        "nameOrig": orig_acc,
        "amount": amount,
        "nameDest": dest_acc,
        "type": txn_type,
        "channel": channel,
        "oldbalanceOrg": old_bal,
        "newbalanceOrig": new_bal,
        "oldbalanceDest": 0.0 if is_anomaly else round(random.uniform(1000.0, 50000.0), 2),
        "newbalanceDest": amount if is_anomaly else round(random.uniform(1000.0, 100000.0), 2),
        "cyber_compromise_in_window": cyber_flag,
        "dest_mule_cluster_id": mule_cluster,
        "channel_risk_score": channel_risk
    }

def generate_transaction_universe(customers: list, total_txns: int = 1000, anomaly_pct: float = 0.02, seed: int = 42) -> list:
    """
    Generates millions/thousands of transactions with realistic distribution.
    Part 6 & Part 7 of Digital Banking Universe.
    """
    random.seed(seed)
    txns = []
    num_anomalies = int(total_txns * anomaly_pct)
    
    for i in range(total_txns):
        cust = random.choice(customers)
        is_anom = (i < num_anomalies) or (cust["customer_id"] == "usr_abc" and i == 0)
        days = random.randint(0, 30)
        txns.append(simulate_customer_transaction(cust, is_anomaly=is_anom, days_ago=days))

    # Sort chronologically
    txns.sort(key=lambda x: x["timestamp"])
    return txns

