import hmac
import hashlib
import os
import json
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional

from api.pipeline_engine import execute_pipeline
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
        
    # Store received webhook payloads via api/store.py so the demo can replay them offline
    put("webhooks", webhook_id, {"headers": dict(request.headers), "body": payload})
    
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

    # Normalize the payload into the platform's internal transaction schema
    # Supporting Razorpay format as an example
    event_type = payload.get("event", "payment.captured")
    
    amount = 0.0
    user_id = "usr_webhook"
    txn_id = webhook_id
    
    if "payload" in payload and "payment" in payload["payload"]:
        payment_entity = payload["payload"]["payment"].get("entity", {})
        amount = payment_entity.get("amount", 0.0) / 100.0
        user_id = payment_entity.get("contact", "usr_webhook")
        txn_id = payment_entity.get("id", webhook_id)
        
    normalized_txn = {
        "txn_id": txn_id,
        "step": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "TRANSFER",
        "amount": amount,
        "nameOrig": f"USER_{user_id}",
        "user_id": user_id,
        "device_id": "webhook_device",
        "ip": request.client.host if request.client else "127.0.0.1",
        "oldbalanceOrg": amount,
        "newbalanceOrig": 0.0,
        "nameDest": "MERCHANT_GATEWAY",
        "dest_user_id": "merch_gw",
        "dest_device_id": "none",
        "dest_ip": "none",
        "oldbalanceDest": 0.0,
        "newbalanceDest": amount,
        "cyber_compromise_in_window": False,
        "dest_mule_cluster_id": None
    }
    
    # Feed it into the real pipeline
    result = execute_pipeline(normalized_txn)
    
    return {"status": "ok", "pipeline_result": result}
