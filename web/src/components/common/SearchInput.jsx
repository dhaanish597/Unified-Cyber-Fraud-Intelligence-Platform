import React from 'react';
import { Search, X } from 'lucide-react';

export default function SearchInput({ value, onChange, onClear, placeholder = 'Search...', className = '' }) {
  return (
    <div className={`relative flex items-center ${className}`}>
      <Search className="w-4 h-4 text-soc-dim absolute left-3 pointer-events-none" />
      <input
        type="text"
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className="w-full bg-soc-bg border border-soc-border focus:border-soc-primary rounded-lg pl-9 pr-8 py-1.5 text-xs font-mono text-soc-text placeholder-soc-dim focus:outline-none transition-colors"
      />
      {value && (
        <button onClick={onClear} className="absolute right-2.5 text-soc-dim hover:text-soc-text">
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
}
