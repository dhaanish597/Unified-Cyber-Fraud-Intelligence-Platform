import sys
import requests
import time
import subprocess
import datetime

proc = subprocess.Popen(["python", "-m", "uvicorn", "api.main:app", "--port", "8000"])
time.sleep(3)

try:
    print("Testing Part 1...")
    ts = "2026-07-15 18:44:00"
    
    res1 = requests.post("http://localhost:8000/session/analyse", json={
        "user_id": "usr_abc",
        "city": "Moscow",
        "timestamp": ts,
        "session_age_minutes": 5,
        "token_previously_seen": True
    }).json()
    
    res2 = requests.post("http://localhost:8000/session/analyse", json={
        "user_id": "usr_abc",
        "city": "Mumbai",
        "timestamp": ts,
        "session_age_minutes": 5,
        "token_previously_seen": True
    }).json()
    
    score1 = res1["checkpoints"]["checkpoint_3_session"]["score"]
    score2 = res2["checkpoints"]["checkpoint_3_session"]["score"]
    
    if score1 == score2:
        print(f"FAIL: Same score {score1} for Moscow and Mumbai")
        sys.exit(1)
    else:
        print(f"PASS: Moscow={score1}, Mumbai={score2}")
        
    print("Generating universe...")
    requests.post("http://localhost:8000/synthetic/universe/generate", json={"num_customers": 50, "num_txns": 100}).json()
    
    print("Testing Part 2...")
    res_a = requests.post("http://localhost:8000/session/analyse", json={"user_id": "usr_retail_101", "city": "Pune", "amount": 100}).json()
    res_b = requests.post("http://localhost:8000/session/analyse", json={"user_id": "usr_victim_09", "city": "Bangalore", "amount": 100}).json()
    res_c = requests.post("http://localhost:8000/session/analyse", json={"user_id": "usr_abc", "city": "Chennai", "amount": 100}).json()
    
    trust_a = res_a["overall_trust"]
    trust_b = res_b["overall_trust"]
    trust_c = res_c["overall_trust"]
    
    if len(set([trust_a, trust_b, trust_c])) < 3:
        print(f"FAIL: Not all different: {trust_a}, {trust_b}, {trust_c}")
        sys.exit(1)
    else:
        print(f"PASS: {trust_a}, {trust_b}, {trust_c}")
        
finally:
    proc.terminate()
