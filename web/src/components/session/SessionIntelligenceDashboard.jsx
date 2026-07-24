import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { authenticatedWebSocketUrl } from '../../platformAuth';
import { Clock3, RefreshCw, Search, ShieldCheck, Wifi, WifiOff } from 'lucide-react';
import Card from '../common/Card';
import TrustComponentHeatmap from './TrustComponentHeatmap';
import TrustPassportCard from './TrustPassportCard';
import TrustTimelineChart from './TrustTimelineChart';

const API_BASE = import.meta.env.VITE_API_BASE || (import.meta.env.DEV ? 'http://localhost:8001' : 'https://fusion.example.invalid');
const WS_BASE = (import.meta.env.VITE_WS_BASE || API_BASE).replace(/^http/, 'ws');

export default function SessionIntelligenceDashboard() {
  const [sessions, setSessions] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [detail, setDetail] = useState(null);
  const [history, setHistory] = useState([]);
  const [range, setRange] = useState('last_hour');
  const [query, setQuery] = useState('');
  const [stateFilter, setStateFilter] = useState('');
  const [connectionState, setConnectionState] = useState('CONNECTING');
  const [error, setError] = useState('');
  const [latency, setLatency] = useState(null);

  const loadSessions = useCallback(async () => {
    try {
      const params = new URLSearchParams({ limit: '200' });
      if (query) params.set('search', query);
      if (stateFilter) params.set('state', stateFilter);
      const response = await fetch(`${API_BASE}/sessions?${params}`);
      if (!response.ok) throw new Error(`Session registry returned ${response.status}`);
      const payload = await response.json();
      setSessions(payload.sessions || []);
      setSelectedId((current) => current || payload.sessions?.[0]?.session_id || '');
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    }
  }, [query, stateFilter]);

  const loadSelected = useCallback(async () => {
    if (!selectedId) {
      setDetail(null);
      setHistory([]);
      return;
    }
    const started = performance.now();
    try {
      const [detailResponse, historyResponse] = await Promise.all([
        fetch(`${API_BASE}/sessions/${encodeURIComponent(selectedId)}`),
        fetch(`${API_BASE}/trust-history/${encodeURIComponent(selectedId)}?range=${range}`),
      ]);
      if (!detailResponse.ok || !historyResponse.ok) throw new Error('Unable to load selected session');
      setDetail(await detailResponse.json());
      const historyPayload = await historyResponse.json();
      setHistory(historyPayload.snapshots || []);
      setLatency(Math.round(performance.now() - started));
      setError('');
    } catch (requestError) {
      setError(requestError.message);
    }
  }, [range, selectedId]);

  useEffect(() => {
    loadSessions();
    const timer = window.setInterval(loadSessions, 5000);
    return () => window.clearInterval(timer);
  }, [loadSessions]);

  useEffect(() => {
    loadSelected();
  }, [loadSelected]);

  useEffect(() => {
    if (!selectedId) {
      setConnectionState('WAITING');
      return undefined;
    }
    let retryTimer;
    let disposed = false;
    let socket;

    const connect = () => {
      setConnectionState('CONNECTING');
      socket = new WebSocket(authenticatedWebSocketUrl(`${WS_BASE}/ws/stream?session_id=${encodeURIComponent(selectedId)}`));
      socket.onopen = () => setConnectionState('LIVE');
      socket.onmessage = (message) => {
        const envelope = JSON.parse(message.data);
        if (envelope.msg_type !== 'trust_passport_update') return;
        setDetail((current) => ({
          ...(current || {}),
          passport: envelope.passport,
          deltas: [...(envelope.deltas || []), ...(current?.deltas || [])].slice(0, 100),
          session: current?.session,
          recovery_events: [
            ...(envelope.deltas || []).filter((delta) => delta.is_recovery),
            ...(current?.recovery_events || []),
          ].slice(0, 100),
        }));
        if (envelope.snapshot) {
          setHistory((current) => [...current, envelope.snapshot].slice(-1000));
        }
        setSessions((current) => current.map((session) => (
          session.session_id === envelope.session_id
            ? {
              ...session,
              trust: envelope.passport.overall_trust,
              confidence: envelope.passport.confidence,
              current_state: envelope.passport.current_status,
              trust_trend: envelope.passport.trust_trend,
              last_activity: envelope.passport.updated_time,
            }
            : session
        )));
      };
      socket.onclose = () => {
        if (!disposed) {
          setConnectionState('RECONNECTING');
          retryTimer = window.setTimeout(connect, 1500);
        }
      };
      socket.onerror = () => socket.close();
    };

    connect();
    return () => {
      disposed = true;
      window.clearTimeout(retryTimer);
      socket?.close();
    };
  }, [selectedId]);

  const activeCount = useMemo(
    () => sessions.filter((session) => session.current_state !== 'CLOSED').length,
    [sessions],
  );

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <Metric label="Live sessions" value={activeCount} icon={ShieldCheck} />
        <Metric label="Backend latency" value={latency === null ? '—' : `${latency} ms`} icon={Clock3} />
        <Metric label="Trust stream" value={connectionState} icon={connectionState === 'LIVE' ? Wifi : WifiOff} />
      </div>

      {error && (
        <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 px-4 py-3 text-xs text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-4 xl:grid-cols-[340px_1fr]">
        <Card
          header={
            <>
              <span>Live Session Registry</span>
              <button onClick={loadSessions} className="text-soc-muted hover:text-soc-text" title="Refresh sessions">
                <RefreshCw className="h-4 w-4" />
              </button>
            </>
          }
          className="xl:row-span-2"
        >
          <div className="mb-3 grid gap-2 sm:grid-cols-[1fr_110px] xl:grid-cols-1">
            <label className="flex items-center gap-2 rounded-lg border border-soc-border bg-soc-bg px-3 py-2">
              <Search className="h-3.5 w-3.5 text-soc-muted" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search session, user, device"
                className="w-full bg-transparent text-xs text-soc-text outline-none placeholder:text-soc-dim"
              />
            </label>
            <select
              value={stateFilter}
              onChange={(event) => setStateFilter(event.target.value)}
              className="rounded-lg border border-soc-border bg-soc-bg px-3 py-2 text-xs text-soc-text outline-none"
            >
              <option value="">All states</option>
              {['ACTIVE', 'IDLE', 'SUSPICIOUS', 'CHALLENGED', 'BLOCKED', 'CLOSED'].map((state) => (
                <option key={state}>{state}</option>
              ))}
            </select>
          </div>
          <div className="max-h-[690px] space-y-2 overflow-y-auto pr-1">
            {sessions.length === 0 ? (
              <div className="py-12 text-center text-xs text-soc-muted">
                No sessions match the current filters.
              </div>
            ) : sessions.map((session) => (
              <button
                key={session.session_id}
                onClick={() => setSelectedId(session.session_id)}
                className={`w-full rounded-lg border p-3 text-left transition ${
                  selectedId === session.session_id
                    ? 'border-soc-primary bg-soc-primary/10'
                    : 'border-soc-border bg-soc-bg hover:border-soc-border-hover'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-mono text-xs font-bold text-soc-text">{session.user_id}</span>
                  <span className="text-sm font-black text-soc-text">{Number(session.trust).toFixed(1)}</span>
                </div>
                <div className="mt-1 truncate font-mono text-[9px] text-soc-muted">{session.session_id}</div>
                <div className="mt-2 flex items-center justify-between text-[9px]">
                  <span className="rounded bg-soc-panel px-1.5 py-0.5 text-soc-muted">{session.current_state}</span>
                  <span className="text-soc-muted">{session.threat_count} threats</span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <TrustPassportCard passport={detail?.passport} connectionState={connectionState} />
        <TrustComponentHeatmap components={detail?.passport?.components} />
      </div>

      <div className="flex items-center justify-end gap-2">
        <span className="text-[10px] uppercase tracking-wider text-soc-muted">History range</span>
        <select
          value={range}
          onChange={(event) => setRange(event.target.value)}
          className="rounded-lg border border-soc-border bg-soc-surface px-3 py-2 text-xs text-soc-text"
        >
          <option value="last_minute">Last minute</option>
          <option value="last_hour">Last hour</option>
          <option value="last_day">Last day</option>
        </select>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        <TrustTimelineChart snapshots={history} />
        <EventList title="Trust Delta" rows={detail?.deltas || []} empty="No component changes recorded." />
        <EventList title="Trust Recovery" rows={detail?.recovery_events || []} empty="No recovery events recorded." recovery />
        <HistoryTable snapshots={history} />
      </div>
    </div>
  );
}

function Metric({ label, value, icon: Icon }) {
  return (
    <div className="rounded-xl border border-soc-border bg-soc-surface p-4">
      <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider text-soc-muted">
        <Icon className="h-4 w-4 text-soc-primary" /> {label}
      </div>
      <div className="mt-2 font-mono text-xl font-black text-soc-text">{value}</div>
    </div>
  );
}

function EventList({ title, rows, empty, recovery = false }) {
  return (
    <Card header={title}>
      <div className="max-h-64 space-y-2 overflow-y-auto">
        {rows.length === 0 ? (
          <div className="py-10 text-center text-xs text-soc-muted">{empty}</div>
        ) : rows.map((row) => (
          <div key={row.delta_id} className="rounded-lg border border-soc-border bg-soc-bg p-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase text-soc-text">{row.component}</span>
              <span className={`font-mono text-xs font-black ${row.difference > 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                {row.difference > 0 ? '+' : ''}{Number(row.difference).toFixed(1)}
              </span>
            </div>
            <div className="mt-1 text-[10px] text-soc-muted">
              {Number(row.previous_trust).toFixed(1)} → {Number(row.current_trust).toFixed(1)}
            </div>
            <div className="mt-1 text-[10px] text-soc-muted">{row.reason}</div>
            {recovery && <span className="mt-2 inline-block rounded bg-emerald-500/10 px-1.5 py-0.5 text-[9px] text-emerald-300">RECOVERED</span>}
          </div>
        ))}
      </div>
    </Card>
  );
}

function HistoryTable({ snapshots }) {
  return (
    <Card header="Trust History">
      <div className="max-h-64 overflow-auto">
        {snapshots.length === 0 ? (
          <div className="py-10 text-center text-xs text-soc-muted">No historical snapshots available.</div>
        ) : (
          <table className="w-full text-left text-[10px]">
            <thead className="sticky top-0 bg-soc-surface uppercase text-soc-muted">
              <tr><th className="py-2">Time</th><th>Event</th><th>Trust</th><th>Delta</th></tr>
            </thead>
            <tbody>
              {[...snapshots].reverse().map((snapshot) => (
                <tr key={snapshot.snapshot_id} className="border-t border-soc-border text-soc-text">
                  <td className="py-2">{new Date(snapshot.timestamp).toLocaleTimeString()}</td>
                  <td>{snapshot.event_type}</td>
                  <td>{Number(snapshot.current_trust).toFixed(1)}</td>
                  <td className={snapshot.delta >= 0 ? 'text-emerald-300' : 'text-rose-300'}>
                    {snapshot.delta > 0 ? '+' : ''}{Number(snapshot.delta).toFixed(1)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Card>
  );
}
