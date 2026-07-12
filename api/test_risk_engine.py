import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics import recall_score

# Add project root to sys.path
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.risk_engine import evaluate
from ml.predict import reload_models

def run_test():
    print("Loading data...")
    df = pd.read_csv(ROOT / 'data' / 'processed' / 'transactions.csv')
    
    # Take a sample for speed (e.g. last 100,000 to simulate test set)
    df = df.tail(100000).reset_index(drop=True)
    
    print("Evaluating transactions with and without fusion context...")
    
    scores_fusion = []
    scores_baseline = []
    
    # We will just evaluate them manually to get scores
    # Since evaluating 100k transactions might be slow with row-by-row dict conversion,
    # let's vectorize where possible or just run a subset.
    # Actually, we can use ml.predict directly for finding the threshold if we want,
    # but the instructions say "the full fused engine" which includes graph features!
    # So we MUST run the full engine.
    # To save time, we will run the engine over 20,000 transactions.
    df = df.tail(20000).reset_index(drop=True)
    
    y_true = df['isFraud'].values
    cyber_flags = df['cyber_compromise_in_window'].values
    
    for i, row in df.iterrows():
        txn = row.to_dict()
        # Ensure cyber_compromise_in_window is bool
        txn['cyber_compromise_in_window'] = bool(txn.get('cyber_compromise_in_window', False))
        
        # Fused engine score
        res_fusion = evaluate(txn, include_cyber_context=True)
        scores_fusion.append(res_fusion['score'])
        
        # Baseline engine score (no cyber context)
        res_baseline = evaluate(txn, include_cyber_context=False)
        scores_baseline.append(res_baseline['score'])
        
    scores_fusion = np.array(scores_fusion)
    scores_baseline = np.array(scores_baseline)
    
    # Calculate threshold for 0.5% FPR
    legit_mask = (y_true == 0)
    
    if legit_mask.sum() == 0:
        print("No legit transactions to calculate FPR.")
        return
        
    legit_scores_fusion = scores_fusion[legit_mask]
    legit_scores_baseline = scores_baseline[legit_mask]
    
    # We want FPR = 0.5%, so we find the 99.5th percentile of legit scores
    thresh_fusion = np.percentile(legit_scores_fusion, 99.5)
    thresh_baseline = np.percentile(legit_scores_baseline, 99.5)
    
    # Now evaluate recall on cyber-preceded frauds
    cyber_fraud_mask = (y_true == 1) & (cyber_flags == True)
    
    if cyber_fraud_mask.sum() == 0:
        print("No cyber-preceded frauds in sample to calculate uplift.")
        return
        
    recall_fusion = np.mean(scores_fusion[cyber_fraud_mask] >= thresh_fusion)
    recall_baseline = np.mean(scores_baseline[cyber_fraud_mask] >= thresh_baseline)
    
    uplift = recall_fusion - recall_baseline
    
    print(f"Thresholds (0.5% FPR) - Fusion: {thresh_fusion:.2f}, Baseline: {thresh_baseline:.2f}")
    print(f"Recall on cyber-preceded frauds - Fusion: {recall_fusion:.4f}, Baseline: {recall_baseline:.4f}")
    print(f"Fusion Uplift: +{uplift:.4f}")
    
    # Print a few sample verdicts
    print("\nSample Verdicts:")
    for i in range(5):
        txn = df.iloc[i].to_dict()
        res = evaluate(txn)
        print(f"Txn {txn['txn_id']} (Fraud: {txn['isFraud']}) - Action: {res['action']} - Score: {res['score']:.2f}")
        for r in res['reasons']:
            print(f"  - {r}")
            
    # Save uplift to ml/metrics_report.md
    report_path = ROOT / 'ml' / 'metrics_report.md'
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write("\n\n## True Fusion Uplift (Risk Engine)\n\n")
        f.write("| Metric | Tabular-Only (Engine) | Tabular + Cyber + Graph (Engine) | Δ |\n")
        f.write("|---|---|---|---|\n")
        f.write(f"| Recall @0.5% FPR on Cyber-Frauds | {recall_baseline:.4f} | {recall_fusion:.4f} | +{uplift:.4f} |\n")
        f.write("\n*This metric compares the full Risk Engine (including graph features and anomaly adjustments) with cyber-context enabled vs. disabled, specifically on frauds preceded by a cyber compromise event.*")

if __name__ == '__main__':
    run_test()
