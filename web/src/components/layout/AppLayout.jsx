import React from 'react';
import { Outlet } from 'react-router-dom';
import TopBar from './TopBar';
import Sidebar from './Sidebar';
import MainContent from './MainContent';
import StatusBar from './StatusBar';
import UniversalSearch from '../common/UniversalSearch';
import { useSearch } from '../../context/SearchContext';

function InnerAppLayout({ quantumData }) {
  const { isSearchOpen, closeSearch } = useSearch();

  return (
    <div className="flex flex-col h-screen w-screen bg-soc-bg text-soc-text overflow-hidden font-sans">
      {/* Top Header Navigation */}
      <TopBar quantumData={quantumData} />

      {/* Main Body Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Collapsible Sidebar */}
        <Sidebar />

        {/* Dynamic Route Content */}
        <MainContent>
          <Outlet />
        </MainContent>
      </div>

      {/* Footer Status Bar */}
      <StatusBar />

      {/* Global Command Search Overlay Modal */}
      <UniversalSearch isOpen={isSearchOpen} onClose={closeSearch} />
    </div>
  );
}

export default function AppLayout({ quantumData }) {
  return <InnerAppLayout quantumData={quantumData} />;
}
