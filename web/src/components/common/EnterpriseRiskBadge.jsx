import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function EnterpriseRiskBadge({ evaluation, currentTxn, size = 'md' }) {
  if (!evaluation || !currentTxn) {
    return (
      <div className="flex flex-col items-center gap-2">
        <div className="text-soc-dim animate-pulse text-sm font-mono">Awaiting Transaction Evaluation...</div>
      </div>
    );
  }

  const { action, score, reasons } = evaluation;
  let color = 'text-soc-success';
  let Icon = ShieldCheck;
  let bg = 'bg-soc-success/20';
  let border = 'border-soc-success';

  if (action === 'BLOCK') {
    color = 'text-soc-danger';
    Icon = ShieldAlert;
    bg = 'bg-soc-danger/20';
    border = 'border-soc-danger';
  } else if (action === 'CHALLENGE') {
    color = 'text-soc-warning';
    Icon = AlertTriangle;
    bg = 'bg-soc-warning/20';
    border = 'border-soc-warning';
  }

  return (
    <div className="relative z-10 flex flex-col items-center w-full">
      <div className="text-soc-dim text-xs mb-2 font-mono">EVALUATING: {currentTxn.txn_id}</div>
      <div className={`flex items-center gap-4 px-6 py-3 rounded-xl border-2 ${border} ${bg} backdrop-blur-sm mb-3 shadow-lg`}>
        <Icon className={`w-10 h-10 ${color}`} />
        <div className="flex flex-col">
          <span className={`text-3xl font-mono font-black tracking-widest ${color}`}>{action}</span>
          <span className="text-soc-text font-mono font-semibold text-xs mt-0.5">RISK SCORE: {Math.round(score)}/100</span>
        </div>
      </div>
      {reasons && reasons.length > 0 && (
        <div className="w-full max-w-md bg-soc-surface p-3 rounded-lg border border-soc-border">
          <h4 className="text-[10px] uppercase text-soc-dim mb-1.5 font-mono font-semibold">Decision Vectors</h4>
          <ul className="text-xs text-soc-text font-mono space-y-1">
            {reasons.map((r, i) => {
              if (r.startsWith('Counterfactual')) return null;
              return (
                <li key={i} className="flex gap-2">
                  <span className="text-soc-primary">•</span> 
                  {r}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}
