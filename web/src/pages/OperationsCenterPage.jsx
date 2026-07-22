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
  Layers,
  Landmark,
  User,
  Smartphone,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

import EnterpriseBadge from '../components/common/EnterpriseBadge';
import StatusBadge from '../components/common/StatusBadge';
import SeverityBadge from '../components/common/SeverityBadge';
import RiskBadge from '../components/common/RiskBadge';
import MetricCard from '../components/common/MetricCard';
import Table from '../components/common/Table';
import SearchInput from '../components/common/SearchInput';
import Button from '../components/common/Button';

// Pre-Transaction Security & Runtime Components
import FusionLifecyclePipeline from '../components/runtime/FusionLifecyclePipeline';
import FraudDevToolsInspector from '../components/runtime/FraudDevToolsInspector';
import NarrativeAIStoryteller from '../components/runtime/NarrativeAIStoryteller';
import CSVSchemaMapperModal from '../components/runtime/CSVSchemaMapperModal';
import SessionTrustPassportPanel from '../components/trust/SessionTrustPassportPanel';
import InvestigationIntelligencePanel from '../components/investigation/InvestigationIntelligencePanel';

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
  const [websocketStages, setWebsocketStages] = useState([]);
  const [showSecondaryFeeds, setShowSecondaryFeeds] = useState(false); // Progressive disclosure for raw logs

  // Engine Metrics State
  const [apiLatency, setApiLatency] = useState(48);
  const [wsConnected, setWsConnected] = useState(false);
  const [totalLossPrevented, setTotalLossPrevented] = useState(750000);

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

        if (data.msg_type === 'pipeline_overview') {
          setWebsocketStages([]);
        }

        if (data.msg_type === 'pipeline_stage') {
          setWebsocketStages(prev => [...prev, data]);
        }

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
    }
  ], []);

  const displayCases = evaluatedCases.length > 0 ? evaluatedCases : defaultCases;
  const activeCase = selectedCase || displayCases[0];

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
    <div className="flex flex-col gap-5 max-w-[1850px] mx-auto select-none font-sans text-soc-text pb-8">
      
      {/* SECTION 1: MISSION OVERVIEW (PRE-TRANSACTION PLATFORM HEADER) */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 flex flex-wrap items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3.5">
          <div className="p-3 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <ShieldAlert className="w-7 h-7 text-soc-primary animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-mono font-black text-soc-text tracking-wider uppercase">
                Fusion Risk OS — Pre-Transaction Cyber Fraud Prevention Platform
              </h1>
              <span className="text-[10px] font-mono px-2.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                PRE-TRANSACTION PROTECTION ACTIVE
              </span>
            </div>
            <p className="text-xs text-soc-muted font-mono mt-0.5">
              Evaluating Banking Session Trust & Mule Rings BEFORE money movement occurs
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="flex flex-col text-right">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Total Loss Prevented</span>
            <span className="font-mono font-black text-emerald-400 text-sm">INR {totalLossPrevented.toLocaleString('en-IN')}</span>
          </div>

          <div className="flex flex-col text-right border-l border-soc-border pl-6">
            <span className="text-[10px] text-soc-dim uppercase font-semibold">Pre-Tx Engine SLA</span>
            <span className="font-mono font-bold text-amber-400 text-sm">0.14 ms</span>
          </div>

          <div className="flex items-center gap-2 pl-2">
            <button
              onClick={() => setIsCSVMapperOpen(true)}
              className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-mono font-bold flex items-center gap-1.5 transition-colors shadow"
            >
              <Upload className="w-3.5 h-3.5 text-soc-primary" />
              <span>Upload Dataset</span>
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
      </div>

      {/* SECTION 2: ACTIVE SESSION / INVESTIGATION FOCUS */}
      <div className="p-4 bg-soc-panel border border-soc-border rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-soc-bg border border-soc-border rounded-xl">
            <User className="w-6 h-6 text-soc-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
                ACTIVE FOCUS SESSION: {activeTxnPayload.user_id}
              </span>
              <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                CRITICAL IN REVIEW
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1 flex items-center gap-3">
              Target Customer: Rajesh Kumar ({activeTxnPayload.user_id})
              <span className="text-xs text-soc-dim font-normal">| Device Fingerprint: <strong className="text-soc-text font-bold">{activeTxnPayload.device_id}</strong></span>
            </h2>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="flex flex-col text-right">
            <span className="text-[10px] text-soc-dim uppercase">Assigned SOC Analyst</span>
            <span className="font-bold text-soc-text">Analyst_04 (Tier-3)</span>
          </div>

          <div className="flex flex-col text-right border-l border-soc-border pl-6">
            <span className="text-[10px] text-soc-dim uppercase">Active Transfer Payload</span>
            <span className="font-bold text-rose-400 text-sm">INR {activeTxnPayload.amount?.toLocaleString('en-IN')}</span>
          </div>
        </div>
      </div>

      {/* SECTION 3: MULTI-CHECKPOINT PRE-TRANSACTION TRUST PIPELINE */}
      <div className="w-full">
        <FusionLifecyclePipeline activeTxn={activeTxnPayload} evaluation={activeCase} websocketStages={websocketStages} />
      </div>

      {/* SECTION 3.5: SESSION TRUST PASSPORT */}
      <SessionTrustPassportPanel sessionId="SESS_9921_CRITICAL" activeTxn={activeTxnPayload} />

      {/* SECTION 4: THREAT CORRELATION TIMELINE & MULE RING INTELLIGENCE */}
      <InvestigationIntelligencePanel caseId={activeCase.id} activeTxn={activeTxnPayload} />

      {/* SECTION 5 & 6: DECISION SUMMARY & NARRATIVE AI RESPONSE */}
      <NarrativeAIStoryteller activeTxn={activeTxnPayload} evaluation={activeCase} />

      {/* PROGRESSIVE DISCLOSURE: EXPANDABLE SECONDARY RAW STREAM FEEDS */}
      <div className="bg-soc-surface border border-soc-border rounded-xl overflow-hidden shadow-lg">
        <button
          onClick={() => setShowSecondaryFeeds(!showSecondaryFeeds)}
          className="w-full p-3.5 flex items-center justify-between bg-soc-panel hover:bg-soc-border/50 text-left transition-colors font-mono text-xs font-bold text-soc-text"
        >
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-soc-primary" />
            <span>Raw Operational Stream Feeds & Inspector (Click to Expand / Collapse)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] text-soc-muted">
              {showSecondaryFeeds ? 'Collapse Secondary Logs' : 'Expand Raw Logs & DevTools'}
            </span>
            {showSecondaryFeeds ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
          </div>
        </button>

        {showSecondaryFeeds && (
          <div className="p-4 space-y-4 font-mono text-xs border-t border-soc-border">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              {/* TRANSACTION FEED */}
              <div className="lg:col-span-6 bg-soc-panel border border-soc-border rounded-xl p-3.5">
                <div className="flex items-center justify-between border-b border-soc-border pb-2 mb-3">
                  <h3 className="text-xs font-bold text-soc-text uppercase flex items-center gap-2">
                    <Landmark className="w-4 h-4 text-soc-primary" />
                    <span>Incoming Transaction Stream</span>
                  </h3>
                  <span className="text-[10px] text-soc-muted">{displayCases.length} Txns</span>
                </div>
                <div className="max-h-[220px] overflow-y-auto space-y-2 text-[11px]">
                  {displayCases.map((c) => (
                    <div key={c.id} onClick={() => setSelectedCase(c)} className="p-2 bg-soc-bg border border-soc-border rounded flex justify-between cursor-pointer">
                      <span>{c.id} — {c.nameOrig} → {c.nameDest}</span>
                      <span className="font-bold text-rose-400">INR {c.amount.toLocaleString('en-IN')}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* SIEM LOGS */}
              <div className="lg:col-span-6 bg-soc-panel border border-soc-border rounded-xl p-3.5">
                <div className="flex items-center justify-between border-b border-soc-border pb-2 mb-3">
                  <h3 className="text-xs font-bold text-soc-text uppercase flex items-center gap-2">
                    <Radio className="w-4 h-4 text-rose-400 animate-pulse" />
                    <span>Synchronized SIEM Cyber Logs</span>
                  </h3>
                  <span className="text-[10px] text-soc-muted">{cyberEvents.length} Logs</span>
                </div>
                <div className="max-h-[220px] overflow-y-auto space-y-2 text-[11px]">
                  {cyberEvents.length === 0 ? (
                    <div className="p-2 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded">
                      [T-0:40s] Impossible Travel Login Detected (IP 185.15.2.22, Moscow ➔ Mumbai)
                    </div>
                  ) : (
                    cyberEvents.map((evt, idx) => (
                      <div key={idx} className="p-2 bg-soc-bg border border-soc-border rounded text-soc-muted">
                        {evt.timestamp} • {evt.event_type} • User: {evt.user_id} • IP: {evt.ip}
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* DEVTOOLS INSPECTOR */}
            <div className="h-[320px]">
              <FraudDevToolsInspector activeTxn={activeTxnPayload} evaluation={activeCase} />
            </div>
          </div>
        )}
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

