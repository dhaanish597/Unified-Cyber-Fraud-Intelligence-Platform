import React from 'react';

export default function PageContainer({ children, title, subtitle, action, className = '' }) {
  return (
    <div className={`flex flex-col gap-4 max-w-[1800px] mx-auto select-none ${className}`}>
      {(title || action) && (
        <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-md">
          <div>
            {title && <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">{title}</h1>}
            {subtitle && <p className="text-xs text-soc-muted mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
}
