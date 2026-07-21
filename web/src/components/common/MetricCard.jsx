import React from 'react';

export default function MetricCard({ title, value, subtext, icon: Icon, trend, color = 'primary' }) {
  const colors = {
    primary: 'text-soc-primary bg-soc-primary/10 border-soc-primary/30',
    danger: 'text-soc-danger bg-soc-danger/10 border-soc-danger/30',
    warning: 'text-soc-warning bg-soc-warning/10 border-soc-warning/30',
    success: 'text-soc-success bg-soc-success/10 border-soc-success/30',
    quantum: 'text-purple-400 bg-purple-500/10 border-purple-500/30'
  };

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 flex items-center justify-between shadow-md select-none">
      <div>
        <span className="text-[10px] font-mono uppercase text-soc-dim font-semibold">{title}</span>
        <div className="text-xl font-mono font-bold text-soc-text mt-1">{value}</div>
        {subtext && <span className="text-[11px] font-mono text-soc-muted mt-0.5 inline-block">{subtext}</span>}
      </div>
      {Icon && (
        <div className={`p-3 rounded-xl border ${colors[color] || colors.primary}`}>
          <Icon className="w-5 h-5" />
        </div>
      )}
    </div>
  );
}
