import React from 'react';
import { CheckCircle2, Loader2, ShieldCheck, Server, Cpu, AlertTriangle, ArrowDown } from 'lucide-react';

export default function FusionLifecyclePipeline({ activeTxn, evaluation }) {
  if (!activeTxn) {
    return (
      <div className="bg-soc-panel border border-soc-border rounded-xl p-6 text-center text-soc-dim font-mono text-xs">
        Select or stream a transaction to observe live Fusion Runtime execution pipeline...
      </div>
    );
  }

  const isComplete = Boolean(evaluation);

  const stages = [
    { id: 'received', name: '1. Ingestion & Normalization', desc: `Ingested ${activeTxn.type || 'TRANSFER'} from ${activeTxn.nameOrig}`, done: true },
    { id: 'cyber', name: '2. Cyber SIEM Lookup', desc: activeTxn.cyber_compromise_in_window ? 'COMPROMISE DETECTED (Impossible Travel)' : 'Clean SIEM History', done: true, flagged: activeTxn.cyber_compromise_in_window },
    { id: 'device', name: '3. Device & IP Fingerprint', desc: `IP: ${activeTxn.ip || '185.15.2.22'} | Dev: ${activeTxn.device_id || 'dev_9999'}`, done: true },
    { id: 'graph', name: '4. Neo4j Graph Correlation', desc: activeTxn.dest_mule_cluster_id ? `MULE RING MATCH (${activeTxn.dest_mule_cluster_id})` : 'Graph Centrality Normal', done: true, flagged: Boolean(activeTxn.dest_mule_cluster_id) },
    { id: 'ai', name: '5. Supervised + Zero-Day AI Evaluation', desc: isComplete ? `LightGBM + IsoForest Scored (${evaluation.score}/100)` : 'Running ML Models...', done: isComplete, loading: !isComplete },
    { id: 'decision', name: '6. Unified Decision & Evidence Lock', desc: isComplete ? `Action Enforced: ${evaluation.action}` : 'Pending Final Verdict', done: isComplete, final: true }
  ];

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 shadow-lg select-none">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-4">
        <div>
          <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
            <Cpu className="w-4 h-4 text-soc-primary animate-pulse" />
            <span>Fusion Runtime Pipeline Lifecycle</span>
          </h3>
          <span className="text-[11px] font-mono text-soc-muted">
            Inspect transaction execution through the unified correlation engine
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-surface text-soc-primary border border-soc-primary/30">
          TXN: {activeTxn.txn_id || 'txn_demo_999'}
        </span>
      </div>

      {/* Vertical Lifecycle Execution Tree */}
      <div className="space-y-3 font-mono text-xs">
        {stages.map((stage, idx) => (
          <div key={stage.id} className="relative">
            <div className={`p-3 rounded-lg border flex items-start justify-between transition-all ${
              stage.flagged 
                ? 'bg-rose-500/10 border-rose-500/40 text-rose-400' 
                : stage.final && evaluation?.action === 'BLOCK'
                ? 'bg-rose-500/15 border-rose-500/50 text-rose-400 font-bold'
                : stage.done 
                ? 'bg-soc-surface border-soc-border text-soc-text' 
                : 'bg-soc-bg border-soc-border/50 text-soc-dim'
            }`}>
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  {stage.loading ? (
                    <Loader2 className="w-4 h-4 text-soc-primary animate-spin" />
                  ) : stage.flagged || (stage.final && evaluation?.action === 'BLOCK') ? (
                    <AlertTriangle className="w-4 h-4 text-rose-400 animate-pulse" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  )}
                </div>
                <div>
                  <div className="font-bold text-xs">{stage.name}</div>
                  <div className="text-[11px] text-soc-muted mt-0.5">{stage.desc}</div>
                </div>
              </div>

              {stage.final && evaluation && (
                <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                  evaluation.action === 'BLOCK' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}>
                  VERDICT: {evaluation.action}
                </span>
              )}
            </div>

            {idx < stages.length - 1 && (
              <div className="flex justify-center my-1">
                <ArrowDown className="w-3.5 h-3.5 text-soc-dim" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
