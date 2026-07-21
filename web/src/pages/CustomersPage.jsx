import React from 'react';
import { Users, Search, ArrowUpRight, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function CustomersPage() {
  const navigate = useNavigate();

  const customers = [
    { id: 'usr_abc', name: 'Rajesh Kumar', account: 'ACC_ABC_123', risk: 'HIGH (Score 94)', status: 'COMPROMISED', location: 'Mumbai, IN', balance: '₹1,450,000.00' },
    { id: 'usr_xyz', name: 'Priya Sharma', account: 'ACC_XYZ_992', risk: 'HIGH (Score 82)', status: 'SUSPICIOUS', location: 'Delhi, IN', balance: '₹2,800,000.00' },
    { id: 'usr_404', name: 'Amit Patel', account: 'ACC_404_112', risk: 'MEDIUM (Score 64)', status: 'CHALLENGED', location: 'Ahmedabad, IN', balance: '₹890,000.00' },
    { id: 'usr_882', name: 'Sunita Verma', account: 'ACC_882_554', risk: 'LOW (Score 28)', status: 'CLEAN', location: 'Bangalore, IN', balance: '₹4,200,000.00' }
  ];

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Customer 360 Risk Index
            </h1>
            <span className="text-xs text-soc-muted">Unified Identity & Risk Grade Profiles</span>
          </div>
        </div>
      </div>

      <div className="bg-soc-surface border border-soc-border rounded-xl p-4">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-soc-border text-soc-dim uppercase text-[10px]">
              <th className="py-2.5 px-3">Customer ID</th>
              <th className="py-2.5 px-3">Name</th>
              <th className="py-2.5 px-3">Primary Account</th>
              <th className="py-2.5 px-3">Account Balance</th>
              <th className="py-2.5 px-3">Location</th>
              <th className="py-2.5 px-3">Risk Grade</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-soc-border/50 text-soc-text">
            {customers.map((c) => (
              <tr key={c.id} className="hover:bg-soc-panel/60 transition-colors">
                <td className="py-3 px-3 font-bold text-soc-primary">{c.id}</td>
                <td className="py-3 px-3 text-soc-text font-semibold">{c.name}</td>
                <td className="py-3 px-3 text-soc-muted">{c.account}</td>
                <td className="py-3 px-3 font-bold">{c.balance}</td>
                <td className="py-3 px-3 text-soc-dim">{c.location}</td>
                <td className="py-3 px-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] ${
                    c.status === 'COMPROMISED' ? 'bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30' : 'bg-soc-bg text-soc-muted'
                  }`}>
                    {c.risk}
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <button
                    onClick={() => navigate('/investigation/CASE-2026-8942')}
                    className="px-2.5 py-1 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded text-xs font-mono"
                  >
                    View 360 →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
