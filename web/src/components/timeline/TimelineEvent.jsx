import React from 'react';
import SeverityBadge from '../common/SeverityBadge';

export default function TimelineEvent({ events = [] }) {
  if (!events.length) {
    return <div className="text-xs font-mono text-soc-dim text-center mt-8">Awaiting SIEM cyber events...</div>;
  }

  return (
    <div className="flex flex-col gap-2.5">
      {events.map((evt, i) => (
        <div 
          key={i} 
          className={`p-2.5 rounded-lg border-l-4 bg-soc-panel/60 border-soc-border hover:border-soc-primary transition-colors ${
            evt.severity === 'critical' 
              ? 'border-l-soc-danger bg-soc-danger/10' 
              : evt.severity === 'medium' 
              ? 'border-l-soc-warning bg-soc-warning/10' 
              : 'border-l-soc-primary bg-soc-primary/10'
          }`}
        >
          <div className="flex justify-between items-start mb-1">
            <span className="text-[11px] font-mono text-soc-muted">{evt.timestamp ? evt.timestamp.split(' ')[1] : '10:00:00'}</span>
            <SeverityBadge severity={evt.severity || 'info'} />
          </div>
          <div className="text-xs font-mono font-bold text-soc-text uppercase">
            {(evt.event_type || 'CYBER_EVENT').replace(/_/g, ' ')}
          </div>
          <div className="text-[11px] font-mono text-soc-muted mt-1 flex flex-col gap-0.5">
            <span>User: <span className="text-soc-text font-bold">{evt.user_id}</span></span>
            <span>IP: <span className="text-soc-text font-bold">{evt.ip}</span></span>
            {evt.km_from_baseline > 100 && (
              <span className="text-soc-danger font-bold">Impossible Travel: {evt.km_from_baseline} km</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
