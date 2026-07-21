import React from 'react';
import { User, Shield, MapPin, DollarSign, Clock, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function DigitalTwinBaseline({ userId = 'usr_abc' }) {
  const twinProfile = {
    userId: 'usr_abc',
    trustedDevices: ['dev_1102 (iPhone 15)', 'dev_1103 (MacBook Pro)'],
    trustedLocation: 'Mumbai, Maharashtra, IN (Home Geo)',
    normalAmountRange: 'INR 500.00 – INR 50,000.00',
    typicalCadence: 'Weekday 09:00 – 21:00 IST',
    loginBaseline: 'Chrome Desktop / Jio Fiber IP 103.45.xx.xx'
  };

  return (
    <div className="bg-soc-surface border border-soc-border rounded-xl p-4 shadow-lg select-none font-mono text-xs">
      <div className="flex items-center justify-between border-b border-soc-border pb-3 mb-3">
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-soc-primary" />
          <div>
            <h3 className="font-bold text-soc-text text-xs uppercase tracking-wider">
              Digital Twin Customer Behavioral Baseline — {userId}
            </h3>
            <span className="text-[10px] text-soc-muted">
              Historical behavioral profile learned over observation period
            </span>
          </div>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded bg-soc-primary/10 text-soc-primary border border-soc-primary/30">
          DIGITAL TWIN ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
          <span className="text-[10px] text-soc-dim uppercase font-semibold flex items-center gap-1">
            <Shield className="w-3 h-3 text-soc-primary" />
            <span>Trusted Registered Devices</span>
          </span>
          <div className="text-soc-text font-bold">{twinProfile.trustedDevices.join(', ')}</div>
        </div>

        <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
          <span className="text-[10px] text-soc-dim uppercase font-semibold flex items-center gap-1">
            <MapPin className="w-3 h-3 text-emerald-400" />
            <span>Trusted Home Geolocation</span>
          </span>
          <div className="text-soc-text font-bold">{twinProfile.trustedLocation}</div>
        </div>

        <div className="p-3 bg-soc-panel border border-soc-border rounded-lg space-y-1">
          <span className="text-[10px] text-soc-dim uppercase font-semibold flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-amber-400" />
            <span>Normal Transaction Amount Range</span>
          </span>
          <div className="text-soc-text font-bold">{twinProfile.normalAmountRange}</div>
        </div>
      </div>
    </div>
  );
}
