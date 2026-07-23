import sys
from api.pipeline_engine import execute_pipeline
t1 = execute_pipeline({'amount': 750000.0, 'user_id': 'usr_abc'})
t2 = execute_pipeline({'amount': 750001.0, 'user_id': 'usr_abc'})
print(f'Score 1: {t1["composite_score"]}')
print(f'Score 2: {t2["composite_score"]}')
print('Success' if t1["composite_score"] != t2["composite_score"] else 'Failed')
