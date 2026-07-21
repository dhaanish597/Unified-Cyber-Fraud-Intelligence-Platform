import React, { useState } from 'react';
import { Upload, FileText, Check, ArrowRight, X, Sliders } from 'lucide-react';

export default function CSVSchemaMapperModal({ isOpen, onClose, onIngest }) {
  const [datasetType, setDatasetType] = useState('banking');
  const [fileName, setFileName] = useState('sample_bank_transactions.csv');
  const [mappings, setMappings] = useState({
    txn_amount: 'Amount',
    cust_id: 'Customer ID',
    beneficiary_acc: 'Beneficiary Account',
    ip_addr: 'IP Address',
    device_fingerprint: 'Device ID',
    timestamp: 'Event Timestamp'
  });

  if (!isOpen) return null;

  const datasetOptions = [
    { id: 'banking', label: 'Banking Transactions (PaySim / CBS)' },
    { id: 'siem', label: 'SIEM Events (Splunk / Elastic Logs)' },
    { id: 'combined', label: 'Combined Cyber-Fraud Dataset' },
    { id: 'fraud', label: 'Historical Fraud Ground Truth Dataset' },
    { id: 'upi', label: 'UPI Real-Time Transaction Log' },
    { id: 'custom', label: 'Custom Banking Schema Mapping' }
  ];

  const handleMappingChange = (csvCol, targetCol) => {
    setMappings(prev => ({ ...prev, [csvCol]: targetCol }));
  };

  const handleCompleteIngest = () => {
    if (onIngest) onIngest({ datasetType, fileName, mappings });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn font-mono">
      <div className="w-full max-w-2xl bg-soc-surface border border-soc-border rounded-xl shadow-2xl overflow-hidden flex flex-col select-none">
        
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-soc-border bg-soc-panel">
          <div className="flex items-center gap-2">
            <Upload className="w-4 h-4 text-soc-primary" />
            <h3 className="text-sm font-mono font-bold text-soc-text uppercase tracking-wider">
              CSV Dataset Ingestion & Dynamic Schema Mapper
            </h3>
          </div>
          <button onClick={onClose} className="text-soc-dim hover:text-soc-text p-1 rounded">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-4 space-y-4 max-h-[80vh] overflow-y-auto text-xs">
          
          {/* 1. Dataset Type Selector */}
          <div>
            <label className="text-[10px] text-soc-dim uppercase font-semibold block mb-1">
              1. Select Dataset Category & Schema Standard
            </label>
            <select
              value={datasetType}
              onChange={(e) => setDatasetType(e.target.value)}
              className="w-full bg-soc-bg border border-soc-border rounded p-2 text-xs font-mono text-soc-text focus:outline-none focus:border-soc-primary"
            >
              {datasetOptions.map(opt => (
                <option key={opt.id} value={opt.id}>{opt.label}</option>
              ))}
            </select>
          </div>

          {/* 2. File Drag & Drop Target */}
          <div className="border-2 border-dashed border-soc-border hover:border-soc-primary/50 bg-soc-bg rounded-lg p-6 text-center cursor-pointer transition-colors">
            <FileText className="w-8 h-8 text-soc-primary mx-auto mb-2" />
            <div className="font-bold text-soc-text">{fileName}</div>
            <div className="text-soc-muted text-[11px] mt-1">Drag and drop any banking CSV file here or click to browse</div>
          </div>

          {/* 3. Column Schema Mapper Matrix */}
          <div>
            <label className="text-[10px] text-soc-dim uppercase font-semibold block mb-2">
              2. Dynamic Column Schema Mapping Matrix
            </label>
            <div className="space-y-2 bg-soc-bg border border-soc-border p-3 rounded-lg">
              {Object.entries(mappings).map(([csvCol, targetCol], idx) => (
                <div key={idx} className="flex items-center justify-between gap-4 p-2 bg-soc-surface border border-soc-border rounded">
                  <span className="text-soc-primary font-bold w-1/3 truncate">{csvCol}</span>
                  <ArrowRight className="w-4 h-4 text-soc-dim shrink-0" />
                  <select
                    value={targetCol}
                    onChange={(e) => handleMappingChange(csvCol, e.target.value)}
                    className="w-1/2 bg-soc-panel border border-soc-border rounded px-2 py-1 text-xs font-mono text-soc-text focus:outline-none"
                  >
                    <option value="Amount">Map to: Amount (INR)</option>
                    <option value="Customer ID">Map to: Customer ID</option>
                    <option value="Beneficiary Account">Map to: Beneficiary Account</option>
                    <option value="IP Address">Map to: IP Address</option>
                    <option value="Device ID">Map to: Device ID</option>
                    <option value="Event Timestamp">Map to: Event Timestamp</option>
                  </select>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-4 py-3 bg-soc-panel border-t border-soc-border">
          <span className="text-[11px] text-soc-muted">Automatic normalization into Fusion Runtime</span>
          <button
            onClick={handleCompleteIngest}
            className="px-4 py-2 bg-soc-primary hover:bg-blue-600 text-white rounded font-mono font-bold text-xs flex items-center gap-2 shadow"
          >
            <Check className="w-4 h-4" />
            <span>Ingest into Pipeline</span>
          </button>
        </div>
      </div>
    </div>
  );
}
