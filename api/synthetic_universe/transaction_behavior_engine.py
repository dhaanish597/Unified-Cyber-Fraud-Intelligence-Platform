import random
import numpy as np
from datetime import datetime, timedelta

PAYMENT_TYPES = ["TRANSFER", "PAYMENT", "CASH_OUT", "DEPOSIT", "DEBIT"]

def simulate_customer_transaction(customer: dict, is_anomaly: bool = False, days_ago: int = 0) -> dict:
    user_id = customer["customer_id"]
    salary = customer["annual_salary"]
    orig_acc = customer["primary_account"]
    
    dt = datetime.now() - timedelta(days=days_ago, seconds=random.randint(0, 86400))
    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

    if is_anomaly or user_id == "usr_abc":
        amount = 750000.0
        txn_type = "TRANSFER"
        dest_acc = "ACC_MULE_NEW"
        cyber_flag = True
        mule_cluster = "cluster_alpha"
    else:
        cyber_flag = False
        mule_cluster = None
        txn_type = random.choices(PAYMENT_TYPES, weights=[0.4, 0.4, 0.1, 0.05, 0.05])[0]
        
        if txn_type == "TRANSFER":
            amount = round(random.uniform(500.0, min(50000.0, salary * 0.05)), 2)
            dest_acc = f"ACC_BENEF_{random.randint(100, 999)}"
        elif txn_type == "PAYMENT":
            amount = round(random.uniform(100.0, 5000.0), 2)
            dest_acc = f"ACC_MERCHANT_{random.randint(10, 99)}"
        elif txn_type == "CASH_OUT":
            amount = round(random.uniform(2000.0, 20000.0), 2)
            dest_acc = "ACC_ATM_404"
        else:
            amount = round(random.uniform(1000.0, 10000.0), 2)
            dest_acc = f"ACC_GENERIC_{random.randint(100, 999)}"

    txn_id = f"txn_syn_{abs(hash(user_id + str(amount) + timestamp)) % 900000 + 100000}"
    if user_id == "usr_abc" and is_anomaly:
        txn_id = "txn_demo_999"

    return {
        "txn_id": txn_id,
        "step": random.randint(1, 744),
        "timestamp": timestamp,
        "user_id": user_id,
        "nameOrig": orig_acc,
        "amount": amount,
        "nameDest": dest_acc,
        "type": txn_type,
        "oldbalanceOrg": round(amount * random.uniform(1.0, 2.5), 2),
        "newbalanceOrig": 0.0 if is_anomaly else round(amount * random.uniform(0.1, 1.5), 2),
        "oldbalanceDest": 0.0 if is_anomaly else round(random.uniform(1000.0, 50000.0), 2),
        "newbalanceDest": amount if is_anomaly else round(random.uniform(1000.0, 100000.0), 2),
        "cyber_compromise_in_window": cyber_flag,
        "dest_mule_cluster_id": mule_cluster
    }

def generate_transaction_universe(customers: list, total_txns: int = 1000, anomaly_pct: float = 0.02) -> list:
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
