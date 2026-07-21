import React, { useState } from 'react';
import { ShieldAlert, FileText, CheckCircle2, Lock, Sparkles, Download, MessageSquare } from 'lucide-react';

export default function EvidenceLocker({ currentTxn, evaluation, onDownloadReport }) {
  const [notes, setNotes] = useState(
    "Investigation Note: High-risk correlation confirmed between impossible travel login (4,500km from Mumbai) and immediate ₹7.5L UPI transfer to flagged mule cluster ACC_MULE_NEW."
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [decisionExecuted, setDecisionExecuted] = useState(null);

  const handleAction = (actionType) => {
    setIsSubmitting(true);
    setTimeout(() => {
      setDecisionExecuted(actionType);
      setIsSubmitting(false);
    }, 600);
  };

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between border-b border-soc-border pb-2.5 mb-3">
          <div className="flex items-center gap-2">
            <Lock className="w-4 h-4 text-soc-primary" />
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">
              Analyst Evidence Locker & Decision Execution
            </h3>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-surface text-soc-muted border border-soc-border">
            CERT-In 6-Hour Compliance Queue
          </span>
        </div>

        {/* Pinned Evidence Checklist */}
        <div className="space-y-2 mb-4">
          <span className="text-[10px] font-mono uppercase text-soc-dim">Pinned Case Artifacts</span>
          
          <div className="p-2 rounded bg-soc-surface border border-soc-border flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-rose-500"></span>
              <span className="text-soc-text">Cyber Alert: Impossible Travel (RU IP: 185.15.2.22)</span>
            </div>
            <span className="text-soc-dim text-[10px]">T-0:40s</span>
          </div>

          <div className="p-2 rounded bg-soc-surface border border-soc-border flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500"></span>
              <span className="text-soc-text">CBS Txn: INR 7,500,000.00 (ACC_ABC_123 → ACC_MULE_NEW)</span>
            </div>
            <span className="text-soc-dim text-[10px]">T+0:00s</span>
          </div>

          <div className="p-2 rounded bg-soc-surface border border-soc-border flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-purple-500"></span>
              <span className="text-soc-text">Neo4j Ring: Mule Cluster Alpha (6 Shared Nodes)</span>
            </div>
            <span className="text-soc-dim text-[10px]">Graph Match</span>
          </div>
        </div>

        {/* Analyst Notes Editor */}
        <div className="mb-4">
          <div className="flex items-center gap-1.5 mb-1 text-[10px] font-mono uppercase text-soc-dim">
            <MessageSquare className="w-3 h-3" />
            <span>Analyst Rationale Log</span>
          </div>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            className="w-full bg-soc-surface border border-soc-border rounded p-2 text-xs font-mono text-soc-text focus:outline-none focus:border-soc-primary"
            placeholder="Enter analyst justification notes here..."
          />
        </div>
      </div>

      {/* Decision Execution Bar */}
      <div>
        {decisionExecuted ? (
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-xs font-mono font-bold text-emerald-400">
                CASE RESOLVED: {decisionExecuted} EXECUTION RECORDED
              </span>
            </div>
            <button
              onClick={onDownloadReport}
              className="px-3 py-1 bg-soc-primary hover:bg-blue-600 text-white rounded text-xs font-mono flex items-center gap-1.5 transition-colors shadow"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download CERT-In PDF</span>
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleAction('BLOCK & INTERCEPT')}
              disabled={isSubmitting}
              className="flex-1 px-3 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition-colors shadow-lg shadow-rose-950/40"
            >
              <ShieldAlert className="w-4 h-4" />
              <span>{isSubmitting ? 'ENFORCING...' : 'CONFIRM BLOCK'}</span>
            </button>

            <button
              onClick={() => handleAction('CHALLENGE MFA')}
              disabled={isSubmitting}
              className="px-3 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-mono font-bold flex items-center justify-center gap-1.5 transition-colors"
            >
              <span>STEP-UP MFA</span>
            </button>

            <button
              onClick={onDownloadReport}
              className="px-3 py-2 bg-soc-surface hover:bg-soc-border border border-soc-border text-soc-text rounded-lg text-xs font-mono flex items-center justify-center gap-1.5 transition-colors"
              title="Generate CERT-In PDF Report"
            >
              <FileText className="w-4 h-4 text-soc-primary" />
              <span>CERT-In PDF</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
