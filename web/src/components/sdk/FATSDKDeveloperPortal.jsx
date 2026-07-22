import React, { useState, useEffect, useRef } from 'react';
import {
  Code2, Terminal, Zap, Globe, Shield, Radio, Play, Download,
  RefreshCw, CheckCircle2, AlertTriangle, Smartphone, Cpu, 
  Network, Activity, BookOpen, Settings, ChevronDown, ChevronRight,
  Copy, ExternalLink, Server, Lock, Layers
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

// ─── Syntax-highlight JSON for the API Explorer ───
function JsonBlock({ data }) {
  const str = JSON.stringify(data, null, 2);
  return (
    <pre className="bg-soc-bg border border-soc-border rounded-lg p-3 text-[11px] font-mono text-emerald-300 overflow-x-auto max-h-60">
      {str}
    </pre>
  );
}

// ─── Code snippet block with copy ───
function CodeSnippet({ code, lang = 'kotlin' }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };
  return (
    <div className="relative">
      <pre className="bg-[#0d1117] border border-soc-border rounded-lg p-3 text-[11px] font-mono text-cyan-200 overflow-x-auto leading-relaxed">
        {code}
      </pre>
      <button
        onClick={copy}
        className="absolute top-2 right-2 px-2 py-1 text-[10px] bg-soc-panel border border-soc-border rounded text-soc-muted hover:text-white transition-colors flex items-center gap-1"
      >
        <Copy className="w-3 h-3" />
        {copied ? 'Copied!' : 'Copy'}
      </button>
    </div>
  );
}

const KOTLIN_INIT = `// Fusion Adaptive Trust SDK — Kotlin Integration
import com.fusion.sdk.Fusion
import com.fusion.sdk.FusionConfig

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        Fusion.initialize(
            context = this,
            config = FusionConfig.Builder()
                .apiKey("fat_live_xxxxxxxxxxxxxxxx")
                .applicationId("com.yourbank.mobile")
                .tenantId("TENANT_YOURBANK_001")
                .environment(FusionConfig.Environment.PRODUCTION)
                .sdkVersion("FAT-SDK v2.4.1")
                .build()
        )
        
        Fusion.startSession(userId = "usr_authenticated_id")
    }
}`;

const KOTLIN_EVENT = `// Reporting a Transfer Event
Fusion.reportEvent(
    FusionEvent.Builder()
        .type(EventType.TRANSFER_INITIATED)
        .amount(75000.0)
        .currency("INR")
        .beneficiaryId("BENEF_7821")
        .build()
)`;

const KOTLIN_DECISION = `// Request Trust Decision before transfer
val decision = Fusion.requestDecision(
    DecisionRequest.Builder()
        .eventType(EventType.TRANSFER_INITIATED)
        .amount(75000.0)
        .build()
).await()

when (decision.action) {
    DecisionAction.ALLOW -> proceedWithTransfer()
    DecisionAction.REQUIRE_BIOMETRIC -> requestBiometric()
    DecisionAction.REQUIRE_OTP -> sendOTP()
    DecisionAction.BLOCK_TRANSACTION -> showBlockedScreen()
    DecisionAction.TERMINATE_SESSION -> terminateAndLogout()
}`;

const KOTLIN_EVENTS_LIST = [
  'APPLICATION_STARTED', 'USER_LOGIN', 'USER_LOGOUT', 'SESSION_STARTED', 'SESSION_ENDED',
  'BENEFICIARY_ADDED', 'BENEFICIARY_REMOVED', 'TRANSFER_INITIATED', 'TRANSFER_CONFIRMED',
  'QR_SCAN', 'BILL_PAYMENT', 'PROFILE_UPDATED', 'LOCATION_CHANGED', 'NETWORK_CHANGED',
  'VPN_ENABLED', 'OVERLAY_DETECTED', 'RUNTIME_THREAT', 'DEVICE_CHANGED', 'POLICY_UPDATED'
];

