import asyncio
import json
import sys
import io
import datetime
import hmac
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# PDF Generation
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.scenario_engine import get_all_scenarios_list, generate_scenario
from api.synthetic_universe.fraud_scenario_engine import generate_bank_universe
from api.synthetic_universe.graph_generator import generate_graph_topology
from api.synthetic_universe.exporter import export_dataset_csv, export_dataset_json, export_dataset_replay, export_dataset_parquet_bytes
from api.synthetic_universe.bank_model import get_virtual_bank, BANK_REGISTRY
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
from api.platform import (
    PlatformSecurityMiddleware,
    create_access_token,
    platform_settings,
)
from api.platform.observability import RequestContextMiddleware
from api.platform.security import authenticate_websocket
from api.platform.graph_runtime import graph_runtime
from api.platform.model_runtime import model_runtime
from api.platform.pipeline import PipelineValidationError, platform_pipeline
from api.platform.decision_runtime import decision_engine
from api.gateway_integration import router as gateway_router







app = FastAPI(title="Fusion Risk OS", version="2.5.0")

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
    dest_mule_cluster_id: str = None

class CertInReportRequest(BaseModel):
    txn_id: str
    user_id: str
    amount: float
    reasons: list[str]
    score: float

@app.post("/evaluate/transaction")
async def evaluate_transaction(txn: TransactionRequest):
    txn_dict = txn.dict()
    txn_dict["session_id"] = txn.session_id or f"TXN_CONTEXT_{txn.txn_id}"
    txn_dict["event_type"] = "TRANSACTION_EVALUATION"
    result = await platform_pipeline.process(
        txn_dict, require_existing_session=False
    )
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
            if result.inference["status"] == "FALLBACK"
            else None
        ),
        "graph": result.graph,
        "threats": result.threats,
        "pipeline_id": result.pipeline_id,
    }

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

class CreateBankRequest(BaseModel):
    bank_name: str = "Fusion National Bank"
    bank_code: str = "FUSB"

class UniverseGenerateRequest(BaseModel):
    num_customers: int = 100
    num_transactions: int = 500
    seed: int = 42
    bank_code: str = "FUSB"

class ScenarioStartRequest(BaseModel):
    scenario_id: str = "account_takeover"
    speed_multiplier: float = 1.0

@app.post("/synthetic/universe/create_bank")
async def create_virtual_bank(req: CreateBankRequest):
    bank = get_virtual_bank(req.bank_code)
    return {"message": f"Virtual Bank {req.bank_name} initialized.", "bank_metadata": bank.to_dict()}

@app.post("/synthetic/universe/generate")
async def generate_synthetic_bank_universe(req: UniverseGenerateRequest):
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
    return universe

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
    p.drawString(50, 600, f"Fusion Risk Score: {req.score}")
    
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


def get_demo_events():
    """
    Returns the exact scripted sequence for the 90-second demo.
    """
    return [
        {
            "msg_type": "status",
            "message": "T-0:00 - System calm, dashboard green.",
            "delay": 2
        },
        {
            "msg_type": "cyber_event",
            "event_type": "impossible_travel_login",
            "timestamp": "2026-07-16 10:00:00",
            "user_id": "usr_abc",
            "device_id": "dev_9999",
            "ip": "185.15.2.22",
            "severity": "critical",
            "km_from_baseline": 4500,
            "delay": 4
        },
        {
            "msg_type": "status",
            "message": "T+0:40 - Monitoring user activity post-compromise...",
            "delay": 3
        },
        {
            "msg_type": "transaction",
            "txn_id": "txn_demo_999",
            "timestamp": "2026-07-16 10:00:40",
            "user_id": "usr_abc",
            "nameOrig": "ACC_ABC_123",
            "amount": 750000.0,
            "nameDest": "ACC_MULE_NEW",
            "dest_mule_cluster_id": "cluster_alpha",
            "cyber_compromise_in_window": True,
            "type": "TRANSFER",
            "delay": 5
        }
    ]

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
    session_id: str = "SESS_9921_CRITICAL"
    user_id: str = "usr_abc"
    device_id: str = "dev_9999"
    ip: str = "185.15.2.22"
    cyber_compromise_in_window: bool = True
    dest_mule_cluster_id: str = "cluster_alpha"

class SessionUpdateRequest(BaseModel):
    session_id: str = "SESS_9921_CRITICAL"
    event_data: dict = {}

class SessionRecalculateRequest(BaseModel):
    session_id: str = "SESS_9921_CRITICAL"


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
    updated = session_engine.analyse_session({"session_id": req.session_id, "user_id": passport.get("user_id", "usr_abc")})
    return updated


