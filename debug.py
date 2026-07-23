from api.session_intelligence_engine import session_engine

print("Testing Session")
res1 = session_engine.analyse_session({
    "user_id": "usr_abc",
    "city": "Moscow",
    "timestamp": "2026-07-15 18:44:00",
    "session_age_minutes": 5,
    "token_previously_seen": True
})
print("Moscow score:", res1["checkpoints"]["checkpoint_3_session"]["score"])
print("Moscow reasons:", res1["checkpoints"]["checkpoint_3_session"]["reasons"])

res2 = session_engine.analyse_session({
    "user_id": "usr_abc",
    "city": "Mumbai",
    "timestamp": "2026-07-15 18:44:00",
    "session_age_minutes": 5,
    "token_previously_seen": True
})
print("Mumbai score:", res2["checkpoints"]["checkpoint_3_session"]["score"])
print("Mumbai reasons:", res2["checkpoints"]["checkpoint_3_session"]["reasons"])
