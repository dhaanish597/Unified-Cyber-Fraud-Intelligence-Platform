import React, { useRef, useState, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { ZoomIn, ZoomOut, RefreshCw, Layers, ShieldAlert, Info } from 'lucide-react';

export default function Neo4jGraphStudio({ graphData, onNodeClick }) {
  const fgRef = useRef();
  const [selectedNode, setSelectedNode] = useState(null);
  const [highlightMule, setHighlightMule] = useState(true);

  const activeData = (graphData && graphData.nodes && graphData.nodes.length > 0)
    ? graphData
    : { nodes: [], links: [] };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (fgRef.current) {
      fgRef.current.centerAt(node.x, node.y, 1000);
      fgRef.current.zoom(2.5, 1000);
    }
    if (onNodeClick) onNodeClick(node);
  };

  const handleResetZoom = () => {
    if (fgRef.current) {
      fgRef.current.zoomToFit(800, 40);
    }
  };

  return (
    <div className="relative w-full h-full min-h-[380px] bg-soc-bg border border-soc-border rounded-xl overflow-hidden flex flex-col">
      {/* Graph Toolbar Header */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-soc-panel border-b border-soc-border z-10">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-soc-primary" />
          <span className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">
            Neo4j Threat Graph Visualizer
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-bg border border-soc-border text-soc-muted">
            NetworkX / GraphSAGE Centrality Engine
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setHighlightMule(!highlightMule)}
            className={`px-2.5 py-1 text-xs font-mono rounded border flex items-center gap-1.5 transition-colors ${
              highlightMule 
                ? 'bg-rose-500/20 border-rose-500/50 text-rose-400' 
                : 'bg-soc-bg border-soc-border text-soc-muted'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Mule Ring Overlay</span>
          </button>
          
          <div className="flex items-center bg-soc-bg border border-soc-border rounded p-0.5">
            <button
              onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.3, 400)}
              className="p-1 text-soc-muted hover:text-soc-text"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.3, 400)}
              className="p-1 text-soc-muted hover:text-soc-text"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleResetZoom}
              className="p-1 text-soc-muted hover:text-soc-text border-l border-soc-border ml-1 pl-1"
              title="Reset Camera"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Force Graph Canvas Area */}
      <div className="relative flex-1 bg-soc-bg">
        <ForceGraph2D
          ref={fgRef}
          graphData={activeData}
          nodeAutoColorBy="group"
          nodeRelSize={7}
          linkWidth={1.5}
          linkColor={() => '#2A3447'}
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const label = node.name || node.id;
            const fontSize = 12 / globalScale;
            ctx.font = `${fontSize}px JetBrains Mono, monospace`;
            
            // Draw circle node
            const radius = (node.val || 15) / 2;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
            
            if (node.isMule && highlightMule) {
              ctx.fillStyle = '#EF4444';
              ctx.shadowColor = '#EF4444';
              ctx.shadowBlur = 10;
            } else {
              ctx.fillStyle = node.color || '#3B82F6';
              ctx.shadowBlur = 0;
            }
            ctx.fill();
            ctx.strokeStyle = '#FFFFFF';
            ctx.lineWidth = 1 / globalScale;
            ctx.stroke();

            // Text Label
            if (globalScale > 1.2) {
              ctx.textAlign = 'center';
              ctx.textBaseline = 'middle';
              ctx.fillStyle = '#F3F4F6';
              ctx.fillText(label, node.x, node.y + radius + fontSize);
            }
          }}
          onNodeClick={handleNodeClick}
          cooldownTicks={100}
        />

        {/* Selected Node Details Card Overlay */}
        {selectedNode && (
          <div className="absolute top-4 right-4 w-72 bg-soc-surface/95 border border-soc-border p-3.5 rounded-lg shadow-2xl backdrop-blur-md z-20">
            <div className="flex items-start justify-between border-b border-soc-border pb-2 mb-2">
              <div>
                <span className="text-[10px] font-mono uppercase text-soc-dim">Entity Inspection</span>
                <h4 className="text-xs font-mono font-bold text-soc-primary truncate">{selectedNode.id}</h4>
              </div>
              <button 
                onClick={() => setSelectedNode(null)} 
                className="text-soc-dim hover:text-soc-text text-xs"
              >
                ✕
              </button>
            </div>
            <div className="space-y-1.5 text-xs font-mono">
              <div className="flex justify-between">
                <span className="text-soc-muted">Type:</span>
                <span className="text-soc-text capitalize">{selectedNode.group || 'Account'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-soc-muted">PageRank:</span>
                <span className="text-soc-text">{selectedNode.pagerank || '0.0042'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-soc-muted">Betweenness:</span>
                <span className="text-soc-text">{selectedNode.betweenness || '0.0120'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-soc-muted">Mule Cluster:</span>
                <span className={selectedNode.isMule ? "text-soc-danger font-bold" : "text-soc-success"}>
                  {selectedNode.isMule ? "FLAGGED RING" : "CLEAN"}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Graph Legend Overlay */}
        <div className="absolute bottom-3 left-3 bg-soc-panel/90 border border-soc-border px-3 py-2 rounded-md backdrop-blur-sm z-10 flex gap-4 text-[11px] font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-500 inline-block"></span>
            <span className="text-soc-muted">User</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-500 inline-block"></span>
            <span className="text-soc-muted">Account</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span>
            <span className="text-soc-muted">IP</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-purple-500 inline-block"></span>
            <span className="text-soc-muted">Device</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block animate-pulse"></span>
            <span className="text-soc-danger font-bold">Mule Cluster</span>
          </div>
        </div>
      </div>
    </div>
  );
}
