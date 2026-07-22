import React, { useState } from 'react';
import { Sliders, ShieldCheck, AlertTriangle, CheckCircle2, RefreshCw, ArrowRight, Zap } from 'lucide-react';

export default function DecisionStabilityInspector({ trustData, action = 'BLOCK' }) {
  if (!trustData || !trustData.dsi) return null;

  const dsi = trustData.dsi;
  const isStable = dsi.tier === 'STABLE';

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl font-mono text-xs select-none space-y-3">
      
      {/* HEADER */}
      <div className="flex items-center justify-between border-b border-soc-border pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-soc-primary/20 border border-soc-primary/40 rounded-lg">
            <Sliders className="w-5 h-5 text-soc-primary animate-pulse" />
          </div>
          <div>
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <span>Decision Stability Index (DSI)</span>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${
                isStable ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
              }`}>
                {dsi.tier} ({dsi.stability_score}%)
              </span>
            </h3>
            <p className="text-[11px] text-soc-muted">
              Perturbation simulation proving decision robustness against minor feature variations
            </p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[9px] text-soc-muted uppercase">Robustness Score</div>
          <span className="text-base font-bold text-emerald-400">{dsi.stability_score}%</span>
        </div>
      </div>

      {/* FEATURE PERTURBATION TABLE */}
      <div className="space-y-2">
        <div className="text-[10px] font-bold text-soc-muted uppercase tracking-wider flex items-center gap-1.5">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>Feature Sensitivity Simulations</span>
        </div>

        <div className="space-y-2 font-mono text-xs">
          {dsi.simulations.map((sim, idx) => (
            <div 
              key={idx}
              className={`p-3 rounded-xl border flex flex-col md:flex-row md:items-center justify-between gap-2 transition-all ${
                sim.decision_changed
                  ? 'bg-amber-500/10 border-amber-500/40 text-amber-400'
                  : 'bg-soc-panel border-soc-border text-soc-text'
              }`}
            >
              <div className="space-y-0.5">
                <div className="font-bold flex items-center gap-2 text-xs">
                  <span>{sim.parameter}</span>
                  <span className="text-[10px] text-soc-muted font-normal">({sim.variation})</span>
                </div>
                {sim.note && <div className="text-[11px] text-amber-400/90 font-bold">{sim.note}</div>}
              </div>

              <div className="flex items-center gap-3 shrink-0">
                <div className="flex items-center gap-1.5 text-[11px] font-bold">
                  <span className="text-soc-muted">Result:</span>
                  <span>Risk {sim.resulting_score}</span>
                  <ArrowRight className="w-3 h-3 text-soc-dim" />
                  <span className={`px-2 py-0.5 rounded border ${
                    sim.resulting_action === 'BLOCK' ? 'bg-rose-500/20 text-rose-400 border-rose-500/40' : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                  }`}>
                    {sim.resulting_action}
                  </span>
                </div>

                <span className={`px-2 py-0.5 text-[10px] font-bold rounded border ${
                  sim.decision_changed ? 'bg-amber-500/20 text-amber-400 border-amber-500/40' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                }`}>
                  {sim.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
