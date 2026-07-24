import React from 'react';
import PageContainer from '../components/layout/PageContainer';
import SessionIntelligenceDashboard from '../components/session/SessionIntelligenceDashboard';

export default function SessionIntelligencePage() {
  return (
    <PageContainer title="Enterprise Session Intelligence">
      <SessionIntelligenceDashboard />
    </PageContainer>
  );
}
