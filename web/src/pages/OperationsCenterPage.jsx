import React, { useState, useEffect, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ShieldAlert, 
  Activity, 
  DollarSign, 
  Cpu, 
  ArrowUpRight, 
  CheckCircle2, 
  AlertTriangle, 
  FileText, 
  Radio, 
  Server, 
  Zap, 
  Sparkles, 
  Search, 
  Filter, 
  Lock, 
  Clock, 
  UserCheck, 
  TrendingUp, 
  RefreshCw,
  Upload,
  Terminal,
  Layers
} from 'lucide-react';

import EnterpriseBadge from '../components/common/EnterpriseBadge';
import StatusBadge from '../components/common/StatusBadge';
import SeverityBadge from '../components/common/SeverityBadge';
import RiskBadge from '../components/common/RiskBadge';
import MetricCard from '../components/common/MetricCard';
import Table from '../components/common/Table';
import SearchInput from '../components/common/SearchInput';
import Button from '../components/common/Button';

// Fusion Runtime Components
import FusionLifecyclePipeline from '../components/runtime/FusionLifecyclePipeline';
import FraudDevToolsInspector from '../components/runtime/FraudDevToolsInspector';
import NarrativeAIStoryteller from '../components/runtime/NarrativeAIStoryteller';
import CSVSchemaMapperModal from '../components/runtime/CSVSchemaMapperModal';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';
const WS_BASE = API_BASE.replace(/^http/, 'ws');

