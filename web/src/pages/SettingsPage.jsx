import React, { useState } from 'react';
import { Sliders, Save, ShieldAlert, Cpu } from 'lucide-react';

export default function SettingsPage() {
  const [blockThreshold, setBlockThreshold] = useState(75);
  const [challengeThreshold, setChallengeThreshold] = useState(50);
  const [windowSeconds, setWindowSeconds] = useState(300);

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Sliders className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Risk Engine Policy & Threshold Tuning
            </h1>
            <span className="text-xs text-soc-muted">Adjust cutoffs for BLOCK, CHALLENGE, and Cyber Compromise Windows</span>
          </div>
        </div>
      </div>

      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 max-w-2xl space-y-4">
        <div>
          <label className="text-xs font-mono text-soc-muted flex justify-between mb-1">
            <span>BLOCK Verdict Cutoff Threshold (Score ≥ N):</span>
            <span className="text-rose-400 font-bold font-mono">{blockThreshold}/100</span>
          </label>
          <input
            type="range"
            min="60"
            max="95"
            value={blockThreshold}
            onChange={(e) => setBlockThreshold(e.target.value)}
            className="w-full"
          />
        </div>

        <div>
          <label className="text-xs font-mono text-soc-muted flex justify-between mb-1">
            <span>CHALLENGE Verdict Cutoff Threshold (Score ≥ N):</span>
            <span className="text-amber-400 font-bold font-mono">{challengeThreshold}/100</span>
          </label>
          <input
            type="range"
            min="30"
            max="65"
            value={challengeThreshold}
            onChange={(e) => setChallengeThreshold(e.target.value)}
            className="w-full"
          />
        </div>

        <div>
          <label className="text-xs font-mono text-soc-muted flex justify-between mb-1">
            <span>Cyber Compromise Correlation Window:</span>
            <span className="text-soc-primary font-bold font-mono">{windowSeconds} seconds (5 mins)</span>
          </label>
          <input
            type="range"
            min="60"
            max="900"
            step="30"
            value={windowSeconds}
            onChange={(e) => setWindowSeconds(e.target.value)}
            className="w-full"
          />
        </div>

        <button className="px-4 py-2 bg-soc-primary hover:bg-blue-600 text-white rounded text-xs font-mono font-bold flex items-center gap-2 transition-colors mt-4">
          <Save className="w-4 h-4" />
          <span>Save Policy Configuration</span>
        </button>
      </div>
    </div>
  );
}
