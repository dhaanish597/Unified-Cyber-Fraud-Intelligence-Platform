import React from 'react';

export default function KeyValueGrid({ data = [] }) {
  return (
    <div className="grid grid-cols-2 gap-3 text-xs font-mono">
      {data.map((item, idx) => (
        <div key={idx} className="flex flex-col">
          <span className="text-soc-dim uppercase text-[10px]">{item.key}</span>
          <span className="text-soc-text font-semibold mt-0.5">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