export default function OperationsCenterPage() {
  const navigate = useNavigate();

  // Real-time State
  const [streamEvents, setStreamEvents] = useState([]);
  const [cyberEvents, setCyberEvents] = useState([]);
  const [evaluatedCases, setEvaluatedCases] = useState([]);
  const [selectedCase, setSelectedCase] = useState(null);
  const [quantumData, setQuantumData] = useState(null);
  const [isCSVMapperOpen, setIsCSVMapperOpen] = useState(false);

  // Engine Metrics State
  const [apiLatency, setApiLatency] = useState(48);
  const [wsConnected, setWsConnected] = useState(false);
  const [totalLossPrevented, setTotalLossPrevented] = useState(750000);
  const [filterVerdict, setFilterVerdict] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('score');

  const wsRef = useRef(null);

  useEffect(() => {
    fetchQuantumPosture();
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const fetchQuantumPosture = async () => {
    try {
      const res = await fetch(`${API_BASE}/quantum/posture`);
      if (res.ok) {
        const data = await res.json();
        setQuantumData(data);
      }
    } catch (e) {
      console.warn("Quantum API fetch warning:", e);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    wsRef.current = new WebSocket(`${WS_BASE}/ws/stream`);

    wsRef.current.onopen = () => setWsConnected(true);
    wsRef.current.onclose = () => setWsConnected(false);

    wsRef.current.onmessage = async (evt) => {
      try {
        const data = JSON.parse(evt.data);
        if (data.msg_type === 'status') return;

        if (data.msg_type === 'cyber_event') {
          setCyberEvents(prev => [data, ...prev].slice(0, 50));
        }

        if (data.msg_type === 'transaction') {
          setStreamEvents(prev => [data, ...prev].slice(0, 50));

          const startTime = performance.now();
          const evalRes = await fetch(`${API_BASE}/evaluate/transaction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });

          const latency = Math.round(performance.now() - startTime);
          setApiLatency(latency > 0 ? latency : 48);

          if (evalRes.ok) {
            const evalData = await evalRes.json();
            
            const caseRecord = {
              id: `CASE-2026-${Math.floor(8900 + Math.random() * 100)}`,
              txn_id: data.txn_id || 'txn_demo_999',
              user_id: data.user_id || 'usr_abc',
              nameOrig: data.nameOrig || 'ACC_ABC_123',
              nameDest: data.nameDest || 'ACC_MULE_NEW',
              amount: data.amount || 750000,
              score: evalData.score || 94,
              action: evalData.action || 'BLOCK',
              reasons: evalData.reasons || [],
              shap_features: evalData.shap_features || [],
              counterfactual_sentence: evalData.counterfactual_sentence || '',
              assignedAnalyst: 'Analyst_04',
              createdTime: data.timestamp || new Date().toLocaleTimeString(),
              status: evalData.action === 'BLOCK' ? 'CRITICAL IN REVIEW' : 'PENDING TRIAGE',
              slaRemaining: '04m 12s',
              rawTxn: data
            };

            setEvaluatedCases(prev => {
              const exists = prev.some(c => c.txn_id === caseRecord.txn_id);
              if (exists) return prev;
              return [caseRecord, ...prev];
            });

            if (!selectedCase || evalData.action === 'BLOCK') {
              setSelectedCase(caseRecord);
            }

            if (evalData.action === 'BLOCK') {
              setTotalLossPrevented(prev => prev + (data.amount || 750000));
            }
          }
        }
      } catch (e) {
        console.error("WS Message Error:", e);
      }
    };
  };

  const defaultCases = useMemo(() => [
    {
      id: 'CASE-2026-8942',
      txn_id: 'txn_demo_999',
      user_id: 'usr_abc',
      nameOrig: 'ACC_ABC_123',
      nameDest: 'ACC_MULE_NEW',
      amount: 750000,
      score: 94,
      action: 'BLOCK',
      reasons: [
        'High baseline fraud probability (Tabular Score: 0.82)',
        'Recent cyber compromise detected (Login from unusual IP prior to transfer)',
        'Beneficiary is part of a known mule cluster (cluster_alpha)'
      ],
      shap_features: [
        { feature: 'cyber_flag', impact: 2.1 },
        { feature: 'log_amount', impact: 1.2 },
        { feature: 'dest_balance_ratio', impact: 0.8 },
        { feature: 'time_since_last_txn', impact: -0.4 }
      ],
      counterfactual_sentence: 'Counterfactual: With no prior cyber compromise, score = 61 -> CHALLENGE, not BLOCK.',
      assignedAnalyst: 'Analyst_04 (Tier-3)',
      createdTime: '10:00:40 IST',
      status: 'CRITICAL IN REVIEW',
      slaRemaining: '03m 45s',
      cyber_compromise_in_window: true,
      dest_mule_cluster_id: 'cluster_alpha',
      ip: '185.15.2.22',
      device_id: 'dev_9999',
      type: 'TRANSFER'
    },
    {
      id: 'CASE-2026-8941',
      txn_id: 'txn_demo_998',
      user_id: 'usr_xyz',
      nameOrig: 'ACC_XYZ_992',
      nameDest: 'ACC_ATM_404',
      amount: 1200000,
      score: 82,
      action: 'BLOCK',
      reasons: [
        'New device login with MFA cookie reuse',
        'Account balance completely drained in single transaction'
      ],
      shap_features: [
        { feature: 'zero_orig_after', impact: 1.8 },
        { feature: 'log_amount', impact: 1.1 }
      ],
      counterfactual_sentence: 'Counterfactual: Without balance drain, score = 58 -> CHALLENGE.',
      assignedAnalyst: 'Analyst_04 (Tier-3)',
      createdTime: '09:45:10 IST',
      status: 'PENDING CERT-IN',
      slaRemaining: '08m 10s',
      cyber_compromise_in_window: true,
      ip: '103.45.12.8',
      device_id: 'dev_8812',
      type: 'CASH_OUT'
    }
  ], []);

  const displayCases = evaluatedCases.length > 0 ? evaluatedCases : defaultCases;
  const activeCase = selectedCase || displayCases[0];

  const filteredCases = useMemo(() => {
    return displayCases.filter(c => {
      const matchesVerdict = filterVerdict === 'ALL' || c.action === filterVerdict;
      const matchesSearch = searchQuery === '' || 
        c.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.user_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.nameOrig.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.nameDest.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesVerdict && matchesSearch;
    }).sort((a, b) => {
      if (sortBy === 'score') return b.score - a.score;
      if (sortBy === 'amount') return b.amount - a.amount;
      return 0;
    });
  }, [displayCases, filterVerdict, searchQuery, sortBy]);

  const activeTxnPayload = activeCase.rawTxn || {
    txn_id: activeCase.txn_id,
    user_id: activeCase.user_id,
    nameOrig: activeCase.nameOrig,
    nameDest: activeCase.nameDest,
    amount: activeCase.amount,
    type: activeCase.type || 'TRANSFER',
    ip: activeCase.ip || '185.15.2.22',
    device_id: activeCase.device_id || 'dev_9999',
    cyber_compromise_in_window: activeCase.cyber_compromise_in_window || true,
    dest_mule_cluster_id: activeCase.dest_mule_cluster_id || 'cluster_alpha'
  };

  return (
    <div className="flex flex-col gap-4 max-w-[1850px] mx-auto select-none font-sans text-soc-text">
      
      {/* 1. HEADER STRIP */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <ShieldAlert className="w-6 h-6 text-soc-primary animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-mono font-black text-soc-text tracking-wider uppercase">
                Fusion Risk OS — Operations Center Command Center
              </h1>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                FUSION RUNTIME ACTIVE
              </span>
            </div>
            <p className="text-xs text-soc-muted font-mono mt-0.5">
              Unified correlation pipeline: Ingesting Live Streams, Datasets, and Replay into one runtime
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <button
            onClick={() => setIsCSVMapperOpen(true)}
            className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-mono font-bold flex items-center gap-1.5 transition-colors shadow"
          >
            <Upload className="w-3.5 h-3.5 text-soc-primary" />
            <span>Upload CSV Dataset</span>
          </button>

          <button
            onClick={connectWebSocket}
            className="px-3 py-1.5 bg-soc-primary hover:bg-blue-600 text-white rounded-lg font-mono font-bold flex items-center gap-1.5 transition-colors shadow"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Replay Stream</span>
          </button>
        </div>
      </div>

      {/* 2. KPI STRIP (4 CARDS) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard title="Today's Prevented Loss" value={`INR ${totalLossPrevented.toLocaleString('en-IN')}`} subtext="100% In-Flight Interception" icon={DollarSign} color="success" />
        <MetricCard title="Critical Triage Queue" value={`${displayCases.filter(c => c.action === 'BLOCK').length} Critical Cases`} subtext={`Total Evaluated: ${displayCases.length}`} icon={ShieldAlert} color="danger" />
        <MetricCard title="AI Risk Engine SLA" value={`${apiLatency}ms Inference Avg`} subtext="LightGBM + IsoForest + GraphSAGE" icon={Activity} color="primary" />
        <MetricCard title="Post-Quantum Posture" value={`${quantumData?.vulnerable_percent || 85}% Vulnerable`} subtext="HNDL Harvest Alert Active" icon={Cpu} color="quantum" />
      </div>

      {/* 3. NARRATIVE AI STORYTELLER */}
      <NarrativeAIStoryteller activeTxn={activeTxnPayload} evaluation={activeCase} />

      {/* 4. SYNCHRONIZED 3-COLUMN OPERATIONAL INSPECTOR VIEW */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* LEFT COLUMN: INCOMING TRANSACTIONS FEED (4/12) */}
        <div className="lg:col-span-4 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg flex flex-col justify-between h-[480px]">
          <div>
            <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
              <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
                <Landmark className="w-4 h-4 text-soc-primary" />
                <span>Incoming Transaction Stream</span>
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-bg text-soc-muted border border-soc-border">
                {displayCases.length} Transactions
              </span>
            </div>

            <div className="overflow-y-auto max-h-[380px] space-y-2 font-mono text-xs pr-1 select-none">
              {displayCases.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedCase(c)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all ${
                    activeCase?.id === c.id 
                      ? 'bg-soc-primary/10 border-soc-primary shadow-md' 
                      : 'bg-soc-panel/60 border-soc-border hover:border-soc-borderHover'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-[11px] text-soc-muted font-bold">{c.createdTime}</span>
                    <EnterpriseBadge action={c.action} score={c.score} size="sm" />
                  </div>
                  <div className="flex justify-between items-center my-1 font-bold">
                    <span>{c.type || 'TRANSFER'}</span>
                    <span className="text-soc-text">INR {c.amount.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="text-[11px] text-soc-muted flex justify-between">
                    <span className="truncate w-24">{c.nameOrig}</span>
                    <span>→</span>
                    <span className="truncate w-24 text-right text-soc-primary font-bold">{c.nameDest}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CENTER COLUMN: FUSION RUNTIME PIPELINE (4/12) */}
        <div className="lg:col-span-4 h-[480px]">
          <FusionLifecyclePipeline activeTxn={activeTxnPayload} evaluation={activeCase} />
        </div>

        {/* RIGHT COLUMN: CYBER SIEM THREAT LOG STREAM (4/12) */}
        <div className="lg:col-span-4 bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg flex flex-col justify-between h-[480px]">
          <div>
            <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
              <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
                <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
                <span>Synchronized SIEM Cyber Logs</span>
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-bg text-soc-muted border border-soc-border">
                {cyberEvents.length} Alerts
              </span>
            </div>

            <div className="overflow-y-auto max-h-[380px] space-y-2 font-mono text-xs pr-1">
              {cyberEvents.length === 0 ? (
                <div className="p-3 rounded-lg border-l-4 border-l-rose-500 bg-rose-500/10 text-rose-400">
                  <div className="font-bold">[T-0:40s] Impossible Travel Login Detected</div>
                  <div className="text-[11px] text-soc-muted mt-1">IP: 185.15.2.22 (RU) | User: {activeCase?.user_id || 'usr_abc'} | 4,500 km Anomaly</div>
                </div>
              ) : (
                cyberEvents.map((evt, idx) => (
                  <div 
                    key={idx} 
                    className={`p-2.5 rounded-lg border-l-4 bg-soc-panel/60 border-soc-border ${
                      evt.severity === 'critical' ? 'border-l-rose-500 bg-rose-500/10' : 'border-l-amber-500 bg-amber-500/10'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-[11px] text-soc-muted">{evt.timestamp}</span>
                      <SeverityBadge severity={evt.severity || 'critical'} />
                    </div>
                    <div className="text-xs font-bold text-soc-text uppercase">
                      {(evt.event_type || 'COMPROMISE').replace(/_/g, ' ')}
                    </div>
                    <div className="text-[11px] text-soc-muted mt-1 flex justify-between">
                      <span>User: <strong className="text-soc-text">{evt.user_id}</strong></span>
                      <span>IP: <strong className="text-soc-text">{evt.ip}</strong></span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 5. FRAUD DEVTOOLS INSPECTOR ("CHROME DEVTOOLS FOR FRAUD") */}
      <div className="h-[360px]">
        <FraudDevToolsInspector activeTxn={activeTxnPayload} evaluation={activeCase} />
      </div>

      {/* CSV Dataset Ingestion Modal */}
      <CSVSchemaMapperModal 
        isOpen={isCSVMapperOpen} 
        onClose={() => setIsCSVMapperOpen(false)} 
        onIngest={(data) => console.log('CSV Ingested:', data)} 
      />

    </div>
  );
}
