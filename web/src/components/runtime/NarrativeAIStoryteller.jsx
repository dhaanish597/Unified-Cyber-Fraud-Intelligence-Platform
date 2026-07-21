import React from 'react';
import { Sparkles, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function NarrativeAIStoryteller({ activeTxn, evaluation }) {
  if (!activeTxn || !evaluation) return null;

  const narrativeSteps = [
    { label: 'Transaction Accepted', status: 'normal', desc: `${activeTxn.type || 'TRANSFER'} of INR ${activeTxn.amount?.toLocaleString('en-IN')}` },
    { label: 'Amount Evaluation', status: activeTxn.amount > 500000 ? 'warning' : 'normal', desc: activeTxn.amount > 500000 ? 'High-Value Transfer' : 'Normal Amount' },
    { label: 'Behavior Profile', status: 'warning', desc: 'Abnormal User Velocity (3 txns in same step)' },
    { label: 'Cyber SIEM Lookup', status: activeTxn.cyber_compromise_in_window ? 'danger' : 'normal', desc: activeTxn.cyber_compromise_in_window ? 'Credential Theft & Impossible Travel Login' : 'Clean Login' },
    { label: 'Graph Topology', status: activeTxn.dest_mule_cluster_id ? 'danger' : 'normal', desc: activeTxn.dest_mule_cluster_id ? 'Beneficiary Matched Mule Ring Cluster' : 'Clean Beneficiary' },
    { label: 'AI Risk Engine Verdict', status: evaluation.action === 'BLOCK' ? 'danger' : 'warning', desc: `${evaluation.action} (Composite Score ${Math.round(evaluation.score)}/100)` }
  ];

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 shadow-lg select-none">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-soc-primary" />
          <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">
            Narrative AI Storyteller — Step-by-Step Investigation Story
          </h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-surface text-soc-muted border border-soc-border">
          Human-Readable Explainability
        </span>
      </div>

      {/* Horizontal Story Sequence Flow */}
      <div className="flex flex-wrap md:flex-nowrap items-center gap-2 font-mono overflow-x-auto py-2">
        {narrativeSteps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className={`p-3 rounded-lg border flex-1 min-w-[140px] text-xs ${
              step.status === 'danger'
                ? 'bg-rose-500/10 border-rose-500/40 text-rose-400 font-bold'
                : step.status === 'warning'
                ? 'bg-amber-500/10 border-amber-500/40 text-amber-400 font-bold'
                : 'bg-soc-surface border-soc-border text-soc-text'
            }`}>
              <div className="text-[10px] text-soc-dim uppercase font-semibold mb-0.5">{step.label}</div>
              <div className="text-xs truncate" title={step.desc}>{step.desc}</div>
            </div>

            {idx < narrativeSteps.length - 1 && (
              <ArrowRight className="w-4 h-4 text-soc-dim shrink-0 hidden md:block" />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}
