import sys
from api.pipeline_engine import execute_pipeline
t1 = execute_pipeline({'amount': 750000.0, 'user_id': 'usr_abc', 'nameOrig': 'ACC_ABC_123', 'nameDest': 'ACC_MULE_NEW', 'ip': '185.15.2.22', 'device_id': 'dev_9999', 'cyber_compromise_in_window': True, 'dest_mule_cluster_id': 'cluster_alpha', 'oldbalanceOrg': 750000.0})
t2 = execute_pipeline({'amount': 750001.0, 'user_id': 'usr_abc', 'nameOrig': 'ACC_ABC_123', 'nameDest': 'ACC_MULE_NEW', 'ip': '185.15.2.22', 'device_id': 'dev_9999', 'cyber_compromise_in_window': True, 'dest_mule_cluster_id': 'cluster_alpha', 'oldbalanceOrg': 750001.0})
print(f'Score 1: {t1["composite_score"]}')
print(f'Score 2: {t2["composite_score"]}')
