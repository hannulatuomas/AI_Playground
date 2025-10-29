import React from 'react';
import { SchemaStatus } from './SchemaStatusBadge';

interface CellStatusIndicatorsProps {
  executing?: boolean;
  error?: string | null;
  schemaStatus?: SchemaStatus;
  isFileBacked?: boolean;
}

const indicatorStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 8,
  fontSize: 15,
  marginLeft: 8
};

export const CellStatusIndicators: React.FC<CellStatusIndicatorsProps> = ({ executing, error, schemaStatus, isFileBacked }) => {
  return (
    <span style={indicatorStyle}>
      {executing && (
        <span
          style={{ display: 'inline-flex', alignItems: 'center', color: 'var(--color-primary)', fontWeight: 600 }}
          aria-label="Cell is running"
          title="Cell is running"
        >
          <span className="cell-spinner" style={{ width: 16, height: 16, marginRight: 4, display: 'inline-block' }}>
            <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
              <circle cx="8" cy="8" r="7" stroke="var(--color-primary)" strokeWidth="2" fill="none" opacity="0.2" />
              <path d="M8 1a7 7 0 0 1 7 7" stroke="var(--color-primary)" strokeWidth="2" fill="none" strokeLinecap="round">
                <animateTransform attributeName="transform" type="rotate" from="0 8 8" to="360 8 8" dur="0.8s" repeatCount="indefinite" />
              </path>
            </svg>
          </span>
          Running
        </span>
      )}
      {isFileBacked && schemaStatus === 'unconfirmed' && (
        <span
          style={{ color: 'var(--color-error)', fontWeight: 600 }}
          aria-label="Schema not confirmed"
          title="Schema not confirmed"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" style={{ marginRight: 2 }}>
            <circle cx="8" cy="8" r="8" fill="var(--color-error)" />
            <text x="8" y="12" textAnchor="middle" fontSize="12" fill="#fff" fontWeight="bold">!</text>
          </svg>
          Schema not confirmed
        </span>
      )}
      {error && (
        <span
          style={{ color: 'var(--color-error)', fontWeight: 600 }}
          aria-label="Cell error"
          title={typeof error === 'string' ? error : 'Cell error'}
        >
          <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" style={{ marginRight: 2 }}>
            <circle cx="8" cy="8" r="8" fill="var(--color-error)" />
            <text x="8" y="12" textAnchor="middle" fontSize="12" fill="#fff" fontWeight="bold">!</text>
          </svg>
          Error
        </span>
      )}
    </span>
  );
};

export default CellStatusIndicators;
