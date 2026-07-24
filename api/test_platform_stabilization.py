import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from api.main import app
from api.platform.graph_runtime import GraphRuntime, NetworkXGraphRepository
from api.platform.model_runtime import ModelRuntime


client = TestClient(app)


def token(client_id: str, secret: str) -> str:
    response = client.post(
        "/auth/token",
        json={"client_id": client_id, "client_secret": secret},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_every_non_public_endpoint_requires_authentication():
    response = client.get("/platform/status")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHORIZATION_FAILED"


def test_roles_are_enforced():
    sdk_token = token("fusion-android-dev", "fusion-android-local-only")
    response = client.get(
        "/platform/status",
        headers={"Authorization": f"Bearer {sdk_token}"},
    )
    assert response.status_code == 403


def test_authoritative_sdk_pipeline_reports_explicit_model_and_graph_state():
    sdk_token = token("fusion-android-dev", "fusion-android-local-only")
    headers = {"Authorization": f"Bearer {sdk_token}"}
    device_id = "device-platform-test"
    device = client.post(
        "/sdk/device",
        headers=headers,
        json={
            "device_id": device_id,
            "model": "test-device",
            "manufacturer": "test",
            "android_version": "14",
            "security_patch": "2026-07-01",
            "screen_lock_enabled": True,
            "root_detected": False,
            "emulator_detected": False,
            "frida_detected": False,
            "debugger_attached": False,
            "overlay_detected": False,
            "timezone": "UTC",
            "locale": "en",
        },
    )
    assert device.status_code == 200
    assert device.json()["device_trust_score"] is None

    session = client.post(
        "/sdk/session/start",
        headers=headers,
        json={
            "app_id": "com.fusionbank.mobileapp",
            "tenant_id": "TENANT_FUSB_001",
            "sdk_version": "FAT-SDK v2.4.1",
            "user_id": "platform-test-user",
            "device_id": device_id,
            "environment": "TEST",
        },
    )
    assert session.status_code == 200
    session_id = session.json()["session_id"]
    assert session.json()["composite_trust_score"] is None

    decision = client.post(
        "/sdk/request-decision",
        headers=headers,
        json={
            "session_id": session_id,
            "event_type": "TRANSFER_INITIATED",
            "amount": 75_000,
        },
    )
    assert decision.status_code == 200
    body = decision.json()
    assert body["model_used"] is None
    assert body["fallback_used"] == "POLICY_FALLBACK"
    assert body["confidence"] is None
    assert body["decision"] in {"REQUIRE_BIOMETRIC", "REQUIRE_FACE_AUTHENTICATION"}


def test_model_runtime_never_pretends_missing_artifacts_executed(tmp_path):
    result = ModelRuntime(tmp_path).infer({"amount": 1})
    assert result.status == "FALLBACK"
    assert result.fraud_probability is None
    assert result.anomaly_score is None
    assert result.error_code == "MODEL_METADATA_MISSING"


def test_networkx_graph_detects_shared_device_from_observed_evidence():
    runtime = GraphRuntime.__new__(GraphRuntime)
    runtime.repository = NetworkXGraphRepository()
    runtime.error_code = "TEST_NETWORKX"
    for user in ("user-a", "user-b"):
        runtime.repository.observe(
            {
                "event_id": user,
                "event_type": "DEVICE_ATTESTATION",
                "session_id": f"session-{user}",
                "user_id": user,
                "device_id": "shared-device",
            }
        )
    findings = runtime.repository.analyze(
        {"user_id": "user-b", "device_id": "shared-device"}
    )
    assert any(finding.finding_type == "SHARED_DEVICE" for finding in findings)


def test_gateway_rejects_invalid_signature_before_processing(monkeypatch):
    monkeypatch.setenv("GATEWAY_WEBHOOK_SECRET", "gateway-test-secret")
    payload = {"event_type": "TRANSFER", "txn_id": "invalid-signature"}
    response = client.post(
        "/gateway/webhook",
        content=json.dumps(payload),
        headers={"X-Razorpay-Signature": "invalid"},
    )
    assert response.status_code == 401

    body = json.dumps(payload).encode()
    signature = hmac.new(
        b"gateway-test-secret", body, hashlib.sha256
    ).hexdigest()
    valid = client.post(
        "/gateway/webhook",
        content=body,
        headers={"X-Razorpay-Signature": signature},
    )
    assert valid.status_code == 200
