import React, { useState, useEffect } from 'react';
import DecisionTrustReport from '../trust/DecisionTrustReport';
import InvestigationTrustPanel from '../trust/InvestigationTrustPanel';
import DecisionStabilityInspector from '../trust/DecisionStabilityInspector';
import TrustFabricLedgerBadge from '../trust/TrustFabricLedgerBadge';
import { 
  Play, 
  RotateCcw, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2, 
  Cpu, 
  Database, 
  Sliders, 
  Share2, 
  ShieldAlert, 
  TrendingUp, 
  Zap, 
  Layers, 
  Activity, 
  Shield, 
  FileText, 
  Layout, 
  ChevronRight, 
  ChevronDown,
  ChevronUp,
  Eye, 
  ArrowDown, 
  Terminal, 
  Lock, 
  Sparkles,
  Inbox,
  CheckSquare,
  RefreshCw,
  UserCheck,
  Smartphone,
  Globe,
  Clock,
  Radio,
  ExternalLink
} from 'lucide-react';

const SAMPLE_DATASETS = [
  { id: 'paysim', name: 'PaySim Fraud Dataset (Kaggle)', records: '6.3M Txns' },
  { id: 'ieee_cis', name: 'IEEE-CIS Fraud & Identity', records: '590K Txns' },
  { id: 'elliptic', name: 'Elliptic Bitcoin Graph', records: '203K Nodes' },
  { id: 'synthetic_fusion', name: 'Synthetic Cyber-Overlay (Controlled)', records: '50K Events' }
];

const SAMPLE_TRANSACTIONS = [
  {
    txn_id: 'TXN-81293',
    user_id: 'usr_abc',
    amount: 750000.0,
    type: 'TRANSFER',
    nameOrig: 'ACC_ABC_123',
    nameDest: 'ACC_MULE_NEW',
    ip: '185.15.2.22',
    device_id: 'dev_9999',
    cyber_compromise_in_window: true,
    dest_mule_cluster_id: 'cluster_alpha',
    description: 'Critical Cyber-Preceded Transfer (Demo standard)'
  },
  {
    txn_id: 'TXN-81294',
    user_id: 'usr_xyz',
    amount: 1200000.0,
    type: 'CASH_OUT',
    nameOrig: 'ACC_XYZ_992',
    nameDest: 'ACC_ATM_404',
    ip: '103.45.12.8',
    device_id: 'dev_8812',
    cyber_compromise_in_window: true,
    dest_mule_cluster_id: 'cluster_beta',
    description: 'High-Value Balance Drain to ATM Ring'
  },
  {
    txn_id: 'TXN-81295',
    user_id: 'usr_clean_01',
    amount: 4500.0,
    type: 'PAYMENT',
    nameOrig: 'ACC_RETAIL_10',
    nameDest: 'ACC_MERCHANT_99',
    ip: '49.207.18.9',
    device_id: 'dev_1102',
    cyber_compromise_in_window: false,
    dest_mule_cluster_id: null,
    description: 'Normal Retail Merchant Payment'
  }
];

