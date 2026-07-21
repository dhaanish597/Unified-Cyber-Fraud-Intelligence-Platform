import React, { useState, useEffect } from 'react';
import { Search, ShieldAlert, Cpu, Bell, Sun, Moon, CheckCircle2 } from 'lucide-react';
import { useSearch } from '../../context/SearchContext';
import { useTheme } from '../../context/ThemeContext';
import { useNotifications } from '../../context/NotificationContext';

export default function TopBar({ quantumData }) {
  const { openSearch } = useSearch();
  const { theme, toggleTheme } = useTheme();
  const { unreadCount } = useNotifications();
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-14 bg-soc-surface border-b border-soc-border px-4 flex items-center justify-between z-30 shrink-0 select-none">
      {/* Brand Logo & Platform Header */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-soc-primary/20 border border-soc-primary/40 flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-soc-primary animate-pulse" />
          </div>
          <div className="flex flex-col">
            <span className="font-mono font-black text-sm text-soc-text tracking-wider flex items-center gap-1.5">
              FUSION RISK OS
              <span className="text-[9px] font-mono px-1.5 py-0.2 bg-soc-primary/20 text-soc-primary rounded border border-soc-primary/30">
                ENTERPRISE SOC v2.6
              </span>
            </span>
            <span className="text-[10px] font-mono text-soc-dim">Unified Cyber-Fraud Intelligence Platform</span>
          </div>
        </div>

        <div className="h-5 w-px bg-soc-border hidden md:block" />

        {/* Live System Health */}
        <div className="hidden lg:flex items-center gap-2 text-xs font-mono text-soc-muted">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
          <span>FASTAPI RISK ENGINE ONLINE</span>
        </div>
      </div>

      {/* Global Command Search Bar Trigger */}
      <div className="flex-1 max-w-md mx-6">
        <button
          onClick={openSearch}
          className="w-full h-9 bg-soc-bg border border-soc-border hover:border-soc-primary/50 rounded-lg px-3 flex items-center justify-between text-xs font-mono text-soc-dim hover:text-soc-muted transition-colors shadow-inner"
        >
          <div className="flex items-center gap-2">
            <Search className="w-3.5 h-3.5 text-soc-muted" />
            <span>Global Search (Customer, Account, IP, Device, Case ID)...</span>
          </div>
          <kbd className="px-1.5 py-0.5 bg-soc-panel border border-soc-border rounded text-[10px] text-soc-muted font-mono">
            ⌘K
          </kbd>
        </button>
      </div>

      {/* Right Tool Actions & Analyst Profile */}
      <div className="flex items-center gap-3">
        {/* Post-Quantum TLS Posture Shield */}
        {quantumData && (
          <div 
            className="hidden sm:flex items-center gap-2 px-2.5 py-1 bg-purple-500/10 border border-purple-500/30 rounded-md text-xs font-mono text-purple-300"
            title={quantumData.hndl_details}
          >
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <span>PQC Shield: {quantumData.vulnerable_percent}% Vulnerable</span>
          </div>
        )}

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          className="p-1.5 rounded-lg bg-soc-bg border border-soc-border hover:border-soc-primary text-soc-muted hover:text-soc-text transition-colors"
          title="Toggle Light/Dark Theme"
        >
          {theme === 'dark' ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-soc-primary" />}
        </button>

        {/* Notifications Bell Button */}
        <div className="relative">
          <button className="p-1.5 rounded-lg bg-soc-bg border border-soc-border hover:border-soc-primary text-soc-muted hover:text-soc-text transition-colors">
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-rose-500 text-white rounded-full text-[9px] font-mono font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>
        </div>

        {/* Analyst Profile */}
        <div className="flex items-center gap-2 pl-2 border-l border-soc-border">
          <div className="w-7 h-7 rounded-full bg-soc-primary/20 border border-soc-primary/40 flex items-center justify-center text-soc-primary font-mono text-xs font-bold">
            A4
          </div>
          <div className="hidden xl:flex flex-col text-left">
            <span className="text-xs font-mono font-bold text-soc-text">Analyst_04</span>
            <span className="text-[9px] font-mono text-soc-dim">Tier-3 SOC Specialist</span>
          </div>
        </div>
      </div>
    </header>
  );
}
