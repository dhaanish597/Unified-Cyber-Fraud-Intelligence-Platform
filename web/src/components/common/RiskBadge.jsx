import React from 'react';
import Badge from './Badge';

export default function RiskBadge({ score = 0 }) {
  let variant = 'success';
  let label = 'LOW RISK';

  if (score >= 75) {
    variant = 'danger';
    label = 'CRITICAL RISK';
  } else if (score >= 50) {
    variant = 'warning';
    label = 'ELEVATED RISK';
  }

  return (
    <Badge variant={variant} size="sm">
      {label} ({Math.round(score)})
    </Badge>
  );
}
