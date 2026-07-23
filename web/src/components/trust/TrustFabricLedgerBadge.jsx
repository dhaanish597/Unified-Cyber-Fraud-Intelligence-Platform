import React from 'react';
import { ShieldCheck, Database, Lock } from 'lucide-react';

export default function TrustFabricLedgerBadge({ ledgerRecord }) {
  if (!ledgerRecord) return null;

  return (
    <div className="bg-soc-panel border border-soc-border rounded-xl p-3 flex flex-col gap-2 font-mono text-xs text-soc-text">
      <div className="flex items-center gap-2 border-b border-soc-border pb-2">
        <ShieldCheck className="w-4 h-4 text-emerald-400" />
        <span className="font-bold text-soc-muted uppercase tracking-wider">Trust Fabric Ledger</span>
      </div>
      <div className="flex flex-col gap-1">
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-soc-muted">Tx Hash:</span>
          <span className="font-bold text-soc-text">{ledgerRecord.tx_hash || 'N/A'}</span>
        </div>
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-soc-muted">Block:</span>
          <span className="font-bold text-soc-text">{ledgerRecord.block_number || 'N/A'}</span>
        </div>
        <div className="flex justify-between items-center text-[10px]">
          <span className="text-soc-muted">Status:</span>
          <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full font-bold">
            {ledgerRecord.status || 'VERIFIED'}
          </span>
        </div>
      </div>
    </div>
  );
}
