import React from 'react';
import { Radio, Server, ShieldAlert, Cpu } from 'lucide-react';
import Timeline from '../components/Timeline';

export default function TelemetryPage() {
  const sampleEvents = [
    { timestamp: "2026-07-16 10:00:00", event_type: "impossible_travel_login", user_id: "usr_abc", ip: "185.15.2.22", severity: "critical", km_from_baseline: 4500 },
    { timestamp: "2026-07-16 09:58:12", event_type: "new_device_mfa_cookie_reuse", user_id: "usr_xyz", ip: "103.45.12.8", severity: "medium", km_from_baseline: 12 },
    { timestamp: "2026-07-16 09:55:04", event_type: "credential_stuffing_success", user_id: "usr_404", ip: "45.12.88.19", severity: "critical", km_from_baseline: 890 }
  ];

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Radio className="w-6 h-6 text-soc-primary animate-pulse" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              SIEM Cyber Telemetry Stream
            </h1>
            <span className="text-xs text-soc-muted">Real-time network login anomalies and compromise signals</span>
          </div>
        </div>
      </div>

      <div className="bg-soc-surface border border-soc-border rounded-xl p-4">
        <Timeline events={sampleEvents} />
      </div>
    </div>
  );
}
