import os
import sys

def run_test():
    with open("test_ev_id.txt", "r") as f:
        ev_id = f.readline().strip()
        expected_height = int(f.readline().strip())

    from api.ledger_service import ledger_service
    from api.trust_fabric_engine import trust_fabric

    rec = ledger_service.verify_evidence(ev_id)
    if not rec or not rec.get("verified"):
        print("Verification failed or record not found!")
        sys.exit(1)
    
    actual_height = rec["block_height"]
    print(f"Reloaded block height: {actual_height}")
    
    if actual_height == expected_height:
        print("Success! Heights match.")
    else:
        print("Failed! Heights mismatch.")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
