import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, ShieldAlert, Briefcase, Users, Radio, Landmark, Share2, FlaskConical, FileCheck2, Sliders, ChevronLeft, ChevronRight, Activity, BarChart3, ChevronDown, Code2, ShieldCheck } from 'lucide-react';
import { useSidebar } from '../../context/SidebarContext';
import Tooltip from '../common/Tooltip';

export default function Sidebar() {
  const { isCollapsed, toggleSidebar } = useSidebar();
  const [openCategories, setOpenCategories] = useState({
    pre_tx: true,
    intel: true,
    infra: true,
    sdk: true
  });

  const toggleCategory = (cat) => {
    setOpenCategories(prev => ({ ...prev, [cat]: !prev[cat] }));
  };

  const navCategories = [
    {
      id: 'pre_tx',
      title: 'Pre-Transaction Security',
      items: [
        { to: '/dashboard', label: 'Mission Overview', icon: LayoutDashboard },
        { to: '/operations', label: 'Operations Center', icon: Activity, badge: 'LIVE' },
        { to: '/investigation/CASE-2026-8942', label: 'Investigation Studio', icon: ShieldAlert, highlight: true }
      ]
    },
    {
      id: 'intel',
      title: 'Fraud Intelligence',
      items: [
        { to: '/threats', label: 'Threat Intelligence', icon: ShieldAlert, badge: 'NEW', highlight: true },
        { to: '/sessions', label: 'Session Intelligence', icon: ShieldCheck, badge: 'LIVE', highlight: true },
        { to: '/analytics', label: 'Cyber Analytics', icon: BarChart3 },
        { to: '/cases', label: 'Cases Workqueue', icon: Briefcase, badge: '12' },
        { to: '/customers', label: 'Customer Digital Twin', icon: Users }
      ]
    },
    {
      id: 'infra',
      title: 'Infrastructure & Tools',
      items: [
        { to: '/telemetry', label: 'Cyber Telemetry', icon: Radio },
        { to: '/banking', label: 'Core Banking Universe', icon: Landmark },
        { to: '/graph', label: 'Neo4j Threat Graph', icon: Share2 },
        { to: '/lab', label: 'Synthetic Data Lab', icon: FlaskConical },
        { to: '/reports', label: 'CERT-In Incident Reports', icon: FileCheck2 },
        { to: '/settings', label: 'Policy & Guardrails', icon: Sliders }
      ]
    },
    {
      id: 'sdk',
      title: 'Developer Platform',
      items: [
        { to: '/developer', label: 'FAT-SDK Platform', icon: Code2, badge: 'NEW', highlight: true }
      ]
    }
  ];

  return (
    <aside 
      className={`${
        isCollapsed ? 'w-16' : 'w-60'
      } bg-soc-surface border-r border-soc-border flex flex-col justify-between p-2.5 shrink-0 select-none transition-all duration-300 z-20 font-mono text-xs`}
    >
      <div className="space-y-3">
        {/* Collapse toggle header */}
        <div className="flex items-center justify-between px-2 py-1.5 border-b border-soc-border pb-2">
          {!isCollapsed && (
            <span className="text-[10px] uppercase text-soc-dim tracking-wider font-bold">
              Navigation Menu
            </span>
          )}
          <button
            onClick={toggleSidebar}
            className="p-1 rounded bg-soc-bg hover:bg-soc-panel border border-soc-border text-soc-muted hover:text-soc-text transition-colors mx-auto"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Grouped Category Navigation */}
        <div className="space-y-3 overflow-y-auto max-h-[calc(100vh-140px)] pr-0.5">
          {navCategories.map((cat) => {
            const isCatOpen = openCategories[cat.id];
            return (
              <div key={cat.id} className="space-y-1">
                {!isCollapsed && (
                  <button
                    onClick={() => toggleCategory(cat.id)}
                    className="w-full px-2 py-1 flex items-center justify-between text-[10px] font-bold text-soc-dim uppercase tracking-wider hover:text-soc-text transition-colors text-left"
                  >
                    <span>{cat.title}</span>
                    {isCatOpen ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                  </button>
                )}

                {(isCollapsed || isCatOpen) && (
                  <div className="space-y-1">
                    {cat.items.map((item) => {
                      const Icon = item.icon;
                      const content = (
                        <NavLink
                          to={item.to}
                          className={({ isActive }) =>
                            `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-mono transition-all ${
                              isActive
                                ? 'bg-soc-primary text-white font-bold shadow-md shadow-blue-950/40'
                                : item.highlight
                                ? 'bg-soc-panel text-soc-primary border border-soc-primary/40 hover:bg-soc-primary/10'
                                : 'text-soc-muted hover:text-soc-text hover:bg-soc-panel/80'
                            }`
                          }
                        >
                          <div className="flex items-center gap-2.5 truncate">
                            <Icon className="w-4 h-4 shrink-0" />
                            {!isCollapsed && <span className="truncate">{item.label}</span>}
                          </div>

                          {!isCollapsed && item.badge && (
                            <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-rose-500/20 text-rose-300 font-bold border border-rose-500/30">
                              {item.badge}
                            </span>
                          )}
                        </NavLink>
                      );

                      return isCollapsed ? (
                        <Tooltip key={item.to} text={item.label}>
                          {content}
                        </Tooltip>
                      ) : (
                        <React.Fragment key={item.to}>{content}</React.Fragment>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Footer System Status */}
      {!isCollapsed && (
        <div className="p-2.5 bg-soc-bg border border-soc-border rounded-lg text-[11px] font-mono space-y-1">
          <div className="flex justify-between text-soc-muted">
            <span>Pre-Tx Pipeline:</span>
            <span className="text-emerald-400 font-bold">0.14 ms</span>
          </div>
          <div className="flex justify-between text-soc-muted">
            <span>Decision Quality:</span>
            <span className="text-soc-text font-bold">96.5% HIGH</span>
          </div>
        </div>
      )}
    </aside>
  );
}

