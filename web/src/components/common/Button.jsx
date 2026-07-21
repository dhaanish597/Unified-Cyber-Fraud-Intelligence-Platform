import React from 'react';

export default function Button({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  disabled = false, 
  onClick, 
  className = '', 
  icon: Icon,
  ...props 
}) {
  const base = 'inline-flex items-center justify-center font-mono font-bold rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-soc-primary/50 disabled:opacity-50 disabled:cursor-not-allowed select-none';
  
  const variants = {
    primary: 'bg-soc-primary hover:bg-blue-600 text-white shadow-md shadow-blue-950/40',
    danger: 'bg-soc-danger hover:bg-rose-600 text-white shadow-md shadow-rose-950/40',
    warning: 'bg-soc-warning hover:bg-amber-600 text-white shadow-md shadow-amber-950/40',
    success: 'bg-soc-success hover:bg-emerald-600 text-white shadow-md shadow-emerald-950/40',
    secondary: 'bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text',
    ghost: 'bg-transparent hover:bg-soc-panel text-soc-muted hover:text-soc-text'
  };

  const sizes = {
    sm: 'px-2.5 py-1 text-xs gap-1.5',
    md: 'px-3.5 py-2 text-xs gap-2',
    lg: 'px-5 py-2.5 text-sm gap-2.5'
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant] || variants.primary} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {Icon && <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />}
      <span>{children}</span>
    </button>
  );
}
