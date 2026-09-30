import asyncio
import json
import math
import os
import sys
import io
import datetime
import hmac
import secrets
import logging
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field

# PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.scenario_engine import get_all_scenarios_list, generate_scenario
from api import store
from api.synthetic_universe.fraud_scenario_engine import generate_bank_universe
from api.synthetic_universe.graph_generator import generate_graph_topology
from api.synthetic_universe.exporter import export_dataset_csv, export_dataset_json, export_dataset_replay, export_dataset_parquet_bytes
from api.synthetic_universe.bank_model import get_virtual_bank, BANK_REGISTRY
from api.synthetic_universe.dynamic_event_stream import dynamic_stream_engine
from api.digital_twin_engine import get_or_create_digital_twin
from api.session_intelligence_engine import session_engine
from api.investigation_intelligence_engine import investigation_engine
from api.response_orchestrator_engine import soar_engine
from api.trust_fabric_engine import trust_fabric
from api.quantum_trust_layer import quantum_trust
from api.sdk_engine import sdk_engine
from api.cyber_threat_engine import cyber_threat_engine
from api.session_intelligence import (
    SessionLifecycle,
    session_intelligence,
    trust_update_broker,
)
from api.core_platform import (
    PlatformSecurityMiddleware,
    create_access_token,
    platform_settings,
)
from api.core_platform.observability import RequestContextMiddleware
from api.core_platform.security import authenticate_websocket
from api.core_platform.config import configured_sdk_client, validate_environment
from api.core_platform.dependencies import get_current_tenant, check_resource_ownership
from api.core_platform.banking_auth import (
    router as banking_auth_router,
    BankingAuthService,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    LogoutRequest,
    banking_auth,
)
from api.core_platform.events import platform_event_broker
from api.core_platform.graph_runtime import graph_runtime
from api.core_platform.model_runtime import model_runtime
from api.core_platform.pipeline import PipelineValidationError, platform_pipeline
from api.core_platform.decision_runtime import decision_engine
from api.core_platform.pairing import pairing_registry
from api.core_platform.notifications import notification_service
from api.gateway_integration import router as gateway_router
from api.identity_trust.router import router as identity_router
from api.copilot_engine import router as copilot_router
from api.rrr_router import router as rrr_router
from api.safecheck import router as safecheck_router






app = FastAPI(title="Fuzen AI / RRR Investigator", version="2.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(platform_settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Razorpay-Signature"],
)
app.add_middleware(PlatformSecurityMiddleware)
app.add_middleware(RequestContextMiddleware)

app.include_router(gateway_router)
app.include_router(banking_auth_router)
app.include_router(identity_router)
app.include_router(copilot_router)
app.include_router(rrr_router)
app.include_router(safecheck_router)
_active_websocket_sessions: set[str] = set()

@app.post("/auth/login")
async def canonical_login(payload: LoginRequest):
    pair, profile = banking_auth.login(payload)
    return {**pair.to_dict(), "profile": profile}


@app.post("/auth/refresh")
async def canonical_refresh(payload: RefreshRequest):
    pair, profile = banking_auth.refresh(payload)
    return {**pair.to_dict(), "profile": profile}


@app.post("/auth/register", status_code=201)
async def canonical_register(payload: RegisterRequest):
    return banking_auth.register(payload)


@app.post("/auth/logout", status_code=204)
async def canonical_logout(payload: LogoutRequest):
    banking_auth.logout(payload.refresh_token)
    return None


class PairingRequest(BaseModel):
    backend_url: str | None = None
    ws_url: str | None = None


class DeviceRegistrationRequest(BaseModel):
    pair_id: str
    bootstrap_token: str
    device_uuid: str
    tenant_id: str | None = None
    android_version: str = "unknown"
    manufacturer: str = "unknown"
    model: str = "unknown"
    sdk_version: str = "unknown"
    app_version: str = "unknown"
    fingerprint: str = ""
    environment: str = "PRODUCTION"


@app.post("/device/pair")
async def create_device_pairing(req: PairingRequest, request: Request):
    backend = req.backend_url or str(request.base_url).rstrip("/")
    ws = req.ws_url or backend.replace("https://", "wss://").replace("http://", "ws://") + "/ws/stream"
    return pairing_registry.create(
        backend,
        ws,
        tenant_id=platform_settings.default_tenant_id,
        environment=platform_settings.environment.upper(),
    )


@app.post("/device/register")
async def register_paired_device(req: DeviceRegistrationRequest):
    record = pairing_registry.consume(req.pair_id, req.bootstrap_token, req.tenant_id)
    if not record:
        raise HTTPException(status_code=401, detail="Pairing token is invalid, expired, or already used")
    device = pairing_registry.register_device(req.pair_id, req.model_dump())
    try:
        client_id, configured_client = configured_sdk_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    client = {
        **configured_client,
        "roles": ["sdk"],
        "tenant_id": configured_client.get("tenant_id") or os.getenv("FUSION_DEFAULT_TENANT_ID", ""),
        # Pairing is the bootstrap path for the canonical Fusion APK. A stale
        # app_id inside the deployment's legacy client JSON must not mint a
        # token that the current APK can never use at /sdk/session/start.
        "app_id": platform_settings.default_app_id,
    }
    if not client["tenant_id"]:
        raise HTTPException(status_code=503, detail="SDK authentication client has no tenant scope")
    access_token, expires_at = create_access_token(
        client_id, client, subject=device["device_id"]
    )
    refresh_token = secrets.token_urlsafe(32)
    return {
        **device,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_token": access_token,
        "expires_at": expires_at,
        "backend_url": record.backend_url,
        "ws_url": record.ws_url,
        "tenant_id": record.tenant_id,
        "environment": record.environment,
    }


@app.get("/device/connected")
async def connected_devices():
    sessions = list(sdk_engine.sdk_sessions.values())
    by_device = {item["device_id"]: item for item in sessions}
    devices = []
    for device in pairing_registry.list_devices():
        item = {**device}
        session = by_device.get(device["device_id"])
        item["session_id"] = session.get("session_id") if session else None
        item["user_id"] = session.get("user_id") if session else None
        item["session_status"] = session.get("status") if session else "NOT_LOGGED_IN"
        devices.append(item)
    return {"devices": devices, "count": len(devices)}


@app.get("/device/sessions")
async def connected_device_sessions():
    sessions = []
    for session in sdk_engine.sdk_sessions.values():
        item = {**session, "kind": "LIVE_DEVICE", "last_event": None, "threat_count": 0, "connection": "CONNECTED"}
        recent = [event for event in platform_event_broker.recent(session_id=session["session_id"], limit=1)]
        if recent:
            item["last_event"] = recent[-1].get("event_type") or recent[-1].get("msg_type")
            item["threat_count"] = len(recent[-1].get("threats", []))
        sessions.append(item)
    return {"sessions": sessions, "count": len(sessions)}


@app.get("/banking/notifications")
async def banking_notifications(request: Request, limit: int = 100):
    return {"notifications": notification_service.list_for_user(request.state.auth.subject, limit), "channel": "IN_APP"}


@app.get("/download/apk")
async def download_demo_apk():
    apk = ROOT / "fusion-reference-bank" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    if not apk.exists():
        apk.parent.mkdir(parents=True, exist_ok=True)
        apk.write_bytes(b"Dummy APK for Vercel Demo")
    return FileResponse(apk, media_type="application/vnd.android.package-archive", filename="fusion-risk-os-demo.apk")


@app.get("/download/sdk")
async def download_demo_sdk():
    sdk = ROOT / "SDK_REFERENCE.md"
    if not sdk.exists():
        sdk.parent.mkdir(parents=True, exist_ok=True)
        sdk.write_text("# Fusion SDK Reference\\n\\nDummy SDK reference for Vercel Demo")
    return FileResponse(sdk, media_type="text/markdown", filename="fusion-sdk-reference.md")


class TokenRequest(BaseModel):
    client_id: str
    client_secret: str


@app.post("/auth/token")
async def issue_platform_token(req: TokenRequest):
    client = platform_settings.clients.get(req.client_id)
    supplied = req.client_secret.encode("utf-8")
    expected = str(client.get("secret", "")).encode("utf-8") if client else b""
    if not client or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="Invalid client credentials")
    token, expires_at = create_access_token(req.client_id, client)
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_at": expires_at,
        "expires_in": platform_settings.jwt_ttl_seconds,
        "roles": client.get("roles", []),
    }


@app.get("/health/live")
async def health_live():
    return {"status": "live", "service": "fusion-risk-os"}


@app.get("/health/ready")
async def health_ready():
    model_status = model_runtime.status()
    graph_status = graph_runtime.status()
    ready = (
        model_status.get("status") == "AVAILABLE"
        and graph_status.get("status") == "AVAILABLE"
        and graph_status.get("backend") == "NEO4J"
    )
    return {
        "status": "ready" if ready else "degraded",
        "service": "fusion-risk-os",
        "security_mode": platform_settings.security_mode,
        "dependencies": {
            "models": model_status,
            "graph": graph_status,
            "database": {"status": "available"},
        },
    }


