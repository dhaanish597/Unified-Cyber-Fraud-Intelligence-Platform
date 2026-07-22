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
  Eye, 
  ArrowDown, 
  Terminal, 
  Lock, 
  Sparkles,
  Inbox,
  CheckSquare,
  RefreshCw,
  UserCheck,
  Smartphone
} from 'lucide-react';

const STAGE_ICON_MAP = {
  stage_1_incoming: Inbox,
  stage_2_validation: CheckSquare,
  stage_3_normalization: RefreshCw,
  stage_4_feature_eng: Sliders,
  stage_5_behavior: UserCheck,
  stage_6_cyber: ShieldAlert,
  stage_7_device: Smartphone,
  stage_8_graph_lookup: Share2,
  stage_9_graph_sage: Cpu,
  stage_10_lightgbm: TrendingUp,
  stage_11_iso_forest: Zap,
  stage_12_shap: Layers,
  stage_13_fusion: Activity,
  stage_14_decision: Shield,
  stage_15_evidence: FileText,
  stage_16_ops_center: Layout
};

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
  const [currentStepIndex, setCurrentStepIndex] = useState(16); // 16 = fully completed by default
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeStageEvidence, setActiveStageEvidence] = useState(null);

  useEffect(() => {
    if (activeTxn) {
      const matched = SAMPLE_TRANSACTIONS.find(t => t.txn_id === activeTxn.txn_id);
      if (matched) {
        setSelectedTxn(matched);
      }
    }
  }, [activeTxn]);

  // Handle incoming websocket stage updates if streaming live
  useEffect(() => {
    if (websocketStages && websocketStages.length > 0) {
      setCurrentStepIndex(websocketStages.length);
    }
  }, [websocketStages]);

  const handlePlayPipeline = () => {
    setIsPlaying(true);
    setCurrentStepIndex(1);
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev >= 16) {
          clearInterval(interval);
          setIsPlaying(false);
          return 16;
        }
        return prev + 1;
      });
    }, 180);
  };

  const handleResetPipeline = () => {
    setIsPlaying(false);
    setCurrentStepIndex(16);
    setActiveStageEvidence(null);
  };

  const isCyberTxn = selectedTxn.cyber_compromise_in_window;
  const isMuleTxn = Boolean(selectedTxn.dest_mule_cluster_id);
  const isCleanTxn = !isCyberTxn && !isMuleTxn;

  const compositeRiskScore = isCleanTxn ? 18 : 94;
  const verdictAction = isCleanTxn ? 'ALLOW' : 'BLOCK';
  const lightgbmProb = isCleanTxn ? 0.08 : 0.87;
  const isoForestScore = isCleanTxn ? 0.12 : 0.94;
  const pageRankScore = isCleanTxn ? 0.0012 : 0.0421;

  // 16 Detailed Stages Definition with Evidence
  const pipelineStages = [
    {
      stage_index: 1,
      stage_id: 'stage_1_incoming',
      name: 'Incoming Transaction',
      checklist: `✔ Received ${selectedTxn.txn_id}`,
      status: currentStepIndex >= 1 ? 'completed' : 'pending',
      evidence: {
        txn_id: selectedTxn.txn_id,
        user_id: selectedTxn.user_id,
        amount: selectedTxn.amount,
        type: selectedTxn.type,
        nameOrig: selectedTxn.nameOrig,
        nameDest: selectedTxn.nameDest,
        timestamp: new Date().toISOString()
      }
    },
    {
      stage_index: 2,
      stage_id: 'stage_2_validation',
      name: 'Validation',
      checklist: '✔ Validated',
      status: currentStepIndex >= 2 ? 'completed' : 'pending',
      evidence: {
        schema_format: 'ISO_20022 / JSON',
        field_completeness: '100%',
        mandatory_checks: ['user_id', 'amount', 'nameOrig', 'nameDest'],
        validation_status: 'PASSED'
      }
    },
    {
      stage_index: 3,
      stage_id: 'stage_3_normalization',
      name: 'Normalization',
      checklist: '✔ Parsed',
      status: currentStepIndex >= 3 ? 'completed' : 'pending',
      evidence: {
        scaled_amount: selectedTxn.amount,
        log_amount: Math.log1p(selectedTxn.amount).toFixed(3),
        clean_orig: selectedTxn.nameOrig,
        clean_dest: selectedTxn.nameDest
      }
    },
    {
      stage_index: 4,
      stage_id: 'stage_4_feature_eng',
      name: 'Feature Engineering',
      checklist: '✔ Feature Engineered',
      status: currentStepIndex >= 4 ? 'completed' : 'pending',
      evidence: {
        feature_vector_dimension: 18,
        features: {
          log_amount: Math.log1p(selectedTxn.amount).toFixed(3),
          balance_drain_ratio: isCleanTxn ? 0.05 : 1.0,
          dest_balance_zero_before: !isCleanTxn,
          time_delta_last_txn_sec: isCleanTxn ? 86400 : 40
        }
      }
    },
    {
      stage_index: 5,
      stage_id: 'stage_5_behavior',
      name: 'Behavior Analysis',
      checklist: '✔ Behavior Analyzed',
      status: currentStepIndex >= 5 ? 'completed' : 'pending',
      evidence: {
        historical_user_avg_amount: 15000,
        amount_percentile: isCleanTxn ? 45.0 : 99.8,
        is_midnight_transfer: false,
        spending_velocity_anomaly: !isCleanTxn
      }
    },
    {
      stage_index: 6,
      stage_id: 'stage_6_cyber',
      name: 'Cyber Correlation',
      checklist: isCyberTxn ? '✔ Cyber Event Correlated' : '✔ SIEM Clean',
      status: currentStepIndex >= 6 ? (isCyberTxn ? 'flagged' : 'completed') : 'pending',
      evidence: {
        siem_lookup_window: '60 seconds',
        impossible_travel_login: isCyberTxn,
        origin_ip: selectedTxn.ip,
        geo_jump: isCyberTxn ? 'Moscow, RU ➔ Mumbai, IN (4,500 km in 40s)' : 'Mumbai, IN (Normal)',
        matched_siem_alert_id: isCyberTxn ? 'ALT-CYBER-8819' : 'NONE'
      }
    },
    {
      stage_index: 7,
      stage_id: 'stage_7_device',
      name: 'Device Intelligence',
      checklist: '✔ Device Fingerprint Found',
      status: currentStepIndex >= 7 ? (isCyberTxn ? 'flagged' : 'completed') : 'pending',
      evidence: {
        device_id: selectedTxn.device_id,
        mfa_cookie_reuse: isCyberTxn,
        proxy_vpn_detected: isCyberTxn,
        device_trust_score: isCyberTxn ? 0.12 : 0.98
      }
    },
    {
      stage_index: 8,
      stage_id: 'stage_8_graph_lookup',
      name: 'Graph Lookup',
      checklist: '✔ Graph Built',
      status: currentStepIndex >= 8 ? 'completed' : 'pending',
      evidence: {
        nodes_traversed: isMuleTxn ? 14 : 3,
        edges_traversed: isMuleTxn ? 28 : 2,
        beneficiary_cluster: selectedTxn.dest_mule_cluster_id || 'Clean Individual'
      }
    },
    {
      stage_index: 9,
      stage_id: 'stage_9_graph_sage',
      name: 'GraphSAGE Embedding',
      checklist: `✔ PageRank Computed (${pageRankScore})`,
      status: currentStepIndex >= 9 ? 'completed' : 'pending',
      evidence: {
        pagerank_centrality: pageRankScore,
        graphsage_embedding_dim: 64,
        louvain_community: isMuleTxn ? 'Mule Ring Alpha' : 'Standard Cluster 04'
      }
    },
    {
      stage_index: 10,
      stage_id: 'stage_10_lightgbm',
      name: 'LightGBM Prediction',
      checklist: `✔ LightGBM Prediction ${lightgbmProb}`,
      status: currentStepIndex >= 10 ? 'completed' : 'pending',
      evidence: {
        model: 'LightGBM Supervised Fraud Classifier',
        probability: lightgbmProb,
        trees_evaluated: 100
      }
    },
    {
      stage_index: 11,
      stage_id: 'stage_11_iso_forest',
      name: 'Isolation Forest',
      checklist: `✔ Isolation Forest ${isoForestScore}`,
      status: currentStepIndex >= 11 ? 'completed' : 'pending',
      evidence: {
        model: 'Isolation Forest Zero-Day Anomaly Detector',
        anomaly_index: isoForestScore,
        raw_score: isCleanTxn ? 0.12 : -0.24,
        zero_day_pattern_flag: !isCleanTxn
      }
    },
    {
      stage_index: 12,
      stage_id: 'stage_12_shap',
      name: 'SHAP Explanation',
      checklist: '✔ SHAP Generated',
      status: currentStepIndex >= 12 ? 'completed' : 'pending',
      evidence: {
        top_drivers: [
          { feature: 'cyber_compromise_flag', impact: isCyberTxn ? +2.1 : 0.0 },
          { feature: 'log_amount', impact: +1.2 },
          { feature: 'mule_cluster_risk', impact: isMuleTxn ? +0.8 : 0.0 }
        ]
      }
    },
    {
      stage_index: 13,
      stage_id: 'stage_13_fusion',
      name: 'Risk Fusion Engine',
      checklist: `✔ Composite Risk ${compositeRiskScore}`,
      status: currentStepIndex >= 13 ? (compositeRiskScore >= 75 ? 'flagged' : 'completed') : 'pending',
      evidence: {
        composite_risk_score: compositeRiskScore,
        weights: {
          lightgbm_tabular: '60%',
          cyber_siem_overlay: '15%',
          graph_centrality: '10%',
          isolation_forest: '15%'
        }
      }
    },
    {
      stage_index: 14,
      stage_id: 'stage_14_decision',
      name: 'Decision Engine',
      checklist: `✔ ${verdictAction}`,
      status: currentStepIndex >= 14 ? (verdictAction === 'BLOCK' ? 'flagged' : 'completed') : 'pending',
      evidence: {
        verdict: verdictAction,
        policy_rule: verdictAction === 'BLOCK' ? 'RULE_CRITICAL_FUSION_BLOCK' : 'RULE_ALLOW_STANDARD',
        counterfactual: isCyberTxn ? 'With no prior cyber compromise, score = 61 -> CHALLENGE, not BLOCK.' : 'Clean parameters.'
      }
    },
    {
      stage_index: 15,
      stage_id: 'stage_15_evidence',
      name: 'Evidence Generator',
      checklist: '✔ Evidence Package Sealed',
      status: currentStepIndex >= 15 ? 'completed' : 'pending',
      evidence: {
        evidence_package_id: `EVID-${selectedTxn.txn_id}`,
        sha256_hash: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`,
        cert_in_report_eligible: verdictAction === 'BLOCK'
      }
    },
    {
      stage_index: 16,
      stage_id: 'stage_16_ops_center',
      name: 'Operations Center',
      checklist: '✔ Dispatched to SOC Command',
      status: currentStepIndex >= 16 ? 'completed' : 'pending',
      evidence: {
        case_id: `CASE-2026-${selectedTxn.txn_id.slice(-4)}`,
        assigned_tier: 'Analyst_04 (Tier-3)',
        status: 'LOCKED IN CRITICAL TRIAGE QUEUE'
      }
    }
  ];

  const dataFlowHierarchy = [
    { label: 'Input Dataset', val: selectedDataset.name },
    { label: 'Selected Transaction', val: `${selectedTxn.txn_id} (INR ${selectedTxn.amount.toLocaleString('en-IN')})` },
    { label: 'Feature Vector', val: '18 Engineered Features' },
    { label: 'Graph Features', val: `PageRank ${pageRankScore}` },
    { label: 'Cyber Features', val: isCyberTxn ? 'Impossible Travel (4,500km)' : 'Clean SIEM' },
    { label: 'Models', val: `LGBM (${lightgbmProb}) + IsoForest (${isoForestScore})` },
    { label: 'Output', val: `Risk ${compositeRiskScore} ➔ ${verdictAction}` }
  ];

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl font-mono text-xs select-none">
      
      {/* HEADER & CONTROLS */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-soc-border pb-3 mb-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-soc-primary/20 border border-soc-primary/40 rounded-lg">
            <Cpu className="w-5 h-5 text-soc-primary animate-pulse" />
          </div>
          <div>
            <h2 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <span>Real-Time Processing Pipeline — 16-Stage Execution Lifecycle</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                WEBSOCKET LIVE BROADCAST
              </span>
            </h2>
            <p className="text-[11px] text-soc-muted">
              Granular stage-by-stage evidence production & evidence hash verification
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handlePlayPipeline}
            disabled={isPlaying}
            className={`px-3 py-1.5 rounded-lg font-mono font-bold text-xs flex items-center gap-1.5 transition-all shadow ${
              isPlaying 
                ? 'bg-soc-panel text-soc-muted cursor-not-allowed' 
                : 'bg-emerald-600 hover:bg-emerald-500 text-white'
            }`}
          >
            {isPlaying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-current" />}
            <span>{isPlaying ? 'Stepping Stages...' : 'Play Pipeline Live'}</span>
          </button>

          <button
            onClick={handleResetPipeline}
            className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-mono font-bold text-xs flex items-center gap-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset View</span>
          </button>
        </div>
      </div>

      {/* DATASET & TRANSACTION SELECTOR STRIP */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4 bg-soc-bg p-3 rounded-xl border border-soc-border">
        <div>
          <label className="text-[10px] font-bold text-soc-muted uppercase tracking-wider block mb-1.5 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-soc-primary" />
            <span>Input Dataset Context</span>
          </label>
          <select
            value={selectedDataset.id}
            onChange={(e) => setSelectedDataset(SAMPLE_DATASETS.find(d => d.id === e.target.value))}
            className="w-full bg-soc-surface border border-soc-border rounded-lg px-2.5 py-1.5 text-soc-text font-mono text-xs focus:outline-none focus:border-soc-primary"
          >
            {SAMPLE_DATASETS.map(d => (
              <option key={d.id} value={d.id}>{d.name} ({d.records})</option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-[10px] font-bold text-soc-muted uppercase tracking-wider block mb-1.5 flex items-center gap-1.5">
            <Inbox className="w-3.5 h-3.5 text-rose-400" />
            <span>Selected Transaction Payload</span>
          </label>
          <select
            value={selectedTxn.txn_id}
            onChange={(e) => {
              const matched = SAMPLE_TRANSACTIONS.find(t => t.txn_id === e.target.value);
              setSelectedTxn(matched);
              handleResetPipeline();
            }}
            className="w-full bg-soc-surface border border-soc-border rounded-lg px-2.5 py-1.5 text-soc-text font-mono text-xs focus:outline-none focus:border-soc-primary"
          >
            {SAMPLE_TRANSACTIONS.map(t => (
              <option key={t.txn_id} value={t.txn_id}>
                {t.txn_id} — INR {t.amount.toLocaleString('en-IN')} ({t.description})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* HIGH-LEVEL DATA FLOW HIERARCHY */}
      <div className="mb-4 bg-soc-panel/70 border border-soc-border rounded-xl p-3">
        <div className="text-[10px] font-bold text-soc-muted uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-amber-400" />
          <span>Pipeline Data Flow Cascade</span>
        </div>
        
        <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-mono">
          {dataFlowHierarchy.map((item, idx) => (
            <React.Fragment key={idx}>
              <div className={`px-2.5 py-1.5 rounded-lg border flex flex-col ${
                idx === dataFlowHierarchy.length - 1
                  ? verdictAction === 'BLOCK' 
                    ? 'bg-rose-500/20 border-rose-500/50 text-rose-400 font-bold' 
                    : 'bg-emerald-500/20 border-emerald-500/50 text-emerald-400 font-bold'
                  : 'bg-soc-surface border-soc-border text-soc-text'
              }`}>
                <span className="text-[9px] text-soc-muted uppercase">{item.label}</span>
                <span className="font-bold">{item.val}</span>
              </div>
              {idx < dataFlowHierarchy.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-soc-dim shrink-0" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* 16-STAGE LIFECYCLE LIST & EVIDENCE INSPECTOR SIDE-BY-SIDE */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* STAGES LIST (7/12) */}
        <div className="lg:col-span-7 bg-soc-panel border border-soc-border rounded-xl p-3 max-h-[460px] overflow-y-auto space-y-1.5">
          <div className="flex justify-between items-center pb-2 border-b border-soc-border text-[10px] font-bold text-soc-muted uppercase">
            <span>Stage & Checklist Summary</span>
            <span>Status</span>
          </div>

          {pipelineStages.map((stage) => {
            const Icon = STAGE_ICON_MAP[stage.stage_id] || Cpu;
            const isCompleted = stage.status === 'completed' || stage.status === 'flagged';
            const isFlagged = stage.status === 'flagged';
            const isSelected = activeStageEvidence?.stage_id === stage.stage_id;

            return (
              <div
                key={stage.stage_id}
                onClick={() => setActiveStageEvidence(stage)}
                className={`p-2.5 rounded-lg border cursor-pointer transition-all flex items-center justify-between ${
                  isSelected
                    ? 'bg-soc-primary/20 border-soc-primary shadow-md'
                    : isFlagged
                    ? 'bg-rose-500/10 border-rose-500/40 text-rose-400'
                    : isCompleted
                    ? 'bg-soc-surface border-soc-border hover:border-soc-borderHover text-soc-text'
                    : 'bg-soc-bg border-soc-border/40 text-soc-dim opacity-60'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <div className={`p-1.5 rounded-md ${
                    isFlagged ? 'bg-rose-500/20 text-rose-400' : isCompleted ? 'bg-emerald-500/15 text-emerald-400' : 'bg-soc-bg text-soc-dim'
                  }`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <div className="font-bold text-xs flex items-center gap-1.5">
                      <span>{stage.name}</span>
                      {isSelected && <span className="text-[9px] px-1.5 py-0.2 rounded bg-soc-primary text-white font-bold">INSPECTING</span>}
                    </div>
                    <div className={`text-[11px] font-bold mt-0.5 ${
                      isFlagged ? 'text-rose-400' : isCompleted ? 'text-emerald-400' : 'text-soc-muted'
                    }`}>
                      {stage.checklist}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  {isFlagged ? (
                    <span className="px-2 py-0.5 text-[10px] font-bold rounded bg-rose-500/20 text-rose-400 border border-rose-500/40">
                      FLAGGED
                    </span>
                  ) : isCompleted ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : (
                    <span className="text-[10px] text-soc-dim">Pending</span>
                  )}
                  <Eye className="w-3.5 h-3.5 text-soc-muted hover:text-soc-primary" />
                </div>
              </div>
            );
          })}
        </div>

        {/* EVIDENCE INSPECTOR PANE (5/12) */}
        <div className="lg:col-span-5 bg-soc-bg border border-soc-border rounded-xl p-3.5 flex flex-col justify-between max-h-[460px]">
          <div>
            <div className="flex items-center justify-between border-b border-soc-border pb-2.5 mb-3">
              <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
                <Terminal className="w-4 h-4 text-soc-primary" />
                <span>Stage Evidence Inspector</span>
              </h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-surface text-soc-primary border border-soc-primary/30">
                {activeStageEvidence ? activeStageEvidence.name : 'Select a Stage'}
              </span>
            </div>

            {activeStageEvidence ? (
              <div className="space-y-3 font-mono text-xs overflow-y-auto max-h-[360px] pr-1">
                <div className="p-2.5 bg-soc-surface rounded-lg border border-soc-border">
                  <div className="text-[10px] text-soc-muted font-bold uppercase mb-1">Checklist Output</div>
                  <div className="text-xs font-bold text-emerald-400">{activeStageEvidence.checklist}</div>
                </div>

                <div>
                  <div className="text-[10px] text-soc-muted font-bold uppercase mb-1 flex items-center gap-1">
                    <FileText className="w-3 h-3 text-soc-primary" />
                    <span>Raw Stage Evidence Payload (JSON)</span>
                  </div>
                  <pre className="p-3 bg-slate-950 border border-soc-border rounded-lg text-emerald-400 text-[11px] overflow-x-auto font-mono leading-relaxed">
                    {JSON.stringify(activeStageEvidence.evidence, null, 2)}
                  </pre>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-soc-dim space-y-2">
                <Eye className="w-8 h-8 mx-auto text-soc-muted/50" />
                <p className="text-xs font-mono">
                  Click any stage on the left to inspect its exact evidence payload, extracted vectors, model probabilities, and cryptographic signatures.
                </p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-soc-border flex items-center justify-between text-[11px] text-soc-muted font-mono">
            <span>Overall Verdict: <strong className={verdictAction === 'BLOCK' ? 'text-rose-400 font-bold' : 'text-emerald-400 font-bold'}>{verdictAction}</strong></span>
            <span>Composite Risk: <strong className="text-soc-text">{compositeRiskScore}/100</strong></span>
          </div>
        </div>

      </div>

      {/* TRUST FABRIC & INVESTIGATION CONFIDENCE PANELS */}
      <div className="mt-4 space-y-4">
        <DecisionTrustReport trustData={evaluation?.trust_metrics} action={verdictAction} />
        <InvestigationTrustPanel trustData={evaluation?.trust_metrics} action={verdictAction} />
        <DecisionStabilityInspector trustData={evaluation?.trust_metrics} action={verdictAction} />
        <TrustFabricLedgerBadge ledgerRecord={evaluation?.trust_metrics?.ledger_record} />
      </div>

    </div>
  );
}
