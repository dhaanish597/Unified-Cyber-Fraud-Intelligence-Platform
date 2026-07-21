import React from 'react';
import { Search, CheckCircle2, ArrowRight, ShieldAlert, History } from 'lucide-react';
import EnterpriseBadge from '../common/EnterpriseBadge';

export default function SimilarIncidentSearch({ activeCase }) {
  const similarCases = [
    {
      id: 'CASE-2026-7821',
      match: '92% Similarity',
      action: 'BLOCK',
      amount: 'INR 1,200,000.00',
      reason: 'Impossible travel login followed by mule account transfer',
      recovered: 'Recovered INR 12,000,000.00',
      status: 'RESOLVED & REPORTED'
    },
    {
      id: 'CASE-2026-6145',
      match: '89% Similarity',
      action: 'BLOCK',
      amount: 'INR 800,000.00',
      reason: 'Matched Mule Cluster Alpha (6 shared device accounts)',
      recovered: 'Recovered INR 8,000,000.00',
      status: 'RESOLVED & REPORTED'
    }
  ];

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-soc-primary" />
          <div>
            <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
              Similar Historical Incident Search
            </h3>
            <span className="text-[10px] text-soc-muted">
              Learn from historical case precedents and past recovery outcomes
            </span>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-soc-primary/10 text-soc-primary border border-soc-primary/30">
          KNOWLEDGE GRAPH MATCH
        </span>
      </div>

      <div className="space-y-2">
        {similarCases.map((c) => (
          <div key={c.id} className="p-3 bg-soc-panel border border-soc-border rounded-lg flex items-center justify-between hover:border-soc-primary/50 transition-colors">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="font-bold text-soc-primary">{c.id}</span>
                <span className="px-2 py-0.2 text-[10px] bg-emerald-500/20 text-emerald-400 font-bold rounded border border-emerald-500/40">
                  {c.match}
                </span>
                <EnterpriseBadge action={c.action} score={90} size="sm" />
              </div>
              <p className="text-[11px] text-soc-muted">{c.reason}</p>
              <div className="text-[10px] text-emerald-400 font-bold">{c.recovered}</div>
            </div>

            <button className="px-3 py-1 bg-soc-surface hover:bg-soc-border border border-soc-border text-soc-text rounded text-xs font-bold flex items-center gap-1 transition-colors">
              <span>Inspect Case</span>
              <ArrowRight className="w-3.5 h-3.5 text-soc-primary" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
