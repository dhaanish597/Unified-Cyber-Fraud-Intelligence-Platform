import json
import os
import sys
from pathlib import Path

# Add project root to sys.path so ml.predict can be imported
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.predict import tabular_score, anomaly_score

# Load entity graph features
try:
    with open(ROOT / 'data' / 'processed' / 'entity_graph_features.json', 'r') as f:
        GRAPH_FEATURES = json.load(f)
except FileNotFoundError:
    GRAPH_FEATURES = {}

def evaluate(transaction: dict, include_cyber_context: bool = True) -> dict:
    """
    Evaluates a transaction and returns a risk score (0-100), an action, and a list of reasons.
    """
    # 1. Base ML scores
    # If include_cyber_context is false, force cyber_compromise_in_window to False for the model
    txn_for_model = transaction.copy()
    if not include_cyber_context:
        txn_for_model['cyber_compromise_in_window'] = False
        
    tab_score = tabular_score(txn_for_model, use_fusion=include_cyber_context) # returns 0-1
    anom_score = anomaly_score(txn_for_model) # negative = anomalous, >0 = normal
    
    # 2. Graph/Centrality Features
    orig = str(transaction.get('nameOrig', ''))
    dest = str(transaction.get('nameDest', ''))
    
    orig_features = GRAPH_FEATURES.get(orig, {})
    dest_features = GRAPH_FEATURES.get(dest, {})
    
    orig_pagerank = orig_features.get('pagerank', 0.0)
    dest_mule_cluster = dest_features.get('mule_cluster_flag', False)
    
    # 3. Blending into a 0-100 score
    # Tabular score contribution: 0-60 points
    score = tab_score * 60
    
    # Anomaly score contribution: up to +20 points for highly anomalous
    # anom_score usually in [-0.5, 0.5]. If < -0.1, it's anomalous.
    if anom_score < -0.1:
        # map [-0.5, -0.1] to [20, 0]
        anom_penalty = min(20, max(0, (-0.1 - anom_score) * 50))
        score += anom_penalty
        
    # Graph feature contribution: up to +10 points
    if dest_mule_cluster:
        score += 10
    
    if orig_pagerank > 0.001: # highly central node, usually a known entity (could be good or bad, let's treat as risk if transferring out everything)
        score += 2
        
    # Cyber-context contribution: up to +15 points
    has_cyber_compromise = txn_for_model.get('cyber_compromise_in_window', False)
    if has_cyber_compromise:
        score += 15
        
    score = min(100.0, max(0.0, score))
    
    # 4. Determine Action & Reasons
    reasons = []
    if tab_score > 0.6:
        reasons.append(f"High baseline fraud probability (Tabular Score: {tab_score:.2f})")
    if anom_score < -0.1:
        reasons.append(f"Unusual transaction pattern detected (Anomaly Score: {anom_score:.2f})")
    if has_cyber_compromise:
        reasons.append("Recent cyber compromise detected (Login from unusual IP prior to transfer)")
    if dest_mule_cluster:
        reasons.append("Beneficiary is part of a known mule cluster")
        
    # Thresholds
    if score >= 75:
        action = "BLOCK"
    elif score >= 50:
        action = "CHALLENGE"
    else:
        action = "ALLOW"
        if not reasons:
            reasons.append("Transaction falls within normal parameters")
            
    # Add counterfactual if requested
    counterfactual = None
    if include_cyber_context and has_cyber_compromise:
        cf_result = evaluate(transaction, include_cyber_context=False)
        counterfactual = {
            "score": cf_result["score"],
            "action": cf_result["action"]
        }
        reasons.append(f"Counterfactual: With no prior cyber compromise, score = {cf_result['score']:.0f} -> {cf_result['action']}, not {action}.")
        
    return {
        "score": score,
        "action": action,
        "reasons": reasons,
        "counterfactual": counterfactual
    }
