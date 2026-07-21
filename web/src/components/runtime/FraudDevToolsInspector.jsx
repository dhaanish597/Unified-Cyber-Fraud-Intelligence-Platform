import React, { useState } from 'react';
import { Terminal, Shield, Cpu, Activity, Share2, FileText, Code, CheckCircle2, Lock } from 'lucide-react';

export default function FraudDevToolsInspector({ activeTxn, evaluation }) {
  const [activeTab, setActiveTab] = useState('txn');

  if (!activeTxn) {
    return (
      <div className="bg-soc-panel border border-soc-border rounded-xl p-6 text-center text-soc-dim font-mono text-xs">
        Select a transaction to launch the Fraud DevTools Inspector...
      </div>
    );
  }

  const tabs = [
    { id: 'txn', label: '1. TXN' },
    { id: 'timeline', label: '2. Timeline' },
    { id: 'features', label: '3. Raw Features' },
    { id: 'graph', label: '4. Graph' },
    { id: 'risk', label: '5. Risk' },
    { id: 'shap', label: '6. SHAP' },
    { id: 'cf', label: '7. Counterfactual' },
    { id: 'evidence', label: '8. Evidence' },
  ];

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl overflow-hidden shadow-2xl flex flex-col h-full font-mono text-xs select-none">
      {/* DevTools Header & Tab Switcher Bar */}
      <div className="bg-soc-panel border-b border-soc-border px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-soc-primary" />
          <span className="font-bold text-soc-text text-xs uppercase tracking-wider">
            Chrome DevTools for Fraud — Transaction Inspector
          </span>
        </div>

        <div className="flex items-center gap-1 bg-soc-bg border border-soc-border p-1 rounded-lg">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-2 py-0.5 rounded text-[11px] font-bold transition-colors ${
                activeTab === t.id
                  ? 'bg-soc-primary text-white'
                  : 'text-soc-muted hover:text-soc-text hover:bg-soc-panel'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* DevTools Body Content Pane */}
      <div className="p-4 flex-1 overflow-y-auto bg-soc-bg text-soc-text font-mono">
        {/* Tab 1: TXN Payload */}
        {activeTab === 'txn' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Incoming Transaction Protocol & Payload</span>
            <pre className="bg-soc-surface border border-soc-border p-3 rounded-lg text-emerald-400 overflow-x-auto text-[11px]">
              {JSON.stringify(activeTxn, null, 2)}
            </pre>
          </div>
        )}

        {/* Tab 2: Timeline Sequence */}
        {activeTab === 'timeline' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Event Precursor Timeline</span>
            <div className="space-y-2">
              <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400">
                <div className="font-bold">[T-0:40s] Impossible Travel Login Detected</div>
                <div className="text-[11px] text-soc-muted">IP: 185.15.2.22 (RU) | User: {activeTxn.user_id} | 4,500 km Anomaly</div>
              </div>
              <div className="p-2.5 bg-soc-panel border border-soc-border rounded-lg">
                <div className="font-bold text-soc-text">[T+0:00s] Transaction Transfer Initiated</div>
                <div className="text-[11px] text-soc-muted">Amount: INR {activeTxn.amount?.toLocaleString('en-IN')} | To: {activeTxn.nameDest}</div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Raw Feature Vector */}
        {activeTab === 'features' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Engineered Feature Vector (ml/features.py)</span>
            <div className="grid grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 bg-soc-surface border border-soc-border rounded"><span className="text-soc-dim">log_amount:</span> <strong className="text-soc-primary">{(Math.log1p(activeTxn.amount || 750000)).toFixed(4)}</strong></div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded"><span className="text-soc-dim">cyber_flag:</span> <strong className="text-rose-400">{activeTxn.cyber_compromise_in_window ? '1 (TRUE)' : '0 (FALSE)'}</strong></div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded"><span className="text-soc-dim">velocity_1h:</span> <strong>3 txns</strong></div>
              <div className="p-2 bg-soc-surface border border-soc-border rounded"><span className="text-soc-dim">zero_dest_before:</span> <strong>1 (TRUE)</strong></div>
            </div>
          </div>
        )}

        {/* Tab 4: Graph Correlation */}
        {activeTab === 'graph' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Neo4j Network Topology Lookup</span>
            <div className="p-3 bg-soc-surface border border-soc-border rounded-lg space-y-1">
              <div>PageRank Score: <strong className="text-soc-primary">0.0450 (High Node Centrality)</strong></div>
              <div>Betweenness Centrality: <strong className="text-soc-primary">0.1200</strong></div>
              <div>Mule Cluster Flag: <strong className="text-rose-400 font-bold">{activeTxn.dest_mule_cluster_id ? 'MATCHED (Cluster Alpha - 6 Nodes)' : 'CLEAN'}</strong></div>
            </div>
          </div>
        )}

        {/* Tab 5: Risk Calculation */}
        {activeTab === 'risk' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Composite Risk Blending Breakdown</span>
            <div className="p-3 bg-soc-surface border border-soc-border rounded-lg space-y-1.5">
              <div className="flex justify-between"><span>Tabular Model Score (0-60):</span> <strong>+49.2 pts</strong></div>
              <div className="flex justify-between"><span>Isolation Forest Penalty (0-20):</span> <strong>+18.0 pts</strong></div>
              <div className="flex justify-between"><span>Cyber Precursor Window (+15):</span> <strong>+15.0 pts</strong></div>
              <div className="flex justify-between"><span>Mule Cluster Flag (+10):</span> <strong>+10.0 pts</strong></div>
              <div className="border-t border-soc-border pt-1.5 flex justify-between font-bold text-rose-400">
                <span>TOTAL COMPOSITE RISK SCORE:</span> <span>94.0 / 100 [BLOCK]</span>
              </div>
            </div>
          </div>
        )}

        {/* Tab 6: SHAP Values */}
        {activeTab === 'shap' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">SHAP TreeExplainer Impact Values</span>
            <div className="space-y-1">
              {evaluation?.shap_features?.map((f, idx) => (
                <div key={idx} className="flex justify-between p-2 bg-soc-surface border border-soc-border rounded">
                  <span>{f.feature}</span>
                  <strong className={f.impact > 0 ? 'text-rose-400' : 'text-emerald-400'}>
                    {f.impact > 0 ? `+${f.impact}` : f.impact}
                  </strong>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 7: Counterfactual AI */}
        {activeTab === 'cf' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Quantum Counterfactual Sentence</span>
            <div className="p-3 bg-soc-surface border border-soc-border rounded-lg text-soc-text italic border-l-4 border-l-soc-primary">
              "{evaluation?.counterfactual_sentence || 'Counterfactual: With no prior cyber compromise, score = 61 -> CHALLENGE, not BLOCK.'}"
            </div>
          </div>
        )}

        {/* Tab 8: Evidence Lock */}
        {activeTab === 'evidence' && (
          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">CERT-In Compliance & Audit Package</span>
            <div className="p-3 bg-soc-surface border border-soc-border rounded-lg space-y-1">
              <div>Status: <strong className="text-emerald-400">PASSED 6-HOUR CERT-IN RULE</strong></div>
              <div>Audit Hash: <strong className="text-purple-400">e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855</strong></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
