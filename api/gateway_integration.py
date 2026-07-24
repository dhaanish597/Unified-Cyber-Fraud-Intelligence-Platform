import hmac
import hashlib
import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional

from api.platform.pipeline import platform_pipeline
from api.store import put

router = APIRouter(prefix="/gateway", tags=["Gateway Integration"])

@router.get("/status")
async def gateway_status():
    secret = os.environ.get("GATEWAY_WEBHOOK_SECRET")
    return {"configured": bool(secret)}

@router.post("/webhook")
async def gateway_webhook(request: Request, x_razorpay_signature: Optional[str] = Header(None)):
    secret = os.environ.get("GATEWAY_WEBHOOK_SECRET")
    
    body = await request.body()
    
    webhook_id = str(uuid.uuid4())
    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
    if not secret:
        raise HTTPException(status_code=401, detail="Gateway credentials not configured")
        
    if not x_razorpay_signature:
        raise HTTPException(status_code=401, detail="Missing signature")
        
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, x_razorpay_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Persist only after authentication and never store authorization/signature headers.
    put("webhooks", webhook_id, {"body": payload})

    # Normalize the payload into the platform's internal transaction schema
    # Supporting Razorpay format as an example
    event_type = str(payload.get("event") or payload.get("event_type") or "").upper()
    if not event_type:
        raise HTTPException(status_code=422, detail="Gateway event type is required")
    
    amount = 0.0
    user_id = ""
    txn_id = webhook_id
    
    if "payload" in payload and "payment" in payload["payload"]:
        payment_entity = payload["payload"]["payment"].get("entity", {})
        amount = payment_entity.get("amount", 0.0) / 100.0
        user_id = str(payment_entity.get("contact") or payment_entity.get("customer_id") or "")
        txn_id = payment_entity.get("id", webhook_id)
        
    normalized_txn = {
        "session_id": f"GATEWAY_{txn_id}",
        "txn_id": txn_id,
        "step": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "type": event_type,
        "amount": amount,
        "nameOrig": user_id,
        "user_id": user_id,
        "device_id": payment_entity.get("device_id", "") if "payment_entity" in locals() else "",
        "ip": request.client.host if request.client else "",
        "oldbalanceOrg": 0.0,
        "newbalanceOrig": 0.0,
        "nameDest": payment_entity.get("merchant_id", "") if "payment_entity" in locals() else "",
        "dest_user_id": "",
        "dest_device_id": "",
        "dest_ip": "",
        "oldbalanceDest": 0.0,
        "newbalanceDest": amount,
        "cyber_compromise_in_window": False,
        "dest_mule_cluster_id": None
    }
    
    # Feed it into the real pipeline
    result = await platform_pipeline.process(
        normalized_txn, require_existing_session=False
    )
    
    return {"status": "ok", "pipeline_result": result.to_dict()}
