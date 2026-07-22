import React, { useState } from 'react';
import { 
  ShieldCheck, 
  Activity, 
  Layers, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  FileText, 
  Lock, 
  Cpu, 
  Share2, 
  Smartphone, 
  Radio, 
  Database,
  Sliders,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function InvestigationTrustPanel({ trustData, action = 'BLOCK' }) {
  const [showDetails, setShowDetails] = useState(false);

  if (!trustData) return null;

  const iti = trustData.iti || 98.0;
  const sdqs = trustData.sdqs || {
    identity_confidence: 92,
    device_trust: 14,
    transaction_context: 98,
    cyber_visibility: 91,
    graph_coverage: 96,
    historical_context: 90,
    behavior_profile_completeness: 94,
    telemetry_quality: 98,
    evidence_integrity: 100,
    audit_readiness: 100
  };

  const eqs = trustData.eqs || {
    score: 100,
    checklist: [
      { name: 'Timeline', present: true },
      { name: 'Cyber SIEM Logs', present: true },
      { name: 'Transaction History', present: true },
      { name: 'Graph Snapshot', present: true },
      { name: 'XAI SHAP Explanation', present: true },
      { name: 'Counterfactual Sentence', present: true },
      { name: 'Analyst Notes', present: true },
      { name: 'Digital Signature', present: true },
      { name: 'Blockchain Ledger Record', present: true }
    ],
    missing_items: []
  };

  const gri = trustData.gri || {
    overall_score: 93,
    known_mule_ring_confidence: 96,
    pagerank_confidence: 94,
    community_detection_certainty: 91,
    historical_node_matches: 18,
    graph_coverage_percent: 96
  };

  const attribution = trustData.threat_attribution || {
    "Account Takeover": 96.0,
    "Credential Stuffing": 88.0,
    "Money Mule Network": 78.0,
    "SIM Swap": 42.0,
    "QR Scam": 18.0,
    "Business Email Compromise": 12.0,
    "Insider Fraud": 3.0
  };

  const isEqsComplete = eqs.score === 100;

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl font-mono text-xs select-none space-y-4">
      
      {/* HEADER & OVERARCHING ITI SCORE */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-soc-border pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2.5 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <ShieldCheck className="w-6 h-6 text-soc-primary animate-pulse" />
          </div>
          <div>
            <h2 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <span>Investigation Trust Index (ITI)</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                REGULATOR READY
              </span>
            </h2>
            <p className="text-[11px] text-soc-muted">
              Multi-dimensional investigation confidence, graph reliability, & threat attribution
            </p>
          </div>
        </div>

        {/* OVERARCHING SCORE BANNER */}
        <div className="flex items-center gap-3 bg-soc-bg px-4 py-2 rounded-xl border border-soc-border">
          <div className="text-right">
            <div className="text-[9px] text-soc-muted uppercase font-bold">Investigation Trust</div>
            <div className="text-lg font-black font-mono text-emerald-400">
              {iti} <span className="text-xs text-soc-muted font-normal">/ 100</span>
            </div>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="p-1.5 bg-soc-panel hover:bg-soc-border rounded-lg text-soc-text transition-colors"
          >
            {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* METRIC CARDS STRIP (4 CARDS) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        
        {/* CARD 1: EVIDENCE QUALITY SCORE */}
        <div className="bg-soc-panel border border-soc-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-soc-muted font-bold uppercase">Evidence Quality (EQS)</span>
            <FileText className="w-4 h-4 text-soc-primary" />
          </div>
          <div className="my-1.5 flex items-baseline justify-between">
            <span className={`text-xl font-bold font-mono ${isEqsComplete ? 'text-emerald-400' : 'text-amber-400'}`}>
              {eqs.score}%
            </span>
            <span className="text-[10px] text-soc-muted">
              {isEqsComplete ? '10/10 Artifacts Signed' : `${eqs.missing_items.length} Missing`}
            </span>
          </div>
          <div className="w-full bg-soc-bg rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-500 h-full transition-all" style={{ width: `${eqs.score}%` }} />
          </div>
        </div>

        {/* CARD 2: GRAPH RELIABILITY INDEX */}
        <div className="bg-soc-panel border border-soc-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-soc-muted font-bold uppercase">Graph Reliability (GRI)</span>
            <Share2 className="w-4 h-4 text-soc-primary" />
          </div>
          <div className="my-1.5 flex items-baseline justify-between">
            <span className="text-xl font-bold font-mono text-soc-text">
              {gri.overall_score}%
            </span>
            <span className="text-[10px] text-emerald-400 font-bold">
              Mule Ring {gri.known_mule_ring_confidence}%
            </span>
          </div>
          <div className="w-full bg-soc-bg rounded-full h-1.5 overflow-hidden">
            <div className="bg-soc-primary h-full transition-all" style={{ width: `${gri.overall_score}%` }} />
          </div>
        </div>

        {/* CARD 3: SECURITY DATA QUALITY */}
        <div className="bg-soc-panel border border-soc-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-soc-muted font-bold uppercase">Data Quality (SDQS)</span>
            <Database className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="my-1.5 flex items-baseline justify-between">
            <span className="text-xl font-bold font-mono text-emerald-400">
              95.4 / 100
            </span>
            <span className="text-[10px] text-soc-muted">10 Dimensions</span>
          </div>
          <div className="w-full bg-soc-bg rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-400 h-full transition-all" style={{ width: `95.4%` }} />
          </div>
        </div>

        {/* CARD 4: THREAT ATTRIBUTION HIGHLIGHT */}
        <div className="bg-soc-panel border border-soc-border rounded-xl p-3 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <span className="text-[10px] text-soc-muted font-bold uppercase">Primary Threat Vector</span>
            <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
          </div>
          <div className="my-1.5 flex items-baseline justify-between">
            <span className="text-sm font-bold font-mono text-rose-400 truncate">
              Account Takeover
            </span>
            <span className="text-sm font-bold text-rose-400">
              96%
            </span>
          </div>
          <div className="w-full bg-soc-bg rounded-full h-1.5 overflow-hidden">
            <div className="bg-rose-500 h-full transition-all" style={{ width: `96%` }} />
          </div>
        </div>

      </div>

      {/* THREAT ATTRIBUTION PROBABILITY DISTRIBUTION & DATA QUALITY BREAKDOWN */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* LEFT COLUMN: THREAT ATTRIBUTION PROBABILITY BARS (6/12) */}
        <div className="lg:col-span-6 bg-soc-panel border border-soc-border rounded-xl p-3.5 space-y-2.5">
          <div className="text-[10px] font-bold text-soc-muted uppercase tracking-wider flex items-center justify-between border-b border-soc-border pb-2">
            <span className="flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-rose-400" />
              <span>Multi-Class Threat Attribution Probability Distribution</span>
            </span>
            <span className="text-soc-primary font-bold">Competing Hypotheses</span>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {Object.entries(attribution).map(([threat, prob]) => (
              <div key={threat} className="space-y-1">
                <div className="flex justify-between text-[11px]">
                  <span className="font-bold text-soc-text">{threat}</span>
                  <span className={`font-bold ${prob >= 80 ? 'text-rose-400' : prob >= 40 ? 'text-amber-400' : 'text-soc-muted'}`}>
                    {prob}%
                  </span>
                </div>
                <div className="w-full bg-soc-bg rounded-full h-2 overflow-hidden border border-soc-border/40">
                  <div 
                    className={`h-full transition-all ${
                      prob >= 80 ? 'bg-rose-500' : prob >= 40 ? 'bg-amber-500' : 'bg-soc-dim/60'
                    }`} 
                    style={{ width: `${prob}%` }} 
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT COLUMN: EVIDENCE QUALITY CHECKLIST (6/12) */}
        <div className="lg:col-span-6 bg-soc-panel border border-soc-border rounded-xl p-3.5 space-y-2.5">
          <div className="text-[10px] font-bold text-soc-muted uppercase tracking-wider flex items-center justify-between border-b border-soc-border pb-2">
            <span className="flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-400" />
              <span>Evidence Package Integrity (EQS)</span>
            </span>
            <span className={`font-bold ${isEqsComplete ? 'text-emerald-400' : 'text-amber-400'}`}>
              {isEqsComplete ? '100% COMPLETE' : 'MISSING ARTIFACTS'}
            </span>
          </div>

          {!isEqsComplete && (
            <div className="p-2.5 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 text-[11px] font-mono flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0" />
              <span>Missing Artifacts: <strong>{eqs.missing_items.join(', ')}</strong></span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
            {eqs.checklist.map((item, idx) => (
              <div 
                key={idx} 
                className={`p-2 rounded-lg border flex items-center justify-between ${
                  item.present ? 'bg-soc-surface border-soc-border text-soc-text' : 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                }`}
              >
                <span className="font-bold truncate">{item.name}</span>
                {item.present ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                ) : (
                  <XCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                )}
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
