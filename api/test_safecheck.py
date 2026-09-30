from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from api import store
from api.core_platform.config import platform_settings
from api.main import app
from api.safecheck import _report_attempts


client = TestClient(app)


def test_valid_upi_assessment_is_reproducible_and_does_not_verify_identity():
    payload = "upi://pay?pa=abcstores@bank&pn=ABC%20Stores&am=500&cu=INR&tn=Invoice%2012"
    first = client.post("/risk/qr/analyze", json={"qr_payload": payload, "client_version": "test"})
    second = client.post("/risk/qr/analyze", json={"qr_payload": payload, "client_version": "test"})
    assert first.status_code == second.status_code == 200
    a, b = first.json(), second.json()
    assert a["qrType"] == "UPI"
    assert a["parsedDetails"]["payee_address"] == "abcstores@bank"
    assert a["parsedDetails"]["amount"] == 500.0
    assert a["riskScore"] == b["riskScore"]
    assert a["confidence"] == b["confidence"]
    assert any(signal["code"] == "PAYEE_NAME_ENCODED" for signal in a["signals"])
    assert "independently verified" in " ".join(signal["message"] for signal in a["signals"])


def test_url_and_unknown_qr_types_are_explicit():
    url = client.post("/risk/qr/analyze", json={"qr_payload": "http://192.0.2.10/login"})
    unknown = client.post("/risk/qr/analyze", json={"qr_payload": "not-a-supported-qr"})
    assert url.status_code == 200 and url.json()["qrType"] == "URL"
    assert any(signal["code"] == "URL_NOT_HTTPS" for signal in url.json()["signals"])
    assert unknown.status_code == 200
    assert unknown.json()["riskLevel"] == "UNKNOWN"
    assert unknown.json()["riskScore"] is None


def test_empty_payload_is_rejected():
    response = client.post("/risk/qr/analyze", json={"qr_payload": "   "})
    assert response.status_code == 422


def test_oversized_and_unsafe_qr_payloads_are_rejected():
    oversized = client.post("/risk/qr/analyze", json={"qr_payload": "x" * 4097})
    unsafe = client.post("/risk/qr/analyze", json={"qr_payload": "javascript:alert(1)"})
    assert oversized.status_code == 422
    assert unsafe.status_code == 422


def test_duplicate_upi_parameters_are_signal_not_silently_ignored():
    response = client.post(
        "/risk/qr/analyze",
        json={"qr_payload": "upi://pay?pa=merchant@bank&am=10&am=999"},
    )
    assert response.status_code == 200
    assert any(signal["code"] == "UPI_DUPLICATE_PARAMETER" for signal in response.json()["signals"])


def test_reports_are_unverified_duplicate_checked_and_rate_limited():
    _report_attempts.clear()
    identifier = f"merchant-{uuid.uuid4().hex[:10]}@bank"
    body = {
        "identifier": identifier,
        "category": "scam",
        "description": "Unexpected payment request",
    }
    created = client.post("/reports/payment-identifier", json=body)
    assert created.status_code == 201
    assert created.json()["status"] == "UNVERIFIED"
    duplicate = client.post("/reports/payment-identifier", json=body)
    assert duplicate.status_code == 409

    for index in range(4):
        response = client.post("/reports/payment-identifier", json={**body, "identifier": f"other-{index}-{identifier}"})
        assert response.status_code == 201
    limited = client.post("/reports/payment-identifier", json={**body, "identifier": f"limited-{identifier}"})
    assert limited.status_code == 429


def test_report_text_redacts_obvious_payment_secrets_and_assessments_require_auth():
    _report_attempts.clear()
    identifier = f"safe-{uuid.uuid4().hex[:10]}@bank"
    response = client.post(
        "/reports/payment-identifier",
        json={
            "identifier": identifier,
            "category": "other",
            "description": "otp 123456 and UPI PIN 9876 were requested",
            "evidence": "password=secret-value",
        },
    )
    assert response.status_code == 201
    reports = store.list_all("safecheck_reports", tenant_id=platform_settings.default_tenant_id)
    saved = next(item for item in reports if item["report_id"] == response.json()["reportId"])
    assert "123456" not in saved["description"]
    assert "secret-value" not in (saved["evidence"] or "")
    stored = client.get("/risk/qr/assessments")
    assert stored.status_code == 401
