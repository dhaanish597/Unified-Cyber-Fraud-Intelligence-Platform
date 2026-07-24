import React from 'react';
import { NavLink } from 'react-router-dom';
import { Code2, Menu, Settings, Share2, ShieldAlert } from 'lucide-react';
import { useSidebar } from '../../context/SidebarContext';

const items = [
  { to: '/threats', label: 'Threat Intelligence', icon: ShieldAlert },
  { to: '/graph', label: 'Graph Runtime', icon: Share2 },
  { to: '/developer', label: 'SDK Runtime', icon: Code2 },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const { isCollapsed, toggleSidebar } = useSidebar();
  return (
    <aside className={`${isCollapsed ? 'w-16' : 'w-60'} bg-soc-surface border-r border-soc-border p-3 shrink-0 transition-all`}>
      <button
        onClick={toggleSidebar}
        className="w-full flex items-center gap-2 p-2 mb-4 text-soc-muted hover:text-soc-text"
      >
        <Menu className="w-4 h-4" />
        {!isCollapsed && <span className="font-mono text-xs">Fusion Risk OS</span>}
      </button>
      <nav className="space-y-1">
        {items.map(item => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              title={item.label}
              className={({ isActive }) => `flex items-center gap-3 p-2 rounded-lg text-xs font-mono ${
                isActive ? 'bg-soc-primary text-white' : 'text-soc-muted hover:bg-soc-panel'
              }`}
            >
              <Icon className="w-4 h-4 shrink-0" />
              {!isCollapsed && item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
