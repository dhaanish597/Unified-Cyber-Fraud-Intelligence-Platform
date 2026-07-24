import React, { useState, useEffect } from 'react';
import { User, DollarSign, Clock, Smartphone, Globe, Layers, GitCommit, Sparkles, AlertTriangle, CheckCircle2, RefreshCw, Gauge } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');

export default function DigitalTwinBaseline({ userId = 'usr_abc' }) {
  const [twinData, setTwinData] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [activeTab, setActiveTab] = useState('diffs'); // diffs | identity | devices | graph | predictions | timeline
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDigitalTwinData();
  }, [userId]);

  const fetchDigitalTwinData = async () => {
    setLoading(true);
    try {
      const [twinRes, compRes] = await Promise.all([
        fetch(`${API_BASE}/digital_twin/${userId}`).then(r => r.json()),
        fetch(`${API_BASE}/digital_twin/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: userId, transaction: { amount: 750000.0, nameDest: "ACC_MULE_NEW", cyber_compromise_in_window: true } })
        }).then(r => r.json())
      ]);

      setTwinData(twinRes);
      setComparison(compRes);
    } catch (e) {
      console.error("Digital Twin fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !twinData) {
    return (
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs text-soc-dim flex items-center gap-2">
        <RefreshCw className="w-4 h-4 animate-spin text-soc-primary" />
        <span>Loading Customer Digital Twin Intelligence for {userId}...</span>
      </div>
    );
  }

  const { identity, devices, locations, transactions_profile, behavior, graph, risk, predictions, timeline } = twinData;
  const devIndex = comparison?.overall_deviation_index || 88.5;
  const isHighDeviation = devIndex > 70.0;

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-xl select-none font-mono text-xs">
      
      {/* 1. HEADER & TWIN SUMMARY STRIP */}
      <div className="flex flex-wrap items-center justify-between border-b border-soc-border pb-3 mb-3 gap-3">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-soc-primary/10 border border-soc-primary/30 rounded-lg">
            <User className="w-5 h-5 text-soc-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
                Digital Twin Customer Intelligence — {identity.full_name} ({userId})
              </h3>
              <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                LIVE TWIN ACTIVE
              </span>
            </div>
            <span className="text-[10px] text-soc-muted">
              KYC: {identity.kyc_status} • Segment: {identity.occupation} • Primary Acc: {identity.primary_account}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs">
          <div className="flex items-center gap-2 bg-soc-panel border border-soc-border px-3 py-1.5 rounded-lg">
            <Gauge className="w-4 h-4 text-soc-primary" />
            <span className="text-[10px] text-soc-dim uppercase">Overall Deviation Index:</span>
            <span className={`font-black ${isHighDeviation ? 'text-rose-400' : 'text-emerald-400'}`}>
              {devIndex}% ({comparison?.verdict || 'CRITICAL_DEVIATION'})
            </span>
          </div>

          <button 
            onClick={fetchDigitalTwinData}
            className="p-1.5 bg-soc-bg border border-soc-border hover:border-soc-primary rounded-lg text-soc-text transition-colors"
            title="Refresh Digital Twin State"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* 2. SUB-NAVIGATION TABS */}
      <div className="flex items-center gap-1 border-b border-soc-border pb-2 mb-3 overflow-x-auto text-[11px]">
        {[
          { id: 'diffs', label: 'Expected vs Observed Diffs', icon: AlertTriangle, badge: `${devIndex}%` },
          { id: 'identity', label: 'Identity & Accounts', icon: User },
          { id: 'devices', label: 'Devices & Locations', icon: Smartphone },
          { id: 'graph', label: 'Graph & Mule Ring', icon: Layers },
          { id: 'predictions', label: 'Predictive Intelligence', icon: Sparkles },
          { id: 'timeline', label: 'Audit Timeline', icon: GitCommit, badge: `${timeline?.length || 0}` }
        ].map(t => {
          const Icon = t.icon;
          const isActive = activeTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg font-bold flex items-center gap-2 transition-all ${
                isActive 
                  ? 'bg-soc-primary text-white shadow' 
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
      
      {/* TAB 1: EXPECTED VS OBSERVED DEVIATION DIFFS */}
      {activeTab === 'diffs' && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(comparison?.comparison_diffs || {}).map(([key, val]) => {
              const isAlert = val.includes('UNTRUSTED') || val.includes('IMPOSSIBLE') || val.includes('ANOMALOUS') || val.includes('UNSEEN') || val.includes('BURST') || val.includes('OFF-HOURS');
              return (
                <div key={key} className={`p-3 rounded-lg border space-y-1 ${isAlert ? 'bg-rose-500/10 border-rose-500/30' : 'bg-soc-panel border-soc-border'}`}>
                  <span className="text-[10px] text-soc-dim uppercase font-semibold flex items-center justify-between">
                    <span>{key.replace('_', ' ')}</span>
                    {isAlert ? <AlertTriangle className="w-3 h-3 text-rose-400" /> : <CheckCircle2 className="w-3 h-3 text-emerald-400" />}
                  </span>
                  <div className={`font-bold ${isAlert ? 'text-rose-300' : 'text-soc-text'}`}>{val}</div>
                </div>
              );
            })}
          </div>

          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg">
            <span className="text-[10px] text-soc-dim uppercase font-bold tracking-wider mb-2 block">
              Sub-Vector Deviation Scores Breakdown
            </span>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
              {Object.entries(comparison?.deviations_breakdown || {}).map(([vec, score]) => (
                <div key={vec} className="space-y-1">
                  <div className="flex justify-between text-[10px] text-soc-muted">
                    <span className="truncate">{vec.replace('_deviation', '')}</span>
                    <span className="font-bold text-soc-text">{score}%</span>
                  </div>
                  <div className="w-full bg-soc-bg h-1.5 rounded-full overflow-hidden border border-soc-border">
                    <div 
                      className={`h-full rounded-full ${score > 70 ? 'bg-rose-500' : (score > 40 ? 'bg-amber-400' : 'bg-emerald-400')}`}
                      style={{ width: `${Math.min(100, score)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: IDENTITY & ACCOUNTS */}
      {activeTab === 'identity' && (
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Annual Income</span>
            <div className="text-soc-text font-bold text-sm">INR {identity.annual_salary?.toLocaleString('en-IN')}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Assigned Relationship Mgr</span>
            <div className="text-soc-text font-bold">{identity.relationship_manager}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Account Portfolios</span>
            <div className="text-soc-primary font-bold">{identity.account_types.join(', ')}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Identity Trust Score</span>
            <div className="text-emerald-400 font-bold text-sm">{identity.trust_level} / 100.0</div>
          </div>
        </div>
      )}

      {/* TAB 3: DEVICES & LOCATIONS */}
      {activeTab === 'devices' && (
        <div className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-2">
              <span className="text-[10px] text-soc-dim uppercase font-bold flex items-center gap-1">
                <Smartphone className="w-3.5 h-3.5 text-soc-primary" />
                <span>Trusted Device Profiles ({devices.trusted_devices?.length})</span>
              </span>
              {devices.trusted_devices?.map(d => (
                <div key={d.device_id} className="p-2 bg-soc-bg border border-soc-border rounded text-[11px] flex justify-between items-center">
                  <div>
                    <span className="font-bold text-soc-text">{d.name} ({d.device_id})</span>
                    <div className="text-[10px] text-soc-muted">{d.os} • {d.browser} • Fingerprint: {d.fingerprint}</div>
                  </div>
                  <span className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded">
                    Trust: {d.trust_score * 100}%
                  </span>
                </div>
              ))}
            </div>

            <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-2">
              <span className="text-[10px] text-soc-dim uppercase font-bold flex items-center gap-1">
                <Globe className="w-3.5 h-3.5 text-emerald-400" />
                <span>Geolocation Baseline & Velocity</span>
              </span>
              <div className="p-2 bg-soc-bg border border-soc-border rounded space-y-1">
                <div className="text-soc-text font-bold">Home: {locations.home_location?.city}, {locations.home_location?.country} ({locations.home_location?.lat}, {locations.home_location?.lon})</div>
                <div className="text-[10px] text-soc-muted">Geo-Velocity Baseline: {locations.geo_velocity_kmh} km/h • VPN Usage Count: {locations.vpn_usage_count}</div>
              </div>
              {locations.impossible_travel_events?.length > 0 && (
                <div className="p-2 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded text-[10px]">
                  <strong>IMPOSSIBLE TRAVEL EVENT DETECTED:</strong> {locations.impossible_travel_events[0].location} ({locations.impossible_travel_events[0].km_from_home} km from home)
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 4: GRAPH PROFILE */}
      {activeTab === 'graph' && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Graph Neighborhood Size</span>
            <div className="text-soc-text font-bold text-sm">{graph.neighborhood_size} Entity Nodes</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Distance to Known Mule Ring</span>
            <div className={`font-bold text-sm ${graph.distance_to_known_mule_ring <= 1 ? 'text-rose-400 animate-pulse' : 'text-emerald-400'}`}>
              {graph.distance_to_known_mule_ring <= 1 ? '1 HOP (DIRECT RISK)' : `${graph.distance_to_known_mule_ring} HOPS (SAFE)`}
            </div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">PageRank Centrality</span>
            <div className="text-soc-primary font-bold text-sm">{graph.pagerank_score}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase">Community Cluster</span>
            <div className="text-soc-text font-bold">{graph.community_id}</div>
          </div>
        </div>
      )}

      {/* TAB 5: PREDICTIVE INTELLIGENCE */}
      {activeTab === 'predictions' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase font-bold flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-soc-primary" />
              <span>Predicted Next Login Time</span>
            </span>
            <div className="text-soc-text font-bold">{predictions.predicted_next_login}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase font-bold flex items-center gap-1">
              <DollarSign className="w-3.5 h-3.5 text-amber-400" />
              <span>Predicted Transaction Range</span>
            </span>
            <div className="text-soc-text font-bold">{predictions.predicted_next_amount_range}</div>
          </div>
          <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
            <span className="text-[10px] text-soc-dim uppercase font-bold flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              <span>Likely Merchant Target</span>
            </span>
            <div className="text-soc-text font-bold">{predictions.likely_merchant}</div>
          </div>
        </div>
      )}

      {/* TAB 6: AUDIT TIMELINE */}
      {activeTab === 'timeline' && (
        <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
          {timeline?.map((evt, idx) => (
            <div key={idx} className="p-2 bg-soc-panel border border-soc-border rounded text-[11px] flex items-start gap-3">
              <div className="p-1 bg-soc-bg border border-soc-border rounded text-[10px] font-mono text-soc-dim whitespace-nowrap">
                {evt.timestamp}
              </div>
              <div className="flex-1">
                <span className="font-bold text-soc-text uppercase text-[10px] block">{evt.title} ({evt.event_type})</span>
                <span className="text-soc-muted">{evt.description}</span>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

