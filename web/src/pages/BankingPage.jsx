import React from 'react';
import { Landmark, DollarSign, CreditCard } from 'lucide-react';
import Ledger from '../components/Ledger';

export default function BankingPage() {
  const sampleEvents = [
    { timestamp: "2026-07-16 10:00:40", txn_id: "txn_demo_999", type: "TRANSFER", amount: 750000.0, nameOrig: "ACC_ABC_123", nameDest: "ACC_MULE_NEW" },
    { timestamp: "2026-07-16 09:45:10", txn_id: "txn_demo_998", type: "CASH_OUT", amount: 12000.0, nameOrig: "ACC_XYZ_992", nameDest: "ACC_ATM_404" },
    { timestamp: "2026-07-16 09:30:00", txn_id: "txn_demo_997", type: "TRANSFER", amount: 450000.0, nameOrig: "ACC_404_112", nameDest: "ACC_BENEFICIARY_88" }
  ];

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Landmark className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              Core Banking System (CBS) Transaction Inspector
            </h1>
            <span className="text-xs text-soc-muted">Live transaction ledger & beneficiary mule cluster detection</span>
          </div>
        </div>
      </div>

      <div className="bg-soc-surface border border-soc-border rounded-xl p-4">
        <Ledger events={sampleEvents} />
      </div>
    </div>
  );
}
