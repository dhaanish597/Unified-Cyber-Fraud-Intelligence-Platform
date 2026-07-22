import random
from datetime import datetime, timedelta

CYBER_EVENT_CATALOG = [
    {"type": "impossible_travel_login", "severity": "critical", "km_from_baseline": 4500, "desc": "Login from Moscow, RU (4,500 km away) 40s prior to transfer"},
    {"type": "credential_stuffing_surge", "severity": "critical", "km_from_baseline": 890, "desc": "500 failed authentication requests from botnet proxy pool"},
    {"type": "sim_swap_interception", "severity": "critical", "km_from_baseline": 12, "desc": "SIM card swap reported by telecom carrier 10 mins prior to OTP request"},
    {"type": "cookie_theft_reuse", "severity": "high", "km_from_baseline": 5, "desc": "Stolen session cookie injected on unverified Linux browser"},
    {"type": "vpn_proxy_login", "severity": "medium", "km_from_baseline": 120, "desc": "Login originated from known commercial VPN exit node"},
    {"type": "rooted_device_access", "severity": "high", "km_from_baseline": 0, "desc": "Mobile banking app launched on rooted Android device with Magisk active"},
    {"type": "malware_detected", "severity": "critical", "km_from_baseline": 0, "desc": "Overlay Trojan (Anatsa) detected recording screen overlay touch events"},
    {"type": "session_hijack", "severity": "critical", "km_from_baseline": 450, "desc": "Session token hijacked and replayed from unauthorized IP address"},
    {"type": "brute_force_attack", "severity": "high", "km_from_baseline": 10, "desc": "Multiple rapid invalid PIN attempts on mobile banking endpoint"},
    {"type": "password_reset_suspicious", "severity": "medium", "km_from_baseline": 0, "desc": "Emergency password reset requested from unverified device"},
    {"type": "mfa_disabled_attempt", "severity": "high", "km_from_baseline": 0, "desc": "Attempt to disable biometric MFA from unrecognised device"},
    {"type": "device_changed_sudden", "severity": "medium", "km_from_baseline": 0, "desc": "Primary device switched twice within 30 minutes"},
    {"type": "ip_reputation_drop", "severity": "high", "km_from_baseline": 0, "desc": "IP address flagged on global threat intelligence blacklists"}
]

def generate_cyber_event_for_user(user_id: str, timestamp: str = None) -> dict:
    """
    Generates cyber event telemetry for Part 8. Preserves demo event EVT-CYBER-8819 for usr_abc.
    """
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if user_id == "usr_abc":
        evt_type = CYBER_EVENT_CATALOG[0] # Impossible travel
        ip = "185.15.2.22"
        device_id = "dev_9999"
        session_id = "SESS_9921_CRITICAL"
    else:
        evt_type = random.choice(CYBER_EVENT_CATALOG)
        ip = f"185.15.{random.randint(1, 254)}.{random.randint(1, 254)}"
        device_id = f"dev_{random.randint(1000, 9999)}"
        session_id = f"SESS_{random.randint(1000, 9999)}"

    return {
        "msg_type": "cyber_event",
        "event_id": f"EVT-CYBER-{random.randint(10000, 99999)}",
        "event_type": evt_type["type"],
        "user_id": user_id,
        "device_id": device_id,
        "session_id": session_id,
        "ip": ip,
        "timestamp": timestamp,
        "severity": evt_type["severity"],
        "km_from_baseline": evt_type["km_from_baseline"],
        "description": evt_type["desc"]
    }

def generate_cyber_telemetry_batch(users: list, count: int = 50) -> list:
    """
    Generates batch cyber events linked to customers, devices, sessions, and timestamps.
    Part 8 of Digital Banking Universe.
    """
    events = []
    for _ in range(count):
        u = random.choice(users)
        events.append(generate_cyber_event_for_user(u["customer_id"]))
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events