export default function RealTimeProcessingPipeline({ activeTxn, evaluation, websocketStages }) {
  const [selectedDataset, setSelectedDataset] = useState(SAMPLE_DATASETS[3]);
  const [selectedTxn, setSelectedTxn] = useState(SAMPLE_TRANSACTIONS[0]);
  const [expandedStageId, setExpandedStageId] = useState(null); // Only one expanded at a time
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(10);

  useEffect(() => {
    if (activeTxn) {
      const matched = SAMPLE_TRANSACTIONS.find(t => t.txn_id === activeTxn.txn_id);
      if (matched) {
        setSelectedTxn(matched);
      }
    }
  }, [activeTxn]);

  const isCyberTxn = selectedTxn.cyber_compromise_in_window;
  const isMuleTxn = Boolean(selectedTxn.dest_mule_cluster_id);
  const isCleanTxn = !isCyberTxn && !isMuleTxn;

  const compositeRiskScore = isCleanTxn ? 18 : 94;
  const verdictAction = isCleanTxn ? 'ALLOW' : 'BLOCK';

  // 10 Sequential Pre-Transaction & Response Stages
  const sequentialWorkflowStages = [
    {
      id: 'stg_login',
      name: '1. Login & Auth Ingestion',
      icon: Clock,
      status: 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '99.0%',
      summary: `User ${selectedTxn.user_id} session initiated from IP ${selectedTxn.ip}`,
      details: {
        channel: 'Mobile Banking API',
        mfa_verified: true,
        session_token: 'TOK_JWT_99218',
        timestamp: new Date().toLocaleTimeString()
      }
    },
    {
      id: 'stg_identity',
      name: '2. Identity Intelligence',
      icon: UserCheck,
      status: 'COMPLETED',
      execTimeMs: '0.02 ms',
      confidence: '98.0%',
      summary: 'KYC Verified Tier-3 Biometric • Account Age > 3 Years',
      details: {
        kyc_status: 'VERIFIED TIER-3 (BIOMETRIC)',
        risk_tier: 'HIGH (Corporate)',
        relationship_manager: 'RM_ANKIT_SHARMA',
        trust_level: 94.5
      }
    },
    {
      id: 'stg_device',
      name: '3. Device Intelligence',
      icon: Smartphone,
      status: isCyberTxn ? 'FLAGGED' : 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '94.0%',
      summary: isCyberTxn ? 'Unregistered Fingerprint dev_9999 • SIM Swap Check Flagged' : 'Registered Device iPhone 15 Pro',
      details: {
        device_id: selectedTxn.device_id,
        fingerprint: 'FP_a1b2c3d4e5',
        rooted: false,
        proxy_vpn_flag: isCyberTxn,
        trust_score: isCyberTxn ? 0.12 : 0.98
      }
    },
    {
      id: 'stg_behavior',
      name: '4. Behavior Intelligence',
      icon: Activity,
      status: isCyberTxn ? 'FLAGGED' : 'COMPLETED',
      execTimeMs: '0.02 ms',
      confidence: '96.0%',
      summary: isCyberTxn ? 'Anomalous Transfer Amount (INR 7.5L) • Deviation Index 82.5%' : 'Normal Spending Envelope',
      details: {
        login_hour: '10:00 IST (Preferred)',
        normal_range: 'INR 500 – INR 50,000',
        behavior_drift: isCyberTxn ? 0.82 : 0.04
      }
    },
    {
      id: 'stg_cyber',
      name: '5. Cyber Threat Intelligence',
      icon: Radio,
      status: isCyberTxn ? 'CRITICAL_THREAT' : 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '98.0%',
      summary: isCyberTxn ? 'Impossible Travel (Moscow ➔ Mumbai) • Malicious ASN AS49505' : 'Clean IP Reputation',
      details: {
        mitre_mapped: isCyberTxn ? ['T1078.004 Valid Accounts', 'T1539 Cookie Theft'] : [],
        asn_reputation: isCyberTxn ? 'AS49505 OOO Baxet (Proxy Pool)' : 'Jio Fiber Clean',
        geo_velocity_kmh: isCyberTxn ? 4500 : 12.5
      }
    },
    {
      id: 'stg_graph',
      name: '6. Neo4j Graph Mule Intelligence',
      icon: Share2,
      status: isMuleTxn ? 'MULE_RING_LINK' : 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '96.0%',
      summary: isMuleTxn ? 'Direct 1-Hop Link to Mule Ring Cluster Alpha' : 'Clean Graph Neighborhood',
      details: {
        mule_ring_id: selectedTxn.dest_mule_cluster_id || 'NONE',
        pagerank_centrality: isMuleTxn ? 0.0450 : 0.0012,
        neighborhood_nodes: 14,
        community_id: 'MULE_RING_ALPHA'
      }
    },
    {
      id: 'stg_passport',
      name: '7. Session Trust Passport',
      icon: Shield,
      status: isCleanTxn ? 'ISSUED_ALLOW' : 'ISSUED_BLOCK',
      execTimeMs: '0.02 ms',
      confidence: '97.0%',
      summary: `Overall Session Trust: ${isCleanTxn ? '94.0%' : '29.0%'} • Verdict: ${verdictAction}`,
      details: {
        session_passport_id: 'SESS_9921_CRITICAL',
        verdict: verdictAction,
        monitoring_level: isCleanTxn ? 'LOW' : 'CRITICAL',
        expiry: '15 Minutes Sliding Window'
      }
    },
    {
      id: 'stg_decision',
      name: '8. Fusion Decision Engine',
      icon: Cpu,
      status: 'COMPLETED',
      execTimeMs: '0.02 ms',
      confidence: '98.0%',
      summary: `LightGBM (0.82) + IsoForest (0.94) + GraphSAGE (0.045) ➔ ${verdictAction}`,
      details: {
        model_agreement: '98.0% Agreement',
        composite_risk: compositeRiskScore,
        counterfactual: isCyberTxn ? 'With no prior cyber compromise, score = 61 -> CHALLENGE, not BLOCK.' : 'Clean parameters.'
      }
    },
    {
      id: 'stg_response',
      name: '9. Automated Response Orchestrator',
      icon: Zap,
      status: 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '100%',
      summary: isCleanTxn ? 'Transaction Cleared' : 'Pre-Transaction In-Flight Interception Executed (INR 7.5L Prevented)',
      details: {
        action_type: verdictAction === 'BLOCK' ? 'PRE_TRANSACTION_BLOCK_AND_FREEZE' : 'ALLOW',
        loss_prevented: isCleanTxn ? 'INR 0.00' : 'INR 7,50,000.00'
      }
    },
    {
      id: 'stg_evidence',
      name: '10. Evidence Locker & CERT-In Export',
      icon: FileText,
      status: 'COMPLETED',
      execTimeMs: '0.01 ms',
      confidence: '100%',
      summary: `Cryptographic Evidence Hash Sealed (EVID-${selectedTxn.txn_id})`,
      details: {
        evidence_hash: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        cert_in_eligible: !isCleanTxn
      }
    }
  ];

  const toggleExpandStage = (id) => {
    setExpandedStageId(expandedStageId === id ? null : id);
  };

  const STAGE_ICONS = [
    Inbox, CheckSquare, RefreshCw, Layers, Activity, ShieldAlert, Smartphone, Share2, 
    Share2, Cpu, Cpu, FileText, Database, Shield, Lock, Radio
  ];

  const liveStages = (websocketStages || []).map((stg, i) => ({
    id: stg.stage_id || `live_stg_${i}`,
    name: stg.name || `Stage ${i + 1}`,
    icon: STAGE_ICONS[i % STAGE_ICONS.length] || Activity,
    status: stg.status ? stg.status.toUpperCase() : 'COMPLETED',
    execTimeMs: stg.timing_ms !== undefined ? `${stg.timing_ms} ms` : '0.00 ms',
    confidence: '100%',
    summary: stg.summary || '',
    details: stg.evidence || {}
  }));

  const hasLiveStages = liveStages.length > 0;
  const stagesToRender = hasLiveStages ? liveStages : sequentialWorkflowStages;
  
  const totalLatency = hasLiveStages 
    ? (websocketStages.reduce((sum, s) => sum + (s.timing_ms || 0), 0)).toFixed(2) + ' ms'
    : '0.14 ms';

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl font-mono text-xs select-none space-y-4">
      
      {/* HEADER & DATASET SELECTOR */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-soc-border pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-soc-primary/20 border border-soc-primary/40 rounded-lg">
            <Cpu className="w-5 h-5 text-soc-primary animate-pulse" />
          </div>
          <div>
            <h2 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <span>Multi-Checkpoint Pre-Transaction Workflow</span>
              <span className={`text-[10px] px-2 py-0.5 rounded font-bold border ${hasLiveStages ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'}`}>
                {hasLiveStages ? `${stagesToRender.length} LIVE STAGES` : 'AWAITING LIVE STREAM'}
              </span>
            </h2>
            <p className="text-[11px] text-soc-muted">
              Pre-transaction evaluation from Login & Auth to Evidence Locker
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={selectedTxn.txn_id}
            onChange={(e) => {
              const matched = SAMPLE_TRANSACTIONS.find(t => t.txn_id === e.target.value);
              if (matched) setSelectedTxn(matched);
            }}
            className="bg-soc-bg border border-soc-border rounded-lg px-2.5 py-1 text-soc-text font-mono text-xs focus:outline-none focus:border-soc-primary"
          >
            {SAMPLE_TRANSACTIONS.map(t => (
              <option key={t.txn_id} value={t.txn_id}>
                Payload: {t.txn_id} — INR {t.amount.toLocaleString('en-IN')}
              </option>
            ))}
          </select>

          <span className="text-[10px] font-mono px-2.5 py-1 bg-soc-panel border border-soc-border text-soc-muted rounded font-bold">
            Total Pipeline Latency: <strong className="text-amber-400">{totalLatency}</strong>
          </span>
        </div>
      </div>

      {/* SEQUENTIAL WORKFLOW STAGES (EXPANDABLE ONE AT A TIME) */}
      <div className="space-y-2">
        {stagesToRender.map((stg) => {
          const Icon = stg.icon;
          const isExpanded = expandedStageId === stg.id;
          const isFlagged = stg.status.includes('FLAGGED') || stg.status.includes('CRITICAL') || stg.status.includes('MULE') || stg.status.includes('BLOCK');

          return (
            <div key={stg.id} className="bg-soc-panel border border-soc-border rounded-lg overflow-hidden transition-all shadow-sm">
              <button
                onClick={() => toggleExpandStage(stg.id)}
                className="w-full p-3 flex items-center justify-between bg-soc-surface/60 hover:bg-soc-surface text-left transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded ${isFlagged ? 'bg-rose-500/20 text-rose-400' : 'bg-soc-bg text-soc-primary'}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-bold text-soc-text text-xs">{stg.name}</span>
                    <div className="text-[10px] text-soc-muted truncate max-w-xl">{stg.summary}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className={`font-mono font-bold text-xs ${isFlagged ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {stg.status}
                    </span>
                    <div className="text-[10px] text-soc-dim">{stg.execTimeMs} • Conf: {stg.confidence}</div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-4 h-4 text-soc-dim" /> : <ChevronDown className="w-4 h-4 text-soc-dim" />}
                </div>
              </button>

              {/* EXPANDED STAGE DETAILS (ON-DEMAND) */}
              {isExpanded && (
                <div className="p-3 border-t border-soc-border bg-soc-bg/90 space-y-2 font-mono text-xs">
                  <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider block">Inspected Stage Evidence & Parameters</span>
                  <pre className="p-3 bg-slate-950 border border-soc-border rounded-lg text-emerald-400 text-[11px] overflow-x-auto font-mono leading-relaxed">
                    {JSON.stringify(stg.details, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* TRUST FABRIC SUMMARY */}
      <div className="pt-2">
        <TrustFabricLedgerBadge ledgerRecord={evaluation?.trust_metrics?.ledger_record} />
      </div>

    </div>
  );
}

