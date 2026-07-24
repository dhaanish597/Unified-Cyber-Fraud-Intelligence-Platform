import React, { useEffect, useState } from 'react';
import { Share2 } from 'lucide-react';
import Neo4jGraphStudio from '../components/graph/Neo4jGraphStudio';

const API_BASE = import.meta.env.VITE_API_BASE
  || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');

export default function GraphPage() {
  const [runtime, setRuntime] = useState({
    status: 'LOADING',
    backend: null,
    nodes: [],
    links: [],
  });

  useEffect(() => {
    fetch(`${API_BASE}/graph/topology?limit=500`)
      .then(async response => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
      })
      .then(setRuntime)
      .catch(error => setRuntime({
        status: 'FAILED',
        error_code: error.message,
        nodes: [],
        links: [],
      }));
  }, []);

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto h-[calc(100vh-100px)]">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Share2 className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Graph Intelligence Runtime
            </h1>
            <span className="text-xs text-soc-muted">
              {runtime.backend || 'No backend'} • {runtime.status} • {runtime.nodes.length} observed entities
            </span>
          </div>
        </div>
      </div>
      <div className="flex-1 bg-soc-surface border border-soc-border rounded-xl overflow-hidden">
        <Neo4jGraphStudio graphData={{ nodes: runtime.nodes, links: runtime.links }} />
      </div>
    </div>
  );
}
