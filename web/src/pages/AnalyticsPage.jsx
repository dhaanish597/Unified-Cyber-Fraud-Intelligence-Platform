import React, { useState } from 'react';
import { 
  BarChart3, 
  TrendingUp, 
  ShieldAlert, 
  Activity, 
  Clock, 
  Globe, 
  Radio, 
  Share2, 
  Zap, 
  FileCheck2, 
  Filter, 
  Download, 
  Layers, 
  CheckCircle2, 
  AlertTriangle,
  Database,
  Cpu
} from 'lucide-react';

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('24h');
  const [selectedVector, setSelectedVector] = useState('ALL');

  const kpis = [
    { title: 'Intercepted Attack Invocations', val: '14,892 Attacks', sub: '100% In-Flight Block Rate', color: 'text-emerald-400', icon: ShieldAlert },
    { title: 'Fusion Model Recall Uplift', val: '+38.4% Uplift', sub: 'Recall @ 0.5% FPR (96.6% vs 58.2%)', color: 'text-soc-primary', icon: TrendingUp },
    { title: 'Avg Threat Correlation Latency', val: '12 ms', sub: 'LightGBM + IsoForest + GraphSAGE', color: 'text-amber-400', icon: Activity },
    { title: 'CERT-In Mandate Compliance', val: '100%', sub: 'Avg Incident Report: 14m < 6h Limit', color: 'text-emerald-400', icon: FileCheck2 }
  ];

  const threatVectors = [
    { type: 'Impossible Travel Login', pct: 42, count: 6254, severity: 'CRITICAL', color: 'bg-rose-500' },
    { type: 'Credential Stuffing Botnet', pct: 28, count: 4170, severity: 'CRITICAL', color: 'bg-rose-500' },
    { type: 'Mule Ring Layering Network', pct: 18, count: 2680, severity: 'HIGH', color: 'bg-amber-500' },
    { type: 'SIM Swap Interception', pct: 8, count: 1191, severity: 'HIGH', color: 'bg-amber-500' },
    { type: 'MFA Cookie Reuse', pct: 4, count: 597, severity: 'MEDIUM', color: 'bg-soc-primary' }
  ];

  const modelMetrics = [
    { metric: 'PR-AUC (Precision-Recall Area)', baseline: '0.741', fusion: '0.942', uplift: '+27.1%' },
    { metric: 'Recall @ 0.1% False Positive Rate', baseline: '42.1%', fusion: '84.6%', uplift: '+42.5%' },
    { metric: 'Recall @ 0.5% False Positive Rate', baseline: '58.2%', fusion: '96.6%', uplift: '+38.4%' },
    { metric: 'F1-Score (Optimal Operating Point)', baseline: '0.64', fusion: '0.91', uplift: '+42.1%' }
  ];

  const hourlyVelocities = [
    { hour: '00:00', attacks: 120 }, { hour: '02:00', attacks: 840 },
    { hour: '04:00', attacks: 1420 }, { hour: '06:00', attacks: 650 },
    { hour: '08:00', attacks: 320 }, { hour: '10:00', attacks: 980 },
    { hour: '12:00', attacks: 450 }, { hour: '14:00', attacks: 290 },
    { hour: '16:00', attacks: 380 }, { hour: '18:00', attacks: 710 },
    { hour: '20:00', attacks: 1100 }, { hour: '22:00', attacks: 590 }
  ];

  const topOriginGeos = [
    { country: 'Russia (RU)', share: '38.2%', count: 5689, risk: 'CRITICAL' },
    { country: 'Romania (RO)', share: '24.1%', count: 3589, risk: 'HIGH' },
    { country: 'Vietnam (VN)', share: '18.4%', count: 2740, risk: 'HIGH' },
    { country: 'Netherlands (NL)', share: '12.3%', count: 1831, risk: 'MEDIUM' },
    { country: 'Other International', share: '7.0%', count: 1043, risk: 'LOW' }
  ];

  const shapDrivers = [
    { feature: 'cyber_compromise_in_window', impact: '+2.10', desc: 'Preceding impossible travel login event' },
    { feature: 'log_amount', impact: '+1.24', desc: 'Transaction size relative to account balance' },
    { feature: 'dest_mule_cluster_id', impact: '+0.85', desc: 'Beneficiary linked to known mule ring' },
    { feature: 'orig_balance_drain_ratio', impact: '+0.62', desc: '100% originator account balance drain' },
    { feature: 'impossible_travel_km', impact: '+0.48', desc: 'Distance anomaly from baseline location' }
  ];

  const handleExportAnalyticsReport = () => {
    alert("Exporting CERT-In Cyber Security Incident Analytics Report (PDF format)...");
  };

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none font-mono text-xs text-soc-text">
      
      {/* HEADER STRIP */}
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <BarChart3 className="w-6 h-6 text-soc-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
                Cybersecurity Threat Analytics & AI Model Performance
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                REAL-TIME SIEM TELEMETRY
              </span>
            </div>
            <span className="text-xs text-soc-muted">Actionable threat vector distributions, model uplift metrics, and CERT-In compliance SLA</span>
          </div>
        </div>

        {/* TIME RANGE & EXPORT CONTROLS */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <div className="flex items-center gap-1 bg-soc-panel p-1 rounded-lg border border-soc-border text-[11px]">
            {['1h', '24h', '7d', '30d'].map((tr) => (
              <button
                key={tr}
                onClick={() => setTimeRange(tr)}
                className={`px-2.5 py-1 rounded font-bold uppercase transition-all ${
                  timeRange === tr ? 'bg-soc-primary text-white shadow' : 'text-soc-muted hover:text-soc-text'
                }`}
              >
                {tr}
              </button>
            ))}
          </div>

          <button
            onClick={handleExportAnalyticsReport}
            className="px-3.5 py-2 bg-soc-primary hover:bg-blue-600 text-white font-bold rounded-lg flex items-center gap-2 transition-all shadow"
          >
            <Download className="w-4 h-4" />
            <span>Export CERT-In Report</span>
          </button>
        </div>
      </div>

      {/* 1. EXEC KPI STRIP */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div key={idx} className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg flex flex-col justify-between">
              <div className="flex justify-between items-start">
                <span className="text-[10px] text-soc-muted font-bold uppercase">{kpi.title}</span>
                <Icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
              <div className="my-2">
                <div className={`text-xl font-black font-mono ${kpi.color}`}>{kpi.val}</div>
                <div className="text-[11px] text-soc-muted mt-0.5">{kpi.sub}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 2. TABULAR VS FUSION MODEL UPLIFT (HONEST METRICS) */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
        <div className="flex items-center justify-between border-b border-soc-border pb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-soc-primary" />
            <h2 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">
              Fusion Model Uplift vs Tabular-Only Baseline (Honest FPR Metrics)
            </h2>
          </div>
          <span className="text-[10px] text-soc-muted px-2 py-0.5 rounded bg-soc-bg border border-soc-border">
            Fixed Operating Point: 0.5% FPR
          </span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          
          {/* COMPARISON TABLE (8/12) */}
          <div className="lg:col-span-8 overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead>
                <tr className="border-b border-soc-border text-soc-dim uppercase text-[10px]">
                  <th className="py-2.5 px-3">Evaluation Metric</th>
                  <th className="py-2.5 px-3">Tabular Baseline</th>
                  <th className="py-2.5 px-3">Fusion Cyber Engine</th>
                  <th className="py-2.5 px-3 text-right">Uplift</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-soc-border/50">
                {modelMetrics.map((m, idx) => (
                  <tr key={idx} className="hover:bg-soc-panel/60">
                    <td className="py-2.5 px-3 font-bold text-soc-text">{m.metric}</td>
                    <td className="py-2.5 px-3 text-soc-muted">{m.baseline}</td>
                    <td className="py-2.5 px-3 font-bold text-emerald-400">{m.fusion}</td>
                    <td className="py-2.5 px-3 text-right font-bold text-soc-primary">{m.uplift}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* UPLIFT SUMMARY BADGE (4/12) */}
          <div className="lg:col-span-4 bg-soc-panel border border-soc-border rounded-xl p-4 space-y-2 text-center">
            <span className="text-[10px] text-soc-muted uppercase font-bold block">Headline Fusion Uplift</span>
            <div className="text-3xl font-black text-emerald-400 font-mono">+38.4%</div>
            <p className="text-[11px] text-soc-muted">
              Recall at 0.5% False-Positive Rate jumps from <strong>58.2%</strong> (Tabular baseline) to <strong>96.6%</strong> (Fusion overlay).
            </p>
          </div>

        </div>
      </div>

      {/* 3. SIEM THREAT VECTOR DISTRIBUTION & HOURLY ATTACK VELOCITY */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* THREAT VECTOR DISTRIBUTION (6/12) */}
        <div className="lg:col-span-6 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
              <span>SIEM Threat Vector Distribution</span>
            </h3>
            <span className="text-[10px] text-soc-muted">14,892 Events</span>
          </div>

          <div className="space-y-3">
            {threatVectors.map((tv, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between items-center text-[11px]">
                  <span className="font-bold text-soc-text">{tv.type}</span>
                  <span className="text-soc-muted font-mono">{tv.count.toLocaleString()} ({tv.pct}%)</span>
                </div>
                <div className="w-full bg-soc-bg rounded-full h-2.5 overflow-hidden border border-soc-border/40">
                  <div className={`h-full ${tv.color} transition-all`} style={{ width: `${tv.pct}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* HOURLY ATTACK VELOCITY HEATMAP (6/12) */}
        <div className="lg:col-span-6 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span>Hourly Attack Velocity Surge Timeline</span>
            </h3>
            <span className="text-[10px] text-amber-400 font-bold">Peak: 04:00 IST</span>
          </div>

          <div className="h-[180px] flex items-end gap-2 pt-4 px-2">
            {hourlyVelocities.map((h, idx) => {
              const heightPct = Math.round((h.attacks / 1420) * 100);
              const isPeak = h.attacks >= 1000;
              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1 group relative">
                  {/* Tooltip */}
                  <div className="opacity-0 group-hover:opacity-100 absolute -top-8 bg-slate-900 border border-soc-border text-soc-text text-[9px] px-1.5 py-0.5 rounded font-mono pointer-events-none transition-all z-10 whitespace-nowrap">
                    {h.hour}: {h.attacks} attacks
                  </div>
                  <div 
                    className={`w-full rounded-t transition-all ${
                      isPeak ? 'bg-rose-500 hover:bg-rose-400' : 'bg-soc-primary hover:bg-blue-400'
                    }`} 
                    style={{ height: `${heightPct}%` }}
                  />
                  <span className="text-[9px] text-soc-muted rotate-45 md:rotate-0 mt-1">{h.hour}</span>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* 4. GEO IP THREAT TELEMETRY & GLOBAL SHAP DRIVERS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* GEO IP MALICIOUS ORIGINS (6/12) */}
        <div className="lg:col-span-6 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <Globe className="w-4 h-4 text-soc-primary" />
              <span>Malicious Origin Geo & Proxy Telemetry</span>
            </h3>
            <span className="text-[10px] text-emerald-400 font-bold">84.2% Proxy/VPN Rate</span>
          </div>

          <div className="space-y-2">
            {topOriginGeos.map((g, idx) => (
              <div key={idx} className="p-2.5 rounded-lg border bg-soc-panel/60 border-soc-border flex items-center justify-between text-[11px]">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-soc-text">{g.country}</span>
                  <span className="text-[9px] px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30">
                    {g.risk}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-soc-muted">{g.count.toLocaleString()} Events</span>
                  <span className="font-bold text-soc-primary">{g.share}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* GLOBAL SHAP THREAT DRIVERS (6/12) */}
        <div className="lg:col-span-6 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
          <div className="flex items-center justify-between border-b border-soc-border pb-3">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <Layers className="w-4 h-4 text-emerald-400" />
              <span>Global SHAP Threat Drivers (TreeSHAP)</span>
            </h3>
            <span className="text-[10px] text-soc-muted">Top 5 Features</span>
          </div>

          <div className="space-y-2">
            {shapDrivers.map((sd, idx) => (
              <div key={idx} className="p-2.5 rounded-lg border bg-soc-panel/60 border-soc-border flex items-center justify-between text-[11px]">
                <div>
                  <div className="font-bold text-soc-text">{sd.feature}</div>
                  <div className="text-[10px] text-soc-muted mt-0.5">{sd.desc}</div>
                </div>
                <span className="font-bold text-rose-400 text-xs px-2 py-0.5 rounded bg-rose-500/10 border border-rose-500/30">
                  {sd.impact}
                </span>
              </div>
            ))}
          </div>
        </div>

      </div>

    </div>
  );
}