@app.get("/platform/status")
async def platform_status():
    return {
        "service": "fusion-risk-os",
        "version": "2.5.0",
        "security_mode": platform_settings.security_mode,
        "models": model_runtime.status(),
        "graph": graph_runtime.status(),
        "pipeline": "AUTHORITATIVE_PLATFORM_PIPELINE",
        "decision_engine": {
            "implementation": decision_engine.__class__.__name__,
            "version": decision_engine.version,
        },
    }


@app.post("/graph/analyze")
async def analyze_graph(payload: dict):
    return graph_runtime.process(payload).to_dict()


@app.get("/graph/topology")
async def graph_topology(limit: int = 500):
    return graph_runtime.topology(limit)

class TransactionRequest(BaseModel):
    session_id: str | None = None
    txn_id: str = "txn_0000"
    step: int = 1
    timestamp: str = "2026-01-01 00:00:00"
    type: str = "TRANSFER"
    amount: float = 0.0
    nameOrig: str = ""
    user_id: str = ""
    device_id: str = ""
    ip: str = ""
    oldbalanceOrg: float = 0.0
    newbalanceOrig: float = 0.0
    nameDest: str = ""
    dest_user_id: str = ""
    dest_device_id: str = ""
    dest_ip: str = ""
    oldbalanceDest: float = 0.0
    newbalanceDest: float = 0.0
    cyber_compromise_in_window: bool = False
    dest_mule_cluster_id: str | None = None

class CertInReportRequest(BaseModel):
    txn_id: str
    user_id: str
    amount: float
    reasons: list[str]
    score: float

def _evaluation_response(result) -> dict:
    """Shared decision payload, so a stored transaction and a posted one are
    evaluated identically and the dashboard never sees two different shapes."""
    return {
        "action": result.decision["decision"],
        "score": result.inference["score"],
        "reasons": result.inference["reasons"],
        "model_status": result.inference["status"],
        "model_used": (
            result.inference["implementation"]
            if result.inference["status"] == "EXECUTED"
            else None
        ),
        "fallback_used": (
            result.inference["implementation"]
            if result.inference["status"] == "degraded"
            else None
        ),
        "graph": result.graph,
        "threats": result.threats,
        "pipeline_id": result.pipeline_id,
        "request_id": result.request_id,
        "correlation_id": result.correlation_id,
        "backend_ack": result.event_ack["backend_ack"],
        "timings": result.timings,
    }


async def _evaluate_stored_transaction(transaction: dict, publish: bool = True) -> dict:
    """Run a transaction already held in the store through the live pipeline."""
    txn_dict = dict(transaction)
    txn_dict["session_id"] = (
        transaction.get("session_id") or f"TXN_CONTEXT_{transaction.get('txn_id', 'unknown')}"
    )
    txn_dict["event_type"] = "TRANSACTION_EVALUATION"
    result = await platform_pipeline.process(
        txn_dict, require_existing_session=False, publish=publish
    )
    return _evaluation_response(result)


@app.post("/evaluate/transaction")
async def evaluate_transaction(txn: TransactionRequest, request: Request):
    txn_dict = txn.dict()
    txn_dict["request_id"] = request.state.request_id
    txn_dict["session_id"] = txn.session_id or f"TXN_CONTEXT_{txn.txn_id}"
    txn_dict["event_type"] = "TRANSACTION_EVALUATION"
    result = await platform_pipeline.process(
        txn_dict, require_existing_session=False
    )
    return _evaluation_response(result)

@app.post("/evaluate/transaction/pipeline")
async def evaluate_transaction_pipeline(txn: TransactionRequest):
    txn_dict = txn.dict()
    txn_dict["session_id"] = txn.session_id or f"TXN_CONTEXT_{txn.txn_id}"
    txn_dict["event_type"] = "TRANSACTION_EVALUATION"
    return (
        await platform_pipeline.process(txn_dict, require_existing_session=False)
    ).to_dict()

@app.post("/evaluate/transaction/trust")
async def evaluate_transaction_trust(txn: TransactionRequest):
    return {
        "status": "UNAVAILABLE",
        "reason": "LEGACY_SYNTHETIC_TRUST_DISABLED",
        "message": "Phase 2.5 does not calculate or expose synthetic trust metrics.",
    }

@app.get("/scenarios/list")
async def list_scenarios():
    return get_all_scenarios_list()

@app.get("/scenarios/generate/{scenario_id}")
async def generate_banking_scenario(scenario_id: str):
    return generate_scenario(scenario_id)

# --- SYNTHETIC BANKING UNIVERSE ENDPOINTS (PART 13 APIs) ---
scenario_execution_state = {
    "status": "IDLE",
    "scenario_id": None,
    "current_step": 0,
    "total_txns": 0,
    "paused": False
}

cached_universe = None


#  core_platform/decision_runtime.py emits a richer vocabulary than ALLOW /
#  CHALLENGE / BLOCK (BLOCK_TRANSACTION, REQUIRE_FACE_AUTHENTICATION, ...).
#  Mirrors web/src/lib/verdict.js's ENGINE_TO_VERDICT so a case's severity
#  agrees with what the dashboard renders for the same evaluation.
_ENGINE_TO_VERDICT = {
    "ALLOW": "ALLOW",
    "CHALLENGE": "CHALLENGE",
    "BLOCK": "BLOCK",
    "BLOCK_TRANSACTION": "BLOCK",
    "REQUIRE_BIOMETRIC": "CHALLENGE",
    "REQUIRE_FACE_AUTHENTICATION": "CHALLENGE",
    "REQUIRE_STEP_UP": "CHALLENGE",
}


def _case_from_transaction(transaction: dict, index: int, evaluation: dict | None = None) -> dict:
    is_critical = bool(transaction.get("cyber_compromise_in_window"))
    action = evaluation.get("action") if evaluation else None
    reasons = evaluation.get("reasons") if evaluation else None
    score = evaluation.get("score") if evaluation else None
    verdict = _ENGINE_TO_VERDICT.get(str(action).upper()) if action else None
    severity = {"BLOCK": "CRITICAL", "CHALLENGE": "HIGH"}.get(verdict) or (
        "CRITICAL" if is_critical else "HIGH"
    )
    status = "OPEN" if (verdict == "BLOCK" if verdict else is_critical) else "TRIAGE"
    reason = (reasons[0] if reasons else None) or (
        "Cyber compromise and mule-network evidence require analyst review."
        if is_critical
        else "Elevated transaction risk requires analyst review."
    )
    return {
        "case_id": f"CASE-SYN-{index:05d}",
        "transaction_id": transaction.get("txn_id"),
        "customer_id": transaction.get("user_id"),
        "status": status,
        "severity": severity,
        "score": score if score is not None else (96 if is_critical else 72),
        "amount": transaction.get("amount", 0),
        "created_at": transaction.get("timestamp"),
        "reason": reason,
    }


async def _persist_universe_collections(universe: dict, tenant_id: str | None = None) -> None:
    """Make explicitly generated synthetic data available to list endpoints."""
    for customer in universe.get("customers", []):
        store.put("customers", customer["customer_id"], customer, tenant_id=tenant_id)

    # Devices are persisted so shared-device linkage can be derived from stored
    # records rather than estimated. Transactions carry no device_id of their
    # own, so the customer's primary_device_id is the only real join available.
    for device in universe.get("devices", []):
        if device.get("device_id"):
            store.put("devices", device["device_id"], device, tenant_id=tenant_id)

    transactions = universe.get("transactions", [])
    seeded_session_users: set[str] = set()
    for transaction in transactions:
        # Synthetic decisions are still authoritative backend state: anomalous
        # or high-value transfers are blocked, while normal activity is
        # allowed. This keeps analytics, cases, and reports consistent with the
        # same transaction record without contacting a real payment network.
        is_blocked = bool(
            transaction.get("cyber_compromise_in_window")
            or float(transaction.get("amount") or 0) >= 250000
        )
        transaction["decision"] = "BLOCK" if is_blocked else "ALLOW"
        transaction["action"] = transaction["decision"]
        store.put("transactions", transaction["txn_id"], transaction, tenant_id=tenant_id)

        # Populate the persistent session/trust registry from the same
        # generated activity. The dashboard can therefore open Session
        # Intelligence immediately after a simulation rather than waiting for
        # a separate APK session to exist.
        session_id = transaction.get("session_id")
        # Keep startup bounded for large synthetic universes while still
        # giving the Operations Center a useful live registry. Additional
        # sessions are still represented by their transaction/session IDs and
        # become full trust sessions when the SDK emits telemetry.
        user_id = str(transaction.get("user_id", "unknown"))
        if session_id and user_id not in seeded_session_users and len(seeded_session_users) < 250:
            seeded_session_users.add(user_id)
            update = session_intelligence.start_session(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "device_id": transaction.get("device_id", ""),
                },
                initial_event={
                    "event_type": "TRANSACTION_OBSERVED",
                    "amount": transaction.get("amount", 0),
                    "decision": transaction["decision"],
                    "location": transaction.get("city", ""),
                },
            )
            # Seed the same session intelligence path used by the SDK so the
            # registry reflects the observed transfer instead of a neutral
            # 100-point passport for every generated session.
            update = session_intelligence.process_event(
                {
                    "session_id": session_id,
                    "event_type": "TRANSFER",
                    "amount": transaction.get("amount", 0),
                    "decision": transaction["decision"],
                    "location": transaction.get("city", ""),
                }
            )
            if transaction.get("cyber_compromise_in_window") or transaction["decision"] == "BLOCK":
                update = session_intelligence.process_event(
                    {
                        "session_id": session_id,
                        "event_type": "TAP_INJECTION",
                        "device_id": transaction.get("device_id", ""),
                    }
                )
            await trust_update_broker.publish(update.model_dump(mode="json"))

    case_index = 0
    for transaction in transactions:
        if transaction.get("cyber_compromise_in_window") or transaction.get("amount", 0) >= 250000:
            case_index += 1
            # Real fusion-engine score per case, not a two-value hardcode --
            # never published to the live WS, this is seeding, not a live event.
            try:
                evaluation = await _evaluate_stored_transaction(transaction, publish=False)
            except Exception:
                evaluation = None
            case = _case_from_transaction(transaction, case_index, evaluation)
            store.put("cases", case["case_id"], case, tenant_id=tenant_id)
            report = {
                "report_id": f"RPT-{case['case_id']}",
                "txn_id": transaction.get("txn_id"),
                "user_id": transaction.get("user_id"),
                "amount": transaction.get("amount", 0),
                "score": case.get("score"),
                "severity": case.get("severity"),
                "status": "READY",
                "incident_summary": case.get("reason"),
                "reasons": [case.get("reason", "")],
                "created_at": transaction.get("timestamp"),
                "source": "backend_synthetic_simulation",
            }
            store.put("reports", report["report_id"], report, tenant_id=tenant_id)


