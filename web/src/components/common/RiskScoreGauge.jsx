import React from 'react';

export default function RiskScoreGauge({ score = 0, max = 100 }) {
  const normalized = Math.min(100, Math.max(0, score));
  
  let color = '#10B981'; // Green
  let category = 'LOW RISK';
  if (normalized >= 75) {
    color = '#EF4444'; // Red
    category = 'CRITICAL RISK';
  } else if (normalized >= 50) {
    color = '#F59E0B'; // Amber
    category = 'ELEVATED RISK';
  }

  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalized / max) * circumference;

  return (
    <div className="flex items-center gap-4 bg-soc-panel border border-soc-border p-3 rounded-lg">
      <div className="relative flex items-center justify-center w-20 h-20">
        <svg className="w-20 h-20 transform -rotate-90">
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke="#1E293B"
            strokeWidth="6"
            fill="transparent"
          />
          <circle
            cx="40"
            cy="40"
            r={radius}
            stroke={color}
            strokeWidth="6"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <span className="absolute font-mono font-black text-xl text-soc-text">
          {Math.round(normalized)}
        </span>
      </div>
      <div className="flex flex-col justify-center">
        <span className="text-[10px] font-mono uppercase text-soc-dim tracking-wider">Composite Score</span>
        <span className="text-sm font-bold tracking-wide" style={{ color }}>{category}</span>
        <span className="text-xs text-soc-muted mt-0.5 font-mono">{normalized}/100 Risk Index</span>
      </div>
    </div>
  );
}
