import React from 'react';

export default function Panel({ children, title, subtitle, action, className = '' }) {
  return (
    <div className={`bg-soc-panel border border-soc-border rounded-xl p-4 flex flex-col justify-between ${className}`}>
      {(title || action) && (
        <div className="flex items-center justify-between border-b border-soc-border pb-2.5 mb-3">
          <div>
            {title && <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider">{title}</h3>}
            {subtitle && <p className="text-[10px] font-mono text-soc-dim mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div className="flex-1">{children}</div>
    </div>
  );
}
