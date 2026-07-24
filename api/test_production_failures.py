from __future__ import annotations

from fastapi import HTTPException

from api.platform.config import PlatformSettings
from api.platform.graph_runtime import GraphRuntime
from api.platform.security import create_access_token, validate_access_token


class OfflineGraphRepository:
    backend_name = "NEO4J"

    def verify_connectivity(self):
        raise ConnectionError("offline")

    def observe(self, event):
        raise ConnectionError("offline")

    def analyze(self, event):
        raise AssertionError("analyze must not run after failed observation")

    def topology(self, limit):
        raise ConnectionError("offline")


def test_expired_access_token_is_rejected():
    settings = PlatformSettings(
        jwt_ttl_seconds=-1,
        jwt_secret="test-secret-that-is-longer-than-thirty-two-bytes",
    )
    token, _ = create_access_token(
        "expired-test",
        {"roles": ["sdk"]},
        settings,
    )
    try:
        validate_access_token(token, settings)
    except HTTPException as exception:
        assert exception.status_code == 401
        assert "expired" in str(exception.detail).lower()
    else:
        raise AssertionError("Expired token unexpectedly validated")


def test_neo4j_runtime_failure_is_explicit_and_does_not_crash():
    runtime = GraphRuntime.__new__(GraphRuntime)
    runtime.repository = OfflineGraphRepository()
    runtime.error_code = None
    runtime.settings = PlatformSettings()
    result = runtime.process(
        {
            "session_id": "failure-session",
            "event_type": "TRANSFER_INITIATED",
            "user_id": "failure-user",
        }
    )
    assert result.status == "FAILED"
    assert result.backend == "NEO4J"
    assert result.error_code == "GRAPH_QUERY_FAILED"
    topology = runtime.topology()
    assert topology["status"] == "FAILED"
    assert topology["error_code"] == "GRAPH_TOPOLOGY_QUERY_FAILED"
