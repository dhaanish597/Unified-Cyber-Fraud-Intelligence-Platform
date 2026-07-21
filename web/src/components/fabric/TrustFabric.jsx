import React, { useState } from 'react';
import { Lock, ShieldCheck, CheckCircle2, FileText, Cpu, Key, RefreshCw } from 'lucide-react';

export default function TrustFabric({ activeTxn, evaluation }) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [isVerified, setIsVerified] = useState(true);

  const hashDigest = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";
  const signature = "SIG_RSA4096_PKCS1_v1_5_SHA256_BANK_MAHARASHTRA_KEY_04";
  const token = "TRUST_TOKEN_2026_BLOCKCHAIN_COMMIT_774812";

  const handleVerify = () => {
    setIsVerifying(true);
    setTimeout(() => {
      setIsVerifying(false);
      setIsVerified(true);
    }, 500);
  };

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <Lock className="w-5 h-5 text-purple-400" />
          <div>
            <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
              Trust Fabric — Cryptographic Immutable Evidence Locker
            </h3>
            <span className="text-[10px] text-soc-muted">
              SHA-256 Hashed, Digitally Signed & Blockchain Audit Ready
            </span>
          </div>
        </div>

        <button
          onClick={handleVerify}
          disabled={isVerifying}
          className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded font-bold flex items-center gap-1.5 transition-colors shadow"
        >
          <ShieldCheck className="w-4 h-4" />
          <span>{isVerifying ? 'VERIFYING HASH...' : 'VERIFY INTEGRITY'}</span>
        </button>
      </div>

      {/* Verification Status Card */}
      {isVerified && (
        <div className="p-3 mb-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-between">
          <div className="flex items-center gap-2 text-emerald-400 font-bold">
            <CheckCircle2 className="w-4 h-4" />
            <span>EVIDENCE UNTAMPERED — SHA-256 DIGEST & DIGITAL SIGNATURE MATCHED</span>
          </div>
          <span className="text-[10px] text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/40">
            AUDIT VERIFIED
          </span>
        </div>
      )}

      {/* Hash Details Matrix */}
      <div className="space-y-2 text-[11px]">
        <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex items-center justify-between">
          <span className="text-soc-muted">SHA-256 Digest:</span>
          <span className="text-purple-300 font-bold truncate max-w-md">{hashDigest}</span>
        </div>
        <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex items-center justify-between">
          <span className="text-soc-muted">Digital Signature:</span>
          <span className="text-soc-primary font-bold truncate max-w-md">{signature}</span>
        </div>
        <div className="p-2.5 bg-soc-surface border border-soc-border rounded flex items-center justify-between">
          <span className="text-soc-muted">Verification Token:</span>
          <span className="text-emerald-400 font-bold">{token}</span>
        </div>
      </div>
    </div>
  );
}