const API_ENDPOINTS = [
  { method: 'POST', path: '/sdk/session/start', desc: 'Initialize trusted SDK session', category: 'Session' },
  { method: 'POST', path: '/sdk/device', desc: 'Register device intelligence profile', category: 'Device' },
  { method: 'POST', path: '/sdk/network', desc: 'Register network trust telemetry', category: 'Network' },
  { method: 'POST', path: '/sdk/event', desc: 'Ingest SDK security event', category: 'Events' },
  { method: 'POST', path: '/sdk/request-decision', desc: 'Request adaptive trust decision', category: 'Decision' },
  { method: 'GET', path: '/sdk/policies', desc: 'Fetch active adaptive security policies', category: 'Policy' },
  { method: 'GET', path: '/sdk/passport', desc: 'Retrieve Trust Passport for session', category: 'Trust' },
  { method: 'GET', path: '/sdk/health', desc: 'SDK observability & health metrics', category: 'Health' },
  { method: 'GET', path: '/sdk/apps', desc: 'Connected application registry', category: 'Apps' },
  { method: 'GET', path: '/sdk/events', desc: 'Live event stream (last 20 events)', category: 'Events' },
];

export default function FATSDKDeveloperPortal() {
  const [activeTab, setActiveTab] = useState('overview');
  const [health, setHealth] = useState(null);
  const [apps, setApps] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [liveEvents, setLiveEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  // API Explorer state
  const [explorerEndpoint, setExplorerEndpoint] = useState(API_ENDPOINTS[0]);
  const [explorerPayload, setExplorerPayload] = useState('{\n  "app_id": "com.fusionbank.mobileapp",\n  "tenant_id": "TENANT_FUSB_001",\n  "sdk_version": "FAT-SDK v2.4.1",\n  "user_id": "usr_demo",\n  "device_id": "DEV_12345",\n  "environment": "PRODUCTION"\n}');
  const [explorerResult, setExplorerResult] = useState(null);
  const [explorerLoading, setExplorerLoading] = useState(false);

  // Simulator state
  const [simConfig, setSimConfig] = useState({ root: false, vpn: false, amount: 75000, frida: false });
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);

  const liveRef = useRef(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchLive, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [hRes, aRes, pRes, eRes] = await Promise.all([
        fetch(`${API_BASE}/sdk/health`),
        fetch(`${API_BASE}/sdk/apps`),
        fetch(`${API_BASE}/sdk/policies`),
        fetch(`${API_BASE}/sdk/events`),
      ]);
      setHealth(await hRes.json());
      setApps(await aRes.json());
      const pData = await pRes.json();
      setPolicies(pData.policies || []);
      setLiveEvents(await eRes.json());
    } catch (e) {
      console.error('SDK portal fetch error:', e);
    } finally {
      setLoading(false);
    }
  };

  const fetchLive = async () => {
    try {
      const res = await fetch(`${API_BASE}/sdk/events`);
      setLiveEvents(await res.json());
    } catch (_) {}
  };

  const runExplorer = async () => {
    setExplorerLoading(true);
    try {
      const opts = { method: explorerEndpoint.method, headers: { 'Content-Type': 'application/json' } };
      if (explorerEndpoint.method === 'POST') opts.body = explorerPayload;
      const res = await fetch(`${API_BASE}${explorerEndpoint.path}`, opts);
      setExplorerResult(await res.json());
    } catch (e) {
      setExplorerResult({ error: e.message });
    } finally {
      setExplorerLoading(false);
    }
  };

  const runSimulator = async () => {
    setSimLoading(true);
    // Fire events to populate live stream
    await fetch(`${API_BASE}/sdk/event`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: 'SDK_SESS_SIM', event_type: 'TRANSFER_INITIATED', amount: simConfig.amount, composite_trust: 80.0 })
    });
    const res = await fetch(`${API_BASE}/sdk/request-decision`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: 'SDK_SESS_SIM',
        event_type: 'TRANSFER_INITIATED',
        amount: simConfig.amount,
        vpn_detected: simConfig.vpn,
        root_detected: simConfig.root,
        runtime_trust: simConfig.frida ? 20.0 : 94.0,
        composite_trust: simConfig.root ? 30.0 : 82.0
      })
    });
    setSimResult(await res.json());
    setSimLoading(false);
    fetchLive();
  };

  if (loading) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
        <span>Loading Fusion Adaptive Trust SDK Developer Platform...</span>
      </div>
    );
  }

  const TABS = [
    { id: 'overview', label: 'Overview', icon: Globe },
    { id: 'quickstart', label: 'Quick Start', icon: Zap },
    { id: 'sdk', label: 'Android SDK', icon: Smartphone },
    { id: 'explorer', label: 'API Explorer', icon: Terminal },
    { id: 'simulator', label: 'SDK Showcase', icon: Play },
    { id: 'policy', label: 'Policy Engine', icon: Settings },
    { id: 'monitor', label: 'Integration Monitor', icon: Activity },
    { id: 'apps', label: 'Connected Apps', icon: Server },
  ];

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs text-soc-text space-y-4">

      {/* HEADER */}
      <div className="p-4 bg-gradient-to-r from-cyan-950/60 to-soc-panel border border-cyan-500/20 rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-cyan-500/20 border border-cyan-500/40 rounded-xl">
            <Code2 className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                FUSION ADAPTIVE TRUST SDK — DEVELOPER PLATFORM
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                FAT-SDK v2.4.1
              </span>
            </div>
            <h2 className="text-base font-black text-soc-text tracking-wide mt-1">
              ENTERPRISE BANKING SECURITY SDK — STRIPE-CLASS DEVELOPER EXPERIENCE
            </h2>
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs">
          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">SDK Health</span>
            <span className="font-bold text-emerald-400">{health?.sdk_health}</span>
          </div>
          <div className="flex flex-col border-r border-soc-border pr-6">
            <span className="text-[10px] text-soc-dim uppercase">Connected Apps</span>
            <span className="font-bold text-cyan-400">{health?.connected_apps}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[10px] text-soc-dim uppercase">Avg Latency</span>
            <span className="font-bold text-amber-400">{health?.average_latency_ms} ms</span>
          </div>
        </div>
      </div>

      {/* TABS */}
      <div className="flex items-center gap-1 border-b border-soc-border pb-2 overflow-x-auto text-[11px]">
        {TABS.map(t => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-2 transition-all ${
                isActive ? 'bg-cyan-600 text-white shadow' : 'bg-soc-panel border border-soc-border text-soc-muted hover:text-soc-text'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{t.label}</span>
            </button>
          );
        })}
      </div>

      {/* ── OVERVIEW ── */}
      {activeTab === 'overview' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {[
              { label: 'Active Sessions', value: health?.active_sessions, color: 'text-cyan-400', sub: 'Concurrent SDK sessions' },
              { label: 'Events Processed', value: health?.total_events_processed, color: 'text-emerald-400', sub: 'Total ingested events' },
              { label: 'Queued Events', value: health?.queued_events, color: 'text-amber-400', sub: 'Pending delivery' },
              { label: 'Trust Sync Status', value: health?.trust_sync_status, color: 'text-purple-400', sub: 'Passport synchronization' },
            ].map((m, i) => (
              <div key={i} className="p-3 bg-soc-panel border border-soc-border rounded-lg">
                <span className="text-[10px] text-soc-dim uppercase">{m.label}</span>
                <div className={`text-lg font-black ${m.color}`}>{m.value}</div>
                <span className="text-[10px] text-soc-muted">{m.sub}</span>
              </div>
            ))}
          </div>

          {/* Architecture diagram */}
          <div className="p-4 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-3">SDK Architecture Flow</span>
            <div className="flex flex-wrap items-center gap-2 text-[11px] font-bold">
              {['Bank Mobile App', 'FAT-SDK', 'Fusion Event Stream', 'Fusion Risk OS', 'Trust Passport', 'Decision API', 'Bank Backend', 'Core Banking'].map((step, i, arr) => (
                <React.Fragment key={step}>
                  <span className="px-2.5 py-1.5 bg-soc-bg border border-cyan-500/30 text-cyan-300 rounded-lg">{step}</span>
                  {i < arr.length - 1 && <ChevronRight className="w-3 h-3 text-soc-dim" />}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Privacy guarantees */}
          <div className="p-4 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-2">Privacy Guarantees — What the SDK NEVER Collects</span>
            <div className="flex flex-wrap gap-2">
              {['Passwords', 'OTPs', 'Account Numbers', 'Card Numbers', 'Screen Content', 'User Input Text', 'PAN / Aadhaar'].map(item => (
                <span key={item} className="px-2 py-1 text-[10px] bg-rose-500/10 text-rose-300 border border-rose-500/30 rounded font-bold flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3" /> NEVER: {item}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── QUICK START ── */}
      {activeTab === 'quickstart' && (
        <div className="space-y-4">
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-1">Step 1: Add Dependency (build.gradle)</span>
            <CodeSnippet lang="gradle" code={`dependencies {
    implementation("com.fusionrisk:fat-sdk-android:2.4.1")
}`} />
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-1">Step 2: Initialize SDK in Application.kt</span>
            <CodeSnippet lang="kotlin" code={KOTLIN_INIT} />
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-1">Step 3: Report Events</span>
            <CodeSnippet lang="kotlin" code={KOTLIN_EVENT} />
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-1">Step 4: Request Trust Decision Before Transfer</span>
            <CodeSnippet lang="kotlin" code={KOTLIN_DECISION} />
          </div>
        </div>
      )}

      {/* ── ANDROID SDK ── */}
      {activeTab === 'sdk' && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { icon: Smartphone, title: 'Module 1: Initialization API', items: ['Fusion.initialize()', 'Fusion.configure()', 'Fusion.startSession()', 'Fusion.endSession()', 'Fusion.reportEvent()', 'Fusion.requestDecision()', 'Fusion.shutdown()'] },
              { icon: Shield, title: 'Module 2: Device Intelligence', items: ['Device Model & Manufacturer', 'Android Version & Security Patch', 'Root Detection (Magisk/SuperSU)', 'Emulator Detection', 'App Signature Verification', 'Play Integrity API Status'] },
              { icon: Cpu, title: 'Module 3: Runtime Integrity Engine', items: ['Debugger Attachment Detection', 'Frida/Xposed Hook Detection', 'Overlay Detection', 'App Signature Change Monitor', 'Runtime Tampering Score'] },
              { icon: Network, title: 'Module 6: Network Intelligence', items: ['VPN Detection', 'Proxy Detection', 'Carrier & ASN Lookup', 'Network Type (WiFi/5G/4G)', 'Roaming Status', 'Network Change Events'] },
            ].map((mod, i) => {
              const Icon = mod.icon;
              return (
                <div key={i} className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
                  <div className="flex items-center gap-2 font-bold text-soc-text text-[11px] border-b border-soc-border pb-2 mb-2">
                    <Icon className="w-4 h-4 text-cyan-400" />
                    <span>{mod.title}</span>
                  </div>
                  <ul className="space-y-0.5">
                    {mod.items.map(item => (
                      <li key={item} className="text-[10px] text-soc-muted flex items-center gap-1.5">
                        <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold block mb-2">Module 7: Supported Event Types ({KOTLIN_EVENTS_LIST.length} Events)</span>
            <div className="flex flex-wrap gap-1.5">
              {KOTLIN_EVENTS_LIST.map(evt => (
                <span key={evt} className="px-2 py-1 text-[10px] bg-soc-bg border border-soc-border text-cyan-300 rounded font-mono">{evt}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── API EXPLORER ── */}
      {activeTab === 'explorer' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-3">
            <span className="text-[10px] text-soc-dim uppercase font-bold block">Select Endpoint</span>
            <div className="space-y-1 max-h-60 overflow-y-auto">
              {API_ENDPOINTS.map((ep, i) => (
                <button
                  key={i}
                  onClick={() => setExplorerEndpoint(ep)}
                  className={`w-full p-2 flex items-center gap-3 rounded-lg text-left transition-colors ${
                    explorerEndpoint.path === ep.path ? 'bg-cyan-600/20 border border-cyan-500/40' : 'bg-soc-panel border border-soc-border hover:border-soc-dim'
                  }`}
                >
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${ep.method === 'POST' ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'}`}>
                    {ep.method}
                  </span>
                  <span className="text-[11px] font-mono text-soc-text">{ep.path}</span>
                </button>
              ))}
            </div>

            {explorerEndpoint.method === 'POST' && (
              <div>
                <span className="text-[10px] text-soc-dim uppercase font-bold block mb-1">Request Payload (JSON)</span>
                <textarea
                  value={explorerPayload}
                  onChange={e => setExplorerPayload(e.target.value)}
                  className="w-full h-32 bg-soc-bg border border-soc-border rounded-lg p-2 text-[11px] font-mono text-cyan-200 outline-none resize-none"
                />
              </div>
            )}

            <button
              onClick={runExplorer}
              disabled={explorerLoading}
              className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold flex items-center justify-center gap-2 transition-colors"
            >
              {explorerLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
              <span>SEND REQUEST</span>
            </button>
          </div>

          <div className="space-y-2">
            <span className="text-[10px] text-soc-dim uppercase font-bold block">Response</span>
            {explorerResult ? <JsonBlock data={explorerResult} /> : (
              <div className="bg-soc-bg border border-soc-border rounded-lg p-4 text-soc-dim text-[11px] flex items-center justify-center">
                Send a request to see the response
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── SDK SHOWCASE SIMULATOR ── */}
      {activeTab === 'simulator' && (
        <div className="space-y-4">
          <div className="p-4 bg-soc-panel border border-soc-border rounded-lg space-y-4">
            <div className="flex items-center gap-2 text-cyan-400 font-bold border-b border-soc-border pb-2">
              <Play className="w-4 h-4" />
              <span>SDK Showcase — Device & Trust Scenario Simulator</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="text-[10px] text-soc-dim uppercase block mb-1">Transfer Amount (INR)</label>
                <input
                  type="number"
                  value={simConfig.amount}
                  onChange={e => setSimConfig(s => ({ ...s, amount: Number(e.target.value) }))}
                  className="w-full bg-soc-bg border border-soc-border rounded p-2 text-soc-text text-xs outline-none"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-[10px] text-soc-dim uppercase">Device Conditions</label>
                {[
                  { key: 'root', label: 'Root Detected (Magisk)' },
                  { key: 'frida', label: 'Frida Instrumentation' },
                  { key: 'vpn', label: 'VPN Enabled' },
                ].map(opt => (
                  <label key={opt.key} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={simConfig[opt.key]}
                      onChange={e => setSimConfig(s => ({ ...s, [opt.key]: e.target.checked }))}
                      className="accent-cyan-400"
                    />
                    <span className="text-[11px] text-soc-text">{opt.label}</span>
                  </label>
                ))}
              </div>
              <div className="flex items-end">
                <button
                  onClick={runSimulator}
                  disabled={simLoading}
                  className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded font-bold flex items-center justify-center gap-2"
                >
                  {simLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
                  <span>RUN SHOWCASE</span>
                </button>
              </div>
            </div>

            {simResult && (
              <div className="p-3 bg-soc-bg border border-soc-border rounded-lg space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-cyan-400">Decision #{simResult.decision_id}</span>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded border ${
                    simResult.decision === 'ALLOW'
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                  }`}>
                    {simResult.decision}
                  </span>
                </div>
                <div className="text-[11px] space-y-1">
                  <div className="flex justify-between"><span className="text-soc-dim">Confidence:</span><span className="font-bold text-soc-text">{simResult.confidence}%</span></div>
                  <div className="flex justify-between"><span className="text-soc-dim">Latency:</span><span className="font-bold text-amber-400">{simResult.decision_latency_ms} ms</span></div>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {simResult.reason_codes?.map(rc => (
                      <span key={rc} className="px-1.5 py-0.5 text-[10px] bg-soc-panel border border-soc-border text-rose-300 rounded font-mono">{rc}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── POLICY ENGINE ── */}
      {activeTab === 'policy' && (
        <div className="space-y-2">
          <span className="text-[10px] text-soc-dim uppercase font-bold block">Active Adaptive Security Policies</span>
          {policies.map(pol => (
            <div key={pol.id} className="p-3 bg-soc-panel border border-soc-border rounded-lg flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 font-bold text-soc-text text-[11px]">
                  <Settings className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{pol.name}</span>
                  <span className="text-[9px] font-mono text-soc-dim">{pol.id} v{pol.version}</span>
                </div>
                <div className="text-[10px] text-soc-muted">Trigger: <code className="text-amber-300">{pol.trigger}</code></div>
                <div className="text-[10px] text-soc-muted">Action: <span className="text-rose-300 font-bold">{pol.action}</span></div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${pol.priority === 'CRITICAL' ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : pol.priority === 'HIGH' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' : 'bg-soc-bg text-soc-muted border-soc-border'}`}>
                  {pol.priority}
                </span>
                <span className={`w-2 h-2 rounded-full ${pol.active ? 'bg-emerald-400' : 'bg-soc-border'}`} />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── INTEGRATION MONITOR ── */}
      {activeTab === 'monitor' && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {[
              { label: 'Active Sessions', value: health?.active_sessions, color: 'text-cyan-400' },
              { label: 'Avg Latency', value: `${health?.average_latency_ms} ms`, color: 'text-amber-400' },
              { label: 'Dropped Events', value: health?.dropped_events, color: 'text-emerald-400' },
            ].map((m, i) => (
              <div key={i} className="p-3 bg-soc-panel border border-soc-border rounded-lg">
                <span className="text-[10px] text-soc-dim uppercase">{m.label}</span>
                <div className={`text-xl font-black ${m.color}`}>{m.value}</div>
              </div>
            ))}
          </div>
          <div className="space-y-2 max-h-72 overflow-y-auto" ref={liveRef}>
            <span className="text-[10px] text-soc-dim uppercase font-bold block">Live Event Stream</span>
            {liveEvents.length > 0 ? liveEvents.map(evt => (
              <div key={evt.event_id} className="p-2 bg-soc-panel border border-soc-border rounded text-[11px] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono text-[10px]">{evt.event_type}</span>
                  <span className="text-soc-dim">{evt.session_id}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-soc-dim text-[10px]">{evt.ingestion_latency_ms} ms</span>
                  <span className="text-[10px] text-soc-muted">{evt.timestamp}</span>
                </div>
              </div>
            )) : (
              <div className="p-4 bg-soc-panel border border-soc-border rounded text-soc-dim text-[11px] text-center">
                No events yet — run the SDK Showcase to generate events.
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── CONNECTED APPS ── */}
      {activeTab === 'apps' && (
        <div className="space-y-2">
          <span className="text-[10px] text-soc-dim uppercase font-bold block">Connected Application Registry</span>
          {apps.map(app => (
            <div key={app.app_id} className="p-3 bg-soc-panel border border-soc-border rounded-lg flex flex-wrap items-center justify-between gap-2">
              <div>
                <div className="font-bold text-soc-text text-[11px] flex items-center gap-2">
                  <Smartphone className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{app.name}</span>
                </div>
                <div className="text-[10px] text-soc-muted">{app.app_id} • {app.platform} • {app.sdk_version}</div>
                <div className="text-[10px] text-soc-dim">Last heartbeat: {app.last_heartbeat}</div>
              </div>
              <div className="flex items-center gap-4 text-[11px]">
                <div className="text-right">
                  <div className="text-soc-muted text-[10px]">Events Today</div>
                  <div className="font-bold text-cyan-400">{app.events_today.toLocaleString()}</div>
                </div>
                <div className="text-right">
                  <div className="text-soc-muted text-[10px]">Trust Sessions</div>
                  <div className="font-bold text-emerald-400">{app.trust_sessions}</div>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                  app.status === 'CONNECTED' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                }`}>
                  {app.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
