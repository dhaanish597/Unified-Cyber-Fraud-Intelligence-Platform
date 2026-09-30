import React, { useState, useEffect, useRef, useMemo, lazy } from 'react';
import { API_BASE, authenticatedWebSocketUrl, authenticatedWebSocketProtocols } from '../platformAuth';
import { useNavigate } from 'react-router-dom';
import {
  Bot, BookOpen, ExternalLink, Fingerprint, Landmark, Radio, RefreshCw, Search, ShieldAlert,
  Terminal, Upload,
} from 'lucide-react';

import CSVSchemaMapperModal from '../components/runtime/CSVSchemaMapperModal';
import FusionLifecyclePipeline from '../components/runtime/FusionLifecyclePipeline';
import VerdictHero from '../components/common/VerdictHero';
import CollapsibleSection from '../components/common/CollapsibleSection';
import EmptyState from '../components/common/EmptyState';
import PanelState from '../components/common/PanelState';
import useResource from '../lib/useResource';
import { formatAmount, formatTimestamp, normalizeVerdict, severityChip } from '../lib/verdict';

// Secondary panels are lazy so a collapsed section costs no JS on first paint --
// CollapsibleSection does not render its children until the first expand, so
// these chunks are never requested until the analyst asks for them.
const SessionTrustPassportPanel = lazy(() => import('../components/trust/SessionTrustPassportPanel'));
const InvestigationIntelligencePanel = lazy(() => import('../components/investigation/InvestigationIntelligencePanel'));
const NarrativeAIStoryteller = lazy(() => import('../components/runtime/NarrativeAIStoryteller'));
const AICopilotPanel = lazy(() => import('../components/copilot/AICopilotPanel'));
const FraudDevToolsInspector = lazy(() => import('../components/runtime/FraudDevToolsInspector'));

const WS_BASE = API_BASE.replace(/^http/, 'ws');
const QUEUE_PATH = '/cases?page_size=25&sort=-created_at';

