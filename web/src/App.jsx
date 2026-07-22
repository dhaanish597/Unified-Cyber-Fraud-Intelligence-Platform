import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { ThemeProvider } from './context/ThemeContext';
import { SidebarProvider } from './context/SidebarContext';
import { CaseProvider } from './context/CaseContext';
import { CustomerProvider } from './context/CustomerContext';
import { NotificationProvider } from './context/NotificationContext';
import { ReplayProvider } from './context/ReplayContext';
import { SearchProvider } from './context/SearchContext';

import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import OperationsCenterPage from './pages/OperationsCenterPage';
import CasesPage from './pages/CasesPage';
import InvestigationPage from './pages/InvestigationPage';
import CustomersPage from './pages/CustomersPage';
import TelemetryPage from './pages/TelemetryPage';
import BankingPage from './pages/BankingPage';
import GraphPage from './pages/GraphPage';
import SyntheticLabPage from './pages/SyntheticLabPage';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import DeveloperPlatformPage from './pages/DeveloperPlatformPage';


const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function App() {
  const [quantumData, setQuantumData] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE}/quantum/posture`)
      .then(r => r.json())
      .then(data => setQuantumData(data))
      .catch(e => console.error("Quantum fetch error:", e));
  }, []);

  return (
    <ThemeProvider>
      <SidebarProvider>
        <CaseProvider>
          <CustomerProvider>
            <NotificationProvider>
              <ReplayProvider>
                <SearchProvider>
                  <BrowserRouter>
                    <Routes>
                      <Route path="/" element={<AppLayout quantumData={quantumData} />}>
                        <Route index element={<Navigate to="/dashboard" replace />} />
                        <Route path="dashboard" element={<DashboardPage />} />
                        <Route path="operations" element={<OperationsCenterPage />} />
                        <Route path="cases" element={<CasesPage />} />
                        <Route path="investigation/:caseId" element={<InvestigationPage />} />
                        <Route path="customers" element={<CustomersPage />} />
                        <Route path="telemetry" element={<TelemetryPage />} />
                        <Route path="analytics" element={<AnalyticsPage />} />
                        <Route path="banking" element={<BankingPage />} />
                        <Route path="graph" element={<GraphPage />} />
                        <Route path="lab" element={<SyntheticLabPage />} />
                        <Route path="reports" element={<ReportsPage />} />
                        <Route path="settings" element={<SettingsPage />} />
                        <Route path="developer" element={<DeveloperPlatformPage />} />
                        <Route path="*" element={<Navigate to="/dashboard" replace />} />
                      </Route>
                    </Routes>
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
