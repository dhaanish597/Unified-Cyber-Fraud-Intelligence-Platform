import React from 'react';

export default function Timeline({ events }) {
  if (!events.length) return <div className="text-sm text-gray-500 text-center mt-10">Listening for cyber events...</div>;

  return (
    <div className="flex flex-col gap-3">
      {events.map((evt, i) => (
        <div key={i} className={`p-3 rounded-lg border-l-4 ${evt.severity === 'critical' ? 'border-soc-danger bg-soc-danger/10' : evt.severity === 'medium' ? 'border-soc-warning bg-soc-warning/10' : 'border-soc-primary bg-soc-primary/10'}`}>
          <div className="flex justify-between items-start mb-1">
            <span className="text-xs font-mono text-gray-400">{evt.timestamp.split(' ')[1]}</span>
            <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${evt.severity === 'critical' ? 'bg-soc-danger text-white' : evt.severity === 'medium' ? 'bg-soc-warning text-black' : 'bg-soc-primary text-white'}`}>
              {evt.severity}
            </span>
          </div>
          <div className="text-sm font-semibold text-gray-200">{evt.event_type.replace(/_/g, ' ').toUpperCase()}</div>
          <div className="text-xs text-gray-400 mt-1 flex flex-col">
            <span>User: <span className="text-gray-300 font-mono">{evt.user_id}</span></span>
            <span>IP: <span className="text-gray-300 font-mono">{evt.ip}</span></span>
            {evt.km_from_baseline > 100 && <span className="text-soc-danger mt-1">Travel: {evt.km_from_baseline} km</span>}
          </div>
        </div>
      ))}
    </div>
  );
}
