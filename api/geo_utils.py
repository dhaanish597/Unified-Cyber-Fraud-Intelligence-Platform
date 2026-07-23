import math
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Simple mock for IP/City to Geo
GEO_MOCK = {
    "185.15.2.22": {"city": "Moscow", "lat": 55.7558, "lon": 37.6173},
    "49.207.18.9": {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "103.22.45.10": {"city": "Pune", "lat": 18.5204, "lon": 73.8567},
    "14.142.36.2": {"city": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    "117.201.8.44": {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "194.26.29.110": {"city": "St Petersburg", "lat": 59.9311, "lon": 30.3609},
    "Mumbai": {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "Moscow": {"city": "Moscow", "lat": 55.7558, "lon": 37.6173},
    "Chennai": {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
}

_geoip_reader = None
_geoip_warned = False

def get_geoip_reader():
    global _geoip_reader, _geoip_warned
    if _geoip_reader is None and not _geoip_warned:
        try:
            import geoip2.database
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "GeoLite2-City.mmdb")
            if os.path.exists(db_path):
                _geoip_reader = geoip2.database.Reader(db_path)
            else:
                logger.warning(f"GeoLite2 database not found at {db_path}. Falling back to mock data.")
                _geoip_warned = True
        except ImportError:
            logger.warning("geoip2 library not installed. Falling back to mock data.")
            _geoip_warned = True
        except Exception as e:
            logger.warning(f"Failed to load GeoLite2 database: {e}. Falling back to mock data.")
            _geoip_warned = True
    return _geoip_reader

def lookup_ip(ip: str) -> dict:
    reader = get_geoip_reader()
    if reader:
        try:
            response = reader.city(ip)
            return {
                "lat": response.location.latitude or 19.0,
                "lon": response.location.longitude or 72.0,
                "city": response.city.name or "Unknown",
                "country": response.country.iso_code or "Unknown",
                "asn": None
            }
        except Exception:
            pass
    return GEO_MOCK.get(ip, {"city": "Unknown", "lat": 19.0, "lon": 72.0})

def get_coordinates(location_str: str) -> dict:
    if location_str and ("." in location_str or ":" in location_str):
        return lookup_ip(location_str)
    return GEO_MOCK.get(location_str, {"city": "Unknown", "lat": 19.0, "lon": 72.0})

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def _parse_time(ts):
    if isinstance(ts, datetime):
        return ts
    if isinstance(ts, str):
        ts = ts.replace(" IST", "").strip()
        return datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    return datetime.now()

def implied_velocity_kmh(prev_geo: dict, prev_ts, curr_geo: dict, curr_ts) -> float:
    dist = haversine_km(prev_geo.get("lat", 0), prev_geo.get("lon", 0), curr_geo.get("lat", 0), curr_geo.get("lon", 0))
    t1 = _parse_time(prev_ts)
    t2 = _parse_time(curr_ts)
    hours = abs((t2 - t1).total_seconds()) / 3600.0
    if hours == 0:
        return 0.0 if dist == 0 else float('inf')
    return dist / hours
