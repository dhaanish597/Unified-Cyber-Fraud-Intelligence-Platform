from __future__ import annotations

import statistics
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.session_intelligence.broker import TrustUpdateBroker
from api.session_intelligence.engine import SessionIntelligenceEngine
from api.session_intelligence.models import ComponentName, SessionLifecycle
from api.session_intelligence.repository import SessionTrustRepository


@pytest.fixture()
def trust_engine(tmp_path: Path) -> SessionIntelligenceEngine:
    return SessionIntelligenceEngine(
        SessionTrustRepository(tmp_path / "phase3-test.db")
    )


def _start(
    engine: SessionIntelligenceEngine,
    session_id: str = "SESS_PHASE3_TEST",
) -> None:
    engine.start_session(
        {
            "session_id": session_id,
            "user_id": "user_phase3",
            "device_id": "device_phase3",
        },
        {
            "event_type": "DEVICE_ATTESTATION",
            "device_id": "device_phase3",
            "root_detected": False,
            "emulator_detected": False,
        },
    )


def _vpn_threat() -> dict:
    return {
        "threat_name": "Anonymizing Network / VPN Tunnel Active",
        "severity": "HIGH",
        "confidence": 96.0,
        "detection_source": "CyberThreatEngine",
        "trust_impact": {
            "network_trust": -25.0,
            "session_trust": -10.0,
        },
    }


def test_every_component_is_independent_and_bounded(
    trust_engine: SessionIntelligenceEngine,
) -> None:
    _start(trust_engine)
    baseline = trust_engine.repository.get_passport("SESS_PHASE3_TEST")
    assert baseline is not None
    assert set(baseline.components) == set(ComponentName)
    assert all(0 <= component.value <= 100 for component in baseline.components.values())

    update = trust_engine.process_event(
        {
            "session_id": "SESS_PHASE3_TEST",
            "event_type": "VPN_ENABLED",
            "vpn_detected": True,
        },
        [_vpn_threat()],
    )

    assert update.passport.network_trust == 75.0
    assert update.passport.threat_trust == 82.0
    assert update.passport.device_trust == baseline.device_trust
    assert update.passport.runtime_trust == baseline.runtime_trust
    assert {delta.component for delta in update.deltas} == {
        "network",
        "threat",
        "overall",
    }


def test_recovery_increases_trust_and_is_persisted(
    trust_engine: SessionIntelligenceEngine,
) -> None:
    _start(trust_engine)
    degraded = trust_engine.process_event(
        {
            "session_id": "SESS_PHASE3_TEST",
            "event_type": "VPN_ENABLED",
            "vpn_detected": True,
        },
        [_vpn_threat()],
    )
    recovered = trust_engine.process_event(
        {
            "session_id": "SESS_PHASE3_TEST",
            "event_type": "VPN_DISABLED",
            "vpn_detected": False,
        }
    )

    assert recovered.passport.overall_trust > degraded.passport.overall_trust
    assert recovered.passport.network_trust == 100.0
    assert recovered.passport.threat_trust == 100.0
    assert all(delta.is_recovery for delta in recovered.deltas)
    assert {
        delta.component
        for delta in trust_engine.repository.get_recovery_events("SESS_PHASE3_TEST")
    } == {"network", "threat", "overall"}


def test_timeline_history_and_restart_persistence(
    trust_engine: SessionIntelligenceEngine,
) -> None:
    _start(trust_engine)
    trust_engine.process_event(
        {
            "session_id": "SESS_PHASE3_TEST",
            "event_type": "BENEFICIARY_ADDED",
        }
    )
    trust_engine.process_event(
        {
            "session_id": "SESS_PHASE3_TEST",
            "event_type": "TRANSFER_INITIATED",
            "amount": 125_000,
        }
    )

    snapshots = trust_engine.get_history("SESS_PHASE3_TEST", "last_hour")
    assert [snapshot.event_type for snapshot in snapshots] == [
        "SESSION_CREATED",
        "BENEFICIARY_ADDED",
        "TRANSFER_INITIATED",
    ]
    assert snapshots[-1].current_trust < snapshots[0].current_trust

    restarted = SessionIntelligenceEngine(
        SessionTrustRepository(trust_engine.repository.db_path)
    )
    passport = restarted.repository.get_passport("SESS_PHASE3_TEST")
    context = restarted.repository.get_context("SESS_PHASE3_TEST")
    assert passport is not None
    assert context is not None
    assert passport.overall_trust == snapshots[-1].current_trust
    assert context.event_count == 3


