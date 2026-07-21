import React from 'react';

export default function Badge({ children, variant = 'default', size = 'sm', className = '' }) {
  const variants = {
    default: 'bg-soc-panel text-soc-muted border-soc-border',
    primary: 'bg-soc-primary/20 text-soc-primary border-soc-primary/40',
    success: 'bg-soc-success/20 text-soc-success border-soc-success/40',
    warning: 'bg-soc-warning/20 text-soc-warning border-soc-warning/40',
    danger: 'bg-soc-danger/20 text-soc-danger border-soc-danger/40',
    quantum: 'bg-purple-500/20 text-purple-400 border-purple-500/40'
  };

  const sizes = {
    xs: 'px-1.5 py-0.2 text-[9px]',
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-xs'
  };

  return (
    <span className={`inline-flex items-center justify-center font-mono font-bold border rounded ${variants[variant] || variants.default} ${sizes[size] || sizes.sm} ${className}`}>
      {children}
    </span>
  );
}
