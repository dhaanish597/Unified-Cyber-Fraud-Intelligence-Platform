import React, { useState } from 'react';
import { Briefcase, Filter, Search, ArrowUpRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import EnterpriseBadge from '../components/common/EnterpriseBadge';

export default function CasesPage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('ALL');

  const cases = [
    { id: 'CASE-2026-8942', user: 'usr_abc', amount: '₹7,500,000.00', score: 94, action: 'BLOCK', reason: 'Impossible Travel + Mule Ring Target', status: 'CRITICAL IN REVIEW', assigned: 'Analyst_04' },
    { id: 'CASE-2026-8941', user: 'usr_xyz', amount: '₹1,200,000.00', score: 82, action: 'BLOCK', reason: 'New Device MFA Cookie Reuse', status: 'PENDING CERT-IN', assigned: 'Analyst_04' },
    { id: 'CASE-2026-8940', user: 'usr_404', amount: '₹450,000.00', score: 64, action: 'CHALLENGE', reason: 'High Velocity Transfer (3 txns/step)', status: 'STEP-UP SENT', assigned: 'Analyst_02' },
    { id: 'CASE-2026-8939', user: 'usr_882', amount: '₹85,000.00', score: 28, action: 'ALLOW', reason: 'Normal Baseline Parameters', status: 'CLOSED CLEAN', assigned: 'Unassigned' },
    { id: 'CASE-2026-8938', user: 'usr_991', amount: '₹3,400,000.00', score: 91, action: 'BLOCK', reason: 'Credential Stuffing + Zero-Day Anomaly', status: 'CRITICAL IN REVIEW', assigned: 'Analyst_01' }
  ];

  const filteredCases = filter === 'ALL' ? cases : cases.filter(c => c.action === filter);

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="flex items-center justify-between bg-soc-surface border border-soc-border p-4 rounded-xl">
        <div className="flex items-center gap-3">
          <Briefcase className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Enterprise Case Workqueue
            </h1>
            <span className="text-xs text-soc-muted">Triage and assign fraud investigation cases</span>
          </div>
        </div>

        {/* Action Filters */}
        <div className="flex items-center gap-2 bg-soc-bg border border-soc-border p-1 rounded-lg text-xs font-mono">
          {['ALL', 'BLOCK', 'CHALLENGE', 'ALLOW'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded transition-colors ${
                filter === f ? 'bg-soc-primary text-white font-bold' : 'text-soc-muted hover:text-soc-text'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {/* Case List */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4">
        <table className="w-full text-left font-mono text-xs">
          <thead>
            <tr className="border-b border-soc-border text-soc-dim uppercase text-[10px]">
              <th className="py-2.5 px-3">Case Reference</th>
              <th className="py-2.5 px-3">Customer ID</th>
              <th className="py-2.5 px-3">Amount at Risk</th>
              <th className="py-2.5 px-3">Decision Badge</th>
              <th className="py-2.5 px-3">Detection Rationale</th>
              <th className="py-2.5 px-3">Assigned Analyst</th>
              <th className="py-2.5 px-3 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-soc-border/50 text-soc-text">
            {filteredCases.map((c) => (
              <tr key={c.id} className="hover:bg-soc-panel/60 transition-colors">
                <td className="py-3 px-3 font-bold text-soc-primary">{c.id}</td>
                <td className="py-3 px-3 text-soc-muted">{c.user}</td>
                <td className="py-3 px-3 font-bold">{c.amount}</td>
                <td className="py-3 px-3">
                  <EnterpriseBadge action={c.action} score={c.score} size="sm" />
                </td>
                <td className="py-3 px-3 text-soc-muted">{c.reason}</td>
                <td className="py-3 px-3 text-soc-dim">{c.assigned}</td>
                <td className="py-3 px-3 text-right">
                  <button
                    onClick={() => navigate('/investigation/CASE-2026-8942')}
                    className="px-3 py-1 bg-soc-primary hover:bg-blue-600 text-white rounded text-xs font-mono font-bold transition-all shadow"
                  >
                    Open Studio →
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