def test_session_lifecycle_transitions(
    trust_engine: SessionIntelligenceEngine,
) -> None:
    _start(trust_engine)
    idle = trust_engine.process_event(
        {"session_id": "SESS_PHASE3_TEST", "event_type": "SESSION_IDLE"}
    )
    assert idle.passport.current_status == SessionLifecycle.IDLE

    challenged = trust_engine.process_event(
        {"session_id": "SESS_PHASE3_TEST", "event_type": "BIOMETRIC_CHALLENGE"}
    )
    assert challenged.passport.current_status == SessionLifecycle.CHALLENGED

    closed = trust_engine.process_event(
        {"session_id": "SESS_PHASE3_TEST", "event_type": "SESSION_ENDED"}
    )
    assert closed.passport.current_status == SessionLifecycle.CLOSED
    assert trust_engine.repository.list_sessions(include_closed=False) == []


def test_recalculation_latency_is_below_fifty_ms(
    trust_engine: SessionIntelligenceEngine,
) -> None:
    _start(trust_engine)
    samples = [
        trust_engine.recalculate("SESS_PHASE3_TEST").processing_time_ms
        for _ in range(30)
    ]
    assert statistics.quantiles(samples, n=100)[94] < 50.0


def test_rest_api_and_websocket_bootstrap(
    trust_engine: SessionIntelligenceEngine,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from api import main

    _start(trust_engine, "SESS_API_TEST")
    monkeypatch.setattr(main, "session_intelligence", trust_engine)
    monkeypatch.setattr(main, "trust_update_broker", TrustUpdateBroker())

    with TestClient(main.app) as client:
        sessions = client.get("/sessions")
        assert sessions.status_code == 200
        assert sessions.json()["sessions"][0]["session_id"] == "SESS_API_TEST"

        passport = client.get("/trust-passport/SESS_API_TEST")
        assert passport.status_code == 200
        assert passport.json()["overall_trust"] == 100.0
        assert passport.json()["composite_trust"] == 100.0

        components = client.get("/trust-components/SESS_API_TEST")
        assert components.status_code == 200
        assert len(components.json()["components"]) == 9

        history = client.get("/trust-history/SESS_API_TEST?range=last_hour")
        assert history.status_code == 200
        assert history.json()["count"] == 1

        recalculated = client.post(
            "/trust/recalculate", json={"session_id": "SESS_API_TEST"}
        )
        assert recalculated.status_code == 200
        assert recalculated.json()["msg_type"] == "trust_passport_update"

        with client.websocket_connect(
            "/ws/stream?session_id=SESS_API_TEST"
        ) as websocket:
            bootstrap = websocket.receive_json()
            assert bootstrap["msg_type"] == "trust_passport_update"
            assert bootstrap["event_type"] == "TRUST_BOOTSTRAP"
            assert bootstrap["passport"]["session_id"] == "SESS_API_TEST"


def test_registry_supports_one_thousand_sessions(
    tmp_path: Path,
) -> None:
    engine = SessionIntelligenceEngine(
        SessionTrustRepository(tmp_path / "phase3-load.db")
    )
    for index in range(1_000):
        session_id = f"SESS_LOAD_{index:04d}"
        engine.start_session(
            {
                "session_id": session_id,
                "user_id": f"user_{index:04d}",
                "device_id": f"device_{index % 25:02d}",
            }
        )

    sessions = engine.repository.list_sessions(limit=1_000)
    assert len(sessions) == 1_000
    assert all(session.current_state == SessionLifecycle.ACTIVE for session in sessions)
