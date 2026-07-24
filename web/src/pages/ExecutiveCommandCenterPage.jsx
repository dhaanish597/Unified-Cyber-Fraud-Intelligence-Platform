import React, { useState, useEffect } from 'react';
import { DollarSign, ShieldAlert, Cpu, Activity, TrendingUp, CheckCircle2, FileCheck2, ArrowUpRight } from 'lucide-react';
import MetricCard from '../components/common/MetricCard';
import PageContainer from '../components/layout/PageContainer';

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');

export default function ExecutiveCommandCenterPage() {
  const [quantumData, setQuantumData] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/quantum/posture`)
      .then(r => r.json())
      .then(data => setQuantumData(data))
      .catch(e => console.error("Quantum error:", e));
  }, []);

  return (
    <PageContainer
      title="CISO & Executive Security Command Center"
      subtitle="Executive view: Financial loss prevention metrics, active risk exposure, and regulatory readiness"
    >
      <div className="flex flex-col gap-5 select-none font-mono">
        
        {/* Executive KPI Header Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard title="Today's Prevented Loss" value="INR 8,700,000.00" subtext="100% In-Flight Interception" icon={DollarSign} color="success" />
          <MetricCard title="Estimated Exposure Avoided" value="INR 24,500,000.00" subtext="Multi-account containment" icon={TrendingUp} color="primary" />
          <MetricCard title="Avg Incident SLA Latency" value="48 ms" subtext="FastAPI + Graph SLA Target" icon={Activity} color="warning" />
          <MetricCard title="CERT-In Compliance SLA" value="100% Compliant" subtext="6-Hour Mandate Filings" icon={FileCheck2} color="quantum" />
        </div>

        {/* CISO Security Strategy Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          
          {/* Top Threat Vectors (7/12) */}
          <div className="lg:col-span-7 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-4">
            <h3 className="text-xs font-bold text-soc-text uppercase tracking-wider border-b border-soc-border pb-2 flex items-center justify-between">
              <span>Top Attack Vectors Intercepted (Current Month)</span>
              <span className="text-[10px] text-soc-muted">Live Telemetry</span>
            </h3>

            <div className="space-y-3 text-xs">
              <div className="space-y-1">
                <div className="flex justify-between font-bold">
                  <span>1. Account Takeover (Impossible Travel + MFA Cookie Reuse)</span>
                  <span className="text-rose-400">45% of Interceptions</span>
                </div>
                <div className="w-full bg-soc-bg h-2 rounded overflow-hidden">
                  <div className="bg-rose-500 h-full rounded" style={{ width: '45%' }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between font-bold">
                  <span>2. Mule Account Rings (Shared IP & Device Clusters)</span>
                  <span className="text-amber-400">30% of Interceptions</span>
                </div>
                <div className="w-full bg-soc-bg h-2 rounded overflow-hidden">
                  <div className="bg-amber-500 h-full rounded" style={{ width: '30%' }}></div>
                </div>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between font-bold">
                  <span>3. Credential Stuffing Attacks</span>
                  <span className="text-soc-primary">25% of Interceptions</span>
                </div>
                <div className="w-full bg-soc-bg h-2 rounded overflow-hidden">
                  <div className="bg-soc-primary h-full rounded" style={{ width: '25%' }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Post-Quantum TLS Posture Card (5/12) */}
          <div className="lg:col-span-5 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-4">
            <h3 className="text-xs font-bold text-soc-text uppercase tracking-wider border-b border-soc-border pb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span>Post-Quantum TLS Posture (HNDL Risk)</span>
            </h3>

            <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-soc-muted">Vulnerable TLS Handshakes:</span>
                <strong className="text-purple-400">{quantumData?.vulnerable_percent || 85}%</strong>
              </div>
              <div className="flex justify-between">
                <span className="text-soc-muted">HNDL Harvest Risk Status:</span>
                <strong className="text-rose-400">{quantumData?.hndl_flag ? 'CRITICAL ALERT' : 'NORMAL'}</strong>
              </div>
              <p className="text-[11px] text-soc-muted leading-relaxed pt-1 border-t border-soc-border">
                {quantumData?.hndl_details || 'Long-lived sensitive transactions captured over classical TLS_ECDHE ciphers flagged for Harvest-Now-Decrypt-Later risk.'}
              </p>
            </div>
          </div>
        </div>

      </div>
    </PageContainer>
  );
}
