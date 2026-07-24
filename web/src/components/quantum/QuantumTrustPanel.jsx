import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Cpu, 
  Lock, 
  Award, 
  FileText, 
  Download, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2, 
  Play, 
  Search, 
  Server, 
  Layers, 
  ArrowRight,
  ShieldAlert,
  Zap,
  Info
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');

export default function QuantumTrustPanel() {
  const [readiness, setReadiness] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [activeTab, setActiveTab] = useState('overview'); // overview | assessment | inventory | algorithms | migration | compliance | simulation | audit
  const [loading, setLoading] = useState(true);

  // Simulation state
  const [simSelectedAsset, setSimSelectedAsset] = useState('ASSET_001');
  const [simYear, setSimYear] = useState(2032);
  const [simResult, setSimResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Inventory search
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchQuantumData();
  }, []);

  const fetchQuantumData = async () => {
    setLoading(true);
    try {
      const [rRes, aRes, iRes, recRes] = await Promise.all([
        fetch(`${API_BASE}/quantum/readiness`),
        fetch(`${API_BASE}/quantum/assessment`),
        fetch(`${API_BASE}/quantum/inventory`),
        fetch(`${API_BASE}/quantum/recommendations`)
      ]);

      const rData = await rRes.json();
      const aData = await aRes.json();
      const iData = await iRes.json();
      const recData = await recRes.json();

      setReadiness(rData);
      setAssessment(aData);
      setInventory(iData);
      setRecommendations(recData);
    } catch (e) {
      console.error("Quantum Trust fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const res = await fetch(`${API_BASE}/quantum/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          asset_id: simSelectedAsset,
          simulated_year: simYear
        })
      });
      const data = await res.json();
      setSimResult(data);
    } catch (e) {
      console.error("Simulation error:", e);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleExportReport = (format) => {
    const reportData = {
      title: "Fusion Quantum Trust Layer — Readiness & PQC Migration Report",
      generated_at: new Date().toISOString(),
      quantum_readiness: readiness,
      cryptographic_assessment: assessment,
      crypto_inventory: inventory,
      migration_recommendations: recommendations
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Fusion_Quantum_Readiness_Report.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  if (loading || !readiness) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
        <span>Evaluating Enterprise Post-Quantum Cryptographic Posture...</span>
      </div>
    );
  }

  const filteredInventory = inventory.filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.public_key_algo.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">
      
      {/* 1. QUANTUM TRUST LAYER HEADER STRIP */}
      <div className="p-4 bg-soc-panel border border-soc-border rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Cpu className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
                FUSION QUANTUM TRUST LAYER (QTL)
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40">
                NIST PQC ALIGNED
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1 flex items-center gap-3">
              QUANTUM READINESS SCORE: <span className="text-cyan-400">{readiness.readiness_score}%</span>
              <span className="text-xs px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold">
                {readiness.readiness_level}
              </span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">Crypto Agility</span>
            <span className="font-bold text-emerald-400 text-[11px]">{readiness.crypto_agility_status}</span>
          </div>

          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">PQC Adoption</span>
            <span className="font-bold text-cyan-400 text-[11px]">{readiness.pqc_adoption_percent}% Active</span>
          </div>

          <button 
            onClick={() => handleExportReport('json')}
            className="px-3.5 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-bold flex items-center gap-2 transition-colors shadow"
          >
            <Download className="w-4 h-4" />
            <span>PQC Audit Export</span>
          </button>
        </div>
      </div>

      {/* 2. PROGRESSIVE DISCLOSURE TABS */}
      <div className="flex items-center gap-1 border-b border-soc-border pb-2 mb-3 overflow-x-auto text-[11px]">
        {[
          { id: 'overview', label: 'Overview', icon: Award },
          { id: 'assessment', label: 'Assessment', icon: ShieldCheck },
          { id: 'inventory', label: 'Crypto Inventory', icon: Server, badge: inventory.length },
          { id: 'algorithms', label: 'Algorithms', icon: Layers },
          { id: 'migration', label: 'PQC Migration', icon: ArrowRight, badge: recommendations.length },
          { id: 'compliance', label: 'Compliance', icon: CheckCircle2 },
          { id: 'simulation', label: 'Impact Simulator', icon: Play },
          { id: 'audit', label: 'Audit & Reports', icon: FileText }
        ].map(t => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-2 transition-all ${
                isActive 
                  ? 'bg-cyan-600 text-white shadow' 
                  : 'bg-soc-panel border border-soc-border text-soc-muted hover:text-soc-text hover:border-soc-dim'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
              {t.badge !== undefined && (
                <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono ${isActive ? 'bg-black/20 text-white' : 'bg-soc-bg text-soc-dim'}`}>
                  {t.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* 3. TAB CONTENT PANELS */}

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
              <span className="text-[10px] text-soc-dim uppercase">Total Cryptographic Assets</span>
              <div className="text-lg font-bold text-soc-text">{readiness.total_crypto_assets} Protected Systems</div>
            </div>
            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
              <span className="text-[10px] text-soc-dim uppercase">Quantum Resistant Assets</span>
              <div className="text-lg font-bold text-emerald-400">{readiness.quantum_resistant_assets} (ML-KEM / ML-DSA)</div>
            </div>
            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
              <span className="text-[10px] text-soc-dim uppercase">High Quantum Risk Assets</span>
              <div className="text-lg font-bold text-amber-400">{readiness.high_risk_assets} (RSA-2048 / ECDSA)</div>
            </div>
            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
              <span className="text-[10px] text-soc-dim uppercase">Certificates Expiring &lt;90d</span>
              <div className="text-lg font-bold text-rose-400">{readiness.certificates_expiring_90d} Certificates</div>
            </div>
          </div>

          <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-bold">Active Cryptographic Posture Profile</span>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
              <div className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between">
                <span className="text-soc-muted">Active TLS Version:</span>
                <span className="text-cyan-300 font-bold">{assessment?.cryptographic_profile?.active_tls_version}</span>
              </div>
              <div className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between">
                <span className="text-soc-muted">Default Key Exchange:</span>
                <span className="text-soc-text font-bold">{assessment?.cryptographic_profile?.default_key_exchange}</span>
              </div>
              <div className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between">
                <span className="text-soc-muted">Symmetric Encryption:</span>
                <span className="text-emerald-400 font-bold">{assessment?.cryptographic_profile?.symmetric_encryption}</span>
              </div>
              <div className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between">
                <span className="text-soc-muted">PQC Provider Library:</span>
                <span className="text-soc-primary font-bold">{assessment?.cryptographic_profile?.pqc_library_provider}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: ASSESSMENT */}
      {activeTab === 'assessment' && (
        <div className="space-y-3 font-mono text-xs">
          <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Cryptographic Risk Distribution</span>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {assessment?.risk_distribution?.map((rd, i) => (
              <div key={i} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
                <span className="text-[10px] font-bold block" style={{ color: rd.color }}>{rd.risk}</span>
                <div className="text-xl font-black text-soc-text">{rd.count} Assets</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: INVENTORY */}
      {activeTab === 'inventory' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="flex items-center gap-2 bg-soc-panel border border-soc-border px-3 py-1.5 rounded-lg">
            <Search className="w-4 h-4 text-soc-dim" />
            <input
              type="text"
              placeholder="Search crypto assets by name, algorithm, or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-transparent text-soc-text placeholder:text-soc-dim outline-none w-full text-xs"
            />
          </div>

          <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
            {filteredInventory.map(item => (
              <div key={item.id} className="p-3 bg-soc-panel border border-soc-border rounded-lg flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-soc-text text-[11px]">{item.name}</span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-soc-bg border border-soc-border text-soc-dim">{item.id}</span>
                  </div>
                  <div className="text-[10px] text-soc-muted">{item.type} • {item.crypto_library} • Expiry: {item.cert_expiry_days} days</div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-cyan-300 font-bold text-[11px]">{item.public_key_algo}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                    item.pqc_status === 'QUANTUM_RESISTANT' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  }`}>
                    {item.pqc_status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 5: MIGRATION RECOMMENDATIONS */}
      {activeTab === 'migration' && (
        <div className="space-y-3 font-mono text-xs">
          <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Actionable Post-Quantum Migration Recommendations</span>
          <div className="space-y-2">
            {recommendations.map(rec => (
              <div key={rec.id} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1.5">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-soc-text text-[11px]">{rec.title}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">{rec.priority}</span>
                </div>
                <div className="text-[10px] text-soc-muted">{rec.action}</div>
                <div className="flex items-center gap-4 text-[10px] text-soc-dim">
                  <span>Target: <strong>{rec.target_system}</strong></span>
                  <span>Est Time: <strong>{rec.estimated_time_days} Days</strong></span>
                  <span>Benefit: <strong className="text-emerald-400">{rec.security_benefit}</strong></span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 7: SIMULATOR */}
      {activeTab === 'simulation' && (
        <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-4 font-mono text-xs">
          <div className="flex items-center gap-2 text-cyan-400 font-bold border-b border-soc-border pb-2">
            <Play className="w-4 h-4" />
            <span>Educational Post-Quantum Impact Simulator (CRQC Threat Scenario)</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="text-[10px] text-soc-dim uppercase block mb-1">Target Crypto Asset:</label>
              <select 
                value={simSelectedAsset} 
                onChange={(e) => setSimSelectedAsset(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-soc-text text-xs outline-none"
              >
                {inventory.map(a => <option key={a.id} value={a.id}>{a.name} ({a.public_key_algo})</option>)}
              </select>
            </div>

            <div>
              <label className="text-[10px] text-soc-dim uppercase block mb-1">Simulated Threat Horizon Year:</label>
              <select 
                value={simYear} 
                onChange={(e) => setSimYear(Number(e.target.value))}
                className="w-full bg-soc-bg border border-soc-border rounded p-2 text-soc-text text-xs outline-none"
              >
                <option value={2028}>2028 (Early NISQ Era)</option>
                <option value={2032}>2032 (Estimated CRQC Target Horizon)</option>
                <option value={2035}>2035 (Full Cryptographic Migration Deadline)</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={handleRunSimulation}
                disabled={isSimulating}
                className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold flex items-center justify-center gap-2 transition-colors shadow"
              >
                {isSimulating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                <span>RUN SIMULATION</span>
              </button>
            </div>
          </div>

          {simResult && (
            <div className="p-3 bg-soc-bg border border-soc-border rounded-lg space-y-2">
              <div className="flex justify-between items-center font-bold">
                <span className="text-cyan-400">Simulation Result #{simResult.simulation_id} ({simResult.simulated_year})</span>
                <span className="text-soc-text">{simResult.target_asset}</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                <div className="p-2 bg-soc-panel border border-soc-border rounded">
                  <span className="text-soc-dim block text-[10px]">Shor's Algorithm Factoring Time:</span>
                  <span className="font-bold text-rose-400">{simResult.quantum_threat_result.shor_factoring_time_minutes}</span>
                </div>
                <div className="p-2 bg-soc-panel border border-soc-border rounded">
                  <span className="text-soc-dim block text-[10px]">Payload Compromise Risk:</span>
                  <span className="font-bold text-amber-400">{simResult.quantum_threat_result.payload_compromise_risk}</span>
                </div>
              </div>
              <div className="text-[10px] text-soc-muted italic">{simResult.disclaimer}</div>
            </div>
          )}
        </div>
      )}

      {/* TAB 8: AUDIT & REPORTS */}
      {activeTab === 'audit' && (
        <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-3 font-mono text-xs">
          <span className="text-[10px] text-soc-dim uppercase font-bold">Export Quantum Readiness & Compliance Documentation:</span>
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleExportReport('json')}
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold flex items-center gap-2 transition-colors shadow"
            >
              <Download className="w-4 h-4" />
              <span>Export Quantum Readiness JSON Bundle</span>
            </button>

            <button
              onClick={() => handleExportReport('pdf')}
              className="px-4 py-2 bg-soc-bg hover:bg-soc-surface border border-soc-border text-soc-text rounded font-bold flex items-center gap-2 transition-colors"
            >
              <FileText className="w-4 h-4 text-cyan-400" />
              <span>Export PQC Migration Executive PDF</span>
            </button>
          </div>
        </div>
      )}

    </div>
  );
}