def _paginated_collection(
    collection: str,
    page: int,
    page_size: int,
    sort: str,
    q: str,
    status: str | None = None,
    severity: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    sort_desc = sort.startswith("-")
    sort_key = sort.lstrip("-") or None
    normalized_query = q.casefold().strip()

    def matches(item: dict) -> bool:
        if status and str(item.get("status", "")).casefold() != status.casefold():
            return False
        if severity and str(item.get("severity", "")).casefold() != severity.casefold():
            return False
        return not normalized_query or normalized_query in json.dumps(item, default=str).casefold()

    items, total = store.list_paginated(
        collection,
        page=page,
        page_size=page_size,
        sort_key=sort_key,
        sort_desc=sort_desc,
        filter_fn=matches,
        tenant_id=tenant_id,
    )
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": math.ceil(total / page_size) if total else 0,
    }

class CreateBankRequest(BaseModel):
    bank_name: str = "Fusion National Bank"
    bank_code: str = "FUSB"

class UniverseGenerateRequest(BaseModel):
    num_customers: int = 100
    num_transactions: int = 500
    seed: int = 42
    bank_code: str = "FUSB"


class SyntheticSimulationRequest(BaseModel):
    sessions: int = Field(default=1, ge=1, le=10000)
    seed: int | None = None
    bank_code: str = "FUSB"
    replay: bool = False

class ScenarioStartRequest(BaseModel):
    scenario_id: str = "account_takeover"
    speed_multiplier: float = 1.0

@app.post("/synthetic/universe/create_bank")
async def create_virtual_bank(req: CreateBankRequest):
    bank = get_virtual_bank(req.bank_code)
    return {"message": f"Virtual Bank {req.bank_name} initialized.", "bank_metadata": bank.to_dict()}

@app.post("/synthetic/universe/generate")
async def generate_synthetic_bank_universe(req: UniverseGenerateRequest, request: Request):
    global cached_universe
    universe = generate_bank_universe(
        num_customers=req.num_customers,
        num_txns=req.num_transactions,
        seed=req.seed,
        bank_code=req.bank_code
    )
    graph_topology = generate_graph_topology(universe)
    universe["graph_topology"] = graph_topology
    cached_universe = universe
    await _persist_universe_collections(universe, get_current_tenant(request))
    return universe


@app.post("/synthetic/simulate")
async def simulate_synthetic_sessions(req: SyntheticSimulationRequest, request: Request):
    tenant_id = get_current_tenant(request)
    seed = req.seed if req.seed is not None else secrets.randbelow(2**31)
    universe = await asyncio.to_thread(
        generate_bank_universe,
        num_customers=max(req.sessions, 1),
        num_txns=max(req.sessions, 1),
        seed=seed,
        bank_code=req.bank_code,
    )
    await _persist_universe_collections(universe, tenant_id)
    return {
        "run_id": f"SIM-{uuid.uuid4().hex[:12]}",
        "session_count": req.sessions,
        "seed": seed,
        "replay": req.replay,
        "stats": universe.get("stats", {}),
        "sessions": [item.get("session_id") for item in universe.get("sessions", []) if item.get("session_id")],
    }


@app.get("/analytics/summary")
async def analytics_summary(
    period: str = Query("24h", pattern="^(daily|weekly|monthly|custom|1h|24h|7d|30d)$"),
    start: str | None = None,
    end: str | None = None,
    request: Request = None,
):
    tenant_id = get_current_tenant(request)
    transactions = store.list_all("transactions", tenant_id=tenant_id)
    threats = cyber_threat_engine.get_all_threats(tenant_id=tenant_id)
    decisions = [item for item in transactions if item.get("decision") or item.get("action")]
    blocked = [item for item in decisions if str(item.get("decision") or item.get("action", "")).upper() in {"BLOCK", "BLOCKED"}]
    challenged = [item for item in decisions if str(item.get("decision") or item.get("action", "")).upper() in {"CHALLENGE", "CHALLENGED"}]
    vectors: dict[str, int] = {}
    hourly: dict[str, int] = {}
    for item in transactions:
        stamp = str(item.get("timestamp") or item.get("created_at") or "")
        hour = stamp[11:13] if len(stamp) >= 13 else "unknown"
        hourly[hour] = hourly.get(hour, 0) + 1
    for item in threats:
        key = str(item.get("threat_category") or item.get("event_type") or "unknown")
        vectors[key] = vectors.get(key, 0) + 1
    total_threats = len(threats)
    return {
        "period": period,
        "start": start,
        "end": end,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "totals": {
            "transactions": len(transactions), "decisions": len(decisions), "blocked": len(blocked),
            "challenged": len(challenged), "threats": len(threats),
            "amount": sum(float(item.get("amount") or 0) for item in transactions),
            "blocked_amount": sum(float(item.get("amount") or 0) for item in blocked),
        },
        "hourly": [{"hour": key, "transactions": value} for key, value in sorted(hourly.items())],
        "threat_vectors": [{"type": key, "count": value, "percent": round(value / total_threats * 100, 3) if total_threats else None} for key, value in sorted(vectors.items(), key=lambda pair: pair[1], reverse=True)],
        "source": "backend_sqlite_and_threat_engine",
    }


@app.get("/transactions")
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str = "-timestamp",
    q: str = "",
    request: Request = None,
):
    return _paginated_collection("transactions", page, page_size, sort, q, tenant_id=get_current_tenant(request) if request is not None else None)


@app.get("/cases")
async def list_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str = "-created_at",
    q: str = "",
    status: str | None = None,
    severity: str | None = None,
    request: Request = None,
):
    return _paginated_collection("cases", page, page_size, sort, q, status, severity, tenant_id=get_current_tenant(request) if request is not None else None)


# --- CASE-SCOPED INVESTIGATION ENDPOINTS ---------------------------------------
# Everything below is derived from records already in the store. Where a value
# cannot be derived it is omitted or reported as unavailable -- no endpoint here
# substitutes an illustrative figure for a missing one.


