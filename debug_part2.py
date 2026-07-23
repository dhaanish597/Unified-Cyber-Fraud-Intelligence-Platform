import sys
from api.synthetic_universe.fraud_scenario_engine import generate_bank_universe
from api.synthetic_universe.graph_generator import generate_graph_topology
import api.main

# Generate universe first
print("Generating universe...")
universe = generate_bank_universe(num_customers=50, num_txns=100, seed=42)
graph_topology = generate_graph_topology(universe)
universe["graph_topology"] = graph_topology
api.main.cached_universe = universe

customers = universe["customers"]
u1 = customers[0]["customer_id"]
u2 = customers[1]["customer_id"]
u3 = customers[2]["customer_id"]

from api.session_intelligence_engine import session_engine

print(f"Testing Part 2 for {u1}, {u2}, {u3}...")
res_a = session_engine.analyse_session({"user_id": u1, "city": "Pune", "amount": 100})
res_b = session_engine.analyse_session({"user_id": u2, "city": "Bangalore", "amount": 100})
res_c = session_engine.analyse_session({"user_id": u3, "city": "Chennai", "amount": 100})

for u, res in zip([u1, u2, u3], [res_a, res_b, res_c]):
    print(f"\nUser: {u}")
    print(f"Overall: {res['overall_trust']}")
    for k, v in res["checkpoints"].items():
        print(f"  {k}: {v['score']}")
