import React, { useState, useEffect, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { Activity, ShieldAlert, DollarSign, Server, AlertTriangle, CheckCircle, XCircle, FileText, Lock } from 'lucide-react';

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
  const [activeTab, setActiveTab] = useState('demo');
  const [quantumData, setQuantumData] = useState(null);

  const ws = useRef(null);

  useEffect(() => {
    fetch('http://localhost:8001/quantum/posture')
      .then(r => r.json())
      .then(data => setQuantumData(data))
      .catch(e => console.error("Quantum fetch error:", e));
  }, []);

  const startDemo = () => {
    setEvents([]);
    setCurrentTxn(null);
    setEvaluation(null);
    setGraphData({ nodes: [], links: [] });

    if (ws.current) ws.current.close();
    ws.current = new WebSocket('ws://localhost:8001/ws/stream');
    
    ws.current.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      
      if (data.msg_type === 'status') {
         // Optionally handle status messages for the UI
         return;
      }
      
      setEvents(prev => [data, ...prev].slice(0, 50));
      
      setKpi(prev => ({
        tps: Math.floor(Math.random() * 10) + 5,
        intercepted: prev.intercepted
      }));

      if (data.msg_type === 'transaction') {
        setCurrentTxn(data);
        try {
          const res = await fetch('http://localhost:8001/evaluate/transaction', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          });
          const result = await res.json();
          setEvaluation(result);
          
          if (result.action === 'BLOCK') {
             setKpi(prev => ({ ...prev, intercepted: prev.intercepted + data.amount }));
          }

          // Generate Graph Data (expand mule cluster if present)
          const newNodes = [
            { id: data.nameOrig, group: 1, val: 20, name: 'Sender: ' + data.nameOrig },
            { id: data.nameDest, group: 2, val: 20, name: 'Receiver: ' + data.nameDest }
          ];
          const newLinks = [
            { source: data.nameOrig, target: data.nameDest }
          ];

          if (data.dest_mule_cluster_id) {
             // Expand 6-account mule cluster
             for (let i = 1; i <= 6; i++) {
               const muleId = `mule_acc_${i}`;
               newNodes.push({ id: muleId, group: 3, val: 10, name: 'Mule: ' + muleId });
               newLinks.push({ source: data.nameDest, target: muleId });
             }
          }
          setGraphData({ nodes: newNodes, links: newLinks });

        } catch (e) {
          console.error("Evaluation failed", e);
        }
      }
    };
  };

  const downloadCertInReport = async () => {
    if (!currentTxn || !evaluation) return;
    
    const res = await fetch('http://localhost:8001/report/cert-in', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        txn_id: currentTxn.txn_id,
        user_id: currentTxn.user_id,
        amount: currentTxn.amount,
        reasons: evaluation.reasons,
        score: evaluation.score
      })
    });
    
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `CERT-In_Report_${currentTxn.txn_id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
  };

  return (
    <div className="min-h-screen bg-soc-bg text-gray-300 font-sans flex flex-col h-screen overflow-hidden">
      {/* Header */}
      <header className="bg-soc-panel border-b border-soc-border p-4 flex justify-between items-center shrink-0">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <ShieldAlert className="text-soc-primary w-6 h-6" />
            <h1 className="text-xl font-bold text-white tracking-wide">Fusion Risk Engine</h1>
          </div>
          <nav className="flex gap-2 bg-black/40 p-1 rounded-lg">
            <button 
              onClick={() => setActiveTab('demo')}
              className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${activeTab === 'demo' ? 'bg-soc-primary text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Live Monitor
            </button>
            <button 
              onClick={() => setActiveTab('quantum')}
              className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors ${activeTab === 'quantum' ? 'bg-soc-primary text-white' : 'text-gray-400 hover:text-white'}`}
            >
              Quantum Posture
            </button>
          </nav>
        </div>
        
        <div className="flex gap-4">
          <button onClick={startDemo} className="bg-soc-success/20 text-soc-success border border-soc-success px-4 py-2 rounded-lg text-sm font-bold hover:bg-soc-success hover:text-white transition-all">
            ▶ Play Demo
          </button>
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <Activity className="text-soc-success w-4 h-4" />
            <span className="text-sm">TPS: {kpi.tps}</span>
          </div>
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <AlertTriangle className="text-soc-warning w-4 h-4" />
            <span className="text-sm">Threat: ELEVATED</span>
          </div>
          <div className="flex items-center gap-2 bg-soc-bg px-4 py-2 rounded-lg border border-soc-border">
            <DollarSign className="text-soc-danger w-4 h-4" />
            <span className="text-sm font-semibold">Intercepted: ₹{kpi.intercepted.toLocaleString(undefined, {maximumFractionDigits:0})}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      {activeTab === 'demo' ? (
        <main className="flex-1 flex overflow-hidden p-4 gap-4">
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

          <div className="w-2/4 flex flex-col gap-4">
            <div className="bg-soc-panel rounded-xl border border-soc-border p-6 flex flex-col items-center justify-center shrink-0 relative overflow-hidden">
               <div className={`absolute inset-0 opacity-10 ${evaluation?.action === 'BLOCK' ? 'bg-soc-danger' : evaluation?.action === 'CHALLENGE' ? 'bg-soc-warning' : evaluation?.action === 'ALLOW' ? 'bg-soc-success' : 'bg-transparent'}`}></div>
               <VerdictBadge evaluation={evaluation} currentTxn={currentTxn} />
               
               {evaluation && evaluation.action === 'BLOCK' && (
                 <button onClick={downloadCertInReport} className="mt-4 z-10 flex items-center gap-2 bg-soc-danger text-white px-4 py-2 rounded-lg text-sm font-bold shadow-lg shadow-soc-danger/20 hover:scale-105 transition-transform">
                   <FileText className="w-4 h-4" />
                   Generate CERT-In Report
                 </button>
               )}
            </div>
            
            <div className="flex-1 bg-soc-panel rounded-xl border border-soc-border flex flex-col overflow-hidden relative">
              <div className="p-3 border-b border-soc-border bg-black/20 shrink-0 flex justify-between items-center">
                <h2 className="font-semibold text-gray-100">Threat Graph Visualizer</h2>
                {graphData.nodes.length > 2 && <span className="text-xs text-soc-danger bg-soc-danger/20 px-2 py-1 rounded">Mule Cluster Expanded</span>}
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
      ) : (
        <main className="flex-1 overflow-auto p-8 flex justify-center items-start">
          <div className="max-w-4xl w-full bg-soc-panel rounded-xl border border-soc-border overflow-hidden">
            <div className="p-6 border-b border-soc-border bg-black/20 flex items-center gap-3">
              <Lock className="w-6 h-6 text-soc-primary" />
              <h2 className="text-xl font-bold text-white">Quantum Posture Monitor</h2>
            </div>
            
            {quantumData ? (
              <div className="p-8 flex flex-col gap-8">
                <div className="flex items-center gap-8">
                  <div className="relative w-48 h-48 rounded-full border-8 border-soc-border flex items-center justify-center">
                    <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 100 100">
                      <circle cx="50" cy="50" r="46" fill="transparent" stroke="#EF4444" strokeWidth="8" strokeDasharray={`${quantumData.vulnerable_percent * 2.89} 289`} />
                    </svg>
                    <div className="text-center">
                      <div className="text-4xl font-black text-white">{quantumData.vulnerable_percent}%</div>
                      <div className="text-xs text-gray-400 mt-1 uppercase font-semibold">Vulnerable</div>
                    </div>
                  </div>
                  <div className="flex-1 space-y-4">
                    <h3 className="text-lg font-semibold text-gray-200">TLS Cipher Suite Analysis</h3>
                    <p className="text-gray-400 text-sm leading-relaxed">
                      Analyzing real-time TLS handshake records. Classical ciphers (RSA, plain ECDHE) are flagged as quantum-vulnerable.
                      Hybrid/PQC ciphers (ML-KEM) are safe against Store-Now-Decrypt-Later attacks.
                    </p>
                  </div>
                </div>

                {quantumData.hndl_flag && (
                  <div className="mt-4 p-6 rounded-xl border-2 border-soc-danger bg-soc-danger/10 flex gap-4">
                    <AlertTriangle className="w-8 h-8 text-soc-danger shrink-0" />
                    <div>
                      <h4 className="text-soc-danger font-bold text-lg mb-1">Harvest-Now-Decrypt-Later (HNDL) Risk Detected!</h4>
                      <p className="text-gray-300 text-sm leading-relaxed">
                        {quantumData.hndl_details}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 text-center text-gray-500">Loading posture data...</div>
            )}
          </div>
        </main>
      )}
    </div>
  );
}
