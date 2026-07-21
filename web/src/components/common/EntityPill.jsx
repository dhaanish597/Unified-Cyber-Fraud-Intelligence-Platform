import React from 'react';
import { User, Server, Shield, CreditCard } from 'lucide-react';

export default function EntityPill({ type = 'user', id, label, onClick }) {
  const icons = {
    user: User,
    account: CreditCard,
    ip: Server,
    device: Shield
  };
  const Icon = icons[type] || User;

  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-1.5 px-2 py-0.5 bg-soc-bg border border-soc-border hover:border-soc-primary text-soc-text font-mono text-xs rounded transition-colors"
    >
      <Icon className="w-3 h-3 text-soc-primary" />
      <span>{label || id}</span>
    </button>
  );
}
