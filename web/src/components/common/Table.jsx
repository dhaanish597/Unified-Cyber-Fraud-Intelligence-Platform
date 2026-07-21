import React from 'react';

export default function Table({ headers = [], children, className = '' }) {
  return (
    <div className={`overflow-x-auto w-full border border-soc-border rounded-lg ${className}`}>
      <table className="w-full text-left font-mono text-xs select-none">
        {headers.length > 0 && (
          <thead>
            <tr className="border-b border-soc-border bg-soc-panel/80 text-soc-dim uppercase text-[10px]">
              {headers.map((h, i) => (
                <th key={i} className="py-2.5 px-3 font-semibold">{h}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody className="divide-y divide-soc-border/50 text-soc-text bg-soc-surface">
          {children}
        </tbody>
      </table>
    </div>
  );
}
