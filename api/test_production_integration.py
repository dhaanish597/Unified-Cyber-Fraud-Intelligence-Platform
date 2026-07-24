from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from api.main import app
from api.sdk_engine import sdk_engine


client = TestClient(app)


def banking_login(device_id: str = "integration-device") -> dict:
    response = client.post(
        "/banking/auth/login",
        json={
            "username": "demo_user",
            "password": "FusionDemo!2026",
            "device_id": device_id,
        },
    )
    assert response.status_code == 200
    return response.json()


def auth_header(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_pairing_registers_device_and_issues_sdk_credentials():
    pairing = client.post("/device/pair", json={"backend_url": "http://demo.local:18001"})
    assert pairing.status_code == 200
    payload = pairing.json()["pairing"]
    assert payload["pairId"].startswith("PAIR_")
    registration = client.post(
        "/device/register",
        json={
            "pair_id": payload["pairId"],
            "bootstrap_token": payload["bootstrapToken"],
            "device_uuid": "paired-test-device",
            "android_version": "14",
            "manufacturer": "Fusion",
            "model": "Demo Phone",
            "sdk_version": "FAT-SDK v2.4.1",
            "app_version": "1.0.0",
            "fingerprint": "demo-fingerprint",
        },
    )
    assert registration.status_code == 200
    assert registration.json()["device_id"] == "paired-test-device"
    assert registration.json()["access_token"]
    assert client.post(
        "/device/register",
        json={
            "pair_id": payload["pairId"],
            "bootstrap_token": payload["bootstrapToken"],
            "device_uuid": "replay-device",
        },
    ).status_code == 401


def test_customer_registration_and_new_device_notification():
    username = "vision_user_" + uuid.uuid4().hex[:8]
    registered = client.post("/banking/auth/register", json={"username": username, "password": "VisionDemo!2026", "email": f"{username}@example.test", "display_name": "Vision User"})
    assert registered.status_code == 201
    first = client.post("/banking/auth/login", json={"username": username, "password": "VisionDemo!2026", "device_id": "vision-phone-a"})
    second = client.post("/banking/auth/login", json={"username": username, "password": "VisionDemo!2026", "device_id": "vision-phone-b"})
    assert first.status_code == 200 and second.status_code == 200
    assert second.json()["profile"]["new_device"] is True
    notifications = client.get("/banking/notifications", headers=auth_header(second.json()["access_token"]))
    assert notifications.status_code == 200
    assert any(item["kind"] == "NEW_DEVICE_LOGIN" for item in notifications.json()["notifications"])


def register_and_start(auth: dict, device_id: str = "integration-device") -> dict:
    headers = auth_header(auth["access_token"])
    device = client.post(
        "/sdk/device",
        headers=headers,
        json={
            "device_id": device_id,
            "model": "integration-test",
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
    session = client.post(
        "/sdk/session/start",
        headers=headers,
        json={
            "app_id": "com.fusionbank.mobileapp",
            "tenant_id": "TENANT_FUSB_001",
            "sdk_version": "FAT-SDK v2.4.1",
            "user_id": auth["profile"]["user_id"],
            "device_id": device_id,
            "environment": "TEST",
        },
    )
    assert session.status_code == 200
    return session.json()


def test_banking_auth_refresh_rotation_profile_and_logout():
    assert client.post(
        "/banking/auth/login",
        json={
            "username": "demo_user",
            "password": "wrong-password",
            "device_id": "auth-device",
        },
    ).status_code == 401

    auth = banking_login("auth-device")
    profile = client.get(
        "/banking/profile", headers=auth_header(auth["access_token"])
    )
    assert profile.status_code == 200
    assert profile.json()["user_id"] == auth["profile"]["user_id"]

    refreshed = client.post(
        "/banking/auth/refresh",
        json={
            "refresh_token": auth["refresh_token"],
            "device_id": "auth-device",
        },
    )
    assert refreshed.status_code == 200
    rotated = refreshed.json()
    assert rotated["refresh_token"] != auth["refresh_token"]

    replay = client.post(
        "/banking/auth/refresh",
        json={
            "refresh_token": auth["refresh_token"],
            "device_id": "auth-device",
        },
    )
    assert replay.status_code == 401

    logout = client.post(
        "/banking/auth/logout",
        headers=auth_header(rotated["access_token"]),
        json={"refresh_token": rotated["refresh_token"]},
    )
    assert logout.status_code == 204
    assert client.post(
        "/banking/auth/refresh",
        json={
            "refresh_token": rotated["refresh_token"],
            "device_id": "auth-device",
        },
    ).status_code == 401


def test_end_to_end_decision_has_identity_ack_and_live_websocket_delivery():
    auth = banking_login()
    session = register_and_start(auth)
    headers = auth_header(auth["access_token"])
    request_id = "REQ_INTEGRATION_E2E"
    correlation_id = "COR_INTEGRATION_E2E"

    response = client.post(
        "/sdk/request-decision",
        headers={**headers, "X-Request-ID": request_id},
        json={
            "session_id": session["session_id"],
            "event_type": "TRANSFER_INITIATED",
            "amount": 75_000,
            "beneficiary_id": "beneficiary-integration",
            "request_id": request_id,
            "correlation_id": correlation_id,
        },
    )
    assert response.status_code == 200
    decision = response.json()
    assert decision["backend_ack"] is True
    assert decision["request_id"] == request_id
    assert decision["correlation_id"] == correlation_id
    assert decision["pipeline_id"].startswith("PIPE_")
    assert decision["model_status"] in {"EXECUTED", "ModelUnavailable"}
    if decision["model_status"] == "ModelUnavailable":
        assert decision["confidence"] is None
        assert decision["model_error_code"]

    with client.websocket_connect(
        f"/ws/stream?session_id={session['session_id']}"
        f"&access_token={auth['access_token']}"
    ) as websocket:
        connection = websocket.receive_json()
        assert connection["msg_type"] == "connection_ack"
        live = websocket.receive_json()
        while live.get("request_id") != request_id:
            live = websocket.receive_json()
        assert live["msg_type"] == "pipeline_decision"
        assert live["request_id"] == request_id
        assert live["correlation_id"] == correlation_id
        assert live["session_id"] == session["session_id"]
        assert live["event_ack"]["backend_ack"] is True
        assert live["decision"]["decision_id"] == decision["decision_id"]


def test_websocket_rejects_missing_token():
    from starlette.websockets import WebSocketDisconnect

    try:
        with client.websocket_connect("/ws/stream") as websocket:
            websocket.receive_json()
    except WebSocketDisconnect as exception:
        assert exception.code == 4401
    else:
        raise AssertionError("Unauthenticated WebSocket unexpectedly connected")


def test_sdk_retry_is_idempotent_and_does_not_execute_pipeline_twice():
    auth = banking_login("retry-device")
    session = register_and_start(auth, "retry-device")
    headers = auth_header(auth["access_token"])
    payload = {
        "session_id": session["session_id"],
        "event_type": "TRANSFER_INITIATED",
        "amount": 2_500,
        "beneficiary_id": "retry-beneficiary",
        "request_id": "REQ_RETRY_IDEMPOTENCY",
        "correlation_id": "COR_RETRY_IDEMPOTENCY",
    }
    before = len(sdk_engine.event_log)
    first = client.post("/sdk/request-decision", headers=headers, json=payload)
    second = client.post("/sdk/request-decision", headers=headers, json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["pipeline_id"] == second.json()["pipeline_id"]
    assert first.json()["decision_id"] == second.json()["decision_id"]
    assert len(sdk_engine.event_log) == before + 1
