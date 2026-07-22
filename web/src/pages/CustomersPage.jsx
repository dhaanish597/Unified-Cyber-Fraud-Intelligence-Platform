import React, { useState, useMemo } from 'react';
import { Users, Search, ArrowUpRight, ShieldAlert, X, Filter, RotateCcw, CheckCircle2, AlertTriangle, Shield, Smartphone, Globe, Landmark } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function CustomersPage() {
  const navigate = useNavigate();

  const [searchInput, setSearchInput] = useState('');
  const [activeQuery, setActiveQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedCustomer, setSelectedCustomer] = useState(null);

  const initialCustomers = [
    { 
      id: 'usr_abc', 
      name: 'Rajesh Kumar', 
      account: 'ACC_ABC_123', 
      risk: 'HIGH (Score 94)', 
      score: 94,
      status: 'COMPROMISED', 
      location: 'Mumbai, IN', 
      balance: '₹1,450,000.00',
      ip: '185.15.2.22',
      device: 'iPhone 15 Pro (dev_9999)',
      kyc: 'VERIFIED TIER-3',
      lastTxn: '10:00:40 IST',
      caseId: 'CASE-2026-8942'
    },
    { 
      id: 'usr_xyz', 
      name: 'Priya Sharma', 
      account: 'ACC_XYZ_992', 
      risk: 'HIGH (Score 82)', 
      score: 82,
      status: 'SUSPICIOUS', 
      location: 'Delhi, IN', 
      balance: '₹2,800,000.00',
      ip: '103.45.12.8',
      device: 'Samsung S24 (dev_8812)',
      kyc: 'VERIFIED TIER-3',
      lastTxn: '09:45:10 IST',
      caseId: 'CASE-2026-8941'
    },
    { 
      id: 'usr_404', 
      name: 'Amit Patel', 
      account: 'ACC_404_112', 
      risk: 'MEDIUM (Score 64)', 
      score: 64,
      status: 'CHALLENGED', 
      location: 'Ahmedabad, IN', 
      balance: '₹890,000.00',
      ip: '45.12.88.19',
      device: 'MacBook Air (dev_4041)',
      kyc: 'VERIFIED TIER-2',
      lastTxn: '08:20:15 IST',
      caseId: 'CASE-2026-8910'
    },
    { 
      id: 'usr_882', 
      name: 'Sunita Verma', 
      account: 'ACC_882_554', 
      risk: 'LOW (Score 28)', 
      score: 28,
      status: 'CLEAN', 
      location: 'Bangalore, IN', 
      balance: '₹4,200,000.00',
      ip: '49.207.18.9',
      device: 'iPad Air (dev_8820)',
      kyc: 'VERIFIED TIER-3',
      lastTxn: '07:10:00 IST',
      caseId: 'CASE-2026-8800'
    },
    { 
      id: 'usr_990', 
      name: 'Vikramaditya Rao', 
      account: 'ACC_990_331', 
      risk: 'HIGH (Score 91)', 
      score: 91,
      status: 'COMPROMISED', 
      location: 'Hyderabad, IN', 
      balance: '₹5,600,000.00',
      ip: '194.26.29.110',
      device: 'Windows PC (dev_botnet_88)',
      kyc: 'VERIFIED TIER-3',
      lastTxn: '06:40:22 IST',
      caseId: 'CASE-2026-8950'
    }
  ];

  const handleExecuteSearch = (e) => {
    if (e) e.preventDefault();
    setActiveQuery(searchInput.trim());
  };

  const handleClearSearch = () => {
    setSearchInput('');
    setActiveQuery('');
    setSelectedStatus('ALL');
  };

  const filteredCustomers = useMemo(() => {
    return initialCustomers.filter(c => {
      const matchesStatus = selectedStatus === 'ALL' || c.status === selectedStatus;
      const q = activeQuery.toLowerCase();
      const matchesQuery = q === '' ||
        c.id.toLowerCase().includes(q) ||
        c.name.toLowerCase().includes(q) ||
        c.account.toLowerCase().includes(q) ||
        c.location.toLowerCase().includes(q) ||
        c.status.toLowerCase().includes(q) ||
        c.risk.toLowerCase().includes(q);

      return matchesStatus && matchesQuery;
    });
  }, [activeQuery, selectedStatus]);

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none font-mono text-xs text-soc-text">
      
      {/* HEADER STRIP */}
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex flex-wrap items-center justify-between gap-4 shadow-lg">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-soc-primary/20 border border-soc-primary/40 rounded-xl">
            <Users className="w-6 h-6 text-soc-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
                Customer 360 Risk Index
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                SEARCH ACTIVE
              </span>
            </div>
            <span className="text-xs text-soc-muted">Unified Identity, Risk Grade Profiles, and Behavioral History</span>
          </div>
        </div>

        <div className="text-right">
          <div className="text-[10px] text-soc-muted uppercase">Indexed Profiles</div>
          <div className="text-sm font-bold text-soc-text">{filteredCustomers.length} / {initialCustomers.length} Customers</div>
        </div>
      </div>

      {/* SEARCH BAR & FILTERS SECTION */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg space-y-3">
        
        <form onSubmit={handleExecuteSearch} className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[280px]">
            <Search className="w-4 h-4 text-soc-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search by Customer ID (usr_abc), Name, Account (ACC_...), Location, or IP..."
              className="w-full bg-soc-bg border border-soc-border rounded-xl pl-9 pr-8 py-2 text-soc-text font-mono text-xs focus:outline-none focus:border-soc-primary transition-all"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => setSearchInput('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-soc-muted hover:text-soc-text"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* DEDICATED SEARCH BUTTON */}
          <button
            type="submit"
            className="px-4 py-2 bg-soc-primary hover:bg-blue-600 text-white font-mono font-bold rounded-xl flex items-center gap-2 transition-all shadow-md active:scale-95"
          >
            <Search className="w-4 h-4" />
            <span>Search Customers</span>
          </button>

          {/* CLEAR SEARCH BUTTON */}
          {(activeQuery || selectedStatus !== 'ALL' || searchInput) && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="px-3 py-2 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-muted hover:text-soc-text rounded-xl font-mono flex items-center gap-1.5 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Clear</span>
            </button>
          )}
        </form>

        {/* RISK STATUS FILTER PILLS & QUICK SEARCH CHIPS */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-soc-border/60 text-[11px]">
          
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-soc-muted font-bold mr-1 flex items-center gap-1">
              <Filter className="w-3 h-3 text-soc-primary" /> Filter:
            </span>
            {['ALL', 'COMPROMISED', 'SUSPICIOUS', 'CHALLENGED', 'CLEAN'].map((st) => (
              <button
                key={st}
                onClick={() => setSelectedStatus(st)}
                className={`px-2.5 py-1 rounded-lg border font-mono font-bold transition-all ${
                  selectedStatus === st
                    ? 'bg-soc-primary text-white border-soc-primary shadow-sm'
                    : 'bg-soc-panel border-soc-border text-soc-muted hover:text-soc-text'
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5 flex-wrap text-[10px]">
            <span className="text-soc-muted font-bold">Quick Chips:</span>
            {['usr_abc', 'COMPROMISED', 'Mumbai', 'Delhi'].map((chip) => (
              <button
                key={chip}
                onClick={() => {
                  setSearchInput(chip);
                  setActiveQuery(chip);
                }}
                className="px-2 py-0.5 bg-soc-bg hover:bg-soc-panel border border-soc-border text-soc-primary rounded font-mono"
              >
                +{chip}
              </button>
            ))}
          </div>

        </div>

      </div>

      {/* CUSTOMERS TABLE */}
      <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg">
        {filteredCustomers.length === 0 ? (
          <div className="py-12 text-center text-soc-dim space-y-2">
            <Search className="w-8 h-8 mx-auto text-soc-muted/40" />
            <p className="text-xs font-mono">No customer profiles match your search "{activeQuery}".</p>
            <button
              onClick={handleClearSearch}
              className="px-3 py-1.5 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-primary rounded-lg text-xs font-mono font-bold"
            >
              Reset Search & Filters
            </button>
          </div>
        ) : (
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
              {filteredCustomers.map((c) => (
                <tr key={c.id} className="hover:bg-soc-panel/60 transition-colors">
                  <td className="py-3 px-3 font-bold text-soc-primary">{c.id}</td>
                  <td className="py-3 px-3 text-soc-text font-semibold">{c.name}</td>
                  <td className="py-3 px-3 text-soc-muted">{c.account}</td>
                  <td className="py-3 px-3 font-bold text-soc-text">{c.balance}</td>
                  <td className="py-3 px-3 text-soc-dim">{c.location}</td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      c.status === 'COMPROMISED' ? 'bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30' :
                      c.status === 'SUSPICIOUS' ? 'bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30' :
                      'bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30'
                    }`}>
                      {c.risk}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setSelectedCustomer(c)}
                        className="px-2.5 py-1 bg-soc-panel hover:bg-soc-border border border-soc-border text-soc-text rounded text-xs font-mono"
                      >
                        Preview
                      </button>
                      <button
                        onClick={() => navigate(`/investigation/${c.caseId}`)}
                        className="px-2.5 py-1 bg-soc-primary hover:bg-blue-600 text-white font-bold rounded text-xs font-mono shadow"
                      >
                        View 360 →
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* CUSTOMER 360 PREVIEW DRAWER MODAL */}
      {selectedCustomer && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-soc-surface border border-soc-border rounded-xl max-w-xl w-full p-5 shadow-2xl font-mono text-xs select-none space-y-4">
            <div className="flex items-center justify-between border-b border-soc-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-soc-primary/20 border border-soc-primary/40 rounded-lg">
                  <Users className="w-5 h-5 text-soc-primary" />
                </div>
                <div>
                  <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider flex items-center gap-2">
                    <span>{selectedCustomer.name}</span>
                    <span className="text-[9px] px-2 py-0.5 rounded bg-soc-bg text-soc-primary font-bold border border-soc-border">
                      {selectedCustomer.id}
                    </span>
                  </h3>
                  <p className="text-[11px] text-soc-muted">Customer 360 Risk Profile Preview</p>
                </div>
              </div>
              <button 
                onClick={() => setSelectedCustomer(null)}
                className="p-1.5 bg-soc-panel hover:bg-soc-border text-soc-muted hover:text-soc-text rounded-lg"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 bg-soc-panel p-3.5 rounded-xl border border-soc-border">
              <div>
                <span className="text-soc-muted block text-[10px]">Primary Account</span>
                <strong className="text-soc-text">{selectedCustomer.account}</strong>
              </div>
              <div>
                <span className="text-soc-muted block text-[10px]">Total Balance</span>
                <strong className="text-emerald-400 font-bold">{selectedCustomer.balance}</strong>
              </div>
              <div>
                <span className="text-soc-muted block text-[10px]">Location</span>
                <strong className="text-soc-text">{selectedCustomer.location}</strong>
              </div>
              <div>
                <span className="text-soc-muted block text-[10px]">KYC Verification</span>
                <strong className="text-emerald-400 font-bold">{selectedCustomer.kyc}</strong>
              </div>
              <div>
                <span className="text-soc-muted block text-[10px]">Recent IP Address</span>
                <strong className="text-soc-text">{selectedCustomer.ip}</strong>
              </div>
              <div>
                <span className="text-soc-muted block text-[10px]">Device Fingerprint</span>
                <strong className="text-soc-text text-[11px] truncate block">{selectedCustomer.device}</strong>
              </div>
            </div>

            <div className="flex justify-between items-center pt-2 border-t border-soc-border">
              <span className="text-soc-muted">Risk Grade: <strong className="text-rose-400">{selectedCustomer.risk}</strong></span>
              <button
                onClick={() => {
                  const id = selectedCustomer.caseId;
                  setSelectedCustomer(null);
                  navigate(`/investigation/${id}`);
                }}
                className="px-4 py-2 bg-soc-primary hover:bg-blue-600 text-white font-bold rounded-lg text-xs font-mono shadow flex items-center gap-1.5"
              >
                <span>Launch Investigation Studio</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
