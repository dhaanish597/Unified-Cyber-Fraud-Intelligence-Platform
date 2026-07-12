import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Activity, ShieldAlert, DollarSign, Server, AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

// Components
import Timeline from './components/Timeline';
import Ledger from './components/Ledger';
import VerdictBadge from './components/VerdictBadge';
import XAIPanel from './components/XAIPanel';

export default function App() {
  const [events, setEvents] = useState([]);
  const [currentTxn, setCurrentTxn] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [kpi, setKpi] = useState({ tps: 0, intercepted: 0 });
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });

  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/stream');
    
    ws.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [data, ...prev].slice(0, 50)); // Keep last 50
      
      // Update KPI
      setKpi(prev => ({
        tps: Math.floor(Math.random() * 10) + 5,
        intercepted: prev.intercepted + (data.msg_type === 'transaction' && data.amount ? data.amount * 0.05 : 0)
      }));

      if (data.msg_type === 'transaction') {
        setCurrentTxn(data);
        // Call API
        try {
          const res = await fetch('http://localhost:8000/evaluate/transaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          const result = await res.json();
          setEvaluation(result);
          
          if (result.action === 'BLOCK') {
             setKpi(prev => ({ ...prev, intercepted: prev.intercepted + data.amount }));
          }

          // Update Graph Data
          setGraphData({
            nodes: [
              { id: data.nameOrig, group: 1, val: 20, name: 'Sender: ' + data.nameOrig },
              { id: data.nameDest, group: 2, val: 20, name: 'Receiver: ' + data.nameDest },
              { id: data.device_id, group: 3, val: 10, name: 'Device: ' + data.device_id },
              { id: data.ip, group: 4, val: 10, name: 'IP: ' + data.ip }
            ],
            links: [
              { source: data.nameOrig, target: data.nameDest },
              { source: data.nameOrig, target: data.device_id },
              { source: data.nameOrig, target: data.ip }
            ]
          });

        } catch (e) {
          console.error("Evaluation failed", e);
        }
      }
    };

    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-soc-bg text-gray-300 font-sans flex flex-col h-screen overflow-hidden">
      {/* KPI Header */}
      <header className="bg-soc-panel border-b border-soc-border p-4 flex justify-between items-center shrink-0">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-soc-primary w-6 h-6" />
          <h1 className="text-xl font-bold text-white tracking-wide">Fusion Risk Engine</h1>
        </div>
        <div className="flex gap-6">
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <Activity className="text-soc-success w-4 h-4" />
            <span className="text-sm">TPS: {kpi.tps}</span>
          </div>
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <AlertTriangle className="text-soc-warning w-4 h-4" />
            <span className="text-sm">Threat Level: ELEVATED</span>
          </div>
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <DollarSign className="text-soc-danger w-4 h-4" />
            <span className="text-sm font-semibold">Intercepted (24h): ₹{kpi.intercepted.toLocaleString(undefined, {maximumFractionDigits:0})}</span>
          </div>
        </div>
      </header>

      {/* 3-Column Layout */}
      <main className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* Left: SIEM Timeline */}
        <div className="w-1/4 bg-soc-panel rounded-xl border border-soc-border flex flex-col overflow-hidden">
          <div className="p-3 border-b border-soc-border bg-black/20">
            <h2 className="font-semibold text-gray-100 flex items-center gap-2">
              <Server className="w-4 h-4" /> SIEM Timeline
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <Timeline events={events.filter(e => e.msg_type === 'cyber_event')} />
          </div>
        </div>

        {/* Center: Evaluation & Graph */}
        <div className="w-2/4 flex flex-col gap-4">
          <div className="bg-soc-panel rounded-xl border border-soc-border p-6 flex flex-col items-center justify-center shrink-0 relative overflow-hidden">
             {/* Subtle background glow based on action */}
             <div className={`absolute inset-0 opacity-10 ${evaluation?.action === 'BLOCK' ? 'bg-soc-danger' : evaluation?.action === 'CHALLENGE' ? 'bg-soc-warning' : evaluation?.action === 'ALLOW' ? 'bg-soc-success' : 'bg-transparent'}`}></div>
             <VerdictBadge evaluation={evaluation} currentTxn={currentTxn} />
          </div>
          
          <div className="flex-1 bg-soc-panel rounded-xl border border-soc-border flex flex-col overflow-hidden relative">
            <div className="p-3 border-b border-soc-border bg-black/20 shrink-0">
              <h2 className="font-semibold text-gray-100">Threat Graph Visualizer</h2>
            </div>
            <div className="flex-1 relative w-full h-full bg-[#0a0a0a]">
              {graphData.nodes.length > 0 && (
                <ForceGraph2D
                  graphData={graphData}
                  nodeAutoColorBy="group"
                  nodeLabel="name"
                  linkDirectionalParticles={2}
                  linkDirectionalParticleSpeed={0.01}
                  backgroundColor="#0B0F19"
                  nodeRelSize={6}
                />
              )}
            </div>
          </div>

          {evaluation && <XAIPanel evaluation={evaluation} />}
        </div>

        {/* Right: Ledger */}
        <div className="w-1/4 bg-soc-panel rounded-xl border border-soc-border flex flex-col overflow-hidden">
          <div className="p-3 border-b border-soc-border bg-black/20">
            <h2 className="font-semibold text-gray-100 flex items-center gap-2">
              <Activity className="w-4 h-4" /> Transaction Ledger
            </h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            <Ledger events={events.filter(e => e.msg_type === 'transaction')} />
          </div>
        </div>
      </main>
    </div>
  );
}
