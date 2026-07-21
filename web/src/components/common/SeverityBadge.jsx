import React from 'react';
import Badge from './Badge';

export default function SeverityBadge({ severity = 'info' }) {
  let variant = 'default';
  const s = severity.toLowerCase();
  
  if (s === 'critical' || s === 'high') variant = 'danger';
  if (s === 'medium' || s === 'warning') variant = 'warning';
  if (s === 'low' || s === 'info') variant = 'primary';

  return (
    <Badge variant={variant} size="xs">
      {severity.toUpperCase()}
    </Badge>
  );
}