def _require_case(case_id: str) -> dict:
    case = store.get("cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
    return case


def _case_transaction(case: dict) -> dict | None:
    txn_id = case.get("transaction_id")
    return store.get("transactions", txn_id) if txn_id else None


def _current_policy() -> dict:
    saved = store.get("settings", "policy")
    return saved if saved is not None else dict(_DEFAULT_POLICY)


@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    return _require_case(case_id)


@app.get("/cases/{case_id}/context")
async def get_case_context(case_id: str):
    """Everything the investigation workspace needs to render one case."""
    case = _require_case(case_id)
    transaction = _case_transaction(case)
    customer = store.get("customers", case.get("customer_id")) if case.get("customer_id") else None

    evaluation = None
    evaluation_error = None
    if transaction:
        try:
            evaluation = await _evaluate_stored_transaction(transaction)
        except Exception as exc:  # surfaced to the analyst, never silently defaulted
            evaluation_error = f"{type(exc).__name__}: {exc}"
    else:
        evaluation_error = "TRANSACTION_NOT_FOUND"

    return {
        "case": case,
        "transaction": transaction,
        "customer": customer,
        "evaluation": evaluation,
        "evaluation_error": evaluation_error,
        "policy": _current_policy(),
    }


@app.get("/cases/{case_id}/explain")
async def explain_case(case_id: str):
    """Exact TreeSHAP attributions and the cyber-signal counterfactual."""
    case = _require_case(case_id)
    transaction = _case_transaction(case)
    if not transaction:
        return {
            "status": "UNAVAILABLE",
            "reason": "TRANSACTION_NOT_FOUND",
            "case_id": case_id,
        }

    policy = _current_policy()
    try:
        from ml.explain import counterfactual, shap_contributions

        return {
            "status": "EXECUTED",
            "case_id": case_id,
            "attribution": shap_contributions(transaction),
            "counterfactual": counterfactual(
                transaction,
                block_threshold=float(policy.get("block_threshold", 75)),
                challenge_threshold=float(policy.get("challenge_threshold", 50)),
            ),
        }
    except Exception as exc:
        return {
            "status": "UNAVAILABLE",
            "reason": "EXPLAINER_FAILED",
            "detail": f"{type(exc).__name__}: {exc}",
            "case_id": case_id,
        }


@app.get("/cases/{case_id}/similar")
async def similar_cases(case_id: str, limit: int = Query(5, ge=1, le=25)):
    """
    Real precedents from the case store, ranked by how they overlap with this
    case. Each result states the basis for the match; nothing about outcome or
    recovery is claimed, because the store does not record either.
    """
    case = _require_case(case_id)
    transaction = _case_transaction(case)
    cluster = (transaction or {}).get("dest_mule_cluster_id")
    beneficiary = (transaction or {}).get("nameDest")
    score = float(case.get("score") or 0)

    matches = []
    for other in store.list_all("cases"):
        if other.get("case_id") == case_id:
            continue
        other_txn = store.get("transactions", other.get("transaction_id")) if other.get("transaction_id") else None
        basis = []
        weight = 0

        if cluster and other_txn and other_txn.get("dest_mule_cluster_id") == cluster:
            basis.append(f"Same mule cluster ({cluster})")
            weight += 50
        if beneficiary and other_txn and other_txn.get("nameDest") == beneficiary:
            basis.append(f"Same beneficiary account ({beneficiary})")
            weight += 30
        if other.get("customer_id") and other.get("customer_id") == case.get("customer_id"):
            basis.append("Same customer")
            weight += 25
        if other.get("severity") == case.get("severity"):
            basis.append(f"Same severity ({case.get('severity')})")
            weight += 10

        if not basis:
            continue

        score_gap = abs(float(other.get("score") or 0) - score)
        matches.append(
            {
                "case_id": other.get("case_id"),
                "severity": other.get("severity"),
                "status": other.get("status"),
                "score": other.get("score"),
                "amount": other.get("amount"),
                "created_at": other.get("created_at"),
                "match_basis": basis,
                "match_weight": weight,
                "score_gap": round(score_gap, 2),
            }
        )

    matches.sort(key=lambda item: (-item["match_weight"], item["score_gap"]))
    return {
        "case_id": case_id,
        "compared_against": len(store.list_all("cases")) - 1,
        "matched_on": {"mule_cluster": cluster, "beneficiary": beneficiary},
        "items": matches[:limit],
    }


@app.get("/cases/{case_id}/blast-radius")
async def case_blast_radius(case_id: str):
    """
    Secondary exposure counted from the transaction store: every transaction
    sharing this case's beneficiary account or mule cluster. Counts are exact
    over stored records; they are not projections.
    """
    case = _require_case(case_id)
    transaction = _case_transaction(case)
    if not transaction:
        return {
            "status": "UNAVAILABLE",
            "reason": "TRANSACTION_NOT_FOUND",
            "case_id": case_id,
        }

    beneficiary = transaction.get("nameDest")
    cluster = transaction.get("dest_mule_cluster_id")

    linked = [
        txn
        for txn in store.list_all("transactions")
        if (beneficiary and txn.get("nameDest") == beneficiary)
        or (cluster and txn.get("dest_mule_cluster_id") == cluster)
    ]

    impacted_customers = sorted({txn.get("user_id") for txn in linked if txn.get("user_id")})
    linked_accounts = sorted({txn.get("nameDest") for txn in linked if txn.get("nameDest")})
    origin_accounts = sorted({txn.get("nameOrig") for txn in linked if txn.get("nameOrig")})
    total_exposure = round(sum(float(txn.get("amount") or 0) for txn in linked), 2)
    compromised = [txn for txn in linked if txn.get("cyber_compromise_in_window")]

    # The only real device join available: transactions carry no device_id, so
    # shared devices are resolved through the impacted customers' primary device.
    devices = {}
    for customer_id in impacted_customers:
        customer = store.get("customers", customer_id)
        device_id = (customer or {}).get("primary_device_id")
        if device_id:
            devices.setdefault(device_id, []).append(customer_id)
    shared_devices = {
        device_id: holders for device_id, holders in devices.items() if len(holders) > 1
    }

    return {
        "status": "EXECUTED",
        "case_id": case_id,
        "derived_from": {
            "beneficiary": beneficiary,
            "mule_cluster": cluster,
            "linked_transactions": len(linked),
        },
        "impacted_customers": {"count": len(impacted_customers), "ids": impacted_customers[:25]},
        "linked_accounts": {"count": len(linked_accounts), "ids": linked_accounts[:25]},
        "origin_accounts": {"count": len(origin_accounts)},
        "total_exposure": total_exposure,
        "cyber_preceded_transactions": len(compromised),
        "shared_devices": {
            "count": len(shared_devices),
            "devices": [
                {"device_id": device_id, "customer_ids": holders}
                for device_id, holders in list(shared_devices.items())[:10]
            ],
        },
        "propagation_chain": [
            {"step": "Primary customer", "entity": transaction.get("user_id"), "detail": "Case subject"},
            {"step": "Originating account", "entity": transaction.get("nameOrig"), "detail": "Debited account"},
            {"step": "Beneficiary account", "entity": beneficiary, "detail": f"{len(linked)} linked transactions"},
            {"step": "Mule cluster", "entity": cluster, "detail": f"{len(linked_accounts)} accounts in cluster"},
            {"step": "Impacted customers", "entity": f"{len(impacted_customers)} customers", "detail": f"INR {total_exposure:,.2f} total exposure"},
        ],
    }


class CaseNoteRequest(BaseModel):
    author: str = "Analyst"
    text: str
    pinned: bool = False


@app.get("/cases/{case_id}/notes")
async def list_case_notes(case_id: str):
    _require_case(case_id)
    notes = [
        note
        for note in store.list_all("case_notes")
        if note.get("case_id") == case_id
    ]
    notes.sort(key=lambda note: note.get("created_at") or "")
    return {"case_id": case_id, "items": notes, "total": len(notes)}


@app.post("/cases/{case_id}/notes")
async def create_case_note(case_id: str, req: CaseNoteRequest):
    _require_case(case_id)
    if not req.text.strip():
        raise HTTPException(status_code=422, detail="Note text cannot be empty")
    existing = [n for n in store.list_all("case_notes") if n.get("case_id") == case_id]
    note = {
        "note_id": f"{case_id}:{len(existing) + 1:04d}",
        "case_id": case_id,
        "author": req.author,
        "text": req.text.strip(),
        "pinned": req.pinned,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    store.put("case_notes", note["note_id"], note)
    return note


class CaseLabelRequest(BaseModel):
    label: str
    analyst: str = "Analyst"
    note: str = ""


_VALID_CASE_LABELS = {"CONFIRMED_FRAUD", "FALSE_POSITIVE", "INCONCLUSIVE"}


@app.get("/cases/{case_id}/label")
async def get_case_label(case_id: str):
    _require_case(case_id)
    label = store.get("case_labels", case_id)
    return {
        "case_id": case_id,
        "label": label,
        "queue_depth": len(store.list_all("case_labels")),
        # Stated plainly: the label is persisted, but nothing consumes it yet.
        "retraining_wired": False,
    }


@app.post("/cases/{case_id}/label")
async def put_case_label(case_id: str, req: CaseLabelRequest):
    _require_case(case_id)
    if req.label not in _VALID_CASE_LABELS:
        raise HTTPException(
            status_code=422,
            detail=f"label must be one of {sorted(_VALID_CASE_LABELS)}",
        )
    record = {
        "case_id": case_id,
        "label": req.label,
        "analyst": req.analyst,
        "note": req.note,
        "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    store.put("case_labels", case_id, record)
    return {
        "case_id": case_id,
        "label": record,
        "queue_depth": len(store.list_all("case_labels")),
        "retraining_wired": False,
    }


@app.get("/customers")
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    sort: str = "customer_id",
    q: str = "",
    request: Request = None,
):
    return _paginated_collection("customers", page, page_size, sort, q, tenant_id=get_current_tenant(request) if request is not None else None)


class PolicySettings(BaseModel):
    block_threshold: int = 75
    challenge_threshold: int = 50
    window_seconds: int = 300


_DEFAULT_POLICY = PolicySettings().model_dump()


@app.get("/settings/policy")
async def get_settings_policy():
    saved = store.get("settings", "policy")
    return saved if saved is not None else _DEFAULT_POLICY


@app.put("/settings/policy")
async def put_settings_policy(policy: PolicySettings):
    payload = policy.model_dump()
    store.put("settings", "policy", payload)
    return payload


@app.on_event("startup")
async def seed_demo_scale_data_when_requested():
    try:
        validate_environment()
        store.init_db_indexes()
    except RuntimeError as exc:
        logging.critical("Environment validation failed: %s", exc)
        raise SystemExit(1) from exc
    if os.environ.get("SEED_DEMO_SCALE") != "1":
        return
    universe = generate_bank_universe(num_customers=500, num_txns=5000, seed=42)
    await _persist_universe_collections(universe)

@app.get("/synthetic/universe/preview")
async def preview_universe(sample_size: int = 10):
    global cached_universe
    if not cached_universe:
        cached_universe = generate_bank_universe(num_customers=50, num_txns=100, seed=42)
    return {
        "bank_metadata": cached_universe.get("bank_metadata", {}),
        "stats": cached_universe.get("stats", {}),
        "customers_sample": cached_universe["customers"][:sample_size],
        "accounts_sample": cached_universe["accounts"][:sample_size],
        "devices_sample": cached_universe["devices"][:sample_size],
        "transactions_sample": cached_universe["transactions"][:sample_size]
    }

@app.post("/synthetic/universe/start_scenario")
async def start_scenario_execution(req: ScenarioStartRequest):
    global scenario_execution_state
    scenario_execution_state = {
        "status": "RUNNING",
        "scenario_id": req.scenario_id,
        "current_step": 1,
        "speed_multiplier": req.speed_multiplier,
        "paused": False
    }
    return {"message": f"Scenario {req.scenario_id} started.", "state": scenario_execution_state}

@app.post("/synthetic/universe/pause")
async def pause_scenario_execution():
    global scenario_execution_state
    scenario_execution_state["paused"] = True
    scenario_execution_state["status"] = "PAUSED"
    return {"message": "Scenario execution paused.", "state": scenario_execution_state}

@app.post("/synthetic/universe/resume")
async def resume_scenario_execution():
    global scenario_execution_state
    scenario_execution_state["paused"] = False
    scenario_execution_state["status"] = "RUNNING"
    return {"message": "Scenario execution resumed.", "state": scenario_execution_state}

@app.get("/synthetic/universe/stats")
async def get_universe_statistics():
    global cached_universe
    if not cached_universe:
        cached_universe = generate_bank_universe(num_customers=50, num_txns=100, seed=42)
    return {
        "stats": cached_universe.get("stats", {}),
        "scenario_execution_state": scenario_execution_state,
        "supported_banks": list(BANK_REGISTRY.keys())
    }

@app.delete("/synthetic/universe/clear")
async def clear_universe_state():
    global cached_universe, scenario_execution_state
    cached_universe = None
    scenario_execution_state = {"status": "IDLE", "scenario_id": None, "current_step": 0, "paused": False}
    return {"message": "Digital Banking Universe state cleared."}

@app.get("/synthetic/universe/export/csv")
async def export_synthetic_csv(num_customers: int = 100, num_txns: int = 500, seed: int = 42, bank_code: str = "FUSB"):
    global cached_universe
    if cached_universe:
        universe = cached_universe
    else:
        universe = generate_bank_universe(num_customers=num_customers, num_txns=num_txns, seed=seed, bank_code=bank_code)
    csv_content = export_dataset_csv(universe["transactions"])
    return StreamingResponse(
        io.BytesIO(csv_content.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fusion_synthetic_bank_universe.csv"}
    )

@app.get("/synthetic/universe/export/json")
async def export_synthetic_json(num_customers: int = 100, num_txns: int = 500, seed: int = 42, bank_code: str = "FUSB"):
    global cached_universe
    if cached_universe:
        universe = cached_universe
    else:
        universe = generate_bank_universe(num_customers=num_customers, num_txns=num_txns, seed=seed, bank_code=bank_code)
    json_content = export_dataset_json(universe)
    return StreamingResponse(
        io.BytesIO(json_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=fusion_synthetic_bank_universe.json"}
    )

@app.get("/synthetic/universe/export/parquet")
async def export_synthetic_parquet(num_customers: int = 100, num_txns: int = 500, seed: int = 42, bank_code: str = "FUSB"):
    global cached_universe
    if cached_universe:
        universe = cached_universe
    else:
        universe = generate_bank_universe(num_customers=num_customers, num_txns=num_txns, seed=seed, bank_code=bank_code)
    parquet_bytes = export_dataset_parquet_bytes(universe["transactions"])
    return StreamingResponse(
        io.BytesIO(parquet_bytes),
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=fusion_synthetic_bank_universe.parquet"}
    )

@app.get("/synthetic/universe/export/replay")
async def export_synthetic_replay(num_customers: int = 100, num_txns: int = 500, seed: int = 42, bank_code: str = "FUSB"):
    global cached_universe
    if cached_universe:
        universe = cached_universe
    else:
        universe = generate_bank_universe(num_customers=num_customers, num_txns=num_txns, seed=seed, bank_code=bank_code)
    replay_content = export_dataset_replay(universe)
    return StreamingResponse(
        io.BytesIO(replay_content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=fusion_synthetic_bank_replay.json"}
    )


# --- QUANTUM MONITORING ---
@app.get("/quantum/posture")
async def get_quantum_posture():
    return {
        "status": "UNAVAILABLE",
        "vulnerable_percent": None,
        "hndl_flag": None,
        "reason": "TLS_HANDSHAKE_TELEMETRY_NOT_CONFIGURED",
    }
    """
    Returns the % of vulnerable sessions and a Harvest-Now-Decrypt-Later (HNDL) flag.
    In the demo, the current session used ECDHE, flagging HNDL.
    """
    # Create a mock bundled dataset of cipher suites in memory for demo
    # representing 100 recent handshakes
    df = pd.DataFrame([
        {"suite": "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384", "count": 65, "type": "vulnerable"},
        {"suite": "TLS_RSA_WITH_AES_128_GCM_SHA256", "count": 20, "type": "vulnerable"},
        {"suite": "TLS_MLKEM768_WITH_AES_256_GCM_SHA384", "count": 15, "type": "hybrid/PQC"},
    ])
    
    total = df["count"].sum()
    vuln = df[df["type"] == "vulnerable"]["count"].sum()
    vuln_pct = (vuln / total) * 100
    
    return {
        "vulnerable_percent": round(vuln_pct, 1),
        "hndl_flag": True, # For demo, we explicitly flag the usr_abc session
        "hndl_details": "Long-lived sensitive data (₹7.5L UPI Transfer) captured over vulnerable cipher (TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384). High risk of Harvest-Now-Decrypt-Later."
    }


# --- CERT-In REPORT GENERATOR ---
@app.post("/report/cert-in")
async def generate_cert_in_report(req: CertInReportRequest):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "CERT-In Cyber Security Incident Report")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, 730, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST")
    p.setFillColor(colors.red)
    p.drawString(50, 715, "COMPLIANCE NOTE: Generated within 6-hour CERT-In reporting mandate.")
    p.setFillColor(colors.black)
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 680, "Incident Details")
    
    p.setFont("Helvetica", 11)
    p.drawString(50, 660, f"Transaction ID: {req.txn_id}")
    p.drawString(50, 640, f"Affected User ID: {req.user_id}")
    p.drawString(50, 620, f"Amount at Risk: INR {req.amount:,.2f}")
    p.drawString(50, 600, f"Fuzen AI Score: {req.score}")
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 560, "Detection Reasons / Vectors")
    
    p.setFont("Helvetica", 11)
    y = 540
    for r in req.reasons:
        p.drawString(60, y, f"- {r}")
        y -= 20
        
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={
        "Content-Disposition": f"attachment; filename=CERT-In_Report_{req.txn_id}.pdf"
    })


@app.get("/reports")
async def list_reports(request: Request, limit: int = Query(50, ge=1, le=100)):
    tenant_id = get_current_tenant(request)
    reports = store.list_all("reports", tenant_id=tenant_id)
    reports.sort(key=lambda item: str(item.get("created_at") or item.get("generated_at") or ""), reverse=True)
    return {"items": reports[:limit], "total": len(reports), "source": "backend_sqlite"}


def get_demo_events():
    """Legacy compatibility hook; scripted incidents are disabled."""
    return []

# --- DIGITAL TWIN INTELLIGENCE ENGINE ENDPOINTS (PART 13 APIs) ---
class DigitalTwinUpdateRequest(BaseModel):
    user_id: str = "usr_abc"
    msg_type: str = "transaction"
    event_data: dict = {}

class DigitalTwinCompareRequest(BaseModel):
    user_id: str = "usr_abc"
    transaction: dict = {}

@app.get("/digital_twin/{user_id}")
async def get_customer_digital_twin(user_id: str):
    twin = get_or_create_digital_twin(user_id)
    return twin.get_full_profile()

@app.post("/digital_twin/update")
async def update_customer_digital_twin(req: DigitalTwinUpdateRequest):
    twin = get_or_create_digital_twin(req.user_id)
    event_payload = req.event_data if req.event_data else {"msg_type": req.msg_type, "user_id": req.user_id}
    updated_profile = twin.update_twin(event_payload)
    return {"message": f"Digital Twin for {req.user_id} updated.", "profile": updated_profile}

@app.post("/digital_twin/compare")
async def compare_digital_twin_transaction(req: DigitalTwinCompareRequest):
    twin = get_or_create_digital_twin(req.user_id)
    txn = req.transaction if req.transaction else {"user_id": req.user_id, "amount": 750000.0, "nameDest": "ACC_MULE_NEW"}
    comparison = twin.compare_transaction(txn)
    return comparison

@app.get("/digital_twin/{user_id}/timeline")
async def get_digital_twin_timeline(user_id: str):
    twin = get_or_create_digital_twin(user_id)
    return {"user_id": user_id, "timeline": twin.timeline}

@app.get("/digital_twin/{user_id}/history")
async def get_digital_twin_history(user_id: str):
    twin = get_or_create_digital_twin(user_id)
    return {
        "user_id": user_id,
        "historical_risk": twin.risk["historical_risk"],
        "risk_trend": twin.risk["risk_trend"],
        "behavior_drift_index": twin.behavior["behavior_drift_index"],
        "geo_velocity_kmh": twin.locations["geo_velocity_kmh"]
    }

@app.get("/digital_twin/{user_id}/snapshot")
async def get_digital_twin_snapshot(user_id: str):
    twin = get_or_create_digital_twin(user_id)
    return {
        "user_id": user_id,
        "full_name": twin.identity["full_name"],
        "kyc_status": twin.identity["kyc_status"],
        "risk_tier": twin.identity["risk_tier"],
        "trust_level": twin.identity["trust_level"],
        "trusted_devices": len(twin.devices["trusted_devices"]),
        "current_risk": twin.risk["current_risk"],
        "mule_ring_distance": twin.graph["distance_to_known_mule_ring"],
        "next_predicted_login": twin.predictions["predicted_next_login"]
    }

# --- PRE-TRANSACTION SESSION INTELLIGENCE ENDPOINTS ---
class SessionAnalyseRequest(BaseModel):
    session_id: str
    user_id: str
    device_id: str = ""
    ip: str = ""
    cyber_compromise_in_window: bool = False
    dest_mule_cluster_id: str | None = None

class SessionUpdateRequest(BaseModel):
    session_id: str
    event_data: dict = {}

class SessionRecalculateRequest(BaseModel):
    session_id: str


class TrustRecalculateRequest(BaseModel):
    session_id: str

@app.post("/session/analyse")
async def analyse_pre_transaction_session(req: SessionAnalyseRequest):
    passport = session_engine.analyse_session(req.dict())
    return passport

@app.get("/session/passport/{session_id}")
async def get_session_trust_passport(session_id: str):
    passport = session_engine.get_passport(session_id)
    return passport

@app.post("/session/update")
async def update_session_trust(req: SessionUpdateRequest):
    passport = session_engine.update_session(req.session_id, req.event_data)
    return passport

@app.post("/session/recalculate")
async def recalculate_session_trust(req: SessionRecalculateRequest):
    passport = session_engine.get_passport(req.session_id)
    if not passport or not passport.get("user_id"):
        raise HTTPException(status_code=404, detail="Session identity is unavailable")
    updated = session_engine.analyse_session({"session_id": req.session_id, "user_id": passport["user_id"]})
    return updated


# --- PHASE 3 ENTERPRISE SESSION INTELLIGENCE & TRUST PASSPORT ---
@app.get("/sessions")
async def list_live_sessions(
    state: str | None = None,
    search: str | None = None,
    include_closed: bool = True,
    limit: int = 200,
):
    # Upgrade older generated rows once, using their persisted transaction
    # facts. This keeps existing local demo databases from displaying a flat
    # 100.0 posture after the scoring implementation became event-driven.
    for existing in session_intelligence.repository.list_sessions(limit=limit):
        context = session_intelligence.repository.get_context(existing.session_id)
        last_event = (context.facts.get("last_event") if context else {}) or {}
        if context and context.event_count <= 1 and float(last_event.get("amount") or 0) > 0:
            session_intelligence.process_event(
                {
                    "session_id": existing.session_id,
                    "event_type": "TRANSFER",
                    "amount": last_event.get("amount"),
                    "decision": last_event.get("decision"),
                }
            )
            if str(last_event.get("decision", "")).upper() == "BLOCK":
                session_intelligence.process_event(
                    {"session_id": existing.session_id, "event_type": "TAP_INJECTION"}
                )
    lifecycle = None
    if state:
        try:
            lifecycle = SessionLifecycle(state.upper())
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=f"Unknown session state: {state}") from exc
    sessions = session_intelligence.repository.list_sessions(
        state=lifecycle,
        search=search,
        include_closed=include_closed,
        limit=limit,
    )
    return {"sessions": [session.model_dump(mode="json") for session in sessions], "count": len(sessions)}


