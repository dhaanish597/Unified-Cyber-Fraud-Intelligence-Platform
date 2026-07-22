import random
import hashlib
import math

DEVICE_TYPES = [
    {"type": "MOBILE_IOS", "os": "iOS 17.5.1", "browsers": ["Safari Mobile", "Chrome iOS"], "trust": 0.96},
    {"type": "MOBILE_ANDROID", "os": "Android 14 (Samsung OneUI 6.1)", "browsers": ["Chrome Mobile", "Samsung Internet"], "trust": 0.92},
    {"type": "DESKTOP_MAC", "os": "macOS Sonoma 14.5", "browsers": ["Safari", "Chrome Desktop"], "trust": 0.98},
    {"type": "DESKTOP_WIN", "os": "Windows 11 Pro Enterprise", "browsers": ["Edge", "Chrome", "Firefox"], "trust": 0.91},
    {"type": "TABLET_IPAD", "os": "iPadOS 17.5", "browsers": ["Safari"], "trust": 0.96},
    {"type": "ATM_TERMINAL", "os": "Windows Embedded 10 IoT", "browsers": ["Native ATM Shell"], "trust": 0.88}
]

CARRIERS = ["Jio 5G", "Airtel 5G", "Vi 4G", "BSNL Fiber", "ACT Fibernet", "Tata Tele Services"]

GEO_LOCATIONS = [
    {"city": "Mumbai", "state": "Maharashtra", "country": "India", "lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata", "asn": "AS55836 Reliance Jio", "ip_prefix": "49.207"},
    {"city": "Delhi", "state": "Delhi NCR", "country": "India", "lat": 28.7041, "lon": 77.1025, "tz": "Asia/Kolkata", "asn": "AS24560 Bharti Airtel", "ip_prefix": "103.45"},
    {"city": "Bangalore", "state": "Karnataka", "country": "India", "lat": 12.9716, "lon": 77.5946, "tz": "Asia/Kolkata", "asn": "AS133982 ACT Digital", "ip_prefix": "14.142"},
    {"city": "Hyderabad", "state": "Telangana", "country": "India", "lat": 17.3850, "lon": 78.4867, "tz": "Asia/Kolkata", "asn": "AS55836 Reliance Jio", "ip_prefix": "115.240"},
    {"city": "Ahmedabad", "state": "Gujarat", "country": "India", "lat": 23.0225, "lon": 72.5714, "tz": "Asia/Kolkata", "asn": "AS45820 GTPL Broadband", "ip_prefix": "117.201"},
    {"city": "Moscow", "state": "Moscow Federal", "country": "Russia", "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow", "asn": "AS49505 OOO Baxet (Proxy/VPN)", "ip_prefix": "185.15"},
    {"city": "London", "state": "Greater London", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London", "asn": "AS5607 British Sky Broadcasting", "ip_prefix": "82.132"}
]

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance in kilometers between two geo coordinates using Haversine formula."""
    R = 6371.0 # Radius of earth in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def generate_device_profile(user_id: str, is_compromised: bool = False) -> dict:
    """
    Generates device profile for Part 4. Preserves usr_abc demo device dev_9999.
    """
    if user_id == "usr_abc":
        device_id = "dev_9999"
        dev_meta = DEVICE_TYPES[0] # iPhone
        is_rooted = False
        trust_score = 0.12 if is_compromised else 0.98
    else:
        dev_meta = random.choice(DEVICE_TYPES)
        device_id = f"dev_{abs(hash(user_id + dev_meta['type'])) % 90000 + 10000}"
        is_rooted = random.random() < 0.04
        trust_score = round(random.uniform(0.72, 0.99), 2) if not is_compromised else round(random.uniform(0.05, 0.30), 2)

    imei = "".join(random.choices("0123456789", k=15))
    sim_number = f"+9198{random.randint(10000000, 99999999)}"
    fp_hash = hashlib.sha256(f"{device_id}:{imei}:{dev_meta['os']}".encode()).hexdigest()[:32]

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
        "is_preferred": True,
        "registered_date": "2023-01-10"
    }

def generate_location_telemetry(city_name: str = "Mumbai", is_proxy: bool = False, baseline_city: str = "Mumbai") -> dict:
    """
    Generates location telemetry and travel history for Part 5.
    """
    match = next((g for g in GEO_LOCATIONS if g["city"] == city_name), GEO_LOCATIONS[0])
    base = next((g for g in GEO_LOCATIONS if g["city"] == baseline_city), GEO_LOCATIONS[0])
    
    dist_from_base = calculate_haversine_distance(base["lat"], base["lon"], match["lat"], match["lon"])
    ip = f"{match['ip_prefix']}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    return {
        "country": match["country"],
        "city": match["city"],
        "state": match["state"],
        "latitude": match["lat"],
        "longitude": match["lon"],
        "timezone": match["tz"],
        "ip_address": ip,
        "asn": match["asn"],
        "is_vpn_proxy": is_proxy or (city_name in ["Moscow", "London"]),
        "distance_from_home_km": dist_from_base,
        "travel_flag": "IMPOSSIBLE_TRAVEL" if dist_from_base > 1000 and is_proxy else ("TRAVELING" if dist_from_base > 100 else "HOME_ZONE")
    }

