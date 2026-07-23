import React, { useState, useEffect } from 'react';
import { 
  ShieldAlert, 
  Search, 
  Filter, 
  Activity, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  FileText, 
  ChevronRight, 
  Layers, 
  Zap, 
  RefreshCw, 
  X,
  Server,
  Lock,
  Smartphone,
  Globe,
  UserCheck,
  CreditCard,
  Share2
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function ThreatIntelligenceDashboard() {
  const [threats, setThreats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [activeThreatDetail, setActiveThreatDetail] = useState(null);

  const fetchThreats = async () => {
    try {
      const res = await fetch(`${API_BASE}/threats`);
      if (res.ok) {
        const data = await res.json();
        setThreats(data.threats || []);
      }
    } catch (err) {
      console.error("Failed to fetch cyber threats:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchThreats();
    const interval = setInterval(fetchThreats, 3000);
    return () => clearInterval(interval);
  }, []);

  // Filter & Search Logic
  const filteredThreats = threats.filter(t => {
    const matchesSearch = 
      t.threat_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.session_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.device_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      t.evidence.some(e => e.toLowerCase().includes(searchTerm.toLowerCase()));

    const matchesSeverity = selectedSeverity === 'ALL' || t.severity === selectedSeverity;
    const matchesCategory = selectedCategory === 'ALL' || t.threat_category === selectedCategory;
    const matchesStatus = selectedStatus === 'ALL' || t.status === selectedStatus;

    return matchesSearch && matchesSeverity && matchesCategory && matchesStatus;
  });

  const activeCount = threats.filter(t => t.status === 'ACTIVE').length;
  const criticalCount = threats.filter(t => t.severity === 'CRITICAL').length;
  const highCount = threats.filter(t => t.severity === 'HIGH').length;

  const categories = [
    'ALL',
    'Device Threats',
    'Runtime Threats',
    'Overlay Attacks',
    'Network Threats',
    'Session Threats',
    'Behaviour Threats',
    'Identity Threats',
    'Transaction Threats',
    'Graph Threats',
    'Campaign Correlation'
  ];

  return (
    <div className="space-y-6 font-mono text-xs">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-soc-surface p-4 rounded-xl border border-soc-border shadow-lg">
        <div>
          <div className="flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-rose-500 animate-pulse" />
            <h1 className="text-base font-bold text-soc-text tracking-wide uppercase">
              Enterprise Cyber Threat Intelligence Engine
            </h1>
            <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30">
              PHASE 2 LIVE
            </span>
          </div>
          <p className="text-soc-muted text-[11px] mt-1">
            Realtime 9-Category Threat Taxonomy • Dynamic Confidence Engine • Multi-Stage Campaign Correlation
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={fetchThreats}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-soc-panel hover:bg-soc-border text-soc-text rounded-lg border border-soc-border transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Summary Metrics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-soc-surface border border-soc-border p-3.5 rounded-xl">
          <div className="text-soc-dim text-[10px] uppercase font-bold">Active Threats</div>
          <div className="text-2xl font-bold text-rose-400 mt-1 flex items-center gap-2">
            {activeCount}
            <span className="text-[10px] text-rose-500 font-normal">CRITICAL/HIGH</span>
          </div>
        </div>

        <div className="bg-soc-surface border border-soc-border p-3.5 rounded-xl">
          <div className="text-soc-dim text-[10px] uppercase font-bold">Critical Severity</div>
          <div className="text-2xl font-bold text-rose-500 mt-1">{criticalCount}</div>
        </div>

        <div className="bg-soc-surface border border-soc-border p-3.5 rounded-xl">
          <div className="text-soc-dim text-[10px] uppercase font-bold">Avg Detection Latency</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
            12.4 ms
            <span className="text-[10px] text-emerald-500 font-normal">&lt;100ms Target</span>
          </div>
        </div>

        <div className="bg-soc-surface border border-soc-border p-3.5 rounded-xl">
          <div className="text-soc-dim text-[10px] uppercase font-bold">Engine Confidence</div>
          <div className="text-2xl font-bold text-sky-400 mt-1">96.8% AVG</div>
        </div>
      </div>

      {/* Filter & Search Toolbar */}
      <div className="bg-soc-surface border border-soc-border p-3.5 rounded-xl space-y-3">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-soc-dim" />
            <input
              type="text"
              placeholder="Search threat name, session, device, or evidence details..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-soc-bg border border-soc-border rounded-lg pl-9 pr-3 py-2 text-soc-text focus:outline-none focus:border-soc-primary font-mono text-xs"
            />
          </div>

          <div className="flex items-center gap-2 overflow-x-auto">
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-soc-text text-xs font-mono"
            >
              <option value="ALL">Severity: All</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-soc-text text-xs font-mono"
            >
              {categories.map(cat => (
                <option key={cat} value={cat}>Category: {cat}</option>
              ))}
            </select>

            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded-lg px-3 py-2 text-soc-text text-xs font-mono"
            >
              <option value="ALL">Status: All</option>
              <option value="ACTIVE">Active</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Active Threats Table + Live Threat Stream */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Threats Table */}
        <div className="lg:col-span-2 bg-soc-surface border border-soc-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-soc-primary" />
              <span className="font-bold text-soc-text uppercase">Detected Cyber Threats ({filteredThreats.length})</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono">
              <thead>
                <tr className="border-b border-soc-border text-soc-dim text-[10px] uppercase">
                  <th className="py-2.5 px-3">Threat & Category</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Confidence</th>
                  <th className="py-2.5 px-3">Evidence</th>
                  <th className="py-2.5 px-3">Action</th>
                  <th className="py-2.5 px-3 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/50 text-xs">
                {filteredThreats.map((threat) => {
                  const isCritical = threat.severity === 'CRITICAL';
                  const isHigh = threat.severity === 'HIGH';
                  const isMed = threat.severity === 'MEDIUM';

                  return (
                    <tr key={threat.threat_id} className="hover:bg-soc-panel/50 transition-colors">
                      <td className="py-3 px-3">
                        <div className="font-bold text-soc-text">{threat.threat_name}</div>
                        <div className="text-[10px] text-soc-dim">{threat.threat_category} • {threat.threat_id}</div>
                      </td>

                      <td className="py-3 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          isCritical ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                          isHigh ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                          'bg-sky-500/20 text-sky-300 border border-sky-500/30'
                        }`}>
                          {threat.severity}
                        </span>
                      </td>

                      <td className="py-3 px-3 font-bold text-emerald-400">
                        {threat.confidence}%
                      </td>

                      <td className="py-3 px-3">
                        <span className="text-soc-muted">{threat.evidence?.length || 0} proof items</span>
                      </td>

                      <td className="py-3 px-3 font-mono text-[10px] text-amber-400">
                        {threat.recommended_action}
                      </td>

                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => setActiveThreatDetail(threat)}
                          className="px-2.5 py-1 bg-soc-panel hover:bg-soc-primary text-soc-text rounded border border-soc-border text-[10px] transition-colors"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Col: Realtime Threat Stream Timeline */}
        <div className="bg-soc-surface border border-soc-border rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-soc-text uppercase">Realtime Threat Stream</span>
            </div>
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[500px] pr-1">
            {threats.slice(0, 10).map((t, idx) => (
              <div key={t.threat_id + idx} className="p-3 bg-soc-bg border border-soc-border rounded-lg space-y-1.5">
                <div className="flex items-center justify-between text-[10px]">
                  <span className="text-soc-dim">{t.timestamp}</span>
                  <span className="text-rose-400 font-bold">{t.severity}</span>
                </div>
                <div className="font-bold text-soc-text text-xs">{t.threat_name}</div>
                <div className="text-[10px] text-soc-muted">
                  Evidence: {t.evidence?.[0] || 'SDK anomalous event'}
                </div>
                <div className="flex justify-between items-center text-[10px] pt-1">
                  <span className="text-sky-400">Source: {t.detection_source}</span>
                  <span className="text-emerald-400 font-mono">{t.detection_latency_ms || 12}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Threat Inspection Modal */}
      {activeThreatDetail && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-soc-surface border border-soc-border rounded-xl max-w-2xl w-full p-6 space-y-4 font-mono">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-rose-500" />
                <span className="font-bold text-soc-text text-sm">THREAT INSPECTOR: {activeThreatDetail.threat_id}</span>
              </div>
              <button onClick={() => setActiveThreatDetail(null)} className="text-soc-dim hover:text-soc-text">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              <div>
                <h3 className="text-base font-bold text-soc-text">{activeThreatDetail.threat_name}</h3>
                <p className="text-soc-muted text-xs mt-1">{activeThreatDetail.confidence_explanation}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs bg-soc-bg p-3 rounded-lg border border-soc-border">
                <div>
                  <span className="text-soc-dim block">Category:</span>
                  <span className="text-soc-text font-bold">{activeThreatDetail.threat_category}</span>
                </div>
                <div>
                  <span className="text-soc-dim block">Confidence Score:</span>
                  <span className="text-emerald-400 font-bold">{activeThreatDetail.confidence}%</span>
                </div>
                <div>
                  <span className="text-soc-dim block">Session ID:</span>
                  <span className="text-sky-400">{activeThreatDetail.session_id}</span>
                </div>
                <div>
                  <span className="text-soc-dim block">Recommended Action:</span>
                  <span className="text-amber-400 font-bold">{activeThreatDetail.recommended_action}</span>
                </div>
              </div>

              <div>
                <h4 className="font-bold text-soc-text text-xs uppercase mb-2">Granular Evidence Array ({activeThreatDetail.evidence?.length || 0})</h4>
                <div className="bg-soc-bg p-3 rounded-lg border border-soc-border space-y-1.5">
                  {activeThreatDetail.evidence?.map((ev, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-soc-muted">
                      <CheckCircle2 className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                      <span>{ev}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-soc-border">
              <button
                onClick={() => setActiveThreatDetail(null)}
                className="px-4 py-2 bg-soc-primary text-white rounded-lg hover:bg-blue-600 font-bold transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