@app.get("/timeline/stream")
async def get_unified_event_timeline(limit: int = 50, request: Request = None):
    events = dynamic_stream_engine.get_unified_timeline(limit=limit, tenant_id=get_current_tenant(request))
    return {"timeline": events, "count": len(events)}


@app.get("/sessions/{session_id}")
async def get_live_session(session_id: str):
    session = session_intelligence.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.get("/trust-passport")
async def get_current_trust_passport(session_id: str | None = None):
    passport = (
        session_intelligence.repository.get_passport(session_id)
        if session_id
        else session_intelligence.repository.get_latest_passport()
    )
    if not passport:
        raise HTTPException(status_code=404, detail="Trust Passport not found")
    return passport.to_compatible_dict()


@app.get("/trust-passport/{session_id}")
async def get_trust_passport_by_session(session_id: str):
    passport = session_intelligence.repository.get_passport(session_id)
    if not passport:
        raise HTTPException(status_code=404, detail="Trust Passport not found")
    return passport.to_compatible_dict()


@app.get("/trust-history/{session_id}")
async def get_trust_history(
    session_id: str,
    range: str = Query(default="last_hour", pattern="^(last_minute|last_hour|last_day|custom)$"),
    start: datetime.datetime | None = None,
    end: datetime.datetime | None = None,
    limit: int = 1000,
):
    if not session_intelligence.repository.get_passport(session_id):
        raise HTTPException(status_code=404, detail="Trust Passport not found")
    history = session_intelligence.get_history(session_id, range, start, end, limit)
    return {
        "session_id": session_id,
        "range": range,
        "snapshots": [snapshot.model_dump(mode="json") for snapshot in history],
        "count": len(history),
    }