export default function OperationsCenterPage() {
  const navigate = useNavigate();

  // The queue is the stored case list. Live evaluations from the replay stream
  // are layered on top of it -- they never replace it with invented records.
  const queue = useResource(QUEUE_PATH);

  const [liveDecisions, setLiveDecisions] = useState([]);
  const [cyberEvents, setCyberEvents] = useState([]);
  const [selection, setSelection] = useState(null); // { id, source: 'analyst' | 'auto' }
  const [isCSVMapperOpen, setIsCSVMapperOpen] = useState(false);
  const [websocketStages, setWebsocketStages] = useState([]);

  const [apiLatency, setApiLatency] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [blockedValue, setBlockedValue] = useState(null);
  const [safeAssessments, setSafeAssessments] = useState([]);

  const wsRef = useRef(null);

  useEffect(() => {
    fetch(`${API_BASE}/analytics/summary?period=24h`).then((response) => response.json()).then((body) => setBlockedValue((body.data || body).totals?.blocked_amount ?? null)).catch(() => setBlockedValue(null));
    fetch(`${API_BASE}/risk/qr/assessments`).then((response) => response.ok ? response.json() : null).then((body) => setSafeAssessments(body?.assessments || body?.data?.assessments || [])).catch(() => setSafeAssessments([]));
    connectWebSocket();
    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const connectWebSocket = () => {
    if (wsRef.current) wsRef.current.close();
    wsRef.current = new WebSocket(authenticatedWebSocketUrl(`${WS_BASE}/ws/stream`), authenticatedWebSocketProtocols());

    wsRef.current.onopen = () => setWsConnected(true);
    wsRef.current.onclose = () => setWsConnected(false);

    wsRef.current.onmessage = async (evt) => {
      try {
        const data = JSON.parse(evt.data);
        if (data.event_type === 'QR_RISK_ASSESSMENT') {
          setSafeAssessments((prev) => [data, ...prev.filter((item) => item.assessment_id !== data.assessment_id)].slice(0, 50));
        }
        if (data.msg_type === 'status') return;
        if (data.msg_type === 'pipeline_overview') setWebsocketStages([]);
        if (data.msg_type === 'pipeline_stage') setWebsocketStages((prev) => [...prev, data]);
        if (data.msg_type === 'cyber_event') {
          setCyberEvents((prev) => [data, ...prev].slice(0, 50));
        }

        if (data.msg_type === 'transaction') {
          const startTime = performance.now();
          const evalRes = await fetch(`${API_BASE}/evaluate/transaction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
          });
          setApiLatency(Math.round(performance.now() - startTime));
          if (!evalRes.ok) return;

          const evaluation = await evalRes.json();
          const verdict = normalizeVerdict(evaluation.action);
          const decision = {
            id: data.txn_id,
            txn_id: data.txn_id,
            transaction: data,
            evaluation,
            verdict,
            score: evaluation.score,
            amount: data.amount,
            nameOrig: data.nameOrig,
            nameDest: data.nameDest,
            receivedAt: new Date().toISOString(),
            isLive: true,
          };

          setLiveDecisions((prev) => {
            if (prev.some((item) => item.txn_id === decision.txn_id)) return prev;
            return [decision, ...prev].slice(0, 50);
          });

          if (verdict === 'BLOCK') {
            fetch(`${API_BASE}/analytics/summary?period=24h`).then((response) => response.json()).then((body) => setBlockedValue((body.data || body).totals?.blocked_amount ?? null)).catch(() => setBlockedValue(null));
            // A live block takes focus, but the reason is stated in the UI so
            // nobody has to guess why the view moved.
            setSelection({ id: decision.id, source: 'auto' });
          }
        }
      } catch (e) {
        console.error('WS Message Error:', e);
      }
    };
  };

  const queueRows = useMemo(
    () =>
      (queue.data?.items ?? []).map((item) => ({
        id: item.case_id,
        caseId: item.case_id,
        severity: item.severity,
        status: item.status,
        score: item.score,
        amount: item.amount,
        createdAt: item.created_at,
        reason: item.reason,
        customerId: item.customer_id,
        isLive: false,
      })),
    [queue.data],
  );

  const rows = useMemo(() => [...liveDecisions, ...queueRows], [liveDecisions, queueRows]);
  const activeRow = selection ? rows.find((row) => row.id === selection.id) ?? null : null;

  // Only a live decision carries a scored transaction. A stored queue row is a
  // pointer into the investigation workspace, which fetches its own context.
  const activeTransaction = activeRow?.transaction ?? null;
  const activeEvaluation = activeRow?.evaluation ?? null;

  return (
    <div className="mx-auto flex w-full min-w-0 max-w-[1850px] flex-col gap-5 pb-8 font-sans text-soc-text">
      {/* One header. Identity, live engine state, and the two stream controls. */}
      <header className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-soc-border bg-soc-surface p-4 shadow-xl">
        <div className="flex min-w-0 items-center gap-3.5">
          <div className="rounded-xl border border-soc-primary/40 bg-soc-primary/20 p-3">
            <ShieldAlert aria-hidden="true" className="h-6 w-6 text-soc-primary" />
          </div>
          <div className="min-w-0">
            <h1 className="text-base font-bold text-soc-text">Operations Center</h1>
            <p className="mt-0.5 text-xs text-soc-muted">
              Transactions scored against the SIEM signals arriving in the same window.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-end gap-5 font-mono text-xs">
          <div className="text-right">
            <span className="block text-[10px] uppercase text-soc-dim">Stream</span>
            <span
              className={`font-bold ${wsConnected ? 'text-soc-success' : 'text-soc-muted'}`}
            >
              {wsConnected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
          <div className="border-l border-soc-border pl-5 text-right">
            <span className="block text-[10px] uppercase text-soc-dim">Decision latency</span>
            <span className="font-bold tabular-nums text-soc-text">
              {apiLatency == null ? '—' : `${apiLatency} ms`}
            </span>
          </div>
          <div className="border-l border-soc-border pl-5 text-right">
            <span className="block text-[10px] uppercase text-soc-dim">Blocked this session</span>
            <span className="font-bold tabular-nums text-soc-success">
              {blockedValue == null ? 'Waiting for telemetry' : formatAmount(blockedValue)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setIsCSVMapperOpen(true)}
              className="inline-flex items-center gap-1.5 rounded-lg border border-soc-border bg-soc-panel px-3 py-1.5 font-bold text-soc-text transition-colors hover:border-soc-primary"
            >
              <Upload aria-hidden="true" className="h-3.5 w-3.5 text-soc-primary" />
              <span>Upload dataset</span>
            </button>
            <button
              type="button"
              onClick={connectWebSocket}
              className="inline-flex items-center gap-1.5 rounded-lg bg-soc-primary px-3 py-1.5 font-bold text-soc-onPrimary shadow transition-opacity hover:opacity-90"
            >
              <RefreshCw aria-hidden="true" className="h-3.5 w-3.5" />
              <span>Replay stream</span>
            </button>
          </div>
        </div>
      </header>

      <section className="rounded-xl border border-soc-border bg-soc-panel p-4">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold text-soc-text">Fusion SafeCheck assessments</h2>
            <p className="text-xs text-soc-muted">Sanitized QR risk signals received from the public safety surface.</p>
          </div>
          <span className="font-mono text-xs text-soc-info">{safeAssessments.length}</span>
        </div>
        {safeAssessments.length ? (
          <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-4">
            {safeAssessments.slice(0, 8).map((item) => (
              <div key={item.assessment_id || item.assessmentId} className="rounded-lg border border-soc-border bg-soc-surface p-3">
                <div className="flex justify-between text-xs font-bold text-soc-text"><span>{item.qr_type || item.qrType}</span><span>{item.risk_level || item.riskLevel}</span></div>
                <div className="mt-1 font-mono text-[10px] text-soc-muted">{item.assessment_id || item.assessmentId}</div>
                <div className="mt-2 text-[11px] text-soc-muted">Risk {item.risk_score ?? item.riskScore ?? '—'} · Confidence {item.confidence ?? '—'}%</div>
                <div className="mt-1 text-[10px] text-soc-dim">Reports {item.report_count ?? item.reportCount ?? 0} · {item.timestamp || item.assessedAt}</div>
              </div>
            ))}
          </div>
        ) : <p className="text-xs text-soc-muted">No SafeCheck assessments received yet.</p>}
      </section>

      {/* Nothing is selected until an analyst clicks or a live BLOCK arrives,
          and when the view auto-selects it says so. */}
      {activeRow ? (
        <>
          {selection?.source === 'auto' && (
            <p
              role="status"
              className="rounded-lg border border-soc-info/40 bg-soc-info/10 px-3 py-2 text-xs text-soc-text"
            >
              Auto-selected — newest BLOCK decision on the live stream. Select any row below to
              pin a different one.
            </p>
          )}

          <VerdictHero
            verdict={activeRow.verdict ?? null}
            score={activeRow.score}
            reason={activeEvaluation?.reasons?.[0] || activeRow.reason}
            timestamp={formatTimestamp(activeRow.receivedAt || activeRow.createdAt)}
            transactionId={activeRow.txn_id}
          />

          {activeRow.caseId && (
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-soc-border bg-soc-panel px-4 py-3">
              <span className="font-mono text-xs text-soc-muted">
                Case <span className="font-bold text-soc-text">{activeRow.caseId}</span>
                {activeRow.customerId ? ` · ${activeRow.customerId}` : ''}
              </span>
              <button
                type="button"
                onClick={() => navigate(`/investigation/${activeRow.caseId}`)}
                className="inline-flex items-center gap-2 rounded bg-soc-primary px-3 py-1.5 text-xs font-semibold text-soc-onPrimary transition-opacity hover:opacity-90"
              >
                <ExternalLink aria-hidden="true" className="h-3.5 w-3.5" />
                Open investigation
              </button>
            </div>
          )}
        </>
      ) : (
        <EmptyState
          title="No decision selected"
          description="Select a transaction or case below to see its verdict, pipeline and supporting panels. Nothing is pre-selected."
        />
      )}

      {activeTransaction && (
        <FusionLifecyclePipeline
          activeTxn={activeTransaction}
          evaluation={activeEvaluation}
          websocketStages={websocketStages}
        />
      )}

      {/* The fusion view: the decision queue beside the SIEM feed explaining it. */}
      <div className="grid min-w-0 grid-cols-1 gap-4 lg:grid-cols-12">
        <section className="min-w-0 rounded-xl border border-soc-border bg-soc-panel p-3.5 lg:col-span-6">
          <header className="mb-3 flex items-center justify-between border-b border-soc-border pb-2">
            <h2 className="flex items-center gap-2 text-xs font-bold uppercase text-soc-text">
              <Landmark aria-hidden="true" className="h-4 w-4 text-soc-primary" />
              Decision queue
            </h2>
            <span className="font-mono text-[10px] text-soc-muted">
              {liveDecisions.length} live · {queue.data?.total ?? 0} stored
            </span>
          </header>
          <p className="mb-2 text-[10px] text-soc-dim">
            Select a row to drive the verdict and every panel below.
          </p>

          <div className="max-h-[260px] overflow-y-auto pr-1">
            <PanelState
              status={queue.status}
              error={queue.error}
              onRetry={queue.reload}
              isEmpty={rows.length === 0}
              loadingLabel="Loading the case queue…"
              emptyTitle="Queue is empty"
              emptyDescription="No stored cases and nothing on the live stream yet."
            >
              {() => (
                <ul className="space-y-2">
                  {rows.map((row) => (
                    <li key={row.id}>
                      <button
                        type="button"
                        onClick={() => setSelection({ id: row.id, source: 'analyst' })}
                        aria-pressed={row.id === activeRow?.id}
                        className={`flex w-full items-center justify-between gap-2 rounded border bg-soc-bg p-2 text-left text-[11px] transition-colors hover:border-soc-primary ${
                          row.id === activeRow?.id ? 'border-soc-primary' : 'border-soc-border'
                        }`}
                      >
                        <span className="flex min-w-0 items-center gap-2">
                          {row.isLive ? (
                            <span className="shrink-0 rounded border border-soc-success/40 bg-soc-success/10 px-1 py-0.5 font-mono text-[9px] font-bold text-soc-success">
                              LIVE
                            </span>
                          ) : (
                            <span
                              className={`shrink-0 rounded border px-1 py-0.5 font-mono text-[9px] font-bold ${
                                severityChip[row.severity] || severityChip.LOW
                              }`}
                            >
                              {row.severity}
                            </span>
                          )}
                          <span className="truncate font-mono text-soc-text">
                            {row.caseId || row.txn_id}
                          </span>
                          <span className="truncate font-mono text-soc-dim">
                            {row.nameOrig} → {row.nameDest}
                          </span>
                        </span>
                        <span className="shrink-0 font-mono font-bold tabular-nums text-soc-danger">
                          {formatAmount(row.amount)}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </PanelState>
          </div>
        </section>

        <section className="min-w-0 rounded-xl border border-soc-border bg-soc-panel p-3.5 lg:col-span-6">
          <header className="mb-3 flex items-center justify-between border-b border-soc-border pb-2">
            <h2 className="flex items-center gap-2 text-xs font-bold uppercase text-soc-text">
              <Radio aria-hidden="true" className="h-4 w-4 text-soc-danger" />
              Synchronized SIEM logs
            </h2>
            <span className="font-mono text-[10px] text-soc-muted">{cyberEvents.length}</span>
          </header>
          <p className="mb-2 text-[10px] text-soc-dim">
            Cyber events arriving in the same window as the transfers on the left.
          </p>
          <div className="max-h-[260px] space-y-2 overflow-y-auto pr-1 font-mono text-[11px]">
            {cyberEvents.length === 0 ? (
              <EmptyState
                title="No cyber events yet"
                description="Start the replay stream to see SIEM signals as they arrive."
              />
            ) : (
              cyberEvents.map((event, index) => (
                <div
                  key={`${event.timestamp}-${index}`}
                  className="rounded border border-soc-border bg-soc-bg p-2 text-soc-muted"
                >
                  {event.timestamp} • {event.event_type} • {event.user_id} • {event.ip}
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      {/* Progressive disclosure: depth on demand. Each section lazy-mounts on
          first expand and then stays mounted, so re-collapsing never refetches. */}
      {activeTransaction && (
        <>
          <CollapsibleSection
            title="Session Trust Passport"
            description="Identity, device, network, and behaviour checkpoints"
            icon={Fingerprint}
          >
            <SessionTrustPassportPanel
              sessionId={activeEvaluation?.session_id || activeTransaction.session_id}
              activeTxn={activeTransaction}
            />
          </CollapsibleSection>

          <CollapsibleSection
            title="Threat Correlation & Mule Ring Intelligence"
            description="Linked cyber signals and beneficiary network"
            icon={Search}
          >
            <InvestigationIntelligencePanel
              caseId={activeRow?.caseId || activeRow?.txn_id}
              activeTxn={activeTransaction}
            />
          </CollapsibleSection>

          <CollapsibleSection
            title="Narrative AI Decision Summary"
            description="Plain-language account of why this verdict was reached"
            icon={BookOpen}
          >
            <NarrativeAIStoryteller activeTxn={activeTransaction} evaluation={activeEvaluation} />
          </CollapsibleSection>

          <CollapsibleSection
            title="Fraud DevTools Inspector"
            description="Raw features, SHAP values, and engine internals"
            icon={Terminal}
          >
            <div className="h-[320px]">
              <FraudDevToolsInspector
                activeTxn={activeTransaction}
                evaluation={activeEvaluation}
              />
            </div>
          </CollapsibleSection>
        </>
      )}

      <CollapsibleSection
        title="Fuzen AI Copilot"
        description="Ask questions about the platform and the current selection"
        icon={Bot}
      >
        <div className="h-[520px]">
          <AICopilotPanel
            activeContext={{
              user_id: activeTransaction?.user_id ?? activeRow?.customerId,
              session_id: activeEvaluation?.session_id,
            }}
          />
        </div>
      </CollapsibleSection>

      <CSVSchemaMapperModal
        isOpen={isCSVMapperOpen}
        onClose={() => setIsCSVMapperOpen(false)}
        onIngest={(data) => console.log('CSV Ingested:', data)}
      />
    </div>
  );
}
