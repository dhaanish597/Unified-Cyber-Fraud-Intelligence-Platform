"""
RRR — Real-Time Risk & Response
Crypto Fraud Intelligence Mobile Investigator API

This router is a THIN WRAPPER over the existing platform services.
It does NOT implement a second intelligence engine. All intelligence
flows through the existing pipeline, risk engine, and store.

Registered at: /rrr/*
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import io
import json
import logging
import secrets
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from api import store

logger = logging.getLogger("rrr")

router = APIRouter(prefix="/rrr", tags=["RRR Investigator"])

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────

SUPPORTED_CHAINS = ["Ethereum", "Tron", "Binance Smart Chain", "Bitcoin", "Polygon", "Arbitrum", "Solana"]

FRAUD_TYPES = [
    "Investment Fraud",
    "Task Fraud",
    "Phishing",
    "Sextortion",
    "Ransomware",
    "Darknet",
    "Other",
]

RISK_CATEGORIES = {
    (0, 25): "LOW",
    (25, 50): "GUARDED",
    (50, 75): "HIGH",
    (75, 90): "VERY HIGH",
    (90, 101): "CRITICAL",
}


def _risk_category(score: float) -> str:
    for (lo, hi), label in RISK_CATEGORIES.items():
        if lo <= score < hi:
            return label
    return "CRITICAL"


# ─────────────────────────────────────────────────────────────────
# SYNTHETIC CRYPTO CASE GENERATOR
# ─────────────────────────────────────────────────────────────────

def _generate_synthetic_case(
    wallet: str,
    chain: str,
    fraud_type: str,
    complaint_ref: str,
    case_id: str,
    tx_hash: Optional[str] = None,
) -> dict:
    """
    Generate a deterministic synthetic crypto fraud case.
    Always labelled as DEVELOPMENT SYNTHETIC.
    Three scenario archetypes: MIXER, CROSS_CHAIN, VASP_EXIT.
    Archetype selected by hash of wallet address for determinism.
    """
    import hashlib
    h = int(hashlib.sha256(wallet.encode()).hexdigest(), 16)
    scenario = ["MIXER", "CROSS_CHAIN", "VASP_EXIT"][h % 3]

    now = datetime.datetime.now(datetime.timezone.utc)
    ts = lambda offset_s=0: (now + datetime.timedelta(seconds=offset_s)).isoformat(timespec="seconds")

    # Base wallet fingerprints — deterministic from wallet hash
    def fake_wallet(seed: str) -> str:
        return "0x" + hashlib.sha256((wallet + seed).encode()).hexdigest()[:40]

    intermediary_1 = fake_wallet("int1")
    intermediary_2 = fake_wallet("int2")
    mixer_addr = fake_wallet("mixer")
    vasp_addr = fake_wallet("vasp")

    root_amount = round(10 + (h % 90), 2)
    amounts = [
        round(root_amount * 0.99, 2),
        round(root_amount * 0.975, 2),
        round(root_amount * 0.96, 2),
        round(root_amount * 0.945, 2),
    ]

    def make_tx(frm: str, to: str, amt: float, label: str, offset_s: int, risk_contrib: int) -> dict:
        tx_id = "0x" + hashlib.sha256(f"{case_id}:{label}".encode()).hexdigest()
        ev_id = f"EV-{hashlib.sha256(f'{case_id}:{label}'.encode()).hexdigest()[:8].upper()}"
        block = 20000000 + (h % 500000) + offset_s
        return {
            "tx_hash": tx_id,
            "from_address": frm,
            "to_address": to,
            "amount": amt,
            "asset": "ETH" if chain == "Ethereum" else "TRX" if chain == "Tron" else "BTC",
            "chain": chain,
            "block": block,
            "timestamp": ts(offset_s),
            "risk_contribution": risk_contrib,
            "evidence_id": ev_id,
            "label": label,
        }

    transactions = []
    fund_flow_nodes = []
    cross_chain_data = None

    if scenario == "MIXER":
        transactions = [
            make_tx(wallet, intermediary_1, root_amount, "root_to_int1", 0, 5),
            make_tx(intermediary_1, mixer_addr, amounts[0], "int1_to_mixer", 120, 25),
            make_tx(mixer_addr, intermediary_2, amounts[1], "mixer_to_int2", 300, 20),
            make_tx(intermediary_2, vasp_addr, amounts[2], "int2_to_vasp", 480, 10),
        ]
        fund_flow_nodes = [
            {"id": "root", "address": wallet, "label": "ROOT WALLET", "type": "WALLET", "amount": root_amount},
            {"id": "int1", "address": intermediary_1, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[0]},
            {"id": "mixer", "address": mixer_addr, "label": "MIXER", "type": "MIXER", "amount": amounts[1]},
            {"id": "int2", "address": intermediary_2, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[2]},
            {"id": "vasp", "address": vasp_addr, "label": "Demo Exchange", "type": "VASP", "amount": amounts[3]},
        ]
        risk_score = 94
        risk_factors = ["Mixer interaction", "Rapid multi-hop movement", "Layering", "High-value movement", "VASP exposure"]
        patterns = ["MIXER_INTERACTION", "RAPID_HOP", "LAYERING", "VASP_EXIT"]
        vasp_attribution = {
            "entity": "Demo Exchange",
            "type": "VASP / EXCHANGE",
            "role": "Custodial Exchange",
            "chain": chain,
            "hops_from_root": 4,
            "confidence": "HIGH",
            "address": vasp_addr,
            "first_observed": transactions[3]["timestamp"],
            "last_observed": transactions[3]["timestamp"],
            "evidence_count": 1,
            "path": ["ROOT", "INTERMEDIARY", "MIXER", "INTERMEDIARY", "VASP"],
        }

    elif scenario == "CROSS_CHAIN":
        tron_addr = fake_wallet("tron1")
        tron_vasp = fake_wallet("tronvasp")
        transactions = [
            make_tx(wallet, intermediary_1, root_amount, "root_to_int1", 0, 5),
            make_tx(intermediary_1, mixer_addr, amounts[0], "int1_to_bridge", 180, 15),
            make_tx(tron_addr, tron_vasp, amounts[1], "tron_to_vasp", 360, 20),
            make_tx(tron_vasp, fake_wallet("sink"), amounts[2], "final", 540, 10),
        ]
        transactions[1]["label"] = "BRIDGE"
        transactions[1]["to_address"] = "BRIDGE:ETH→TRX"
        transactions[2]["chain"] = "Tron"
        transactions[2]["asset"] = "TRX"
        transactions[3]["chain"] = "Tron"
        transactions[3]["asset"] = "TRX"

        cross_chain_data = {
            "source_chain": chain,
            "destination_chain": "Tron",
            "bridge": "Cross-Chain Bridge (ETH→TRX)",
            "source_tx": transactions[1]["tx_hash"],
            "destination_tx": transactions[2]["tx_hash"],
            "source_amount": amounts[0],
            "destination_amount": amounts[1],
            "asset_in": "ETH",
            "asset_out": "TRX",
            "timestamp": transactions[1]["timestamp"],
            "risk_contribution": 30,
        }

        fund_flow_nodes = [
            {"id": "root", "address": wallet, "label": "ROOT WALLET", "type": "WALLET", "amount": root_amount, "chain": chain},
            {"id": "int1", "address": intermediary_1, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[0], "chain": chain},
            {"id": "bridge", "address": "BRIDGE", "label": "ETH → TRX Bridge", "type": "BRIDGE", "amount": amounts[0], "chain": "Bridge"},
            {"id": "tron1", "address": tron_addr, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[1], "chain": "Tron"},
            {"id": "tronvasp", "address": tron_vasp, "label": "Demo TRON Exchange", "type": "VASP", "amount": amounts[2], "chain": "Tron"},
        ]
        risk_score = 88
        risk_factors = ["Cross-chain bridge detected", "Chain hop obfuscation", "VASP exposure", "Rapid movement"]
        patterns = ["CROSS_CHAIN_HOP", "VASP_EXIT", "RAPID_HOP"]
        vasp_attribution = {
            "entity": "Demo TRON Exchange",
            "type": "VASP / EXCHANGE",
            "role": "Custodial Exchange",
            "chain": "Tron",
            "hops_from_root": 4,
            "confidence": "MEDIUM",
            "address": tron_vasp,
            "first_observed": transactions[2]["timestamp"],
            "last_observed": transactions[2]["timestamp"],
            "evidence_count": 2,
            "path": ["ROOT (ETH)", "INTERMEDIARY", "BRIDGE", "INTERMEDIARY (TRX)", "VASP (TRX)"],
        }

    else:  # VASP_EXIT
        transactions = [
            make_tx(wallet, intermediary_1, root_amount, "root_to_int1", 0, 5),
            make_tx(intermediary_1, intermediary_2, amounts[0], "int1_to_int2", 60, 8),
            make_tx(intermediary_2, vasp_addr, amounts[1], "int2_to_vasp", 180, 15),
        ]
        fund_flow_nodes = [
            {"id": "root", "address": wallet, "label": "ROOT WALLET", "type": "WALLET", "amount": root_amount},
            {"id": "int1", "address": intermediary_1, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[0]},
            {"id": "int2", "address": intermediary_2, "label": "INTERMEDIARY", "type": "INTERMEDIARY", "amount": amounts[1]},
            {"id": "vasp", "address": vasp_addr, "label": "Demo Exchange", "type": "VASP", "amount": amounts[2]},
        ]
        risk_score = 78
        risk_factors = ["Direct VASP exit", "Multi-hop structuring", "High-value movement"]
        patterns = ["RAPID_HOP", "VASP_EXIT"]
        vasp_attribution = {
            "entity": "Demo Exchange",
            "type": "VASP / EXCHANGE",
            "role": "Custodial Exchange",
            "chain": chain,
            "hops_from_root": 3,
            "confidence": "HIGH",
            "address": vasp_addr,
            "first_observed": transactions[2]["timestamp"],
            "last_observed": transactions[2]["timestamp"],
            "evidence_count": 1,
            "path": ["ROOT", "INTERMEDIARY", "INTERMEDIARY", "VASP"],
        }

    # Evidence list
    evidence = []
    for i, tx in enumerate(transactions):
        evidence.append({
            "evidence_id": tx["evidence_id"],
            "tx_hash": tx["tx_hash"],
            "source": "SYNTHETIC_PROVIDER",
            "provider": "Development Synthetic",
            "captured_at": tx["timestamp"],
            "chain": tx.get("chain", chain),
            "block": tx["block"],
            "amount": tx["amount"],
            "asset": tx["asset"],
            "related_wallet": tx["from_address"],
            "related_case": case_id,
            "integrity_hash": hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest(),
        })

    # Timeline
    timeline = [
        {"timestamp": ts(-5), "event": "Complaint registered", "type": "COMPLAINT", "detail": f"Ref: {complaint_ref}"},
        {"timestamp": ts(0), "event": "Wallet identified", "type": "WALLET", "detail": f"{wallet[:10]}..."},
        {"timestamp": ts(5), "event": "Blockchain transactions acquired", "type": "ACQUISITION", "detail": f"{len(transactions)} transactions found"},
        {"timestamp": ts(10), "event": "Fund flow traced", "type": "TRACE", "detail": f"{len(fund_flow_nodes)} nodes in graph"},
        {"timestamp": ts(15), "event": f"{'Mixer interaction detected' if scenario == 'MIXER' else 'Cross-chain bridge detected' if scenario == 'CROSS_CHAIN' else 'Direct VASP exit detected'}", "type": "PATTERN", "detail": f"Pattern: {scenario}"},
        {"timestamp": ts(20), "event": "VASP endpoint attributed", "type": "VASP", "detail": vasp_attribution["entity"]},
        {"timestamp": ts(25), "event": f"Risk assessed: {risk_score}/100 {_risk_category(risk_score)}", "type": "RISK", "detail": ", ".join(risk_factors[:3])},
        {"timestamp": ts(30), "event": "Evidence persisted", "type": "EVIDENCE", "detail": f"{len(evidence)} evidence records"},
    ]

    return {
        "case_id": case_id,
        "complaint_ref": complaint_ref,
        "fraud_type": fraud_type,
        "root_wallet": wallet,
        "root_tx_hash": tx_hash or transactions[0]["tx_hash"],
        "chain": chain,
        "status": "OPEN",
        "created_at": ts(-5),
        "updated_at": ts(30),
        "data_source": "DEVELOPMENT SYNTHETIC",
        "scenario": scenario,
        "risk": {
            "score": risk_score,
            "category": _risk_category(risk_score),
            "factors": risk_factors,
            "history": [
                {"score": max(0, risk_score - 22), "timestamp": ts(5), "reason": "Initial acquisition"},
                {"score": max(0, risk_score - 9), "timestamp": ts(15), "reason": "Pattern detected"},
                {"score": risk_score, "timestamp": ts(20), "reason": "VASP attributed"},
            ],
        },
        "transactions": transactions,
        "graph": {
            "nodes": fund_flow_nodes,
            "node_count": len(fund_flow_nodes),
            "edge_count": len(transactions),
        },
        "patterns": patterns,
        "vasp_attribution": vasp_attribution,
        "cross_chain": cross_chain_data,
        "evidence": evidence,
        "timeline": timeline,
        "watch_active": False,
        "watch_id": None,
        "alert_count": 0,
    }


# ─────────────────────────────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────────────────────────────

class CreateInvestigationRequest(BaseModel):
    complaint_ref: str = Field(..., description="Complaint reference number")
    fraud_type: str = Field(..., description="Type of fraud")
    victim_notes: str = Field(default="", description="Notes from victim")
    chain: str = Field(default="Ethereum", description="Blockchain")
    suspect_wallet: str = Field(..., description="Suspect wallet address")
    tx_hash: Optional[str] = Field(default=None, description="Optional initial transaction hash")


class AcknowledgeAlertRequest(BaseModel):
    investigator: str = "RRR Investigator"
    note: str = ""


class StartWatchRequest(BaseModel):
    wallet: str
    chain: str = "Ethereum"
    case_id: Optional[str] = None


class WatchEventRequest(BaseModel):
    """Inject a synthetic development event into a watch."""
    event_type: str = "NEW_TRANSACTION"
    amount: float = 1.5
    description: str = "Synthetic development event"


class GenerateReportRequest(BaseModel):
    format: str = "pdf"


# ─────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────

@router.get("/dashboard")
async def get_rrr_dashboard():
    """Investigator Command Center metrics."""
    investigations = store.list_all("rrr_cases")
    alerts = store.list_all("rrr_alerts")
    watches = store.list_all("rrr_watches")

    active = [c for c in investigations if c.get("status") == "OPEN"]
    critical = [c for c in investigations if c.get("risk", {}).get("category") == "CRITICAL"]
    new_alerts = [a for a in alerts if a.get("status") == "NEW"]
    active_watches = [w for w in watches if w.get("status") == "ACTIVE"]

    # Total transactions observed across all investigations
    total_txns = sum(len(c.get("transactions", [])) for c in investigations)

    # VASP exposures
    vasp_exposures = [c for c in investigations if c.get("vasp_attribution")]

    # Latest event for live feed
    latest_event = None
    if investigations:
        latest = max(investigations, key=lambda c: c.get("updated_at", ""))
        vasp = latest.get("vasp_attribution", {})
        nodes = latest.get("graph", {}).get("nodes", [])
        risk = latest.get("risk", {})
        latest_event = {
            "case_id": latest["case_id"],
            "fraud_type": latest.get("fraud_type"),
            "root_wallet": latest.get("root_wallet"),
            "risk_score": risk.get("score"),
            "risk_category": risk.get("category"),
            "vasp": vasp.get("entity") if vasp else None,
            "path_preview": " → ".join(n.get("label", n.get("type", "?")) for n in nodes[:4]) if nodes else None,
            "updated_at": latest.get("updated_at"),
        }

    return {
        "active_investigations": len(active),
        "critical_cases": len(critical),
        "active_watches": len(active_watches),
        "new_alerts": len(new_alerts),
        "transactions_observed": total_txns,
        "vasp_exposures": len(vasp_exposures),
        "total_investigations": len(investigations),
        "latest_event": latest_event,
        "data_source": "DEVELOPMENT SYNTHETIC" if investigations and any(
            c.get("data_source") == "DEVELOPMENT SYNTHETIC" for c in investigations
        ) else "LIVE",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────
# INVESTIGATIONS
# ─────────────────────────────────────────────────────────────────

@router.get("/investigations")
async def list_investigations(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    fraud_type: Optional[str] = None,
):
    """List all RRR investigations."""
    cases = store.list_all("rrr_cases")
    if status:
        cases = [c for c in cases if c.get("status", "").upper() == status.upper()]
    if fraud_type:
        cases = [c for c in cases if c.get("fraud_type", "").lower() == fraud_type.lower()]
    cases.sort(key=lambda c: c.get("created_at", ""), reverse=True)
    total = len(cases)
    start = (page - 1) * page_size
    return {
        "items": cases[start: start + page_size],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.post("/investigations", status_code=201)
async def create_investigation(req: CreateInvestigationRequest, background_tasks: BackgroundTasks):
    """
    Create a new RRR investigation.
    Runs the full pipeline:
    Complaint → Case → Wallet → Acquisition → Normalization →
    Fund-flow → Graph → Patterns → Risk → VASP → Evidence → Timeline
    """
    if req.fraud_type not in FRAUD_TYPES:
        raise HTTPException(status_code=422, detail=f"fraud_type must be one of {FRAUD_TYPES}")
    if req.chain not in SUPPORTED_CHAINS:
        raise HTTPException(status_code=422, detail=f"chain must be one of {SUPPORTED_CHAINS}")
    if not req.suspect_wallet.strip():
        raise HTTPException(status_code=422, detail="suspect_wallet is required")

    case_id = f"RRR-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    case = _generate_synthetic_case(
        wallet=req.suspect_wallet.strip(),
        chain=req.chain,
        fraud_type=req.fraud_type,
        complaint_ref=req.complaint_ref.strip() or f"COMP-{uuid.uuid4().hex[:8].upper()}",
        case_id=case_id,
        tx_hash=req.tx_hash,
    )
    case["victim_notes"] = req.victim_notes

    # Also insert a conventional case record so the existing /cases endpoint shows it
    conventional_case = {
        "case_id": case_id,
        "transaction_id": case["root_tx_hash"],
        "customer_id": req.suspect_wallet,
        "status": "OPEN",
        "severity": case["risk"]["category"],
        "score": case["risk"]["score"],
        "amount": sum(t.get("amount", 0) for t in case.get("transactions", [])),
        "created_at": case["created_at"],
        "reason": f"RRR: {req.fraud_type} — {case['scenario']}",
        "fraud_type": req.fraud_type,
        "chain": req.chain,
        "rrr_case": True,
    }
    store.put("cases", case_id, conventional_case)
    store.put("rrr_cases", case_id, case)

    # Auto-generate an alert if risk is HIGH or above
    risk_score = case["risk"]["score"]
    if risk_score >= 50:
        alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
        alert = {
            "alert_id": alert_id,
            "case_id": case_id,
            "status": "NEW",
            "severity": case["risk"]["category"],
            "title": f"{case['risk']['category']}: {req.fraud_type} detected",
            "wallet": req.suspect_wallet,
            "chain": req.chain,
            "risk_score": risk_score,
            "risk_category": case["risk"]["category"],
            "reason": case["risk"]["factors"][0] if case["risk"]["factors"] else "High risk activity detected",
            "vasp": case.get("vasp_attribution", {}).get("entity"),
            "created_at": case["created_at"],
            "acknowledged": False,
            "acknowledged_by": None,
            "acknowledged_at": None,
        }
        store.put("rrr_alerts", alert_id, alert)
        # Update case alert count
        case["alert_count"] = 1
        store.put("rrr_cases", case_id, case)

    return {
        "case_id": case_id,
        "status": "CREATED",
        "pipeline_stages": [
            {"stage": "Complaint registered", "status": "COMPLETE"},
            {"stage": "Wallet identified", "status": "COMPLETE"},
            {"stage": "Blockchain acquisition", "status": "COMPLETE"},
            {"stage": "Transactions normalized", "status": "COMPLETE"},
            {"stage": "Fund flow traced", "status": "COMPLETE"},
            {"stage": "Graph constructed", "status": "COMPLETE"},
            {"stage": "Pattern analysis", "status": "COMPLETE"},
            {"stage": "Risk assessment", "status": "COMPLETE"},
            {"stage": "VASP attribution", "status": "COMPLETE"},
            {"stage": "Evidence persisted", "status": "COMPLETE"},
        ],
        "data_source": "DEVELOPMENT SYNTHETIC",
        "case": case,
    }


@router.get("/investigations/{case_id}")
async def get_investigation(case_id: str):
    """Full investigation summary."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    return case


