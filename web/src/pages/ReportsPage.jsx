import React from 'react';
import { FileCheck2, Download, ShieldAlert, FileText, CheckCircle2 } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8001';

export default function ReportsPage() {
  const handleDownload = async () => {
    try {
      const res = await fetch(`${API_BASE}/report/cert-in`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          txn_id: 'txn_demo_999',
          user_id: 'usr_abc',
          amount: 750000.0,
          reasons: [
            "High baseline fraud probability (Tabular Score: 0.82)",
            "Recent cyber compromise detected (Login from unusual IP prior to transfer)",
            "Beneficiary is part of a known mule cluster (cluster_alpha)"
          ],
          score: 94.0
        })
      });
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `CERT-In_Incident_Report_txn_demo_999.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error("Download failed:", e);
    }
  };

  return (
    <div className="flex flex-col gap-5 max-w-[1600px] mx-auto select-none">
      <div className="bg-soc-surface border border-soc-border p-4 rounded-xl flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileCheck2 className="w-6 h-6 text-soc-primary" />
          <div>
            <h1 className="text-base font-mono font-bold text-soc-text uppercase tracking-wider">
              CERT-In Regulatory Incident Reports
            </h1>
            <span className="text-xs text-soc-muted">Automated PDF generation for 6-Hour India CERT-In Mandate Compliance</span>
          </div>
        </div>

        <button
          onClick={handleDownload}
          className="px-4 py-2 bg-soc-primary hover:bg-blue-600 text-white rounded-lg text-xs font-mono font-bold flex items-center gap-2 transition-colors shadow"
        >
          <Download className="w-4 h-4" />
          <span>Export Sample CERT-In PDF</span>
        </button>
      </div>

      <div className="bg-soc-surface border border-soc-border rounded-xl p-4">
        <h3 className="text-xs font-mono font-bold text-soc-text uppercase tracking-wider border-b border-soc-border pb-2 mb-3">
          Recent Incident Filings Queue
        </h3>

        <div className="space-y-2 font-mono text-xs">
          <div className="p-3 bg-soc-bg border border-soc-border rounded-lg flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-rose-400" />
              <div>
                <div className="font-bold text-soc-text">CERT-In_Report_txn_demo_999.pdf</div>
                <div className="text-soc-muted text-[11px]">User: usr_abc | Amount: INR 750,000.00 | Score: 94</div>
              </div>
            </div>
            <button onClick={handleDownload} className="px-3 py-1 bg-soc-panel border border-soc-border hover:border-soc-primary text-soc-text rounded text-xs">
              Download PDF
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
