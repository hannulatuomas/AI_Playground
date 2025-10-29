import React from 'react';

/**
 * SchemaStatusBadge displays the schema status (confirmed, editing, unconfirmed) as a colored badge with icon and ARIA label.
 * Usage: <SchemaStatusBadge status="confirmed" />
 */
export type SchemaStatus = 'confirmed' | 'editing' | 'unconfirmed';

interface Props {
  status: SchemaStatus;
  className?: string;
  style?: React.CSSProperties;
}

const statusConfig: Record<SchemaStatus, { color: string; label: string; icon: JSX.Element }> = {
  confirmed: {
    color: 'var(--color-success)',
    label: 'Schema Confirmed',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="8" fill="var(--color-success)" />
        <path d="M5 8.5l2 2 4-4" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  editing: {
    color: 'var(--color-warning)',
    label: 'Editing Schema',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="8" fill="var(--color-warning)" />
        <path d="M5.5 10.5l5-5" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
  unconfirmed: {
    color: 'var(--color-error)',
    label: 'Schema Unconfirmed',
    icon: (
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <circle cx="8" cy="8" r="8" fill="var(--color-error)" />
        <path d="M5 5l6 6M11 5l-6 6" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
  },
};

export const SchemaStatusBadge: React.FC<Props> = ({ status, className = '', style }) => {
  const { color, label, icon } = statusConfig[status] || statusConfig.unconfirmed;
  return (
    <span
      className={`schema-status-badge ${className}`}
      style={{ display: 'inline-flex', alignItems: 'center', gap: 4, ...style }}
      aria-label={label}
      title={label}
      tabIndex={0}
      role="img"
    >
      {icon}
      <span style={{ color: color, fontWeight: 600, fontSize: 12 }}>{label}</span>
    </span>
  );
};

export default SchemaStatusBadge;
