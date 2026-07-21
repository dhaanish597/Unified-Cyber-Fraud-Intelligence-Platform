import React from 'react';

export default function TransactionTable({ events = [] }) {
  if (!events.length) {
    return <div className="text-xs font-mono text-soc-dim text-center mt-8">Awaiting transactions...</div>;
  }

  return (
    <div className="flex flex-col gap-2.5">
      {events.map((evt, i) => (
        <div key={i} className="p-2.5 rounded-lg bg-soc-panel/60 border border-soc-border hover:border-soc-primary/50 transition-colors">
          <div className="flex justify-between items-start mb-1">
            <span className="text-[11px] font-mono text-soc-muted">{evt.timestamp ? evt.timestamp.split(' ')[1] : '10:00:40'}</span>
            <span className="text-[10px] font-mono text-soc-dim">{evt.txn_id}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-xs font-mono font-bold text-soc-text">{evt.type}</span>
            <span className="text-xs font-mono font-bold text-soc-text">₹{evt.amount?.toLocaleString()}</span>
          </div>
          <div className="text-[11px] font-mono text-soc-muted mt-1 flex justify-between">
            <span className="truncate w-24">{evt.nameOrig}</span>
            <span>→</span>
            <span className="truncate w-24 text-right">{evt.nameDest}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
