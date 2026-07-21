import React from 'react';
import { Share2 } from 'lucide-react';
import Neo4jGraphStudio from '../components/graph/Neo4jGraphStudio';

export default function GraphPage() {
  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none h-[calc(100vh-100px)]">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Share2 className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Neo4j Graph Studio (Link Analysis)
            </h1>
            <span className="text-xs text-soc-muted">Heterogeneous network topology, PageRank centrality, & mule ring detection</span>
          </div>
        </div>
      </div>

      <div className="flex-1 bg-soc-surface border border-soc-border rounded-xl overflow-hidden">
        <Neo4jGraphStudio />
      </div>
    </div>
  );
}
