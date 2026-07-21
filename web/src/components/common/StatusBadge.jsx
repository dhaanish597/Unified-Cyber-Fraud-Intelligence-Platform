import React from 'react';
import Badge from './Badge';

export default function StatusBadge({ status = 'ONLINE' }) {
  let variant = 'default';
  if (status === 'ONLINE' || status === 'ACTIVE' || status === 'RESOLVED') variant = 'success';
  if (status === 'PENDING' || status === 'IN_REVIEW' || status === 'CHALLENGED') variant = 'warning';
  if (status === 'CRITICAL' || status === 'COMPROMISED' || status === 'BLOCKED') variant = 'danger';

  return (
    <Badge variant={variant} size="xs">
      {status}
    </Badge>
  );
}
