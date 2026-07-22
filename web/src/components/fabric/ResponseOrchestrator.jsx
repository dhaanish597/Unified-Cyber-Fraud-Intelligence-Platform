import React, { useState, useEffect } from 'react';
import { 
  Play, 
  CheckCircle2, 
  Lock, 
  ShieldAlert, 
  Zap, 
  Send, 
  Bell, 
  FileText, 
  Cpu, 
  ChevronRight,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  RotateCcw,
  AlertTriangle,
  UserCheck,
  Smartphone,
  Globe,
  Radio,
  ExternalLink
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function ResponseOrchestrator({ activeCase, onDownloadReport }) {
  const [soarData, setSoarData] = useState(null);
  const [executionResult, setExecutionResult] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [expandedSection, setExpandedSection] = useState('actions'); // actions | playbook | workflow | notifications | timeline
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSoarRecommendation();
  }, [activeCase]);

  const fetchSoarRecommendation = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/response/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: activeCase?.user_id || 'usr_abc',
          amount: activeCase?.amount || 750000.0,
          cyber_compromise_in_window: activeCase?.cyber_compromise_in_window ?? true
        })
      });
      const data = await res.json();
      setSoarData(data);
    } catch (e) {
      console.error("SOAR recommendation error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleExecutePlaybook = async () => {
    setIsExecuting(true);
    try {
      const res = await fetch(`${API_BASE}/response/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: activeCase?.id || 'CASE-2026-8942',
          user_id: activeCase?.user_id || 'usr_abc',
          amount: activeCase?.amount || 750000.0,
          approval_mode: 'AUTOMATIC_EXECUTION'
        })
      });
      const data = await res.json();
      setExecutionResult(data);
      if (onDownloadReport) onDownloadReport();
    } catch (e) {
      console.error("SOAR execution error:", e);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleRollback = async () => {
    try {
      const res = await fetch(`${API_BASE}/response/rollback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: executionResult?.workflow_id || 'SOAR_WF_88291',
          reason: 'SOC Lead Manual Override'
        })
      });
      const data = await res.json();
      alert(`SOAR Workflow Rolled Back: ${data.reason}`);
      setExecutionResult(null);
    } catch (e) {
      console.error("SOAR rollback error:", e);
    }
  };

  if (loading || !soarData) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-soc-primary" />
        <span>Evaluating SOAR Response Playbook Recommendations...</span>
      </div>
    );
  }

  const { primary_verdict, matched_playbook, recommended_actions, approval_type, execution_latency_ms } = soarData;

  const toggleSection = (secKey) => {
    setExpandedSection(expandedSection === secKey ? null : secKey);
  };

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">
      
      {/* 1. SOAR ORCHESTRATION HEADER STRIP */}
      <div className="p-4 bg-soc-panel border border-soc-border rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-soc-primary/20 border border-soc-primary/40 rounded-xl text-soc-primary">
            <Zap className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
                FUSION SOAR RESPONSE ORCHESTRATOR
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                PLAYBOOK: {matched_playbook?.id}
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1 flex items-center gap-3">
              RECOMMENDED VERDICT: <span className="text-rose-400">{primary_verdict}</span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex flex-col text-right">
            <span className="text-[10px] text-soc-dim uppercase">SOAR Latency</span>
            <span className="font-bold text-amber-400 text-sm">{execution_latency_ms} ms</span>
          </div>

          {!executionResult ? (
            <button
              onClick={handleExecutePlaybook}
              disabled={isExecuting}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-50 text-white rounded-lg font-bold flex items-center gap-2 transition-all shadow-lg shadow-rose-950/40"
            >
              {isExecuting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>{isExecuting ? 'ORCHESTRATING SOAR WORKFLOW...' : 'EXECUTE RESPONSE WORKFLOW'}</span>
            </button>
          ) : (
            <div className="flex items-center gap-3">
              <span className="px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-lg font-bold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" />
                <span>WORKFLOW EXECUTED ({executionResult.incident?.incident_id})</span>
              </span>
              <button
                onClick={handleRollback}
                className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-bold flex items-center gap-1.5 transition-colors"
                title="Rollback Response Workflow"
              >
                <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
                <span>Rollback</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* 2. COLLAPSIBLE SOAR MODULE CARDS */}
      <div className="space-y-2">
        
        {/* MODULE 2: RECOMMENDED ACTIONS & REASONING */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden shadow-sm">
          <button
            onClick={() => toggleSection('actions')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-rose-500/20 text-rose-400">
                <ShieldAlert className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">1. Explainable Response Actions ({recommended_actions?.length} Actions)</span>
                <div className="text-[10px] text-soc-muted">Approval Rule: {approval_type}</div>
              </div>
            </div>
            {expandedSection === 'actions' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
          </button>

          {expandedSection === 'actions' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-2 font-mono text-xs">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                {recommended_actions?.map((act, idx) => (
                  <div key={idx} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
                    <div className="flex justify-between items-center">
                      <span className="font-bold text-rose-400 uppercase text-[11px]">{act.action}</span>
                      <span className="text-[9px] px-1.5 py-0.2 rounded bg-soc-bg border border-soc-border text-soc-dim">{act.status}</span>
                    </div>
                    <div className="text-soc-text font-bold text-[10px] truncate">{act.target}</div>
                    <div className="text-[10px] text-soc-muted leading-tight">{act.reasoning}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* MODULE 1: PLAYBOOK CONFIGURATION */}
        <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden shadow-sm">
          <button
            onClick={() => toggleSection('playbook')}
            className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded bg-soc-primary/20 text-soc-primary">
                <FileText className="w-4 h-4" />
              </div>
              <div>
                <span className="font-bold text-soc-text text-xs">2. Matched SOAR Playbook — {matched_playbook?.name}</span>
                <div className="text-[10px] text-soc-muted">{matched_playbook?.description}</div>
              </div>
            </div>
            {expandedSection === 'playbook' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
          </button>

          {expandedSection === 'playbook' && (
            <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div className="p-2.5 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Playbook Priority</span>
                  <div className="text-rose-400 font-bold">{matched_playbook?.priority}</div>
                </div>
                <div className="p-2.5 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Required DQS</span>
                  <div className="text-emerald-400 font-bold">{matched_playbook?.required_dqs}%</div>
                </div>
                <div className="p-2.5 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Approval Rules</span>
                  <div className="text-soc-text font-bold">{matched_playbook?.approval_rules}</div>
                </div>
                <div className="p-2.5 bg-soc-panel border border-soc-border rounded space-y-1">
                  <span className="text-[10px] text-soc-dim uppercase">Rollback Rules</span>
                  <div className="text-soc-primary font-bold">{matched_playbook?.rollback_rules}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* MODULE 3 & 5: WORKFLOW STEPS & NOTIFICATIONS (WHEN EXECUTED) */}
        {executionResult && (
          <>
            <div className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden shadow-sm">
              <button
                onClick={() => toggleSection('workflow')}
                className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className="p-1.5 rounded bg-emerald-500/20 text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-bold text-soc-text text-xs">3. Executed Workflow & Notifications Dispatched</span>
                    <div className="text-[10px] text-soc-muted">Workflow #{executionResult.workflow_id} completed in {executionResult.execution_time_ms} ms</div>
                  </div>
                </div>
                {expandedSection === 'workflow' ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
              </button>

              {expandedSection === 'workflow' && (
                <div className="p-4 border-t border-soc-border bg-soc-bg/80 space-y-3 font-mono text-xs">
                  <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Multi-Channel Dispatched Notifications:</span>
                  <div className="space-y-2">
                    {executionResult.notifications?.map((n, idx) => (
                      <div key={idx} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
                        <div className="flex justify-between items-center font-bold">
                          <span className="text-soc-primary uppercase">{n.recipient} ({n.channel})</span>
                          <span className="text-soc-text">{n.target}</span>
                        </div>
                        <div className="text-soc-text text-[11px]">{n.action_taken}</div>
                        <div className="text-[10px] text-soc-muted">Recommended Next Step: {n.recommended_next_step}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

      </div>

    </div>
  );
}

