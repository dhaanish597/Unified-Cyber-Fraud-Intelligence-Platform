import React from 'react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import Card from '../common/Card';

export default function TrustTimelineChart({ snapshots = [] }) {
  const data = snapshots.map((snapshot) => ({
    trust: snapshot.current_trust,
    event: snapshot.event_type,
    time: new Date(snapshot.timestamp).toLocaleTimeString(),
    reason: snapshot.reason,
  }));

  return (
    <Card header="Trust Timeline">
      {data.length === 0 ? (
        <div className="flex h-64 items-center justify-center text-sm text-soc-muted">
          Trust history will appear after session events arrive.
        </div>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 10, right: 18, left: -18, bottom: 0 }}>
              <CartesianGrid stroke="var(--soc-border-default)" strokeDasharray="3 3" />
              <XAxis dataKey="time" stroke="var(--soc-text-muted)" tick={{ fontSize: 10 }} />
              <YAxis domain={[0, 100]} stroke="var(--soc-text-muted)" tick={{ fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: 'var(--soc-bg-elevated)',
                  border: '1px solid var(--soc-border-default)',
                  borderRadius: 8,
                  fontSize: 11,
                }}
                formatter={(value) => [`${Number(value).toFixed(1)}`, 'Overall trust']}
                labelFormatter={(_, payload) => payload?.[0]?.payload?.event ?? ''}
              />
              <Line
                type="monotone"
                dataKey="trust"
                stroke="#3b82f6"
                strokeWidth={3}
                dot={{ r: 4, fill: '#60a5fa' }}
                activeDot={{ r: 6 }}
                isAnimationActive
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  );
}
