from __future__ import annotations

import hashlib
import ipaddress
import re
import time
import unicodedata
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from enum import Enum
from urllib.parse import parse_qs, unquote, urlparse

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator

from api import store
from api.core_platform.config import platform_settings
from api.core_platform.events import platform_event_broker
from api.core_platform.dependencies import get_current_tenant


router = APIRouter(tags=["Fusion SafeCheck"])
MAX_QR_LENGTH = 4096
REPORT_RATE_LIMIT = 5
REPORT_RATE_WINDOW_SECONDS = 3600
_report_attempts: dict[str, deque[float]] = defaultdict(deque)


class QRType(str, Enum):
    UPI = "UPI"
    URL = "URL"
    UNKNOWN = "UNKNOWN"


class ReportCategory(str, Enum):
    PHISHING = "phishing"
    FAKE_MERCHANT = "fake_merchant"
    IMPERSONATION = "impersonation"
    SUSPICIOUS_PAYMENT_REQUEST = "suspicious_payment_request"
    UNEXPECTED_RECIPIENT = "unexpected_recipient"
    SCAM = "scam"
    OTHER = "other"


class QRAnalyzeRequest(BaseModel):
    qr_payload: str = Field(min_length=1, max_length=MAX_QR_LENGTH)
    application_id: str | None = Field(default=None, max_length=128)
    client_version: str | None = Field(default=None, max_length=64)
    client_context: dict[str, str] | None = None

    @field_validator("qr_payload")
    @classmethod
    def trim_payload(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("QR payload cannot be empty")
        return value


class PaymentIdentifierReportRequest(BaseModel):
    identifier: str = Field(min_length=2, max_length=512)
    category: ReportCategory
    description: str = Field(min_length=3, max_length=2000)
    evidence: str | None = Field(default=None, max_length=2000)

    @field_validator("identifier", "description", "evidence")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None


def _tenant_for_request(request: Request) -> str:
    # SafeCheck is public, so a caller cannot select an arbitrary tenant.
    # Authenticated callers use the middleware-derived tenant; public callers
    # use the deployment's configured default tenant.
    return str(getattr(request.state, "tenant", None) or platform_settings.default_tenant_id)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sanitize_report_text(value: str | None) -> str | None:
    """Keep public reports useful without retaining obvious payment secrets."""
    if value is None:
        return None
    sanitized = re.sub(
        r"(?i)\b(password|passcode|otp|one[- ]time password|upi[ -]?pin|cvv|cvc|bank(?:ing)? credential)\b\s*[:=]?\s*[^\s,;]+",
        "[REDACTED-SENSITIVE-VALUE]",
        value,
    )
    sanitized = re.sub(
        r"(?i)\b(password|passcode|otp|one[- ]time password|upi[ -]?pin|cvv|cvc|bank(?:ing)? credential)\b",
        "[REDACTED-SENSITIVE-TERM]",
        sanitized,
    )
    return re.sub(r"\b\d{6,}\b", "[REDACTED-LONG-NUMBER]", sanitized)


def _safe_float(value: str | None) -> float | None:
    if value is None or not value.strip():
        return None
    try:
        amount = float(value)
    except ValueError:
        return None
    return amount if 0 < amount <= 10_000_000 else None


def _valid_upi(value: str | None) -> bool:
    return bool(value and re.fullmatch(r"[A-Za-z0-9._-]{2,256}@[A-Za-z0-9.-]{2,128}", value))


def _parse_qr(payload: str) -> tuple[QRType, dict, list[dict], int, int]:
    normalized = unicodedata.normalize("NFKC", unquote(payload.strip()))
    signals: list[dict] = []
    score = 0
    confidence = 20

    if normalized.lower().startswith("upi://pay") or re.search(r"(?:^|[?&])pa=", normalized, re.I):
        parsed = urlparse(normalized if "://" in normalized else f"upi://pay?{normalized.lstrip('?')}")
        parsed_values = parse_qs(parsed.query, keep_blank_values=True)
        values = {key.lower(): items[0].strip() for key, items in parsed_values.items() if items}
        payee = values.get("pa")
        name = values.get("pn") or None
        amount_raw = values.get("am")
        amount = _safe_float(amount_raw)
        currency = values.get("cu") or None
        note = values.get("tn") or None
        details = {
            "payee_address": payee,
            "encoded_payee_name": name,
            "amount": amount,
            "currency": currency,
            "transaction_note": note,
            "metadata": {key: value for key, value in values.items() if key not in {"pa", "pn", "am", "cu", "tn"}},
            "raw_payload_sha256": _digest(normalized),
        }
        if not _valid_upi(payee):
            score += 35
            signals.append({"code": "UPI_PAYEE_INVALID", "severity": "HIGH", "message": "The QR does not contain a valid UPI payee address."})
        else:
            confidence += 45
            signals.append({"code": "UPI_PAYLOAD_VALID", "severity": "INFO", "message": "UPI payment fields were parsed successfully."})
        duplicate_keys = [key for key, items in parsed_values.items() if len(items) > 1]
        if duplicate_keys:
            score += 15
            confidence = max(0, confidence - 10)
            signals.append({"code": "UPI_DUPLICATE_PARAMETER", "severity": "MEDIUM", "message": "The QR repeats one or more payment parameters; review the payload carefully."})
        if amount_raw and amount is None:
            score += 20
            signals.append({"code": "UPI_AMOUNT_INVALID", "severity": "MEDIUM", "message": "The amount field is malformed or outside the supported range."})
        if not name:
            confidence -= 5
            signals.append({"code": "PAYEE_NAME_MISSING", "severity": "INFO", "message": "No payee name was encoded in the QR."})
        else:
            signals.append({"code": "PAYEE_NAME_ENCODED", "severity": "INFO", "message": "A payee name is encoded in the QR; it is not independently verified."})
        return QRType.UPI, details, signals, score, max(0, min(confidence, 100))

    parsed = urlparse(normalized)
    if parsed.scheme.lower() in {"http", "https"} and parsed.hostname:
        details = {
            "url": normalized,
            "host": parsed.hostname,
            "scheme": parsed.scheme.lower(),
            "raw_payload_sha256": _digest(normalized),
        }
        confidence = 45
        signals.append({"code": "URL_STRUCTURE_VALID", "severity": "INFO", "message": "The QR contains a syntactically valid web URL."})
        if parsed.scheme.lower() != "https":
            score += 20
            signals.append({"code": "URL_NOT_HTTPS", "severity": "MEDIUM", "message": "The URL does not use HTTPS."})
        try:
            ipaddress.ip_address(parsed.hostname)
            score += 20
            signals.append({"code": "URL_IP_HOST", "severity": "MEDIUM", "message": "The URL uses a numeric host instead of a domain name."})
        except ValueError:
            pass
        if parsed.username or parsed.password:
            score += 25
            signals.append({"code": "URL_USERINFO", "severity": "HIGH", "message": "The URL contains user-info syntax, which can obscure the destination."})
        if parsed.hostname.lower().startswith("xn--") or ".xn--" in parsed.hostname.lower():
            score += 15
            signals.append({"code": "URL_PUNYCODE_HOST", "severity": "MEDIUM", "message": "The domain uses punycode and should be checked carefully."})
        if re.search(r"(login|verify|wallet|claim|urgent|reward|kyc|refund)", normalized, re.I):
            score += 10
            signals.append({"code": "URL_SUSPICIOUS_TERMS", "severity": "MEDIUM", "message": "The URL contains terms commonly seen in social-engineering links."})
        signals.append({"code": "URL_REPUTATION_NOT_QUERIED", "severity": "INFO", "message": "No external reputation lookup was performed for this assessment."})
        return QRType.URL, details, signals, score, confidence

    details = {"raw_payload_sha256": _digest(normalized)}
    signals.append({"code": "QR_UNSUPPORTED", "severity": "MEDIUM", "message": "The QR format is not recognized by SafeCheck."})
    return QRType.UNKNOWN, details, signals, None if not normalized else 50, 10


def _report_score(reports: list[dict]) -> tuple[int, int]:
    score = 0
    corroborated = 0
    weights = {"UNVERIFIED": 5, "UNDER_REVIEW": 10, "CORROBORATED": 20, "CONFIRMED": 35}
    for report in reports:
        status_name = str(report.get("status", "UNVERIFIED"))
        score += weights.get(status_name, 0)
        if status_name in {"CORROBORATED", "CONFIRMED"}:
            corroborated += 1
    return min(score, 70), corroborated


def _risk_level(qr_type: QRType, score: int | None) -> str:
    if qr_type == QRType.UNKNOWN or score is None:
        return "UNKNOWN"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


def _recommendation(level: str) -> str:
    return {
        "LOW": "Verify the recipient name and amount before paying.",
        "MEDIUM": "Pause and independently verify the recipient and destination before continuing.",
        "HIGH": "Do not proceed until the recipient and destination are independently verified.",
        "UNKNOWN": "SafeCheck could not establish enough evidence. Do not proceed without independent verification.",
    }[level]


def _rate_limit(key: str) -> None:
    now = time.time()
    attempts = _report_attempts[key]
    while attempts and attempts[0] <= now - REPORT_RATE_WINDOW_SECONDS:
        attempts.popleft()
    if len(attempts) >= REPORT_RATE_LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Report rate limit exceeded; try again later")
    attempts.append(now)


@router.post("/risk/qr/analyze")
async def analyze_qr(payload: QRAnalyzeRequest, request: Request):
    scheme = payload.qr_payload.strip().split(":", 1)[0].lower() if ":" in payload.qr_payload else ""
    if scheme and scheme not in {"upi", "http", "https"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported or unsafe QR URI scheme")
    tenant_id = _tenant_for_request(request)
    qr_type, parsed_details, signals, score, confidence = _parse_qr(payload.qr_payload)
    identifier = parsed_details.get("payee_address") or parsed_details.get("host")
    reports = store.list_all("safecheck_reports", tenant_id=tenant_id) if identifier else []
    matched_reports = [item for item in reports if item.get("identifier_normalized") == str(identifier).casefold()]
    report_score, corroborated = _report_score(matched_reports)
    if report_score:
        score = (score or 0) + report_score
        signals.append({"code": "COMMUNITY_REPORTS", "severity": "HIGH" if corroborated else "MEDIUM", "message": f"{len(matched_reports)} community report(s) matched this identifier."})
        confidence = min(100, confidence + min(30, len(matched_reports) * 10))
    level = _risk_level(qr_type, score)
    assessed_at = _now()
    assessment_id = f"ASC_{uuid.uuid4().hex[:16].upper()}"
    response = {
        "riskScore": None if qr_type == QRType.UNKNOWN else max(0, min(score or 0, 100)),
        "confidence": max(0, min(confidence, 100)),
        "riskLevel": level,
        "qrType": qr_type.value,
        "parsedDetails": parsed_details,
        "signals": signals,
        "recommendation": _recommendation(level),
        "assessmentId": assessment_id,
        "assessedAt": assessed_at,
        "reportCount": len(matched_reports),
    }
    store.put("safecheck_assessments", assessment_id, {**response, "tenant_id": tenant_id, "identifier_normalized": str(identifier).casefold() if identifier else None})
    await platform_event_broker.publish({
        "event_type": "QR_RISK_ASSESSMENT",
        "assessment_id": assessment_id,
        "tenant_id": tenant_id,
        "qr_type": qr_type.value,
        "risk_level": level,
        "risk_score": response["riskScore"],
        "confidence": response["confidence"],
        "signal_codes": [signal["code"] for signal in signals],
        "report_count": len(matched_reports),
        "timestamp": assessed_at,
    })
    return response


@router.post("/reports/payment-identifier", status_code=status.HTTP_201_CREATED)
async def report_payment_identifier(payload: PaymentIdentifierReportRequest, request: Request):
    tenant_id = _tenant_for_request(request)
    source_key = request.client.host if request.client else "unknown"
    identifier_normalized = payload.identifier.casefold()
    report_key = _digest(f"{tenant_id}|{identifier_normalized}|{payload.category.value}")
    if store.get("safecheck_reports", report_key, tenant_id=tenant_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A report for this identifier and category already exists")
    _rate_limit(source_key)
    report_id = f"RPT_{uuid.uuid4().hex[:16].upper()}"
    safe_description = _sanitize_report_text(payload.description)
    safe_evidence = _sanitize_report_text(payload.evidence)
    report = {
        "report_id": report_id,
        "identifier_normalized": identifier_normalized,
        "identifier_display": payload.identifier,
        "category": payload.category.value,
        "description": safe_description,
        "evidence": safe_evidence,
        "status": "UNVERIFIED",
        "tenant_id": tenant_id,
        "created_at": _now(),
    }
    store.put("safecheck_reports", report_key, report, tenant_id=tenant_id)
    await platform_event_broker.publish({
        "event_type": "COMMUNITY_RISK_REPORT",
        "report_id": report_id,
        "tenant_id": tenant_id,
        "category": payload.category.value,
        "identifier_hash": _digest(identifier_normalized),
        "status": "UNVERIFIED",
        "timestamp": report["created_at"],
    })
    return {
        "reportId": report_id,
        "status": "UNVERIFIED",
        "message": "Your report will be reviewed.",
        "createdAt": report["created_at"],
    }


@router.get("/risk/qr/assessments")
async def list_safecheck_assessments(request: Request, limit: int = 50):
    tenant_id = get_current_tenant(request)
    rows = store.list_all("safecheck_assessments", tenant_id=tenant_id)
    rows.sort(key=lambda item: str(item.get("assessedAt", "")), reverse=True)
    return {"assessments": rows[: max(1, min(limit, 100))], "count": min(len(rows), max(1, min(limit, 100)))}