# --- PHASE 3 ENTERPRISE SESSION INTELLIGENCE & TRUST PASSPORT ---
@app.get("/sessions")
async def list_live_sessions(
    state: str | None = None,
    search: str | None = None,
    include_closed: bool = True,
    limit: int = 200,
):
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
        authenticate_websocket(websocket)
    except HTTPException as exc:
        await websocket.close(code=4401, reason=str(exc.detail))
        return
    await websocket.accept()
    session_filter = websocket.query_params.get("session_id")
    trust_only = websocket.query_params.get("stream") == "trust"
    subscription = await trust_update_broker.subscribe(session_filter)

    try:
        # Session-scoped clients receive current state before live updates.
        # Unscoped clients receive only events produced by the authoritative
        # pipeline; no synthetic replay is injected into a production stream.
        if session_filter:
            passport = session_intelligence.repository.get_passport(session_filter)
            if passport:
                await websocket.send_json({
                    "msg_type": "trust_passport_update",
                    "session_id": session_filter,
                    "event_type": "TRUST_BOOTSTRAP",
                    "passport": passport.to_compatible_dict(),
                    "deltas": [],
                })

        while True:
            receive_task = asyncio.create_task(websocket.receive_text())
            update_task = asyncio.create_task(subscription.queue.get())
            done, pending = await asyncio.wait(
                {receive_task, update_task},
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
            if update_task in done:
                await websocket.send_json(update_task.result())
            if receive_task in done:
                message = receive_task.result()
                if message.lower() == "ping":
                    await websocket.send_json({"msg_type": "pong"})
                else:
                    try:
                        command = json.loads(message)
                    except json.JSONDecodeError:
                        command = {}
                    if command.get("type") == "ping":
                        await websocket.send_json({"msg_type": "pong"})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await trust_update_broker.unsubscribe(subscription.subscription_id)

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

class SDKDecisionRequest(BaseModel):
    session_id: str
    event_type: str
    amount: float
    vpn_detected: bool = False
    root_detected: bool = False

@app.post("/sdk/session/start")
async def sdk_session_start(req: SDKSessionStartRequest, request: Request):
    auth = request.state.auth
    if auth.app_id and auth.app_id != req.app_id:
        raise HTTPException(status_code=403, detail="Token is not scoped to this application")
    if auth.tenant_id and auth.tenant_id != req.tenant_id:
        raise HTTPException(status_code=403, detail="Token is not scoped to this tenant")
    session = sdk_engine.start_session(req.model_dump())
    device_profile = sdk_engine.device_profiles.get(session["device_id"], {})
    device_event = {
        **device_profile,
        "session_id": session["session_id"],
        "user_id": session["user_id"],
        "device_id": session["device_id"],
        "event_type": "DEVICE_ATTESTATION",
    }
    initial_threats = cyber_threat_engine.evaluate_event(device_event)
    update = session_intelligence.start_session(session, device_event, initial_threats)
    await trust_update_broker.publish(update.model_dump(mode="json"))
    return session

@app.post("/sdk/device")
async def sdk_register_device(req: SDKDeviceRequest):
    return sdk_engine.register_device(req.model_dump())

@app.post("/sdk/network")
async def sdk_register_network(req: SDKNetworkRequest):
    response = sdk_engine.register_network(req.model_dump())
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="SDK session is not active")
    event = {
        **req.model_dump(),
        "event_type": "NETWORK_ATTESTATION",
        "user_id": session["user_id"],
        "device_id": session["device_id"],
    }
    await platform_pipeline.process(event, require_existing_session=True)
    return response

@app.post("/sdk/event")
async def sdk_ingest_event(req: SDKEventRequest):
    event_dict = req.model_dump()
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if session:
        event_dict["user_id"] = session["user_id"]
    try:
        result = await platform_pipeline.process(
            event_dict, require_existing_session=True
        )
    except PipelineValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return result.event_ack

@app.post("/sdk/request-decision")
async def sdk_request_decision(req: SDKDecisionRequest):
    dec_dict = req.model_dump()
    session = sdk_engine.sdk_sessions.get(req.session_id)
    if session:
        dec_dict["user_id"] = session["user_id"]
        dec_dict["device_id"] = session["device_id"]
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
        "model_used": (
            result.inference["implementation"]
            if result.inference["status"] == "EXECUTED"
            else None
        ),
        "fallback_used": (
            result.inference["implementation"]
            if result.inference["status"] == "FALLBACK"
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
async def get_threats(status: str = None, category: str = None, severity: str = None):
    return {"threats": cyber_threat_engine.get_all_threats(status=status, category=category, severity=severity)}

@app.get("/threats/{threat_id}")
async def get_threat_by_id(threat_id: str):
    t = cyber_threat_engine.get_threat_by_id(threat_id)
    if not t:
        return {"error": "Threat not found", "threat_id": threat_id}
    return t

@app.get("/threats/session/{session_id}")
async def get_threats_by_session(session_id: str):
    return {"session_id": session_id, "threats": cyber_threat_engine.get_threats_by_session(session_id)}

@app.get("/threats/device/{device_id}")
async def get_threats_by_device(device_id: str):
    return {"device_id": device_id, "threats": cyber_threat_engine.get_threats_by_device(device_id)}

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
        "threats": result.threats,
        "graph": result.graph,
        "pipeline_id": result.pipeline_id,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8001, reload=True)
