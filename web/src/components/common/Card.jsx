import React from 'react';

export default function Card({ children, className = '', header, footer, ...props }) {
  return (
    <div 
      className={`bg-soc-surface border border-soc-border rounded-xl overflow-hidden shadow-lg ${className}`} 
      {...props}
    >
      {header && (
        <div className="px-4 py-3 border-b border-soc-border bg-soc-panel/50 font-mono text-xs font-bold text-soc-text uppercase tracking-wider flex items-center justify-between">
          {header}
        </div>
      )}
      <div className="p-4">{children}</div>
      {footer && (
        <div className="px-4 py-2 border-t border-soc-border bg-soc-panel/30 text-xs font-mono text-soc-muted">
          {footer}
        </div>
      )}
    </div>
  );
}
