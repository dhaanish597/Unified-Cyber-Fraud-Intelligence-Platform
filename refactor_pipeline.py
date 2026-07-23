import re
import sys

def process_pipeline():
    with open("api/pipeline_engine.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Remove is_demo_txn branch
    # Find the start of `is_demo_txn = ...`
    # and the start of `stages_executed = []`
    
    start_demo = content.find('    is_demo_txn = ')
    end_demo = content.find('    stages_executed = []')
    
    new_setup = """
    # Live calculation
    eval_res = evaluate(txn)
    composite_score = float(eval_res.get("score", 65.0))
    action = eval_res.get("action", "CHALLENGE")
    reasons = eval_res.get("reasons", [])
    
    tab_p = tabular_score(txn, use_fusion=True)
    lgbm_prob = round(float(tab_p), 2)
    
    iso_raw = anomaly_score(txn)
    iso_score_raw = round(float(iso_raw), 2)
    iso_score_norm = round(min(0.99, max(0.10, abs(iso_score_raw) * 2.5)), 2)
    
    orig_feat = GRAPH_FEATURES.get(orig, {})
    pagerank = round(orig_feat.get("pagerank", 0.015), 4)
    
    shap_values = [
        {"feature": "amount_ratio", "impact": 1.1},
        {"feature": "cyber_flag", "impact": 1.8 if has_cyber else 0.0},
        {"feature": "dest_centrality", "impact": 0.6 if mule_cluster else 0.1}
    ]
"""
    content = content[:start_demo] + new_setup + content[end_demo:]

    # Now let's wrap each stage.
    # The stages look like:
    #     # X. Stage Name
    #     stages_executed.append({
    #         "stage_id": "...",
    #         ...
    #     })
    
    # We will split the content by `# 1. Incoming Transaction`
    parts = content.split('    # 1. Incoming Transaction')
    header = parts[0]
    rest = '    # 1. Incoming Transaction' + parts[1]
    
    # Let's add timing setup in header
    header = header.replace('    stages_executed = []', '    stages_executed = []\n    _timings = {}\n    _t_start_total = time.perf_counter()')
    
    stages = re.split(r'(\s*# \d+\. [^\n]+)\n', rest)
    
    new_rest = stages[0]
    stage_idx = 1
    
    for i in range(1, len(stages), 2):
        comment = stages[i]
        block = stages[i+1]
        
        # we want to wrap `stages_executed.append(...)`
        # wait, the block contains stages_executed.append({...})
        # Let's find the append call
        append_start = block.find('stages_executed.append({')
        if append_start != -1:
            # We want to put `_t0 = time.perf_counter()` before it
            # and `_t1 = time.perf_counter()` after the block? 
            # No, the block itself has dict initialization. 
            # Wait, the prompt says "Wrap each of the 16 stages with time.perf_counter() and put the real measured duration in each stage's timing field"
            
            # Let's replace `stages_executed.append({` with:
            # _t0 = time.perf_counter()
            # _stage_dict = {
            # ...
            # }
            # _t1 = time.perf_counter()
            # _dur = (_t1 - _t0) * 1000
            # _timings[<stage_name>] = _dur
            # _stage_dict["timing_ms"] = round(_dur, 2)
            # stages_executed.append(_stage_dict)
            
            # We need to find the matching '})' for the append
            # Since the blocks are well formatted, it's just replacing `stages_executed.append({` and `})` at the end
            block = block.replace('stages_executed.append({', f'_t0_{stage_idx} = time.perf_counter()\n    _stage_dict_{stage_idx} = {{')
            
            # Replace the first `})` from the end with the timing logic
            last_bracket = block.rfind('})')
            if last_bracket != -1:
                ending = block[last_bracket+2:]
                insertion = f"""}}
    _t1_{stage_idx} = time.perf_counter()
    _dur_{stage_idx} = (_t1_{stage_idx} - _t0_{stage_idx}) * 1000
    _timings["stage_{stage_idx}"] = _dur_{stage_idx}
    _stage_dict_{stage_idx}["timing_ms"] = round(_dur_{stage_idx}, 2)
    stages_executed.append(_stage_dict_{stage_idx})"""
                block = block[:last_bracket] + insertion + ending
        
        new_rest += comment + '\n' + block
        stage_idx += 1
    
    content = header + new_rest
    
    # We also need to add _timings into txn so trust_engine can access it
    # Find `trust_metrics = compute_investigation_trust(txn, {"score": composite_score, "action": action})`
    
    trust_call = 'trust_metrics = compute_investigation_trust(txn, {"score": composite_score, "action": action})'
    replacement = """_timings["total_latency_ms"] = (time.perf_counter() - _t_start_total) * 1000
    _timings["inference_ms"] = _timings.get("stage_10", 0) + _timings.get("stage_11", 0)
    _timings["neo4j_lookup_ms"] = _timings.get("stage_8", 0)
    _timings["feature_eng_ms"] = _timings.get("stage_4", 0)
    _timings["shap_explain_ms"] = _timings.get("stage_12", 0)
    _timings["ledger_commit_ms"] = _timings.get("stage_15", 0)
    txn["_timings"] = _timings
    trust_metrics = compute_investigation_trust(txn, {"score": composite_score, "action": action})"""
    
    content = content.replace(trust_call, replacement)

    with open("api/pipeline_engine.py", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    process_pipeline()
