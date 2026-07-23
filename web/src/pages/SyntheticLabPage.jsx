import React, { useState } from 'react';
import { FlaskConical, Play, Database, Loader2, FileCode, FileSpreadsheet } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function SyntheticLabPage() {
  const [numCustomers, setNumCustomers] = useState(100);
  const [numTransactions, setNumTransactions] = useState(500);
  const [seed, setSeed] = useState(42);
  const [isGenerating, setIsGenerating] = useState(false);
  const [universeData, setUniverseData] = useState(null);

  const handleGenerateUniverse = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch(`${API_BASE}/synthetic/universe/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          num_customers: parseInt(numCustomers),
          num_transactions: parseInt(numTransactions),
          seed: parseInt(seed)
        })
      });

      if (res.ok) {
        const data = await res.json();
        setUniverseData(data);
      }
    } catch (e) {
      console.error("Universe Generation Error:", e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadExport = (format) => {
    const url = `${API_BASE}/synthetic/universe/export/${format}?num_customers=${numCustomers}&num_txns=${numTransactions}&seed=${seed}`;
    window.open(url, '_blank');
  };

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none font-mono text-xs text-soc-text">
      
      {/* HEADER STRIP */}
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <FlaskConical className="w-6 h-6 text-soc-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
                Fusion Synthetic Banking Universe Generator (Phase 1)
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                FUSION NATIONAL BANK ENGINE
              </span>
            </div>
            <span className="text-xs text-soc-muted">
              Enterprise virtual digital bank simulator powering customers, multi-type accounts, devices, behavioral profiles & fraud injection
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => handleDownloadExport('csv')}
            className="px-3.5 py-2 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-bold flex items-center gap-1.5 transition-colors shadow"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            <span>Export CSV</span>
          </button>
          <button
            onClick={() => handleDownloadExport('json')}
            className="px-3.5 py-2 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded-lg font-bold flex items-center gap-1.5 transition-colors shadow"
          >
            <FileCode className="w-4 h-4 text-soc-primary" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        
        {/* GENERATOR CONTROLS PANEL (5/12) */}
        <div className="lg:col-span-5 bg-soc-surface border border-soc-border rounded-xl p-4 flex flex-col justify-between shadow-lg space-y-4">
          <div className="space-y-4">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider border-b border-soc-border pb-2 flex items-center justify-between">
              <span>Generator Parameter Knobs</span>
              <span className="text-[10px] text-soc-muted">Bank: Fusion National Bank</span>
            </h3>

            <div>
              <label className="text-xs font-mono text-soc-muted flex justify-between mb-1">
                <span>Synthetic Customer Population:</span>
                <span className="text-soc-primary font-bold">{numCustomers} Customers</span>
              </label>
              <input
                type="range"
                min="20"
                max="1000"
                step="20"
                value={numCustomers}
                onChange={(e) => setNumCustomers(e.target.value)}
                className="w-full"
              />
            </div>

            <div>
              <label className="text-xs font-mono text-soc-muted flex justify-between mb-1">
                <span>Transaction & Behavioral Volume:</span>
                <span className="text-soc-primary font-bold">{numTransactions} Transactions</span>
              </label>
              <input
                type="range"
                min="100"
                max="5000"
                step="100"
                value={numTransactions}
                onChange={(e) => setNumTransactions(e.target.value)}
                className="w-full"
              />
            </div>

            <div>
              <label className="text-xs font-mono text-soc-muted block mb-1">Reproducibility Seed:</label>
              <input
                type="number"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                className="w-full bg-soc-bg border border-soc-border rounded-lg p-2 text-xs font-mono text-soc-text focus:outline-none focus:border-soc-primary"
              />
            </div>

            <div className="p-3 bg-soc-panel rounded-xl border border-soc-border text-[11px] space-y-1">
              <div className="flex justify-between text-soc-muted">
                <span>Payment Gateways:</span>
                <span className="text-soc-text font-bold">UPI, NEFT, RTGS, IMPS</span>
              </div>
              <div className="flex justify-between text-soc-muted">
                <span>Graph Engine Topology:</span>
                <span className="text-emerald-400 font-bold">Neo4j Active</span>
              </div>
              <div className="flex justify-between text-soc-muted">
                <span>Fraud Injections:</span>
                <span className="text-rose-400 font-bold">Ground Truth Labeled</span>
              </div>
            </div>
          </div>

          <button
            onClick={handleGenerateUniverse}
            disabled={isGenerating}
            className={`w-full py-2.5 rounded-xl font-mono font-bold text-xs flex items-center justify-center gap-2 transition-all shadow ${
              isGenerating
                ? 'bg-soc-panel text-soc-muted cursor-not-allowed'
                : 'bg-soc-primary hover:bg-blue-600 text-white'
            }`}
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
            <span>{isGenerating ? 'Simulating Virtual Bank Universe...' : 'Generate Fusion Virtual Bank Universe'}</span>
          </button>
        </div>

        {/* GENERATED UNIVERSE PREVIEW & METRICS (7/12) */}
        <div className="lg:col-span-7 bg-soc-surface border border-soc-border rounded-xl p-4 space-y-4 shadow-lg">
          <div className="flex items-center justify-between border-b border-soc-border pb-2">
            <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-400" />
              <span>Virtual Bank Ecosystem Telemetry</span>
            </h3>
            <span className="text-[10px] text-soc-muted">
              {universeData ? 'GENERATION COMPLETE' : 'AWAITING GENERATION'}
            </span>
          </div>

          {universeData ? (
            <div className="space-y-4">
              
              {/* STATS STRIP */}
              <div className="grid grid-cols-3 gap-3">
                <div className="p-3 bg-soc-panel rounded-xl border border-soc-border text-center">
                  <div className="text-[10px] text-soc-muted uppercase">Customers</div>
                  <div className="text-lg font-bold text-soc-primary">{universeData.stats.customers_count}</div>
                </div>
                <div className="p-3 bg-soc-panel rounded-xl border border-soc-border text-center">
                  <div className="text-[10px] text-soc-muted uppercase">Accounts</div>
                  <div className="text-lg font-bold text-emerald-400">{universeData.stats.accounts_count}</div>
                </div>
                <div className="p-3 bg-soc-panel rounded-xl border border-soc-border text-center">
                  <div className="text-[10px] text-soc-muted uppercase">Transactions</div>
                  <div className="text-lg font-bold text-amber-400">{universeData.stats.transactions_count}</div>
                </div>
              </div>

              {/* GRAPH TOPOLOGY SUMMARY */}
              {universeData.graph_topology && (
                <div className="p-3 bg-soc-bg border border-soc-border rounded-xl space-y-1.5 text-[11px]">
                  <div className="font-bold text-soc-text flex justify-between">
                    <span>Neo4j Graph Relationship Topology</span>
                    <span className="text-emerald-400">Modularity: {universeData.graph_topology.graph_properties.louvain_modularity}</span>
                  </div>
                  <div className="flex justify-between text-soc-muted">
                    <span>Nodes: <strong>{universeData.graph_topology.nodes_count}</strong></span>
                    <span>Edges: <strong>{universeData.graph_topology.edges_count}</strong></span>
                    <span>Max PageRank: <strong>{universeData.graph_topology.graph_properties.pagerank_max}</strong></span>
                  </div>
                </div>
              )}

              {/* CUSTOMERS PREVIEW TABLE */}
              <div>
                <div className="text-[10px] font-bold text-soc-muted uppercase mb-1">Generated Customers Sample</div>
                <div className="overflow-x-auto max-h-[220px]">
                  <table className="w-full text-left font-mono text-[11px]">
                    <thead>
                      <tr className="border-b border-soc-border text-soc-dim uppercase text-[9px]">
                        <th className="py-1.5 px-2">ID</th>
                        <th className="py-1.5 px-2">Name</th>
                        <th className="py-1.5 px-2">City</th>
                        <th className="py-1.5 px-2">Salary</th>
                        <th className="py-1.5 px-2">Risk</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-soc-border/40">
                      {universeData.customers.slice(0, 5).map((c) => (
                        <tr key={c.customer_id} className="hover:bg-soc-panel/60">
                          <td className="py-1.5 px-2 font-bold text-soc-primary">{c.customer_id}</td>
                          <td className="py-1.5 px-2 text-soc-text">{c.full_name}</td>
                          <td className="py-1.5 px-2 text-soc-dim">{c.city}</td>
                          <td className="py-1.5 px-2 text-emerald-400 font-bold">₹{c.annual_salary.toLocaleString('en-IN')}</td>
                          <td className="py-1.5 px-2 text-rose-400 font-bold">{c.risk_tier}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

            </div>
          ) : (
            <div className="py-20 text-center text-soc-dim space-y-2">
              <FlaskConical className="w-10 h-10 mx-auto text-soc-muted/40" />
              <p className="text-xs font-mono">
                Click "Generate Fusion Virtual Bank Universe" to simulate a digital banking ecosystem.
              </p>
            </div>
          )}

        </div>

      </div>

    </div>
  );
}
