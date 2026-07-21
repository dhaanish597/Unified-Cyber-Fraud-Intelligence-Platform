import React, { useState } from 'react';

export default function Tooltip({ children, text }) {
  const [show, setShow] = useState(false);

  if (!text) return children;

  return (
    <div 
      className="relative inline-block" 
      onMouseEnter={() => setShow(true)} 
      onMouseLeave={() => setShow(false)}
    >
      {children}
      {show && (
        <div className="absolute z-50 bottom-full mb-1.5 left-1/2 -translate-x-1/2 px-2.5 py-1 bg-soc-surface border border-soc-border text-soc-text text-[11px] font-mono rounded shadow-xl whitespace-nowrap pointer-events-none">
          {text}
        </div>
      )}
    </div>
  );
}