@router.get("/investigations/{case_id}/fundflow")
async def get_fund_flow(case_id: str):
    """Directed predominant fund-flow path."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    return {
        "case_id": case_id,
        "chain": case.get("chain"),
        "nodes": case.get("graph", {}).get("nodes", []),
        "edges": [
            {
                "from": tx.get("from_address"),
                "to": tx.get("to_address"),
                "amount": tx.get("amount"),
                "asset": tx.get("asset"),
                "chain": tx.get("chain", case.get("chain")),
                "tx_hash": tx.get("tx_hash"),
                "timestamp": tx.get("timestamp"),
                "risk_contribution": tx.get("risk_contribution"),
            }
            for tx in case.get("transactions", [])
        ],
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/transactions")
async def get_transactions(case_id: str):
    """Blockchain transaction ledger for investigation."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    return {
        "case_id": case_id,
        "transactions": case.get("transactions", []),
        "total": len(case.get("transactions", [])),
        "chain": case.get("chain"),
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/risk")
async def get_risk(case_id: str):
    """Risk score, factors, and history."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    risk = case.get("risk", {})
    return {
        "case_id": case_id,
        "score": risk.get("score"),
        "category": risk.get("category"),
        "factors": risk.get("factors", []),
        "history": risk.get("history", []),
        "patterns": case.get("patterns", []),
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/vasp")
async def get_vasp_attribution(case_id: str):
    """VASP attribution for investigation."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    vasp = case.get("vasp_attribution")
    if not vasp:
        return {"case_id": case_id, "status": "NO_VASP_DETECTED", "vasp_attribution": None}
    return {
        "case_id": case_id,
        "status": "ATTRIBUTED",
        "nearest_observed_vasp_endpoint": vasp.get("entity"),
        "attribution_confidence": vasp.get("confidence"),
        "vasp_attribution": vasp,
        "data_source": case.get("data_source"),
        "disclaimer": "Attribution shows nearest observed VASP endpoint. Wallet ownership is not proven.",
    }