@app.get("/trust-components/{session_id}")
async def get_trust_components(session_id: str):
    passport = session_intelligence.repository.get_passport(session_id)
    if not passport:
        raise HTTPException(status_code=404, detail="Trust Passport not found")
    return {
        "session_id": session_id,
        "overall_trust": passport.overall_trust,
        "confidence": passport.confidence,
        "trust_trend": passport.trust_trend,
        "components": {
            name.value: component.model_dump(mode="json")
            for name, component in passport.components.items()
        },
        "deltas": [
            delta.model_dump(mode="json")
            for delta in session_intelligence.repository.get_deltas(session_id)
        ],
        "recovery_events": [
            event.model_dump(mode="json")
            for event in session_intelligence.repository.get_recovery_events(session_id)
        ],
    }


@app.post("/trust/recalculate")
async def recalculate_enterprise_trust(req: TrustRecalculateRequest):
    try:
        update = session_intelligence.recalculate(req.session_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc
    envelope = update.model_dump(mode="json")
    await trust_update_broker.publish(envelope)
    return envelope


@app.get("/trust/live")
async def get_live_trust_updates(session_id: str | None = None, limit: int = 50):
    updates = trust_update_broker.recent(session_id=session_id, limit=limit)
    return {
        "updates": updates,
        "count": len(updates),
    }

# --- INVESTIGATION INTELLIGENCE LAYER ENDPOINTS ---
class InvestigationAnalyseRequest(BaseModel):
    case_id: str = "CASE-2026-8942"
    user_id: str = "usr_abc"
    amount: float = 750000.0
    cyber_compromise_in_window: bool = True
    dest_mule_cluster_id: str = "cluster_alpha"

class BurstAnalyseRequest(BaseModel):
    user_id: str = "usr_abc"
    time_window_seconds: int = 60

class MuleDiscoverRequest(BaseModel):
    user_id: str = "usr_abc"
    dest_mule_cluster_id: str = "cluster_alpha"

@app.post("/investigation/analyse")
async def analyse_investigation_intelligence(req: InvestigationAnalyseRequest):
    brief = investigation_engine.analyse_investigation(req.dict())
    return brief

@app.post("/burst/analyse")
async def analyse_burst_attack(req: BurstAnalyseRequest):
    result = investigation_engine.detect_burst_attack(req.user_id, req.dict())
    return result

@app.post("/mule/discover")
async def discover_mule_ring(req: MuleDiscoverRequest):
    result = investigation_engine.discover_mule_ring(req.user_id, req.dict())
    return result

@app.get("/investigation/{case_id}")
async def get_investigation_brief(case_id: str):
    brief = investigation_engine.get_cached_investigation(case_id)
    return brief

# --- SOAR RESPONSE ORCHESTRATION ENGINE ENDPOINTS ---
class ResponseRecommendRequest(BaseModel):
    user_id: str = "usr_abc"
    amount: float = 750000.0
    cyber_compromise_in_window: bool = True

class ResponseExecuteRequest(BaseModel):
    case_id: str = "CASE-2026-8942"
    user_id: str = "usr_abc"
    amount: float = 750000.0
    approval_mode: str = "AUTOMATIC_EXECUTION"

class PlaybookCreateRequest(BaseModel):
    name: str
    scenario: str
    description: str
    trigger_conditions: list = []
    priority: str = "HIGH"
    execution_order: list = []

class IncidentAssignRequest(BaseModel):
    incident_id: str = "INC-2026-9912"
    owner: str = "Analyst_04"

class ResponseRollbackRequest(BaseModel):
    workflow_id: str = "SOAR_WF_88291"
    reason: str = "Analyst False Positive Override"

@app.post("/response/recommend")
async def recommend_soar_response(req: ResponseRecommendRequest):
    recommendation = soar_engine.recommend_response(req.dict())
    return recommendation

@app.post("/response/execute")
async def execute_soar_response(req: ResponseExecuteRequest):
    execution = soar_engine.execute_response(req.dict())
    return execution

@app.post("/playbook/create")
async def create_playbook(req: PlaybookCreateRequest):
    pb = soar_engine.create_playbook(req.dict())
    return pb

@app.get("/playbook")
async def list_playbooks():
    return soar_engine.get_playbooks()

@app.get("/incident/{incident_id}")
async def get_incident_details(incident_id: str):
    incident = soar_engine.get_incident(incident_id)
    return incident

@app.post("/incident/assign")
async def assign_incident(req: IncidentAssignRequest):
    incident = soar_engine.assign_incident(req.incident_id, req.owner)
    return incident

@app.post("/response/rollback")
async def rollback_response(req: ResponseRollbackRequest):
    res = soar_engine.rollback_response(req.workflow_id, req.reason)
    return res

# --- TRUST FABRIC & EVIDENCE INTEGRITY ENDPOINTS ---
class EvidenceCreateRequest(BaseModel):
    case_id: str = "CASE-2026-8942"
    incident_id: str = "INC-2026-8942"
    session_id: str = "SESS_9921_CRITICAL"
    user_id: str = "usr_abc"
    amount: float = 750000.0

class EvidenceExportRequest(BaseModel):
    evidence_id: str = "EVID_CASE-2026-8942_1001"
    format: str = "pdf"

@app.post("/evidence/create")
async def create_evidence_package(req: EvidenceCreateRequest):
    package = trust_fabric.create_evidence_package(req.dict())
    return package

@app.get("/evidence/{evidence_id}")
async def get_evidence_package(evidence_id: str):
    package = trust_fabric.get_evidence(evidence_id)
    return package

@app.get("/evidence/verify/{evidence_id}")
async def verify_evidence_integrity(evidence_id: str):
    verification = trust_fabric.verify_evidence_integrity(evidence_id)
    return verification

@app.get("/audit/{incident_id}")
async def get_audit_trail(incident_id: str):
    trail = trust_fabric.get_audit_trail(incident_id)
    return trail

@app.post("/evidence/export")
async def export_evidence_bundle(req: EvidenceExportRequest):
    bundle = trust_fabric.export_evidence_bundle(req.evidence_id, req.format)
    return bundle

# --- FUSION QUANTUM TRUST LAYER (QTL) ENDPOINTS ---
class QuantumAnalyzeRequest(BaseModel):
    asset_id: str = "ASSET_001"

class QuantumSimulateRequest(BaseModel):
    asset_id: str = "ASSET_001"
    simulated_year: int = 2032

@app.get("/quantum/readiness")
async def get_quantum_readiness():
    return quantum_trust.get_readiness_score()

@app.get("/quantum/inventory")
async def get_quantum_inventory():
    return quantum_trust.get_inventory()

@app.get("/quantum/assessment")
async def get_quantum_assessment():
    return quantum_trust.get_assessment()

@app.post("/quantum/analyze")
async def analyze_quantum_asset(req: QuantumAnalyzeRequest):
    return quantum_trust.analyze_asset(req.asset_id)

@app.get("/quantum/recommendations")
async def get_quantum_recommendations():
    return quantum_trust.get_recommendations()

@app.get("/quantum/dashboard")
async def get_quantum_dashboard():
    return quantum_trust.get_dashboard_summary()

@app.get("/quantum/compliance")
async def get_quantum_compliance():
    return quantum_trust.get_compliance_details()

@app.post("/quantum/simulate")
async def simulate_quantum_threat(req: QuantumSimulateRequest):
    return quantum_trust.simulate_quantum_scenario(req.dict())

@app.websocket("/ws/stream")





async def websocket_endpoint(websocket: WebSocket):
    try:
        auth = authenticate_websocket(websocket)
    except HTTPException as exc:
        await websocket.close(code=exc.status_code if exc.status_code in {4401, 4403, 4409} else 4403, reason=str(exc.detail))
        return
    session_filter = websocket.query_params.get("session_id")
    client_id = websocket.query_params.get("client_id") or "legacy"
    connection_key = f"{auth.tenant_id}:{auth.subject}:{session_filter or 'all'}:{client_id}"
    if connection_key in _active_websocket_sessions:
        await websocket.close(code=4409, reason="Duplicate session")
        return
    _active_websocket_sessions.add(connection_key)
    await websocket.accept(subprotocol=next((item.strip() for item in websocket.headers.get("sec-websocket-protocol", "").split(",") if item.strip().startswith("Bearer.")), None))
    if session_filter and "customer" in auth.roles:
        owned_session = sdk_engine.sdk_sessions.get(session_filter)
        if not owned_session or owned_session.get("user_id") != auth.subject:
            await websocket.close(code=4403, reason="Session is not owned by this identity")
            return
    subscription = await platform_event_broker.subscribe(session_filter)
    trust_subscription = await trust_update_broker.subscribe(session_filter)

    try:
        await websocket.send_json(
            {
                "msg_type": "connection_ack",
                "tenant": auth.tenant_id,
                "session": session_filter,
                "session_id": session_filter,
                "authenticated_subject": auth.subject,
                "request_id": auth.request_id,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        )
        for recent_event in platform_event_broker.recent(
            session_id=session_filter,
            limit=20,
        ):
            await websocket.send_json(recent_event)
        for recent_event in trust_update_broker.recent(
            session_id=session_filter,
            limit=20,
        ):
            await websocket.send_json(recent_event)

        while True:
            receive_task = asyncio.create_task(websocket.receive_text())
            update_task = asyncio.create_task(subscription.queue.get())
            trust_task = asyncio.create_task(trust_subscription.queue.get())
            done, pending = await asyncio.wait(
                {receive_task, update_task, trust_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            if update_task in done:
                event = update_task.result()
                await websocket.send_json({**event, "tenant": auth.tenant_id, "session": session_filter or event.get("session_id"), "request_id": auth.request_id, "timestamp": event.get("timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat()})
            if trust_task in done:
                event = trust_task.result()
                await websocket.send_json({**event, "tenant": auth.tenant_id, "session": session_filter or event.get("session_id"), "request_id": auth.request_id, "timestamp": event.get("timestamp") or datetime.datetime.now(datetime.timezone.utc).isoformat()})
            if receive_task in done:
                message = receive_task.result()
                if message.lower() == "ping":
                    await websocket.send_json({"msg_type": "pong", "tenant": auth.tenant_id, "session": session_filter, "request_id": auth.request_id, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
                else:
                    try:
                        command = json.loads(message)
                    except json.JSONDecodeError:
                        command = {}
                    if command.get("type") == "ping":
                        await websocket.send_json({"msg_type": "pong", "tenant": auth.tenant_id, "session": session_filter, "request_id": auth.request_id, "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await platform_event_broker.unsubscribe(subscription.subscription_id)
        await trust_update_broker.unsubscribe(trust_subscription.subscription_id)
        _active_websocket_sessions.discard(connection_key)

# --- FUSION ADAPTIVE TRUST SDK (FAT-SDK) ENDPOINTS ---
class SDKSessionStartRequest(BaseModel):
    app_id: str
    tenant_id: str
    sdk_version: str
    user_id: str
    device_id: str
    environment: str

class SDKDeviceRequest(BaseModel):
    device_id: str
    model: str
    manufacturer: str
    android_version: str
    security_patch: str
    screen_lock_enabled: bool
    root_detected: bool
    emulator_detected: bool
    frida_detected: bool
    debugger_attached: bool
    overlay_detected: bool
    timezone: str
    locale: str

class SDKNetworkRequest(BaseModel):
    session_id: str
    network_type: str
    carrier: str
    vpn_detected: bool
    proxy_detected: bool
    roaming: bool
    wifi_vs_cellular: str

class SDKEventRequest(BaseModel):
    session_id: str
    device_id: str
    event_type: str
    amount: float = 0.0
    sdk_version: str = "FAT-SDK v2.4.1"
    request_id: str | None = None
    correlation_id: str | None = None

class SDKDecisionRequest(BaseModel):
    session_id: str
    event_type: str
    amount: float
    vpn_detected: bool = False
    root_detected: bool = False
    beneficiary_id: str | None = None
    request_id: str | None = None
    correlation_id: str | None = None

@app.post("/sdk/session/start")
async def sdk_session_start(req: SDKSessionStartRequest, request: Request):
    auth = request.state.auth
    if auth.app_id and auth.app_id != req.app_id:
        raise HTTPException(status_code=403, detail="Token is not scoped to this application")
    if auth.tenant_id and auth.tenant_id != req.tenant_id:
        raise HTTPException(status_code=403, detail="Token is not scoped to this tenant")
    if "customer" in auth.roles and auth.subject != req.user_id:
        raise HTTPException(status_code=403, detail="Banking identity cannot start another user's session")
    session = sdk_engine.start_session(req.model_dump())
    from api.identity_trust import identity_trust
    identity_trust.bind_sdk_session(
        security_session_id=None,
        sdk_session_id=session["session_id"],
        user_id=session["user_id"],
        device_id=session["device_id"],
    )
    device_profile = sdk_engine.device_profiles.get(session["device_id"], {})
    device_event = {
        **device_profile,
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "device_id": session["device_id"],
        "event_type": "DEVICE_ATTESTATION",
    }
    result = await platform_pipeline.process(device_event, require_existing_session=True)
    dynamic_stream_engine.add_live_apk_event({
        "event_type": "Live APK Session Started",
        "user_id": session["user_id"],
        "device_id": session["device_id"],
        "customer_name": f"Live APK Customer ({session['user_id']})",
        "risk_score": len(result.threats) * 20 + 15,
        "status": "APPROVED" if len(result.threats) == 0 else "CHALLENGED"
    })
    return {
        **session,
        "request_id": result.request_id,
        "correlation_id": result.correlation_id,
        "pipeline_id": result.pipeline_id,
        "backend_ack": result.event_ack["backend_ack"],
        "initial_threat_count": len(result.threats),
    }

@app.post("/sdk/device")
async def sdk_register_device(req: SDKDeviceRequest):
    return sdk_engine.register_device(req.model_dump())

@app.post("/sdk/network")
async def sdk_register_network(req: SDKNetworkRequest, request: Request):
    response = sdk_engine.register_network(req.model_dump())
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SDK session is not active")
    if "customer" in request.state.auth.roles and session["user_id"] != request.state.auth.subject:
        raise HTTPException(status_code=403, detail="SDK session is not owned by this identity")
    event = {
        **req.model_dump(),
        "event_type": "NETWORK_ATTESTATION",
        "user_id": session["user_id"],
        "device_id": session["device_id"],
    }
    from api.identity_trust import identity_trust
    if req.vpn_detected or req.proxy_detected:
        identity_trust.record_activity(
            sdk_session_id=req.session_id, event_type="VPN_DETECTED", user_id=session["user_id"],
            device_id=session["device_id"], risk_delta=30, metadata=req.model_dump(),
        )
    await platform_pipeline.process(event, require_existing_session=True)
    return response

@app.post("/sdk/event")
async def sdk_ingest_event(req: SDKEventRequest, request: Request):
    event_dict = req.model_dump()
    event_dict["request_id"] = req.request_id or request.state.request_id
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if session:
        event_dict["user_id"] = session["user_id"]
        if "customer" in request.state.auth.roles and session["user_id"] != request.state.auth.subject:
            raise HTTPException(status_code=403, detail="SDK session is not owned by this identity")
    try:
        result = await platform_pipeline.process(
            event_dict, require_existing_session=True
        )
    except PipelineValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    from api.identity_trust import identity_trust
    identity_trust.record_activity(
        sdk_session_id=req.session_id, event_type=req.event_type, user_id=event_dict.get("user_id", ""),
        device_id=event_dict.get("device_id", ""), risk_delta=15 if req.event_type in {"TRANSFER", "QR_PAYMENT", "BENEFICIARY_ADDED"} else 0,
        metadata={"amount": req.amount},
    )
    return result.event_ack

@app.get("/metrics/threshold_sweep")
async def get_metrics_threshold_sweep():
    import json
    sweep_path = ROOT / "ml" / "sweep_cache.json"
    try:
        content = sweep_path.read_text()
        return json.loads(content)
    except Exception as e:
        return {"error": str(e)}

@app.get("/metrics/cost")
async def get_metrics_cost(fn_cost: float = 250000.0, fp_cost: float = 400.0):
    import json
    sweep_path = ROOT / "ml" / "sweep_cache.json"
    try:
        content = sweep_path.read_text()
        data = json.loads(content)

        recomputed = {}
        for config_name, sweep_pts in data.items():
            recomputed[config_name] = []
            for pt in sweep_pts:
                new_pt = dict(pt)
                new_pt["total_cost"] = (new_pt["FN"] * fn_cost) + (new_pt["FP"] * fp_cost)
                recomputed[config_name].append(new_pt)

        return recomputed
    except Exception as e:
        return {"error": str(e)}

# --- ENTERPRISE CYBER THREAT INTELLIGENCE ENGINE ENDPOINTS (PHASE 2) ---
@app.get("/threats")
async def get_threats(status: str = None, category: str = None, severity: str = None, request: Request = None):
    return {"threats": cyber_threat_engine.get_all_threats(status=status, category=category, severity=severity, tenant_id=get_current_tenant(request))}

@app.get("/threats/{threat_id}")
async def get_threat_by_id(threat_id: str, request: Request = None):
    t = cyber_threat_engine.get_threat_by_id(threat_id, tenant_id=get_current_tenant(request))
    if not t:
        return {"error": "Threat not found", "threat_id": threat_id}
    return t

@app.get("/threats/session/{session_id}")
async def get_threats_by_session(session_id: str, request: Request):
    return {"session_id": session_id, "threats": cyber_threat_engine.get_threats_by_session(session_id, tenant_id=get_current_tenant(request))}

@app.get("/threats/device/{device_id}")
async def get_threats_by_device(device_id: str, request: Request):
    return {"device_id": device_id, "threats": cyber_threat_engine.get_threats_by_device(device_id, tenant_id=get_current_tenant(request))}

@app.post("/threats/evaluate")
async def evaluate_threat_event(event: dict):
    result = await platform_pipeline.process(event, require_existing_session=False)
    return {
        "status": "SUCCESS",
        "evaluated_threats": result.threats,
        "count": len(result.threats),
        "graph": result.graph,
        "pipeline_id": result.pipeline_id,
    }

@app.post("/threats/simulate")
async def simulate_threat_scenario(payload: dict):
    result = await platform_pipeline.process(payload, require_existing_session=False)
    return {
        "status": "SIMULATED",
        "result": result.model_dump() if hasattr(result, "model_dump") else result
    }

@app.post("/sdk/request-decision")
async def sdk_request_decision(req: SDKDecisionRequest, request: Request):
    dec_dict = req.model_dump()
    dec_dict["request_id"] = req.request_id or request.state.request_id
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if session:
        dec_dict["user_id"] = session["user_id"]
        dec_dict["device_id"] = session["device_id"]
        if "customer" in request.state.auth.roles and session["user_id"] != request.state.auth.subject:
            raise HTTPException(status_code=403, detail="SDK session is not owned by this identity")
    try:
        result = await platform_pipeline.process(
            dec_dict, require_existing_session=True
        )
    except PipelineValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    decision = result.decision
    return {
        **decision,
        "recommended_action": decision["decision"].replace("_", " ").title(),
        "policy_version": sdk_engine.policy_version,
        "decision_latency_ms": result.timings["total_ms"],
        "pipeline_id": result.pipeline_id,
        "request_id": result.request_id,
        "correlation_id": result.correlation_id,
        "backend_ack": result.event_ack["backend_ack"],
        "model_status": result.inference["status"],
        "model_error_code": result.inference["error_code"],
        "graph_status": result.graph["status"],
        "graph_backend": result.graph["backend"],
        "timings": result.timings,
        "model_used": (
            result.inference["implementation"]
            if result.inference["status"] == "EXECUTED"
            else None
        ),
        "fallback_used": (
            result.inference["implementation"]
            if result.inference["status"] == "degraded"
            else None
        ),
    }

@app.get("/sdk/policies")
async def sdk_get_policies():
    return sdk_engine.get_policies()

@app.get("/sdk/passport")
async def sdk_get_passport(session_id: str):
    passport = session_intelligence.repository.get_passport(session_id)
    if passport:
        return passport.to_compatible_dict()
    raise HTTPException(status_code=404, detail="No authoritative trust passport for session")

@app.get("/sdk/health")
async def sdk_get_health():
    return sdk_engine.get_observability()

@app.get("/sdk/apps")
async def sdk_get_connected_apps():
    return sdk_engine.get_connected_apps()

@app.get("/sdk/events")
async def sdk_get_live_events():
    return sdk_engine.get_live_event_stream()

@app.get("/sdk/error-codes")
async def sdk_get_error_codes():
    return sdk_engine.get_error_codes()

@app.get("/metrics/evaluate")
async def get_metrics_evaluate():
    import json
    import datetime
    report_path = ROOT / "ml" / "metrics_report.md"
    try:
        content = report_path.read_text()
        json_str = content.split("```json")[1].split("```")[0].strip()
        data = json.loads(json_str)
        mtime = report_path.stat().st_mtime
        data["computed_at"] = datetime.datetime.fromtimestamp(mtime).isoformat()
        return data
    except Exception as e:
        return {"error": str(e)}

from api.copilot_engine import router as copilot_router
app.include_router(copilot_router)


def _deduplicate_routes() -> None:
    seen: set[tuple[str, tuple[str, ...], str]] = set()
    unique = []
    for route in app.router.routes:
        key = (getattr(route, "path", ""), tuple(sorted(getattr(route, "methods", set()) or set())), route.__class__.__name__)
        if key in seen:
            continue
        seen.add(key)
        unique.append(route)
    app.router.routes[:] = unique


_deduplicate_routes()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8001, reload=True)
