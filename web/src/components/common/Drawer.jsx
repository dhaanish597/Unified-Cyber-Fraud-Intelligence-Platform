import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Drawer({ isOpen, onClose, title, children, width = 'w-96' }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-fadeIn">
      <div className={`${width} h-full bg-soc-surface border-l border-soc-border shadow-2xl flex flex-col`}>
        <div className="flex items-center justify-between px-4 py-3.5 border-b border-soc-border bg-soc-panel">
          <h3 className="text-sm font-mono font-bold text-soc-text uppercase tracking-wider">{title}</h3>
          <button onClick={onClose} className="text-soc-dim hover:text-soc-text p-1 rounded hover:bg-soc-border/50">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="p-4 flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
