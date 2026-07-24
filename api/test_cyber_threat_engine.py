import pytest
from api.cyber_threat_engine import CyberThreatEngine

def test_device_threat_detection():
    engine = CyberThreatEngine()
    event = {
        "event_type": "ROOT_DETECTED",
        "root_detected": True,
        "session_id": "TEST_SESS_001",
        "device_id": "TEST_DEV_001"
    }
    threats = engine.evaluate_event(event)
    assert len(threats) >= 1
    root_threat = next((t for t in threats if t["threat_category"] == "Device Threats"), None)
    assert root_threat is not None
    assert root_threat["severity"] == "CRITICAL"
    assert root_threat["confidence"] is None
    assert {"field": "root_detected", "observed_value": True} in root_threat["evidence"]
    assert root_threat["confidence_basis"]["method"] == "NOT_CALIBRATED"

def test_frida_runtime_threat():
    engine = CyberThreatEngine()
    event = {
        "event_type": "FRIDA_DETECTED",
        "frida_detected": True,
        "session_id": "TEST_SESS_002",
        "device_id": "TEST_DEV_002"
    }
    threats = engine.evaluate_event(event)
    frida_threat = next((t for t in threats if t["threat_category"] == "Runtime Threats"), None)
    assert frida_threat is not None
    assert frida_threat["recommended_action"] == "TERMINATE_SESSION"

def test_campaign_correlation():
    engine = CyberThreatEngine()
    event1 = {"event_type": "IMPOSSIBLE_TRAVEL", "session_id": "TEST_SESS_ATO", "device_id": "TEST_DEV_ATO"}
    event2 = {"event_type": "VPN_ENABLED", "vpn_detected": True, "session_id": "TEST_SESS_ATO", "device_id": "TEST_DEV_ATO"}
    
    engine.evaluate_event(event1)
    threats = engine.evaluate_event(event2)
    
    campaign = next((t for t in threats if t["threat_category"] == "Campaign Correlation"), None)
    assert campaign is not None
    assert "ACCOUNT TAKEOVER" in campaign["threat_name"]
    assert campaign["confidence"] is None
    assert campaign["confidence_basis"]["method"] == "NOT_CALIBRATED"

if __name__ == "__main__":
    test_device_threat_detection()
    test_frida_runtime_threat()
    test_campaign_correlation()
    print("All CyberThreatEngine unit tests passed!")
