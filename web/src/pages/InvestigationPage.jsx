import React from 'react';
import { useParams } from 'react-router-dom';
import InvestigationWorkbench from '../components/investigation/InvestigationWorkbench';

export default function InvestigationPage() {
  const { caseId } = useParams();
  return <InvestigationWorkbench caseId={caseId || 'CASE-2026-8942'} />;
}