@router.get("/investigations/{case_id}/crosschain")
async def get_cross_chain(case_id: str):
    """Cross-chain intelligence for investigation."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    cc = case.get("cross_chain")
    if not cc:
        return {"case_id": case_id, "status": "NO_CROSS_CHAIN", "cross_chain": None, "chain": case.get("chain")}
    return {
        "case_id": case_id,
        "status": "CROSS_CHAIN_DETECTED",
        "cross_chain": cc,
        "graph_nodes": case.get("graph", {}).get("nodes", []),
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/evidence")
async def get_evidence(case_id: str):
    """Evidence list for investigation."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")
    return {
        "case_id": case_id,
        "evidence": case.get("evidence", []),
        "total": len(case.get("evidence", [])),
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/timeline")
async def get_timeline(case_id: str):
    """Investigator timeline for investigation."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")

    # Merge with any watch events
    watches = store.list_all("rrr_watches")
    watch_events = []
    for w in watches:
        if w.get("case_id") == case_id:
            for ev in w.get("events", []):
                watch_events.append({
                    "timestamp": ev.get("timestamp"),
                    "event": ev.get("description", "Watch event"),
                    "type": "WATCH_EVENT",
                    "detail": f"Amount: {ev.get('amount', '?')}",
                })

    timeline = case.get("timeline", []) + watch_events
    timeline.sort(key=lambda e: e.get("timestamp", ""))

    return {
        "case_id": case_id,
        "timeline": timeline,
        "total": len(timeline),
        "data_source": case.get("data_source"),
    }


@router.get("/investigations/{case_id}/alerts")
async def get_investigation_alerts(case_id: str):
    """Alerts for specific investigation."""
    alerts = [a for a in store.list_all("rrr_alerts") if a.get("case_id") == case_id]
    alerts.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return {"case_id": case_id, "alerts": alerts, "total": len(alerts)}


@router.post("/investigations/{case_id}/report")
async def generate_report(case_id: str, req: GenerateReportRequest):
    """Generate investigation report."""
    case = store.get("rrr_cases", case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Investigation {case_id} not found")

    report_id = f"RPT-RRR-{uuid.uuid4().hex[:8].upper()}"
    vasp = case.get("vasp_attribution", {})
    risk = case.get("risk", {})

    report = {
        "report_id": report_id,
        "case_id": case_id,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "format": req.format,
        "status": "READY",
        "data_source": case.get("data_source"),
        "summary": {
            "case_id": case_id,
            "complaint_ref": case.get("complaint_ref"),
            "fraud_type": case.get("fraud_type"),
            "root_wallet": case.get("root_wallet"),
            "chain": case.get("chain"),
            "status": case.get("status"),
            "created_at": case.get("created_at"),
        },
        "risk_assessment": {
            "score": risk.get("score"),
            "category": risk.get("category"),
            "factors": risk.get("factors", []),
        },
        "transactions": case.get("transactions", []),
        "transaction_count": len(case.get("transactions", [])),
        "patterns": case.get("patterns", []),
        "vasp_attribution": vasp if vasp else "NO_VASP_DETECTED",
        "cross_chain": case.get("cross_chain"),
        "evidence_count": len(case.get("evidence", [])),
        "evidence": case.get("evidence", []),
        "timeline": case.get("timeline", []),
        "recommended_actions": [
            "Submit VASP information request to attributed exchange",
            "Freeze suspect wallet if jurisdictionally possible",
            "Preserve all blockchain evidence",
            "File formal complaint with relevant cybercrime authority",
            f"Risk score {risk.get('score')}/100 — {'Immediate escalation recommended' if risk.get('score', 0) >= 90 else 'Standard investigation process'}",
        ],
        "fund_flow_nodes": case.get("graph", {}).get("nodes", []),
    }
    store.put("rrr_reports", report_id, report)
    return report


@router.get("/investigations/{case_id}/report/{report_id}")
async def get_report(case_id: str, report_id: str):
    """Get a generated report."""
    report = store.get("rrr_reports", report_id)
    if not report or report.get("case_id") != case_id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


# ─────────────────────────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────────────────────────

@router.get("/alerts")
async def list_alerts(status: Optional[str] = None, limit: int = 50):
    """Global alert feed."""
    alerts = store.list_all("rrr_alerts")
    if status:
        alerts = [a for a in alerts if a.get("status", "").upper() == status.upper()]
    alerts.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    return {"alerts": alerts[:limit], "total": len(alerts)}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, req: AcknowledgeAlertRequest):
    """Acknowledge an alert."""
    alert = store.get("rrr_alerts", alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    alert["acknowledged"] = True
    alert["status"] = "ACKNOWLEDGED"
    alert["acknowledged_by"] = req.investigator
    alert["acknowledged_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    alert["acknowledgment_note"] = req.note
    store.put("rrr_alerts", alert_id, alert)
    return alert


# ─────────────────────────────────────────────────────────────────
# WALLET WATCH
# ─────────────────────────────────────────────────────────────────

@router.get("/watch")
async def list_watches():
    """List all active wallet watches."""
    watches = store.list_all("rrr_watches")
    watches.sort(key=lambda w: w.get("started_at", ""), reverse=True)
    return {"watches": watches, "total": len(watches), "active": sum(1 for w in watches if w.get("status") == "ACTIVE")}


@router.post("/watch", status_code=201)
async def start_watch(req: StartWatchRequest):
    """Start a wallet watch."""
    watch_id = f"WATCH-{uuid.uuid4().hex[:8].upper()}"
    watch = {
        "watch_id": watch_id,
        "wallet": req.wallet,
        "chain": req.chain,
        "case_id": req.case_id,
        "status": "ACTIVE",
        "started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "last_event_at": None,
        "events_observed": 0,
        "events": [],
        "current_risk": None,
    }
    store.put("rrr_watches", watch_id, watch)

    # Update associated case
    if req.case_id:
        case = store.get("rrr_cases", req.case_id)
        if case:
            case["watch_active"] = True
            case["watch_id"] = watch_id
            timeline = case.get("timeline", [])
            timeline.append({
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "event": "Wallet watch activated",
                "type": "WATCH",
                "detail": f"Watch ID: {watch_id}",
            })
            case["timeline"] = timeline
            store.put("rrr_cases", req.case_id, case)

    return watch


@router.delete("/watch/{watch_id}")
async def stop_watch(watch_id: str):
    """Stop a wallet watch."""
    watch = store.get("rrr_watches", watch_id)
    if not watch:
        raise HTTPException(status_code=404, detail=f"Watch {watch_id} not found")
    watch["status"] = "STOPPED"
    watch["stopped_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    store.put("rrr_watches", watch_id, watch)

    # Update case
    case_id = watch.get("case_id")
    if case_id:
        case = store.get("rrr_cases", case_id)
        if case:
            case["watch_active"] = False
            store.put("rrr_cases", case_id, case)

    return {"watch_id": watch_id, "status": "STOPPED"}


@router.get("/watch/{watch_id}")
async def get_watch(watch_id: str):
    """Get watch details."""
    watch = store.get("rrr_watches", watch_id)
    if not watch:
        raise HTTPException(status_code=404, detail=f"Watch {watch_id} not found")
    return watch


@router.post("/watch/{watch_id}/event")
async def inject_watch_event(watch_id: str, req: WatchEventRequest):
    """
    Inject a synthetic development event into a watch.
    Simulates new blockchain activity being detected.
    Labelled as DEVELOPMENT SYNTHETIC.
    """
    watch = store.get("rrr_watches", watch_id)
    if not watch:
        raise HTTPException(status_code=404, detail=f"Watch {watch_id} not found")
    if watch.get("status") != "ACTIVE":
        raise HTTPException(status_code=422, detail="Watch is not active")

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    event = {
        "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
        "event_type": req.event_type,
        "amount": req.amount,
        "description": req.description,
        "timestamp": now,
        "data_source": "DEVELOPMENT SYNTHETIC",
    }

    watch["events"] = watch.get("events", []) + [event]
    watch["events_observed"] = len(watch["events"])
    watch["last_event_at"] = now

    # Update risk if case is linked
    case_id = watch.get("case_id")
    if case_id:
        case = store.get("rrr_cases", case_id)
        if case:
            old_score = case.get("risk", {}).get("score", 50)
            new_score = min(100, old_score + 8)
            case["risk"]["score"] = new_score
            case["risk"]["category"] = _risk_category(new_score)
            case["risk"]["history"] = case.get("risk", {}).get("history", []) + [
                {"score": new_score, "timestamp": now, "reason": f"Watch event: {req.event_type}"}
            ]
            watch["current_risk"] = new_score
            timeline = case.get("timeline", [])
            timeline.append({"timestamp": now, "event": f"New transaction detected", "type": "WATCH_EVENT", "detail": f"Amount: {req.amount} ETH"})
            timeline.append({"timestamp": now, "event": f"Risk changed {old_score} → {new_score}", "type": "RISK", "detail": f"{_risk_category(new_score)}"})
            case["timeline"] = timeline
            case["updated_at"] = now
            store.put("rrr_cases", case_id, case)

            # Create alert
            if new_score >= 75:
                alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
                alert = {
                    "alert_id": alert_id,
                    "case_id": case_id,
                    "status": "NEW",
                    "severity": _risk_category(new_score),
                    "title": f"New blockchain movement detected",
                    "wallet": watch.get("wallet"),
                    "chain": watch.get("chain"),
                    "risk_score": new_score,
                    "risk_score_previous": old_score,
                    "risk_category": _risk_category(new_score),
                    "reason": f"Watch event triggered risk change: {old_score} → {new_score}",
                    "vasp": case.get("vasp_attribution", {}).get("entity"),
                    "created_at": now,
                    "acknowledged": False,
                    "acknowledged_by": None,
                    "acknowledged_at": None,
                }
                store.put("rrr_alerts", alert_id, alert)

    store.put("rrr_watches", watch_id, watch)
    return {"watch_id": watch_id, "event": event, "current_risk": watch.get("current_risk"), "data_source": "DEVELOPMENT SYNTHETIC"}


# ─────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────

@router.get("/config/chains")
async def get_supported_chains():
    """Supported blockchain networks."""
    return {"chains": SUPPORTED_CHAINS, "fraud_types": FRAUD_TYPES}
