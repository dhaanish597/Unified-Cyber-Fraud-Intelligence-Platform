import os
import sys

def run_test():
    from api.ledger_service import ledger_service
    from api.trust_fabric_engine import trust_fabric

    # Initial block height
    initial_block = ledger_service.current_block_height
    print(f"Initial block height: {initial_block}")

    # Create evidence
    ev = trust_fabric.create_evidence_package({"amount": 1000, "user_id": "usr_test"})
    ev_id = ev["evidence_id"]
    print(f"Created evidence: {ev_id}")

    # The ledger_service should have processed it via evaluate/trust_engine, wait, 
    # trust_fabric creates evidence package, but ledger_service is called in trust_engine.py
    # Let's call ledger_service directly to simulate
    from api.trust_engine import compute_investigation_trust
    # compute_investigation_trust calls ledger_service.create_evidence_record
    rec = ledger_service.create_evidence_record(ev)
    block_height = rec["block_height"]
    print(f"Ledger record block height: {block_height}")

    with open("test_ev_id.txt", "w") as f:
        f.write(ev_id)
        f.write("\n")
        f.write(str(block_height))

if __name__ == "__main__":
    run_test()
