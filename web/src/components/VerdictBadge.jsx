import React from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

export default function VerdictBadge({ evaluation, currentTxn }) {
  if (!evaluation || !currentTxn) {
    return (
      <div className="flex flex-col items-center gap-2">
        <div className="text-gray-500 animate-pulse text-lg">Awaiting Stream...</div>
      </div>
    );
  }

  const { action, score, reasons } = evaluation;
  let color = 'text-soc-success';
  let Icon = CheckCircle;
  let bg = 'bg-soc-success/20';
  let border = 'border-soc-success';

  if (action === 'BLOCK') {
    color = 'text-soc-danger';
    Icon = XCircle;
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
      <div className="text-gray-400 text-sm mb-2 font-mono">EVALUATING: {currentTxn.txn_id}</div>
      <div className={`flex items-center gap-4 px-8 py-4 rounded-2xl border-2 ${border} ${bg} backdrop-blur-sm mb-4`}>
        <Icon className={`w-12 h-12 ${color}`} />
        <div className="flex flex-col">
          <span className={`text-4xl font-black tracking-widest ${color}`}>{action}</span>
          <span className="text-gray-300 font-semibold mt-1">RISK SCORE: {score.toFixed(0)}/100</span>
        </div>
      </div>
      <div className="w-full max-w-md">
        <h4 className="text-xs uppercase text-gray-500 mb-2 font-semibold">Decision Reasons</h4>
        <ul className="text-sm text-gray-300 space-y-1">
          {reasons.map((r, i) => {
            if (r.startsWith('Counterfactual')) return null;
            return (
              <li key={i} className="flex gap-2">
                <span className="text-gray-500">•</span> 
                {r}
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
