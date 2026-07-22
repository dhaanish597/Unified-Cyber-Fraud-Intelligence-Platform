import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  ShieldAlert, 
  Briefcase, 
  Users, 
  Radio, 
  Landmark, 
  Share2, 
  FlaskConical, 
  FileCheck2, 
  Sliders,
  ChevronLeft,
  ChevronRight,
  Activity,
  BarChart3
} from 'lucide-react';
import { useSidebar } from '../../context/SidebarContext';
import Tooltip from '../common/Tooltip';

export default function Sidebar() {
  const { isCollapsed, toggleSidebar } = useSidebar();

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, shortcut: '⌥1' },
    { to: '/operations', label: 'Operations Center', icon: Activity, badge: 'LIVE' },
    { to: '/analytics', label: 'Cyber Analytics', icon: BarChart3, badge: 'NEW' },
    { to: '/cases', label: 'Cases Workqueue', icon: Briefcase, badge: '12' },
    { to: '/investigation/CASE-2026-8942', label: 'Investigation Studio', icon: ShieldAlert, highlight: true, shortcut: '⌥3' },
    { to: '/customers', label: 'Customer 360', icon: Users },
    { to: '/telemetry', label: 'Cyber Telemetry', icon: Radio },
    { to: '/banking', label: 'Core Banking', icon: Landmark },
    { to: '/graph', label: 'Threat Graph', icon: Share2 },
    { to: '/lab', label: 'Synthetic Data Lab', icon: FlaskConical },
    { to: '/reports', label: 'CERT-In Reports', icon: FileCheck2 },
    { to: '/settings', label: 'Policy Settings', icon: Sliders },
  ];

  return (
    <aside 
      className={`${
        isCollapsed ? 'w-16' : 'w-56'
      } bg-soc-surface border-r border-soc-border flex flex-col justify-between p-2 shrink-0 select-none transition-all duration-300 z-20`}
    >
      <div className="space-y-1">
        {/* Collapse toggle button header */}
        <div className="flex items-center justify-between px-2 py-1.5 border-b border-soc-border mb-2">
          {!isCollapsed && (
            <span className="text-[10px] font-mono uppercase text-soc-dim tracking-wider font-semibold">
              Navigation
            </span>
          )}
          <button
            onClick={toggleSidebar}
            className="p-1 rounded hover:bg-soc-panel text-soc-muted hover:text-soc-text transition-colors mx-auto"
            title={isCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const content = (
            <NavLink
              to={item.to}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2 rounded-lg text-xs font-mono transition-colors ${
                  isActive
                    ? 'bg-soc-primary text-white font-bold shadow-md shadow-blue-950/50'
                    : item.highlight
                    ? 'bg-soc-panel text-soc-primary border border-soc-primary/30 hover:bg-soc-primary/10'
                    : 'text-soc-muted hover:text-soc-text hover:bg-soc-panel'
                }`
              }
            >
              <div className="flex items-center gap-2.5">
                <Icon className="w-4 h-4 shrink-0" />
                {!isCollapsed && <span className="truncate">{item.label}</span>}
              </div>

              {!isCollapsed && item.badge && (
                <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-rose-500/20 text-rose-400 font-bold border border-rose-500/30">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );

          return isCollapsed ? (
            <Tooltip key={item.to} text={`${item.label} (${item.shortcut || ''})`}>
              {content}
            </Tooltip>
          ) : (
            <React.Fragment key={item.to}>{content}</React.Fragment>
          );
        })}
      </div>

      {/* Footer System SLA Indicator */}
      {!isCollapsed && (
        <div className="p-2.5 bg-soc-bg border border-soc-border rounded-lg text-[11px] font-mono space-y-1">
          <div className="flex justify-between text-soc-muted">
            <span>SLA Latency:</span>
            <span className="text-emerald-400 font-bold">48ms</span>
          </div>
          <div className="flex justify-between text-soc-muted">
            <span>FPR Budget:</span>
            <span className="text-soc-text font-bold">0.48% / 0.5%</span>
          </div>
        </div>
      )}
    </aside>
  );
}
