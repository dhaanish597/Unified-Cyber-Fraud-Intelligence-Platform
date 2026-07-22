import random
import hashlib

DEVICE_TYPES = [
    {"type": "MOBILE_IOS", "os": "iOS 17.5", "browsers": ["Safari Mobile", "Chrome iOS"], "trust": 0.95},
    {"type": "MOBILE_ANDROID", "os": "Android 14 (Samsung OneUI)", "browsers": ["Chrome Mobile", "Samsung Internet"], "trust": 0.92},
    {"type": "DESKTOP_MAC", "os": "macOS Sonoma 14.4", "browsers": ["Safari", "Chrome Desktop"], "trust": 0.98},
    {"type": "DESKTOP_WIN", "os": "Windows 11 Pro", "browsers": ["Edge", "Chrome", "Firefox"], "trust": 0.90},
    {"type": "TABLET_IPAD", "os": "iPadOS 17.5", "browsers": ["Safari"], "trust": 0.96},
    {"type": "ATM_TERMINAL", "os": "Windows Embedded 10", "browsers": ["N/A Native ATM App"], "trust": 0.85}
]

CARRIERS = ["Jio 5G", "Airtel 5G", "Vi 4G", "BSNL Fiber", "ACT Fibernet"]

GEO_LOCATIONS = [
    {"city": "Mumbai", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777, "asn": "AS55836 Reliance Jio", "ip_prefix": "49.207"},
    {"city": "Delhi", "state": "Delhi NCR", "lat": 28.7041, "lon": 77.1025, "asn": "AS24560 Bharti Airtel", "ip_prefix": "103.45"},
    {"city": "Bangalore", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946, "asn": "AS133982 ACT Digital", "ip_prefix": "14.142"},
    {"city": "Hyderabad", "state": "Telangana", "lat": 17.3850, "lon": 78.4867, "asn": "AS55836 Reliance Jio", "ip_prefix": "115.240"},
    {"city": "Moscow", "state": "Moscow Federal", "lat": 55.7558, "lon": 37.6173, "asn": "AS49505 OOO Baxet (Proxy/VPN)", "ip_prefix": "185.15"}
]

def generate_device_profile(user_id: str, is_compromised: bool = False) -> dict:
    if user_id == "usr_abc":
        device_id = "dev_9999"
        dev_meta = DEVICE_TYPES[0] # iPhone
        is_rooted = False
        trust_score = 0.12 if is_compromised else 0.98
    else:
        dev_meta = random.choice(DEVICE_TYPES)
        device_id = f"dev_{abs(hash(user_id + dev_meta['type'])) % 90000 + 10000}"
        is_rooted = random.random() < 0.05
        trust_score = round(random.uniform(0.70, 0.99), 2) if not is_compromised else round(random.uniform(0.05, 0.30), 2)

    imei = "".join(random.choices("0123456789", k=15))
    sim_number = f"+9198{random.randint(10000000, 99999999)}"
    fp_hash = hashlib.sha256(f"{device_id}:{imei}".encode()).hexdigest()[:32]

    return {
        "device_id": device_id,
        "type": dev_meta["type"],
        "os": dev_meta["os"],
        "browser": random.choice(dev_meta["browsers"]),
        "imei": imei,
        "device_fingerprint": f"FP_{fp_hash}",
        "is_rooted": is_rooted,
        "trust_score": trust_score,
        "sim_number": sim_number,
        "carrier": random.choice(CARRIERS),
        "is_preferred": True
    }

def generate_location_telemetry(city_name: str = "Mumbai", is_proxy: bool = False) -> dict:
    match = next((g for g in GEO_LOCATIONS if g["city"] == city_name), GEO_LOCATIONS[0])
    ip = f"{match['ip_prefix']}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    return {
        "country": "Russia" if city_name == "Moscow" else "India",
        "city": match["city"],
        "state": match["state"],
        "latitude": match["lat"],
        "longitude": match["lon"],
        "ip_address": ip,
        "asn": match["asn"],
        "is_vpn_proxy": is_proxy or (city_name == "Moscow")
    }
