import io
import json
import csv

def export_dataset_csv(transactions: list) -> str:
    """Exports transactions list to canonical PaySim/Synthetic CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig",
        "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud", "isFlaggedFraud",
        "user_id", "device_id", "ip", "cyber_compromise_in_window", "dest_mule_cluster_id"
    ])
    
    writer.writeheader()
    for t in transactions:
        row = {
            "step": t.get("step", 1),
            "type": t.get("type", "TRANSFER"),
            "amount": t.get("amount", 0.0),
            "nameOrig": t.get("nameOrig", ""),
            "oldbalanceOrg": t.get("oldbalanceOrg", 0.0),
            "newbalanceOrig": t.get("newbalanceOrig", 0.0),
            "nameDest": t.get("nameDest", ""),
            "oldbalanceDest": t.get("oldbalanceDest", 0.0),
            "newbalanceDest": t.get("newbalanceDest", 0.0),
            "isFraud": 1 if t.get("cyber_compromise_in_window") else 0,
            "isFlaggedFraud": 1 if t.get("cyber_compromise_in_window") else 0,
            "user_id": t.get("user_id", ""),
            "device_id": t.get("device_id", "dev_9999"),
            "ip": t.get("ip", "185.15.2.22"),
            "cyber_compromise_in_window": t.get("cyber_compromise_in_window", False),
            "dest_mule_cluster_id": t.get("dest_mule_cluster_id", "")
        }
        writer.writerow(row)
        
    return output.getvalue()

def export_dataset_json(universe: dict) -> str:
    """Exports complete bank universe to JSON string."""
    return json.dumps(universe, indent=2)
