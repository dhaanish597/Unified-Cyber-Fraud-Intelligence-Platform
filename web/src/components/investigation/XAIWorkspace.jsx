import React from 'react';

export default function XAIWorkspace({ evaluation }) {
  if (!evaluation) return null;
  const { shap_features, counterfactual_sentence } = evaluation;

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl overflow-hidden shadow-lg select-none">
      <div className="p-3 border-b border-soc-border bg-soc-surface/50 flex items-center justify-between">
        <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">
          Explainability Workspace (XAI & Counterfactuals)
        </h3>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-bg text-soc-muted border border-soc-border">
          SHAP TreeExplainer
        </span>
      </div>

      <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* SHAP Waterfall Impact Bar Chart */}
        <div>
          <h4 className="text-[10px] uppercase text-soc-dim mb-3 font-mono font-semibold">
            Top Feature Risk Impacts (SHAP Values)
          </h4>
          <div className="space-y-2 font-mono">
            {shap_features?.map((f, i) => {
              const impact = f.impact;
              const width = Math.min(100, Math.max(8, Math.abs(impact) * 25));
              const isPositive = impact > 0;
              return (
                <div key={i} className="flex items-center text-xs">
                  <div className="w-32 truncate text-soc-muted mr-2" title={f.feature}>{f.feature}</div>
                  <div className="flex-1 flex items-center">
                    {!isPositive && <div className="flex-1 flex justify-end"><div className="h-1.5 bg-soc-success rounded-l" style={{ width: `${width}%` }}></div></div>}
                    {isPositive && <div className="flex-1"></div>}
                    <div className="w-px h-3 bg-soc-border mx-1"></div>
                    {isPositive && <div className="flex-1"><div className="h-1.5 bg-soc-danger rounded-r" style={{ width: `${width}%` }}></div></div>}
                    {!isPositive && <div className="flex-1"></div>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Counterfactual AI Panel */}
        {counterfactual_sentence && (
          <div className="border-t md:border-t-0 md:border-l border-soc-border pt-4 md:pt-0 md:pl-6 flex flex-col justify-center">
            <h4 className="text-[10px] uppercase text-soc-primary mb-2 font-mono font-semibold">
              Quantum-Aware Counterfactual Reasoning
            </h4>
            <div className="text-xs font-mono text-soc-text italic leading-relaxed border-l-2 border-soc-primary pl-3 py-1 bg-soc-surface/40 rounded-r">
              "{counterfactual_sentence.replace('Counterfactual: ', '')}"
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
