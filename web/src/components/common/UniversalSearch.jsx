import React, { useState, useEffect } from 'react';
import { Search, User, Shield, Server, CreditCard, X, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function UniversalSearch({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const mockDatabase = [
    { type: 'user', id: 'usr_abc', label: 'User: usr_abc', sub: 'Primary Target (Impossible Travel Alert)', route: '/investigation/CASE-2026-8942' },
    { type: 'account', id: 'ACC_ABC_123', label: 'Account: ACC_ABC_123', sub: 'Originating Transfer Account', route: '/investigation/CASE-2026-8942' },
    { type: 'account', id: 'ACC_MULE_NEW', label: 'Account: ACC_MULE_NEW', sub: 'Flagged Mule Beneficiary', route: '/investigation/CASE-2026-8942' },
    { type: 'ip', id: '185.15.2.22', label: 'IP: 185.15.2.22', sub: 'High Risk Anonymizer Proxy (RU)', route: '/telemetry' },
    { type: 'device', id: 'dev_9999', label: 'Device: dev_9999', sub: 'New Unregistered Mobile Handset', route: '/telemetry' },
    { type: 'mule', id: 'cluster_alpha', label: 'Mule Ring: cluster_alpha', sub: 'Shared IP & Device Ring (6 Accounts)', route: '/graph' },
    { type: 'transaction', id: 'txn_demo_999', label: 'Txn: txn_demo_999', sub: 'INR 7,500,000 Transfer (Blocked)', route: '/banking' },
  ];

  const results = query.trim() === ''
    ? mockDatabase.slice(0, 5)
    : mockDatabase.filter(item => 
        item.id.toLowerCase().includes(query.toLowerCase()) || 
        item.label.toLowerCase().includes(query.toLowerCase()) ||
        item.sub.toLowerCase().includes(query.toLowerCase())
      );

  const handleSelect = (route) => {
    navigate(route);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/70 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-soc-surface border border-soc-border rounded-xl shadow-2xl overflow-hidden">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3 border-b border-soc-border bg-soc-panel">
          <Search className="w-5 h-5 text-soc-muted mr-3" />
          <input
            type="text"
            placeholder="Search Customer, Account, UPI, IP, Device, Txn ID, Mule Cluster... (Esc to close)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent text-soc-text placeholder-soc-dim font-mono text-sm focus:outline-none"
          />
          <button 
            onClick={onClose}
            className="p-1 text-soc-muted hover:text-soc-text rounded-md hover:bg-soc-border/50"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2">
          <div className="px-3 py-1.5 text-[10px] font-mono uppercase text-soc-dim">
            {query.trim() === '' ? 'Quick Access & Recent Cases' : `Results (${results.length})`}
          </div>

          {results.length === 0 ? (
            <div className="p-8 text-center text-soc-muted text-sm font-mono">
              No matching intelligence records found for "{query}"
            </div>
          ) : (
            <div className="space-y-1">
              {results.map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSelect(item.route)}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-soc-panel cursor-pointer transition-colors border border-transparent hover:border-soc-border group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-md bg-soc-bg border border-soc-border text-soc-primary group-hover:text-white group-hover:border-soc-primary transition-colors">
                      {item.type === 'user' && <User className="w-4 h-4" />}
                      {item.type === 'account' && <CreditCard className="w-4 h-4" />}
                      {item.type === 'ip' && <Server className="w-4 h-4" />}
                      {item.type === 'device' && <Shield className="w-4 h-4" />}
                      {item.type === 'mule' && <Shield className="w-4 h-4 text-soc-danger" />}
                      {item.type === 'transaction' && <CreditCard className="w-4 h-4 text-soc-warning" />}
                    </div>
                    <div>
                      <div className="text-sm font-mono font-semibold text-soc-text group-hover:text-soc-primary">
                        {item.label}
                      </div>
                      <div className="text-xs text-soc-muted">
                        {item.sub}
                      </div>
                    </div>
                  </div>
                  <ArrowRight className="w-4 h-4 text-soc-dim group-hover:text-soc-primary group-hover:translate-x-1 transition-all" />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-2 bg-soc-panel/50 border-t border-soc-border text-[11px] text-soc-dim font-mono">
          <span>Navigate with <kbd className="px-1 py-0.5 bg-soc-bg border border-soc-border rounded">↑</kbd> <kbd className="px-1 py-0.5 bg-soc-bg border border-soc-border rounded">↓</kbd></span>
          <span>Open with <kbd className="px-1 py-0.5 bg-soc-bg border border-soc-border rounded">↵ Enter</kbd></span>
          <span>Close with <kbd className="px-1 py-0.5 bg-soc-bg border border-soc-border rounded">Esc</kbd></span>
        </div>
      </div>
    </div>
  );
}
