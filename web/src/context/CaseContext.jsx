import React, { createContext, useContext, useState } from 'react';

const CaseContext = createContext({
  activeCaseId: 'CASE-2026-8942',
  caseDetails: null,
  selectCase: () => {},
  updateCaseStatus: () => {}
});

export function CaseProvider({ children }) {
  const [activeCaseId, setActiveCaseId] = useState('CASE-2026-8942');
  const [caseDetails, setCaseDetails] = useState({
    id: 'CASE-2026-8942',
    user_id: 'usr_abc',
    account: 'ACC_ABC_123',
    score: 94,
    action: 'BLOCK',
    status: 'IN_REVIEW',
    assignedAnalyst: 'Analyst_04',
    createdTime: '10:00:40 IST'
  });

  const selectCase = (caseId) => {
    setActiveCaseId(caseId);
    setCaseDetails(prev => ({ ...prev, id: caseId }));
  };

  const updateCaseStatus = (newStatus) => {
    setCaseDetails(prev => (prev ? { ...prev, status: newStatus } : null));
  };

  return (
    <CaseContext.Provider value={{ activeCaseId, caseDetails, selectCase, updateCaseStatus }}>
      {children}
    </CaseContext.Provider>
  );
}

export function useCase() {
  return useContext(CaseContext);
}
