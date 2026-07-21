import React from 'react';

export default function Tabs({ tabs = [], activeTab, onChange }) {
  return (
    <div className="flex items-center gap-1 bg-soc-bg border border-soc-border p-1 rounded-lg select-none">
      {tabs.map((t) => (
        <button
          key={t.id}
          onClick={() => onChange(t.id)}
          className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
            activeTab === t.id
              ? 'bg-soc-primary text-white font-bold shadow'
              : 'text-soc-muted hover:text-soc-text hover:bg-soc-panel'
          }`}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
