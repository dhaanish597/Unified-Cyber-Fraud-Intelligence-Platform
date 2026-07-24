import React from 'react';
import { Activity, Clock3, ShieldCheck, TrendingDown, TrendingUp } from 'lucide-react';
import Card from '../common/Card';

const scoreColor = (score) => {
  if (score >= 85) return '#34d399';
  if (score >= 70) return '#fbbf24';
  return '#fb7185';
};

export default function TrustPassportCard({ passport, connectionState }) {
  if (!passport) {
    return (
      <Card header="Trust Passport">
        <div className="py-12 text-center text-sm text-soc-muted">
          Select an active session to load its Trust Passport.
        </div>
      </Card>
    );
  }

  const TrendIcon = passport.trust_trend === 'IMPROVING' ? TrendingUp : TrendingDown;
  const score = Number(passport.overall_trust ?? 0);

  return (
    <Card
      header={
        <>
          <span className="flex items-center gap-2"><ShieldCheck className="h-4 w-4" /> Trust Passport</span>
          <span className="flex items-center gap-1 text-[10px] normal-case text-soc-muted">
            <span className={`h-2 w-2 rounded-full ${connectionState === 'LIVE' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
            {connectionState}
          </span>
        </>
      }
    >
      <div className="grid gap-5 md:grid-cols-[180px_1fr]">
        <div className="flex flex-col items-center justify-center rounded-xl border border-soc-border bg-soc-panel/40 p-5">
          <div
            className="flex h-28 w-28 items-center justify-center rounded-full border-[9px] text-3xl font-black"
            style={{ borderColor: scoreColor(score), color: scoreColor(score) }}
          >
            {score.toFixed(1)}
          </div>
          <span className="mt-3 text-[10px] uppercase tracking-[0.2em] text-soc-muted">Overall trust</span>
        </div>

        <div className="grid content-start gap-3 sm:grid-cols-2">
          <Info label="Status" value={passport.current_status} icon={Activity} />
          <Info label="Confidence" value={`${Number(passport.confidence ?? 0).toFixed(1)}%`} icon={ShieldCheck} />
          <Info
            label="Trend"
            value={passport.trust_trend}
            icon={TrendIcon}
            valueClass={passport.trust_trend === 'DECLINING' ? 'text-rose-300' : 'text-emerald-300'}
          />
          <Info label="Policy version" value={passport.version} icon={ShieldCheck} />
          <Info label="Passport ID" value={passport.passport_id} icon={ShieldCheck} />
          <Info
            label="Last update"
            value={passport.updated_time ? new Date(passport.updated_time).toLocaleTimeString() : '—'}
            icon={Clock3}
          />
        </div>
      </div>
    </Card>
  );
}

function Info({ label, value, icon: Icon, valueClass = 'text-soc-text' }) {
  return (
    <div className="rounded-lg border border-soc-border bg-soc-bg p-3">
      <div className="mb-1 flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-soc-muted">
        <Icon className="h-3 w-3" /> {label}
      </div>
      <div className={`truncate font-mono text-xs font-bold ${valueClass}`} title={String(value ?? '')}>
        {value ?? '—'}
      </div>
    </div>
  );
}
