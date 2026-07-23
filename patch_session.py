import re

def process_file():
    with open('api/session_intelligence_engine.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_func = """    def _eval_session_checkpoint(self, user_id: str, data: dict) -> dict:
        from api.digital_twin_engine import get_or_create_digital_twin
        from api.geo_utils import implied_velocity_kmh, get_coordinates, haversine_km, _parse_time
        import datetime
        
        ip = data.get("ip", "185.15.2.22")
        city = data.get("city")
        curr_geo = get_coordinates(city if city else ip)
        
        twin = get_or_create_digital_twin(user_id)
        home_geo = get_coordinates(twin.locations.get("home_location", {}).get("city", "Mumbai"))
        
        # Determine the most recent known location/time
        history = twin.locations.get("travel_history", [])
        if history:
            # sort chronologically by timestamp
            history_sorted = sorted(history, key=lambda x: _parse_time(x.get("timestamp", "2000-01-01 00:00:00")))
            last_travel = history_sorted[-1]
            prev_ts = last_travel.get("timestamp")
            prev_geo = get_coordinates(last_travel.get("city", "Mumbai"))
        else:
            prev_ts = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            prev_geo = home_geo
            
        curr_ts = data.get("timestamp", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        velocity = implied_velocity_kmh(prev_geo, prev_ts, curr_geo, curr_ts)
        
        score = 100.0
        reasons = []
        
        dist = haversine_km(prev_geo.get("lat", 0), prev_geo.get("lon", 0), curr_geo.get("lat", 0), curr_geo.get("lon", 0))
        t1 = _parse_time(prev_ts)
        t2 = _parse_time(curr_ts)
        mins = max(1, abs((t2 - t1).total_seconds()) / 60.0)
        
        if velocity > 900:
            score -= 85.0
            reasons.append(f"Impossible Travel Event ({prev_geo.get('city', 'Unknown')} to {curr_geo.get('city', 'Unknown')} in {int(mins)} min = {velocity:,.0f} km/h implied velocity)")
        else:
            reasons.append(f"Normal Travel Velocity ({velocity:,.0f} km/h)")
            
        session_age = data.get("session_age_minutes", 10)
        if session_age < 1:
            score -= 10.0
            reasons.append(f"Session just started ({session_age} min)")
        else:
            reasons.append(f"Session age mature ({session_age} min)")
            
        token_seen = data.get("token_previously_seen", True)
        if not token_seen:
            score -= 20.0
            reasons.append("New Session Token")
        else:
            reasons.append("Token previously seen")
            
        scenario = data.get("scenario_id", "")
        if scenario in MITRE_ATTACK_MAPPINGS and MITRE_ATTACK_MAPPINGS[scenario]["id"] != "None":
            reasons = [r + f" [{MITRE_ATTACK_MAPPINGS[scenario]['id']}]" for r in reasons]
            
        score = max(0.0, score)
        return {
            "score": score,
            "reasons": reasons
        }"""

    # Replace the old _eval_session_checkpoint
    content = re.sub(r'    def _eval_session_checkpoint\(self, user_id: str, data: dict\) -> dict:.*?    def _eval_behavior_checkpoint', new_func + '\n\n    def _eval_behavior_checkpoint', content, flags=re.DOTALL)

    with open('api/session_intelligence_engine.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched session_intelligence_engine.py (session checkpoint)")

if __name__ == "__main__":
    process_file()
