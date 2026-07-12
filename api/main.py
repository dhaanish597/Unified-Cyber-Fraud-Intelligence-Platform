import asyncio
import sys
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shap
import json

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.risk_engine import evaluate
from ml.predict import _get_fusion_model, _prepare_single
from ml.features import engineer_features, FEATURE_COLS_FUSION

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionRequest(BaseModel):
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

def get_shap_explanation(txn_dict):
    """Compute SHAP values for the given transaction using the fusion model."""
    try:
        model = _get_fusion_model()
        df = _prepare_single(txn_dict)
        fe = engineer_features(df)
        X = fe[FEATURE_COLS_FUSION]
        
        # We need a tree explainer for XGBoost/LightGBM
        # For simplicity and speed in a single prediction, we use TreeExplainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        
        # shap_values could be a list (multiclass) or array
        if isinstance(shap_values, list):
            sv = shap_values[1][0] # fraud class
        else:
            sv = shap_values[0] # assuming binary classification returning 1D per sample
            if len(sv.shape) > 1 and sv.shape[1] == 2:
                 sv = sv[:, 1]
            
        # Combine feature names and values
        feature_impacts = []
        for i, col in enumerate(FEATURE_COLS_FUSION):
            val = float(sv[i])
            if abs(val) > 0.01: # only keep meaningful impacts
                feature_impacts.append({"feature": col, "impact": val})
                
        # Sort by absolute impact
        feature_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)
        return feature_impacts[:5] # Top 5
    except Exception as e:
        print(f"SHAP error: {e}")
        return []

@app.post("/evaluate/transaction")
async def evaluate_transaction(txn: TransactionRequest):
    txn_dict = txn.dict()
    result = evaluate(txn_dict)
    shap_features = get_shap_explanation(txn_dict)
    
    counterfactual_sentence = ""
    if result.get("counterfactual"):
        cf = result["counterfactual"]
        counterfactual_sentence = f"Counterfactual: With no prior cyber compromise, score = {cf['score']:.0f} -> {cf['action']}, not {result['action']}."
    
    return {
        "action": result["action"],
        "score": result["score"],
        "reasons": result["reasons"],
        "shap_features": shap_features,
        "counterfactual_sentence": counterfactual_sentence
    }

def get_demo_events():
    """Load a subset of transactions and cyber events, combine and sort them by timestamp."""
    print("Loading demo events...")
    try:
        # We'll pick a slice where we know there's a fraud with cyber compromise.
        df_tx = pd.read_csv(ROOT / 'data' / 'processed' / 'transactions.csv')
        df_ev = pd.read_csv(ROOT / 'data' / 'processed' / 'fused_events.csv')
        
        # Find a fraudulent transaction with cyber_compromise_in_window == True
        fraud_tx = df_tx[(df_tx['isFraud'] == 1) & (df_tx['cyber_compromise_in_window'] == True)].iloc[-1:]
        if fraud_tx.empty:
            fraud_tx = df_tx.tail(1)
            
        # Let's take a 5-minute window around that transaction
        target_time = pd.to_datetime(fraud_tx['timestamp'].values[0])
        start_time = target_time - pd.Timedelta(minutes=5)
        end_time = target_time + pd.Timedelta(minutes=1)
        
        df_tx['timestamp_dt'] = pd.to_datetime(df_tx['timestamp'])
        df_ev['timestamp_dt'] = pd.to_datetime(df_ev['timestamp'])
        
        mask_tx = (df_tx['timestamp_dt'] >= start_time) & (df_tx['timestamp_dt'] <= end_time)
        mask_ev = (df_ev['timestamp_dt'] >= start_time) & (df_ev['timestamp_dt'] <= end_time)
        
        slice_tx = df_tx[mask_tx].copy()
        slice_ev = df_ev[mask_ev].copy()
        
        events = []
        for _, row in slice_tx.iterrows():
            d = row.to_dict()
            d.pop('timestamp_dt', None)
            d['msg_type'] = 'transaction'
            events.append(d)
            
        for _, row in slice_ev.iterrows():
            d = row.to_dict()
            d.pop('timestamp_dt', None)
            d['msg_type'] = 'cyber_event'
            events.append(d)
            
        # Sort by timestamp
        events.sort(key=lambda x: x['timestamp'])
        # Limit to 50 events max to not make demo too long, but ensure our target fraud is there
        # We'll just take the last 30 before the target end time
        return events[-40:]
        
    except Exception as e:
        print(f"Error loading demo events: {e}")
        return []

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    events = get_demo_events()
    
    try:
        for event in events:
            # We want to emulate evaluating it if it's a transaction, or UI can call the API
            # For this demo, we just push the raw events and let UI decide.
            # Convert NaN to None for JSON
            clean_event = {k: (None if pd.isna(v) else v) for k, v in event.items()}
            await websocket.send_json(clean_event)
            await asyncio.sleep(1.0) # Demo speed
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
