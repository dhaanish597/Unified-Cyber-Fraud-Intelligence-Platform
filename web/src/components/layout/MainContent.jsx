import React from 'react';

export default function MainContent({ children }) {
  return (
    <main className="flex-1 overflow-y-auto p-4 bg-soc-bg">
      {children}
    </main>
  );
}
