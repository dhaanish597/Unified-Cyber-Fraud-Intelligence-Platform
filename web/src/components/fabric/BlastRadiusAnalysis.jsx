import React from 'react';
import { ShieldAlert, Users, DollarSign, Share2, Layers, AlertTriangle } from 'lucide-react';

export default function BlastRadiusAnalysis({ activeTxn }) {
  const blastMetrics = [
    { label: 'Potentially Impacted Customers', value: '17 Customers', color: 'text-rose-400', icon: Users },
    { label: 'Total Potential Exposure', value: 'INR 24,500,000.00', color: 'text-amber-400', icon: DollarSign },
    { label: 'Linked High-Risk Accounts', value: '8 Mule Accounts', color: 'text-soc-primary', icon: Share2 },
    { label: 'Contained Mule Clusters', value: 'Cluster Alpha (6 Nodes)', color: 'text-purple-400', icon: Layers }
  ];

  const exposureChain = [
    { label: '1. Primary Target', entity: activeTxn?.user_id || 'usr_abc', status: 'Compromised' },
    { label: '2. Shared Device ID', entity: activeTxn?.device_id || 'dev_9999', status: 'Flagged (2 Users)' },
    { label: '3. Shared Proxy IP', entity: activeTxn?.ip || '185.15.2.22', status: 'RU Proxy (5 Accounts)' },
    { label: '4. Linked Beneficiaries', entity: activeTxn?.nameDest || 'ACC_MULE_NEW', status: 'Mule Ring Target' },
    { label: '5. Connected Mule Cluster', entity: activeTxn?.dest_mule_cluster_id || 'cluster_alpha', status: 'Isolated' }
  ];

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-amber-400" />
          <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
            Blast Radius Analysis — Secondary Incident Exposure & Containment
          </h3>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30">
          CONTAINMENT MODELLING
        </span>
      </div>

      {/* Exposure Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        {blastMetrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="p-3 bg-soc-panel border border-soc-border rounded-lg flex items-center justify-between">
              <div>
                <span className="text-[10px] text-soc-dim uppercase font-semibold">{m.label}</span>
                <div className={`text-base font-bold mt-0.5 ${m.color}`}>{m.value}</div>
              </div>
              <Icon className={`w-5 h-5 ${m.color}`} />
            </div>
          );
        })}
      </div>

      {/* Linked Entity Exposure Chain */}
      <div className="space-y-2">
        <span className="text-[10px] text-soc-dim uppercase font-semibold block">Incident Propagation Chain</span>
        <div className="grid grid-cols-1 sm:grid-cols-5 gap-2">
          {exposureChain.map((item, idx) => (
            <div key={idx} className="p-2.5 bg-soc-panel border border-soc-border rounded-lg">
              <span className="text-[10px] text-soc-dim block">{item.label}</span>
              <span className="font-bold text-soc-text truncate block mt-0.5">{item.entity}</span>
              <span className="text-[10px] text-amber-400 font-semibold block mt-1">{item.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
