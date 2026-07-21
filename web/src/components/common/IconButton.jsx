import React from 'react';

export default function IconButton({ 
  icon: Icon, 
  title, 
  onClick, 
  variant = 'ghost', 
  size = 'md', 
  className = '', 
  ...props 
}) {
  const base = 'inline-flex items-center justify-center rounded-lg transition-colors focus:outline-none select-none';
  
  const variants = {
    ghost: 'text-soc-muted hover:text-soc-text hover:bg-soc-panel',
    bordered: 'bg-soc-bg border border-soc-border hover:border-soc-primary text-soc-muted hover:text-soc-text',
    primary: 'bg-soc-primary hover:bg-blue-600 text-white'
  };

  const sizes = {
    sm: 'p-1 text-xs',
    md: 'p-1.5 text-sm',
    lg: 'p-2.5 text-base'
  };

  return (
    <button
      onClick={onClick}
      title={title}
      className={`${base} ${variants[variant] || variants.ghost} ${sizes[size] || sizes.md} ${className}`}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4" />}
    </button>
  );
}
