import React from 'react';
import { Activity, ShieldCheck, Wifi } from 'lucide-react';

export default function StatusBar() {
  return (
    <div className="h-6 bg-soc-surface border-t border-soc-border px-4 flex items-center justify-between text-[10px] font-mono text-soc-dim select-none z-30">
      <div className="flex items-center gap-4">
        <span className="flex items-center gap-1 text-emerald-400">
          <Wifi className="w-3 h-3" />
          <span>WebSocket Stream Connected (port 8001)</span>
        </span>
        <span>SLA Target: &lt;50ms</span>
      </div>

      <div className="flex items-center gap-4">
        <span>FPR Budget: 0.48% / 0.50%</span>
        <span>Graph Engine: NetworkX / Neo4j Aura</span>
        <span className="text-soc-muted">Fusion Risk OS Enterprise v2.6</span>
      </div>
    </div>
  );
}
