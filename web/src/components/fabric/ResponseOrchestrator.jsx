import React, { useState } from 'react';
import { Play, CheckCircle2, Lock, ShieldAlert, Zap, Send, Bell, FileText, Cpu, ChevronRight } from 'lucide-react';

export default function ResponseOrchestrator({ activeCase, onDownloadReport }) {
  const [playbookState, setPlaybookState] = useState([
    { id: 'confirm', name: '1. Incident Confirmed', desc: 'Case flagged by Fusion Risk Engine (Score 94)', status: 'completed', auto: true },
    { id: 'freeze_acc', name: '2. Freeze Account', desc: 'Lock debit transactions on ACC_ABC_123', status: 'pending', auto: false },
    { id: 'block_upi', name: '3. Block UPI Handle', desc: 'Blacklist rajesh@upi across gateway', status: 'pending', auto: false },
    { id: 'block_dest', name: '4. Block Beneficiary', desc: 'Blacklist destination account ACC_MULE_NEW', status: 'pending', auto: true },
    { id: 'term_session', name: '5. Terminate Session', desc: 'Kill active JWT token for usr_abc', status: 'pending', auto: true },
    { id: 'inval_tokens', name: '6. Invalidate Refresh Tokens', desc: 'Revoke OAuth refresh tokens', status: 'pending', auto: true },
    { id: 'pass_reset', name: '7. Force Password Reset', desc: 'Require mandatory credential reset', status: 'pending', auto: false },
    { id: 'notify_cust', name: '8. Notify Customer', desc: 'Send SMS & Push alert to +91-9876543210', status: 'pending', auto: true },
    { id: 'notify_soc', name: '9. Notify SOC Manager', desc: 'Escalate to Tier-3 Security Lead', status: 'pending', auto: true },
    { id: 'cert_report', name: '10. Generate CERT Report', desc: 'Render CERT-In PDF compliance package', status: 'pending', auto: true },
    { id: 'hash_evidence', name: '11. Hash Evidence', desc: 'Compute SHA-256 evidence digest', status: 'pending', auto: true },
    { id: 'audit_commit', name: '12. Store Immutable Audit', desc: 'Commit verification token to Trust Fabric', status: 'pending', auto: true }
  ]);

  const [isExecuting, setIsExecuting] = useState(false);
  const [executionComplete, setExecutionComplete] = useState(false);

  const handleExecutePlaybook = () => {
    setIsExecuting(true);
    playbookState.forEach((step, index) => {
      setTimeout(() => {
        setPlaybookState(prev => prev.map((s, i) => i === index ? { ...s, status: 'completed' } : s));
        if (index === playbookState.length - 1) {
          setIsExecuting(false);
          setExecutionComplete(true);
          if (onDownloadReport) onDownloadReport();
        }
      }, (index + 1) * 350);
    });
  };

  const toggleStepStatus = (id) => {
    setPlaybookState(prev => prev.map(s => s.id === id ? { ...s, status: s.status === 'completed' ? 'pending' : 'completed' } : s));
  };

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-4">
        <div className="flex items-center gap-2">
          <Zap className="w-5 h-5 text-soc-primary animate-pulse" />
          <div>
            <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
              Response Orchestrator — Autonomous Playbook Execution
            </h3>
            <span className="text-[10px] text-soc-muted">
              Playbook: Account Takeover (ATO) Containment & Mitigation Workflow
            </span>
          </div>
        </div>

        {!executionComplete ? (
          <button
            onClick={handleExecutePlaybook}
            disabled={isExecuting}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-700 disabled:opacity-50 text-white rounded-lg font-bold flex items-center gap-2 transition-all shadow-lg shadow-rose-950/40"
          >
            <Play className="w-4 h-4" />
            <span>{isExecuting ? 'ORCHESTRATING PLAYBOOK...' : 'EXECUTE RESPONSE PLAYBOOK'}</span>
          </button>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 rounded-lg font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>CONTAINMENT FULLY EXECUTED & AUDITED</span>
          </div>
        )}
      </div>

      {/* Playbook Orchestration Step Matrix */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {playbookState.map((step) => {
          const isDone = step.status === 'completed';
          return (
            <div
              key={step.id}
              onClick={() => toggleStepStatus(step.id)}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                isDone
                  ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-400'
                  : 'bg-soc-surface border-soc-border text-soc-muted hover:border-soc-primary/50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-bold text-[11px] text-soc-text truncate">{step.name}</span>
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-soc-border shrink-0" />
                )}
              </div>
              <p className="text-[10px] text-soc-dim line-clamp-2">{step.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
