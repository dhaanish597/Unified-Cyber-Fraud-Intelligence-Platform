import React from 'react';

export default function Ledger({ events }) {
  if (!events.length) return <div className="text-sm text-gray-500 text-center mt-10">Awaiting transactions...</div>;

  return (
    <div className="flex flex-col gap-3">
      {events.map((evt, i) => (
        <div key={i} className="p-3 rounded-lg bg-black/30 border border-soc-border hover:border-soc-primary/50 transition-colors">
          <div className="flex justify-between items-start mb-2">
            <span className="text-xs font-mono text-gray-400">{evt.timestamp.split(' ')[1]}</span>
            <span className="text-xs font-mono text-gray-500">{evt.txn_id}</span>
          </div>
          <div className="flex justify-between items-center">
            <div className="text-sm font-semibold text-gray-200">{evt.type}</div>
            <div className="text-sm font-bold text-gray-100">₹{evt.amount.toLocaleString()}</div>
          </div>
          <div className="text-xs text-gray-400 mt-2 flex justify-between">
            <span className="truncate w-20">{evt.nameOrig}</span>
            <span>→</span>
            <span className="truncate w-20 text-right">{evt.nameDest}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
