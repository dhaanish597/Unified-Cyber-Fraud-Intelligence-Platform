import React from 'react';
import PageContainer from '../components/layout/PageContainer';
import ThreatIntelligenceDashboard from '../components/threat/ThreatIntelligenceDashboard';

export default function CyberThreatIntelligencePage() {
  return (
    <PageContainer title="Cyber Threat Intelligence Engine">
      <ThreatIntelligenceDashboard />
    </PageContainer>
  );
}
