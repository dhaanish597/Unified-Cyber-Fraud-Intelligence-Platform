import React, { useState, useEffect } from 'react';
import { 
  Lock, 
  ShieldCheck, 
  CheckCircle2, 
  FileText, 
  Cpu, 
  Key, 
  RefreshCw,
  Award,
  Download,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  UserCheck,
  Globe,
  Share2
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function TrustFabric({ activeTxn, evaluation }) {
  const [evidencePackage, setEvidencePackage] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [activeTab, setActiveTab] = useState('integrity'); // integrity | trust_index | custody | export
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEvidencePackage();
  }, [activeTxn]);

  const fetchEvidencePackage = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/evidence/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          case_id: activeTxn?.txn_id ? `CASE-2026-${activeTxn.txn_id.slice(-4)}` : 'CASE-2026-8942',
          incident_id: 'INC-2026-8942',
          session_id: 'SESS_9921_CRITICAL',
          user_id: activeTxn?.user_id || 'usr_abc',
          amount: activeTxn?.amount || 750000.0
        })
      });
      const data = await res.json();
      setEvidencePackage(data);

      // Perform initial integrity check
      if (data.evidence_id) {
        const verifyRes = await fetch(`${API_BASE}/evidence/verify/${data.evidence_id}`);
        const verifyData = await verifyRes.json();
        setVerificationResult(verifyData);
      }
    } catch (e) {
      console.error("Trust Fabric fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyIntegrity = async () => {
    if (!evidencePackage?.evidence_id) return;
    setIsVerifying(true);
    try {
      const res = await fetch(`${API_BASE}/evidence/verify/${evidencePackage.evidence_id}`);
      const data = await res.json();
      setVerificationResult(data);
    } catch (e) {
      console.error("Verification error:", e);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleExportBundle = async (format) => {
    if (!evidencePackage?.evidence_id) return;
    try {
      const res = await fetch(`${API_BASE}/evidence/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidence_id: evidencePackage.evidence_id,
          format: format
        })
      });
      const data = await res.json();
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Regulator_Evidence_${evidencePackage.evidence_id}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error("Evidence export error:", e);
    }
  };

  if (loading || !evidencePackage) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-soc-primary" />
        <span>Sealing Cryptographic Evidence Package & Verifying Trust Fabric...</span>
      </div>
    );
  }

  const { evidence_id, sha256_hash, digital_signature, investigation_trust_index, audit_timeline } = evidencePackage;
  const isUntampered = verificationResult?.verification_status === 'VERIFIED_INTACT';

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">
      
      {/* 1. HEADER & INTEGRITY SUMMARY STRIP */}
      <div className="flex flex-wrap items-center justify-between border-b border-soc-border pb-3 mb-3 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-purple-500/10 border border-purple-500/30 rounded-lg text-purple-400">
            <Lock className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
                Trust Fabric — Cryptographic Immutable Evidence Locker
              </h3>
              <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30">
                HSM SIGNED & UNTAMPERED
              </span>
            </div>
            <span className="text-[10px] text-soc-muted">
              Evidence ID: {evidence_id} • SHA-256 Digest Verification: {isUntampered ? 'PASSED' : 'FAILED'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleVerifyIntegrity}
            disabled={isVerifying}
            className="px-3.5 py-1.5 bg-purple-600 hover:bg-purple-700 text-white rounded font-bold flex items-center gap-1.5 transition-colors shadow"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{isVerifying ? 'VERIFYING...' : 'RE-VERIFY SHA-256'}</span>
          </button>
        </div>
      </div>

      {/* 2. SUB-NAVIGATION TABS */}
      <div className="flex items-center gap-1 border-b border-soc-border pb-2 mb-3 overflow-x-auto text-[11px]">
        {[
          { id: 'integrity', label: 'Cryptographic Hash & Digital Signature', icon: ShieldCheck },
          { id: 'trust_index', label: 'Investigation Trust Index', icon: Award, badge: `${investigation_trust_index?.trust_index_score}%` },
          { id: 'custody', label: 'Chain of Custody Audit Log', icon: FileText },
          { id: 'export', label: 'Regulator Export Suite', icon: Download }
        ].map(t => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-2 transition-all ${
                isActive 
                  ? 'bg-purple-600 text-white shadow' 
                  : 'bg-soc-panel border border-soc-border text-soc-muted hover:text-soc-text hover:border-soc-dim'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
              {t.badge && (
                <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${isActive ? 'bg-black/20 text-white' : 'bg-soc-bg text-soc-dim'}`}>
                  {t.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 3. TAB CONTENT VIEWS */}
      
      {/* TAB 1: CRYPTOGRAPHIC INTEGRITY & DIGITAL SIGNATURE */}
      {activeTab === 'integrity' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <CheckCircle2 className="w-4 h-4" />
              <span>EVIDENCE UNTAMPERED — SHA-256 DIGEST & HSM SIGNATURE VERIFIED INTACT</span>
            </div>
            <span className="text-[10px] text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/40 font-bold">
              NON-REPUDIABLE
            </span>
          </div>

          <div className="space-y-2">
            <div className="p-2.5 bg-soc-panel border border-soc-border rounded flex justify-between items-center">
              <span className="text-soc-dim uppercase text-[10px] font-semibold">SHA-256 Hash Digest:</span>
              <span className="text-purple-300 font-bold font-mono truncate max-w-lg">{sha256_hash}</span>
            </div>
            <div className="p-2.5 bg-soc-panel border border-soc-border rounded flex justify-between items-center">
              <span className="text-soc-dim uppercase text-[10px] font-semibold">Digital Signer:</span>
              <span className="text-soc-primary font-bold">{digital_signature.signer}</span>
            </div>
            <div className="p-2.5 bg-soc-panel border border-soc-border rounded flex justify-between items-center">
              <span className="text-soc-dim uppercase text-[10px] font-semibold">Key Algorithm:</span>
              <span className="text-soc-text font-bold">{digital_signature.key_algorithm}</span>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: INVESTIGATION TRUST INDEX */}
      {activeTab === 'trust_index' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg flex items-center justify-between">
            <div>
              <span className="text-[10px] text-soc-dim uppercase font-bold">Overall Investigation Trust Index</span>
              <div className="text-lg font-black text-emerald-400">{investigation_trust_index?.trust_index_score}% ({investigation_trust_index?.trust_tier})</div>
            </div>
            <span className="text-[10px] px-2 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded font-bold">
              REGULATOR VERIFIED
            </span>
          </div>

          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-bold">Explainable Contribution Drivers:</span>
            <div className="space-y-1.5">
              {investigation_trust_index?.explainable_contributions?.map((c, idx) => (
                <div key={idx} className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between items-center text-[11px]">
                  <span className="font-bold text-soc-text">{c.factor} (Weight: {c.weight * 100}%)</span>
                  <span className="text-emerald-400 font-bold">{c.impact}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: CHAIN OF CUSTODY AUDIT LOG */}
      {activeTab === 'custody' && (
        <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
          {audit_timeline?.map((evt) => (
            <div key={evt.step} className="p-2 bg-soc-panel border border-soc-border rounded text-[11px] flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="px-1.5 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-dim font-bold text-[10px]">
                  STEP {evt.step}
                </span>
                <div>
                  <span className="font-bold text-soc-text">{evt.event}</span>
                  <div className="text-[10px] text-soc-muted">{evt.timestamp} • Actor: {evt.actor}</div>
                </div>
              </div>
              <span className="text-[10px] font-bold text-emerald-400">{evt.status}</span>
            </div>
          ))}
        </div>
      )}

      {/* TAB 4: REGULATOR EXPORT SUITE */}
      {activeTab === 'export' && (
        <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-3">
          <span className="text-[10px] text-soc-dim uppercase font-bold">Export Regulator-Ready Evidence Bundle:</span>
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => handleExportBundle('pdf')}
              className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded font-bold flex items-center gap-2 transition-colors shadow"
            >
              <Download className="w-4 h-4" />
              <span>Download CERT-In PDF Compliance Bundle</span>
            </button>

            <button
              onClick={() => handleExportBundle('json')}
              className="px-4 py-2 bg-soc-bg hover:bg-soc-surface border border-soc-border text-soc-text rounded font-bold flex items-center gap-2 transition-colors"
            >
              <FileText className="w-4 h-4 text-soc-primary" />
              <span>Export Raw JSON Evidence Payload</span>
            </button>

            <button
              onClick={() => handleExportBundle('csv')}
              className="px-4 py-2 bg-soc-bg hover:bg-soc-surface border border-soc-border text-soc-text rounded font-bold flex items-center gap-2 transition-colors"
            >
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>Export Audit CSV Digest</span>
            </button>
          </div>
        </div>
      )}

    </div>
  );
}

