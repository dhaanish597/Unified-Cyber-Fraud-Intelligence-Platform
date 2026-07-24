import React from 'react';
import Card from '../common/Card';

const order = ['identity', 'device', 'runtime', 'behaviour', 'network', 'geo', 'threat', 'graph', 'transaction'];

const heat = (value) => {
  if (value >= 85) return 'rgba(16,185,129,.22)';
  if (value >= 70) return 'rgba(245,158,11,.22)';
  return 'rgba(244,63,94,.22)';
};

export default function TrustComponentHeatmap({ components = {} }) {
  return (
    <Card header="Trust Component Heatmap">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 xl:grid-cols-5">
        {order.map((name) => {
          const component = components[name];
          const value = Number(component?.value ?? 0);
          const difference = Number(component?.difference ?? 0);
          return (
            <div
              key={name}
              className="rounded-lg border border-soc-border p-3"
              style={{ backgroundColor: heat(value) }}
            >
              <div className="text-[10px] uppercase tracking-wider text-soc-muted">{name}</div>
              <div className="mt-2 flex items-end justify-between">
                <span className="text-xl font-black text-soc-text">{component ? value.toFixed(0) : '—'}</span>
                <span className={`text-[10px] font-bold ${difference > 0 ? 'text-emerald-300' : difference < 0 ? 'text-rose-300' : 'text-soc-muted'}`}>
                  {component ? `${difference > 0 ? '+' : ''}${difference.toFixed(1)}` : ''}
                </span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-soc-bg">
                <div className="h-full rounded-full bg-soc-primary transition-all duration-500" style={{ width: `${value}%` }} />
              </div>
              <div className="mt-2 flex justify-between text-[9px] text-soc-muted">
                <span>{component?.trend ?? 'NO DATA'}</span>
                <span>{component ? `${Number(component.confidence).toFixed(0)}% conf.` : ''}</span>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
