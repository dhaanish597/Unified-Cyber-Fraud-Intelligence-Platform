import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';
import { ThemeProvider } from './context/ThemeContext';
import { SidebarProvider } from './context/SidebarContext';
import { SearchProvider } from './context/SearchContext';
import { NotificationProvider } from './context/NotificationContext';
import { CustomerProvider } from './context/CustomerContext';
import { CaseProvider } from './context/CaseContext';
import { ReplayProvider } from './context/ReplayContext';

const ThreatDashboard = lazy(() => import('./pages/CyberThreatIntelligencePage'));
const GraphPage = lazy(() => import('./pages/GraphPage'));
const DeveloperPlatformPage = lazy(() => import('./pages/DeveloperPlatformPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

function Loading() {
  return <div className="p-6 text-soc-muted">Loading platform view…</div>;
}

export default function App() {
  return (
    <ThemeProvider>
      <SidebarProvider>
        <CaseProvider>
          <CustomerProvider>
            <NotificationProvider>
              <ReplayProvider>
                <SearchProvider>
                  <BrowserRouter>
                    <Suspense fallback={<Loading />}>
                      <Routes>
                        <Route path="/" element={<AppLayout quantumData={null} />}>
                          <Route index element={<Navigate to="/threats" replace />} />
                          <Route path="dashboard" element={<Navigate to="/threats" replace />} />
                          <Route path="threats" element={<ThreatDashboard />} />
                          <Route path="graph" element={<GraphPage />} />
                          <Route path="developer" element={<DeveloperPlatformPage />} />
                          <Route path="settings" element={<SettingsPage />} />
                          <Route path="*" element={<Navigate to="/threats" replace />} />
                        </Route>
                      </Routes>
                    </Suspense>
                  </BrowserRouter>
                </SearchProvider>
              </ReplayProvider>
            </NotificationProvider>
          </CustomerProvider>
        </CaseProvider>
      </SidebarProvider>
    </ThemeProvider>
  );
}
