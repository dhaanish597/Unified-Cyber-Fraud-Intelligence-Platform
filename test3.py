import sys
from api.pipeline_engine import execute_pipeline
from api.risk_engine import evaluate

txn1 = {'amount': 750000.0, 'user_id': 'usr_abc', 'nameOrig': 'ACC_ABC_123', 'nameDest': 'ACC_MULE_NEW', 'cyber_compromise_in_window': True}
txn2 = {'amount': 750001.0, 'user_id': 'usr_abc', 'nameOrig': 'ACC_ABC_123', 'nameDest': 'ACC_MULE_NEW', 'cyber_compromise_in_window': True}

s1 = evaluate(txn1)['score']
s2 = evaluate(txn2)['score']

print(f"S1: {s1}")
print(f"S2: {s2}")
