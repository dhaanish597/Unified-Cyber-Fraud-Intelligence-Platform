import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX, 
  Clock, 
  ChevronDown, 
  ChevronUp, 
  Zap, 
  User, 
  Smartphone, 
  Globe, 
  Activity, 
  Radio, 
  Layers, 
  RefreshCw,
  AlertTriangle,
  CheckCircle2,
  Lock,
  ExternalLink
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function SessionTrustPassportPanel({ sessionId = 'SESS_9921_CRITICAL', activeTxn = null }) {
  const [passport, setPassport] = useState(null);
  const [expandedCheckpoint, setExpandedCheckpoint] = useState(null); // 'chk1', 'chk2', etc.
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSessionPassport();
  }, [sessionId, activeTxn]);

  const fetchSessionPassport = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/session/analyse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: activeTxn?.user_id || 'usr_abc',
          device_id: activeTxn?.device_id || 'dev_9999',
          ip: activeTxn?.ip || '185.15.2.22',
          cyber_compromise_in_window: activeTxn?.cyber_compromise_in_window ?? true,
          dest_mule_cluster_id: activeTxn?.dest_mule_cluster_id || 'cluster_alpha'
        })
      });
      const data = await res.json();
      setPassport(data);
    } catch (e) {
      console.error("Session Trust Passport fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !passport) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-soc-primary" />
        <span>Executing 6-Checkpoint Pre-Transaction Session Pipeline for {sessionId}...</span>
      </div>
    );
  }

  const { decision, overall_trust, monitoring_level, expiry, checkpoints, performance_metrics } = passport;

  const isBlock = decision === 'BLOCK';
  const isChallenge = decision === 'CHALLENGE';

  const toggleCheckpoint = (chkKey) => {
    setExpandedCheckpoint(expandedCheckpoint === chkKey ? null : chkKey);
  };

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">
      
      {/* 1. PRIMARY PASSPORT CARD (COMPACT HIGH-IMPACT HEADER) */}
      <div className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-4 shadow-lg transition-all ${
        isBlock 
          ? 'bg-rose-500/10 border-rose-500/40 shadow-rose-500/5' 
          : (isChallenge ? 'bg-amber-500/10 border-amber-500/40 shadow-amber-500/5' : 'bg-emerald-500/10 border-emerald-500/40')
      }`}>
        <div className="flex items-center gap-4">
          <div className={`p-3 rounded-xl border ${
            isBlock ? 'bg-rose-500/20 border-rose-500/40 text-rose-400' : (isChallenge ? 'bg-amber-500/20 border-amber-500/40 text-amber-400' : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400')
          }`}>
            {isBlock ? <ShieldX className="w-7 h-7 animate-pulse" /> : (isChallenge ? <ShieldAlert className="w-7 h-7" /> : <ShieldCheck className="w-7 h-7" />)}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
                PRE-TRANSACTION SESSION PASSPORT #{passport.session_id}
              </span>
              <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded border ${
                monitoring_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              }`}>
                MONITORING: {monitoring_level}
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1 flex items-center gap-3">
              PRE-TRANSACTION VERDICT: <span className={isBlock ? 'text-rose-400' : (isChallenge ? 'text-amber-400' : 'text-emerald-400')}>{decision}</span>
              <span className="text-xs text-soc-dim font-normal">| Overall Session Trust: <strong className="text-soc-text font-black">{overall_trust}%</strong></span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs">
          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase flex items-center gap-1">
              <Clock className="w-3 h-3 text-soc-primary" />
              <span>Passport Expiry</span>
            </span>
            <span className="font-bold text-soc-text text-[11px]">{expiry}</span>
          </div>

          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase flex items-center gap-1">
              <Zap className="w-3 h-3 text-amber-400" />
              <span>Pipeline Latency</span>
            </span>
            <span className="font-bold text-amber-400 text-[11px]">{performance_metrics?.total_latency_ms} ms</span>
          </div>

          <button 
            onClick={fetchSessionPassport}
            className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border rounded-lg text-soc-text flex items-center gap-1.5 transition-colors font-bold text-[11px]"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Recalculate</span>
          </button>
        </div>
      </div>

      {/* 2. EXPANDABLE 6-CHECKPOINT PIPELINE CARDS */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-[11px] text-soc-dim px-1 font-bold uppercase tracking-wider">
          <span>Pre-Transaction Sequential Pipeline Checkpoints (Click to Expand)</span>
          <span>6 Checkpoints Verified</span>
        </div>

        {[
          { id: 'chk1', key: 'checkpoint_1_identity', title: 'Checkpoint 1: Identity Intelligence', icon: User, data: checkpoints.checkpoint_1_identity },
          { id: 'chk2', key: 'checkpoint_2_device', title: 'Checkpoint 2: Device Intelligence', icon: Smartphone, data: checkpoints.checkpoint_2_device },
          { id: 'chk3', key: 'checkpoint_3_session', title: 'Checkpoint 3: Session Intelligence', icon: Globe, data: checkpoints.checkpoint_3_session },
          { id: 'chk4', key: 'checkpoint_4_behavior', title: 'Checkpoint 4: Behavior Intelligence', icon: Activity, data: checkpoints.checkpoint_4_behavior },
          { id: 'chk5', key: 'checkpoint_5_cyber', title: 'Checkpoint 5: Cyber Threat Intelligence (MITRE)', icon: Radio, data: checkpoints.checkpoint_5_cyber },
          { id: 'chk6', key: 'checkpoint_6_graph', title: 'Checkpoint 6: Graph Intelligence (Neo4j)', icon: Layers, data: checkpoints.checkpoint_6_graph }
        ].map((chk) => {
          const Icon = chk.icon;
          const isExpanded = expandedCheckpoint === chk.id;
          const score = chk.data?.score ?? 100;
          const isLowScore = score < 50;

          return (
            <div key={chk.id} className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
              <button
                onClick={() => toggleCheckpoint(chk.id)}
                className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded ${isLowScore ? 'bg-rose-500/20 text-rose-400' : 'bg-soc-bg text-soc-primary'}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-bold text-soc-text text-xs">{chk.title}</span>
                    <div className="text-[10px] text-soc-muted truncate max-w-xl">
                      {chk.data?.reasons?.[0] || 'Checkpoint evaluation completed'}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className={`font-mono font-bold text-xs ${isLowScore ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {score}% Trust
                    </span>
                    <div className="text-[10px] text-soc-dim">{chk.data?.execution_time_ms} ms</div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
                </div>
              </button>

              {/* EXPANDED ON-DEMAND DETAILS */}
              {isExpanded && (
                <div className="p-3 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
                  
                  {/* MITRE ATT&CK Mapping Badges for Cyber Checkpoint */}
                  {chk.data?.mitre_techniques?.length > 0 && (
                    <div className="space-y-1.5">
                      <span className="text-[10px] text-soc-dim uppercase font-bold">Mapped MITRE ATT&CK Techniques:</span>
                      <div className="flex flex-wrap gap-2">
                        {chk.data.mitre_techniques.map((m, i) => (
                          <span key={i} className="px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30 text-rose-300 text-[10px] font-bold flex items-center gap-1">
                            <ExternalLink className="w-3 h-3 text-rose-400" />
                            <span>{m.id}: {m.name} ({m.tactic})</span>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Relationship Summary for Graph Checkpoint */}
                  {chk.data?.relationship_summary && (
                    <div className="p-2 bg-soc-panel border border-soc-border rounded text-[11px]">
                      <span className="text-[10px] text-soc-dim uppercase block font-bold">Neo4j Graph Relationship Query Result:</span>
                      <span className="text-soc-text font-bold">{chk.data.relationship_summary}</span>
                    </div>
                  )}

                  {/* Reasons & Signals List */}
                  <div className="space-y-1">
                    <span className="text-[10px] text-soc-dim uppercase font-bold">Evaluated Intelligence Signals:</span>
                    <ul className="space-y-1">
                      {chk.data?.reasons?.map((r, i) => (
                        <li key={i} className="flex items-center gap-2 text-[11px] text-soc-text">
                          <span className="w-1.5 h-1.5 rounded-full bg-soc-primary" />
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
}
