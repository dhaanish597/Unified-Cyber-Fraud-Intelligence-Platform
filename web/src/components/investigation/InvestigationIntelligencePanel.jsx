import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Layers, 
  Radio, 
  Activity, 
  GitCommit, 
  Award, 
  CheckCircle2, 
  AlertTriangle, 
  ChevronDown, 
  ChevronUp, 
  RefreshCw,
  Zap,
  Lock,
  ArrowRight,
  User,
  Share2,
  DollarSign
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');

export default function InvestigationIntelligencePanel({ caseId = 'CASE-2026-8942', activeTxn = null }) {
  const [brief, setBrief] = useState(null);
  const [expandedSection, setExpandedSection] = useState('narrative'); // narrative | burst | mule | quality | summary
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchInvestigationBrief();
  }, [caseId, activeTxn]);

  const fetchInvestigationBrief = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/investigation/analyse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: caseId,
          user_id: activeTxn?.user_id || 'usr_abc',
          amount: activeTxn?.amount || 750000.0,
          cyber_compromise_in_window: activeTxn?.cyber_compromise_in_window ?? true,
          dest_mule_cluster_id: activeTxn?.dest_mule_cluster_id || 'cluster_alpha'
        })
      });
      const data = await res.json();
      setBrief(data);
    } catch (e) {
      console.error("Investigation Brief fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !brief) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-soc-primary" />
        <span>Generating Network-Level Investigation Intelligence Brief for {caseId}...</span>
      </div>
    );
  }

  const { burst_attack_intelligence, graph_mule_intelligence, threat_correlation, decision_quality, fusion_investigation_summary } = brief;

  const toggleSection = (secKey) => {
    setExpandedSection(expandedSection === secKey ? null : secKey);
  };

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">
      
      {/* 1. ENTERPRISE INVESTIGATION BRIEF HEADER */}
      <div className="p-4 bg-soc-panel border border-soc-border rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400">
            <Layers className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
                NETWORK-LEVEL FRAUD INTELLIGENCE BRIEF #{brief.case_id}
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                LOSS PREVENTED: {fusion_investigation_summary.estimated_loss_prevented}
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1 flex items-center gap-3">
              {fusion_investigation_summary.attack_type}
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs">
          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">Decision Quality</span>
            <span className="font-bold text-emerald-400 text-[11px]">{decision_quality.decision_quality_score}% ({decision_quality.quality_tier})</span>
          </div>

          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">Threat Confidence</span>
            <span className="font-bold text-rose-400 text-[11px]">{fusion_investigation_summary.threat_confidence}</span>
          </div>

          <button 
            onClick={fetchInvestigationBrief}
            className="px-3 py-1.5 bg-soc-bg hover:bg-soc-border border border-soc-border rounded-lg text-soc-text flex items-center gap-1.5 transition-colors font-bold text-[11px]"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Re-Analyze</span>
          </button>
        </div>
      </div>

      {/* 2. MINIMAL EXPANDABLE INVESTIGATION MODULE CARDS */}
      <div className="space-y-2">
        
        {/* MODULE 3: THREAT CORRELATION & ATTACK NARRATIVE */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
          <button
            onClick={() => toggleSection('narrative')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-rose-500/20 text-rose-400">
                <GitCommit className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">1. Multi-Stage Attack Narrative & Threat Correlation</span>
                <div className="text-[10px] text-soc-muted">{threat_correlation.attack_narrative_title}</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 rounded">
                Stage 5 Execution Attempt
              </span>
              {expandedSection === 'narrative' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
            </div>
          </button>

          {expandedSection === 'narrative' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Correlated Attack Chain Flow</span>
              
              <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
                {threat_correlation.attack_chain?.map((stg) => (
                  <div key={stg.stage} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1 relative">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold text-soc-primary">STAGE {stg.stage}</span>
                      <span className="text-[9px] text-soc-dim">{stg.timestamp.split(' ')[1]}</span>
                    </div>
                    <div className="font-bold text-soc-text text-[11px]">{stg.name}</div>
                    <div className="text-[10px] text-soc-muted leading-tight">{stg.detail}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* MODULE 1: BURST ATTACK DETECTION */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
          <button
            onClick={() => toggleSection('burst')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-amber-500/20 text-amber-400">
                <Radio className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">2. Burst Attack Velocity Detection</span>
                <div className="text-[10px] text-soc-muted">{burst_attack_intelligence.burst_type} ({burst_attack_intelligence.entity_count} entities in {burst_attack_intelligence.time_window_seconds}s)</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 rounded">
                Severity: {burst_attack_intelligence.burst_severity}
              </span>
              {expandedSection === 'burst' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
            </div>
          </button>

          {expandedSection === 'burst' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <div className="text-[10px] text-soc-muted">
                <strong>Velocity Distribution:</strong> {burst_attack_intelligence.distribution}
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                {burst_attack_intelligence.burst_signals?.map((sig, i) => (
                  <div key={i} className="p-2.5 bg-soc-panel border border-soc-border rounded space-y-1">
                    <span className="text-[10px] text-soc-dim uppercase block">{sig.signal}</span>
                    <div className="font-bold text-soc-text">{sig.count} / Threshold {sig.threshold}</div>
                    <span className={`text-[9px] px-1.5 py-0.2 rounded font-bold inline-block ${
                      sig.status.includes('CRITICAL') || sig.status.includes('EXCEEDED') ? 'bg-rose-500/20 text-rose-300' : 'bg-emerald-500/20 text-emerald-300'
                    }`}>
                      {sig.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* MODULE 2: GRAPH MULE DISCOVERY */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
          <button
            onClick={() => toggleSection('mule')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-soc-primary/20 text-soc-primary">
                <Layers className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">3. Neo4j Graph Mule Ring Discovery</span>
                <div className="text-[10px] text-soc-muted">{graph_mule_intelligence.mule_ring_name}</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 rounded">
                Mule Ring Risk: {graph_mule_intelligence.ring_risk_score}%
              </span>
              {expandedSection === 'mule' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
            </div>
          </button>

          {expandedSection === 'mule' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Discovered Mule Ring Topology & Patterns</span>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <span className="text-[10px] text-soc-dim uppercase font-semibold">Graph Topology Signals:</span>
                  <ul className="space-y-1">
                    {graph_mule_intelligence.graph_patterns_discovered?.map((pat, i) => (
                      <li key={i} className="flex items-center gap-2 text-[11px] text-soc-text">
                        <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                        <span>{pat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="space-y-1.5">
                  <span className="text-[10px] text-soc-dim uppercase font-semibold">Discovered Mule Ring Members:</span>
                  <div className="space-y-1">
                    {graph_mule_intelligence.ring_members?.map((m, i) => (
                      <div key={i} className="p-2 bg-soc-panel border border-soc-border rounded text-[11px] flex justify-between items-center">
                        <span className="font-bold text-soc-text">{m.account}</span>
                        <span className="text-[10px] text-rose-400 font-bold">{m.type}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* MODULE 4: DECISION QUALITY SCORE */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
          <button
            onClick={() => toggleSection('quality')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-emerald-500/20 text-emerald-400">
                <Award className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">4. Multi-Vector Decision Quality Score</span>
                <div className="text-[10px] text-soc-muted">Model Agreement: {decision_quality.model_agreement_percent}% • Evidence Completeness: {decision_quality.evidence_completeness_percent}%</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded">
                Quality: {decision_quality.decision_quality_score}%
              </span>
              {expandedSection === 'quality' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
            </div>
          </button>

          {expandedSection === 'quality' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Explainable Feature Contributions to Quality Score</span>

              <div className="space-y-2">
                {decision_quality.explainable_contributions?.map((c, i) => (
                  <div key={i} className="p-2.5 bg-soc-panel border border-soc-border rounded flex justify-between items-center">
                    <div>
                      <span className="font-bold text-soc-text">{c.vector} (Weight: {c.weight * 100}%)</span>
                      <div className="text-[10px] text-soc-muted">{c.reason}</div>
                    </div>
                    <span className="font-mono font-bold text-rose-400 text-sm">{c.impact}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* MODULE 5: FUSION INVESTIGATION SUMMARY BRIEF */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
          <button
            onClick={() => toggleSection('summary')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-soc-primary/20 text-soc-primary">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">5. Fusion Investigation Executive Brief</span>
                <div className="text-[10px] text-soc-muted">Recommended Action: {fusion_investigation_summary.recommended_response}</div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-rose-500/10 text-rose-400 border border-rose-500/30 rounded">
                Executive Brief Ready
              </span>
              {expandedSection === 'summary' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
            </div>
          </button>

          {expandedSection === 'summary' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <div className="p-3 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Attack Type</span>
                  <div className="text-soc-text font-bold">{fusion_investigation_summary.attack_type}</div>
                </div>
                <div className="p-3 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Cyber Threat Classification</span>
                  <div className="text-rose-400 font-bold">{fusion_investigation_summary.cyber_threat}</div>
                </div>
                <div className="p-3 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Recommended Response</span>
                  <div className="text-rose-300 font-bold text-[11px]">{fusion_investigation_summary.recommended_response}</div>
                </div>
              </div>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
