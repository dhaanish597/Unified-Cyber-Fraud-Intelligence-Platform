import sys
from fastapi import HTTPException
from api.scenario_engine import generate_scenario
from api.response_orchestrator_engine import soar_engine
from api.trust_fabric_engine import trust_fabric

try:
    generate_scenario("nonexistent")
    print("FAIL: generate_scenario didn't raise 404")
    sys.exit(1)
except HTTPException as e:
    if e.status_code == 404:
        print("PASS: generate_scenario 404")
    else:
        print(f"FAIL: generate_scenario wrong status {e.status_code}")
        sys.exit(1)

try:
    soar_engine.get_incident("nonexistent")
    print("FAIL: get_incident didn't raise 404")
    sys.exit(1)
except HTTPException as e:
    if e.status_code == 404:
        print("PASS: get_incident 404")
    else:
        print(f"FAIL: get_incident wrong status {e.status_code}")
        sys.exit(1)

ev = trust_fabric.create_evidence_package({})
timeline = ev["audit_timeline"]
first_step = timeline[0]
import datetime
today = datetime.datetime.now().strftime("%Y-%m-%d")
if today in first_step["timestamp"]:
    print(f"PASS: timeline has today's date ({first_step['timestamp']})")
else:
    print(f"FAIL: timeline date is wrong: {first_step['timestamp']} vs {today}")
    sys.exit(1)

from api.synthetic_universe.graph_generator import generate_graph_topology
graph = generate_graph_topology({"customers": [], "transactions": [], "devices": [], "locations": []})
# The logic doesn't crash, that's good. 

import api.main
print("PASS: app started cleanly without import errors")
