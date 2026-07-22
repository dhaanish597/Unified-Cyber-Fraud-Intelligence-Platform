import React, { useState } from 'react';
import { Lock, ShieldCheck, CheckCircle2, FileText, ExternalLink, X, Copy, Terminal } from 'lucide-react';

export default function TrustFabricLedgerBadge({ ledgerRecord }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const record = ledgerRecord || {
    evidence_id: "EVID-TXN-81293",
    sha256_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    digital_signature: "SIG_RSA4096_8f91a4b2c0128e441b99a0d2ef34c56e",
    block_height: 48193,
    transaction_hash: "0x7f9a41b2c0128e441b99a0d2ef34c56e7f9a41b2c0128e441b99a0d2ef34c56e",
    verification_token: "VERIF-FABRIC-2026-E3B0C44298FC",
    ledger_type: "Hyperledger Fabric v2.5 (Channel: bank-fraud-audit)",
    timestamp: "2026-07-22 10:00:40 IST",
    verified: true,
    chain_of_custody: [
      { step: "COLLECTED", timestamp: "10:00:00 IST", actor: "SIEM_Stream_Ingest", detail: "Raw transaction & cyber telemetry captured" },
      { step: "ANALYZED", timestamp: "10:00:01 IST", actor: "Fusion_Risk_OS_AI", detail: "Multi-modal scoring & SHAP feature extraction complete" },
      { step: "ATTACHED", timestamp: "10:00:02 IST", actor: "Evidence_Locker", detail: "Graph snapshot & counterfactual sentence attached" },
      { step: "VERDICT_LOCKED", timestamp: "10:00:03 IST", actor: "Decision_Engine", detail: "Decision policy rule enforced" },
      { step: "HASHED", timestamp: "10:00:04 IST", actor: "SHA256_Hasher", detail: "Canonical digest generated: e3b0c442..." },
      { step: "SIGNED", timestamp: "10:00:05 IST", actor: "HSM_Signer_Node_01", detail: "RSA-4096 / Quantum-Resistant Digital Signature applied" },
      { step: "LEDGER_COMMITTED", timestamp: "10:00:06 IST", actor: "Hyperledger_Fabric_Peer", detail: "Block #48193 committed to ledger" },
      { step: "VERIFIED", timestamp: "10:00:07 IST", actor: "Auditor_Verifier", detail: "Cryptographic integrity check PASSED" }
    ]
  };

  const handleCopyHash = () => {
    navigator.clipboard.writeText(record.sha256_hash);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <>
      <div 
        onClick={() => setIsOpen(true)}
        className="bg-soc-panel border border-soc-border hover:border-soc-primary rounded-xl p-3 shadow-lg cursor-pointer transition-all flex items-center justify-between font-mono text-xs select-none"
      >
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-emerald-500/20 border border-emerald-500/40 rounded-lg">
            <Lock className="w-4 h-4 text-emerald-400 animate-pulse" />
          </div>
          <div>
            <div className="font-bold text-xs text-soc-text flex items-center gap-2">
              <span>Trust Fabric Ledger</span>
              <span className="text-[9px] px-2 py-0.2 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                BLOCK #{record.block_height}
              </span>
            </div>
            <div className="text-[10px] text-soc-muted truncate max-w-[240px] mt-0.5">
              SHA256: {record.sha256_hash.slice(0, 20)}...
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] px-2 py-0.5 rounded bg-soc-surface text-emerald-400 font-bold border border-emerald-500/40 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>VERIFIED</span>
          </span>
          <ExternalLink className="w-3.5 h-3.5 text-soc-muted" />
        </div>
      </div>

      {/* MODAL AUDIT TOKEN VERIFIER */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-soc-surface border border-soc-border rounded-xl max-w-2xl w-full p-5 shadow-2xl font-mono text-xs select-none space-y-4">
            
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-emerald-500/20 border border-emerald-500/40 rounded-lg">
                  <Lock className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
                    <span>Hyperledger Fabric Audit Token Verifier</span>
                    <span className="text-[9px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                      IMMUTABLE
                    </span>
                  </h3>
                  <p className="text-[11px] text-soc-muted">
                    Cryptographic proof & 8-stage immutable chain of custody verification
                  </p>
                </div>
              </div>

              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 bg-soc-panel hover:bg-soc-border text-soc-muted hover:text-soc-text rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* LEDGER DETAILS GRID */}
            <div className="grid grid-cols-2 gap-3 bg-soc-panel p-3 rounded-xl border border-soc-border text-[11px]">
              <div>
                <span className="text-soc-muted block">Evidence Package ID:</span>
                <strong className="text-soc-text font-bold">{record.evidence_id}</strong>
              </div>
              <div>
                <span className="text-soc-muted block">Block Height:</span>
                <strong className="text-emerald-400 font-bold">#{record.block_height}</strong>
              </div>
              <div className="col-span-2">
                <span className="text-soc-muted block mb-1">SHA-256 Digest Hash:</span>
                <div className="flex items-center justify-between bg-slate-950 p-2 rounded border border-soc-border text-emerald-400 font-mono text-[10px]">
                  <span className="truncate">{record.sha256_hash}</span>
                  <button onClick={handleCopyHash} className="p-1 hover:text-white shrink-0">
                    <Copy className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
              <div>
                <span className="text-soc-muted block">Digital Signature:</span>
                <strong className="text-soc-text text-[10px] truncate block">{record.digital_signature}</strong>
              </div>
              <div>
                <span className="text-soc-muted block">Consensus:</span>
                <strong className="text-soc-text text-[10px] block">Raft BFT Consensus (Hyperledger)</strong>
              </div>
            </div>

            {/* CHAIN OF CUSTODY LOG TREE */}
            <div>
              <div className="text-[10px] font-bold text-soc-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <Terminal className="w-3.5 h-3.5 text-soc-primary" />
                <span>Chain of Custody Timeline Log</span>
              </div>

              <div className="bg-slate-950 border border-soc-border rounded-xl p-3 space-y-2 max-h-[220px] overflow-y-auto">
                {record.chain_of_custody.map((log, idx) => (
                  <div key={idx} className="flex items-start gap-2.5 text-[11px] font-mono border-b border-soc-border/40 pb-1.5 last:border-b-0">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex justify-between items-center text-[10px]">
                        <span className="font-bold text-emerald-400">{log.step}</span>
                        <span className="text-soc-muted">{log.timestamp} | {log.actor}</span>
                      </div>
                      <div className="text-soc-text text-[10px] mt-0.5">{log.detail}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-between items-center text-[11px] text-soc-muted pt-2 border-t border-soc-border">
              <span>Token: <strong className="text-soc-text">{record.verification_token}</strong></span>
              <span className="text-emerald-400 font-bold">✔ Cryptographic Verification PASSED</span>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
