import React, { useEffect } from 'react';
import { X } from 'lucide-react';

export default function Modal({ isOpen, onClose, title, children, maxWidth = 'max-w-2xl' }) {
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fadeIn">
      <div className={`w-full ${maxWidth} bg-soc-surface border border-soc-border rounded-xl shadow-2xl overflow-hidden flex flex-col`}>
        <div className="flex items-center justify-between px-4 py-3 border-b border-soc-border bg-soc-panel">
          <h3 className="text-sm font-mono font-bold text-soc-text uppercase tracking-wider">{title}</h3>
          <button onClick={onClose} className="text-soc-dim hover:text-soc-text p-1 rounded hover:bg-soc-border/50">
            <X className="w-4 h-4" />
          </button>
        </div>
        <div className="p-4 max-h-[80vh] overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
