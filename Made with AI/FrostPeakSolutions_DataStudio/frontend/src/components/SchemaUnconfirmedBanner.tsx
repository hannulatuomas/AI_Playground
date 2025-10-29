import React from 'react';

/**
 * Banner warning users that a file-backed cell's schema is unconfirmed.
 * Use this in any context where schema confirmation is required before running queries.
 */
interface SchemaUnconfirmedBannerProps {
  style?: React.CSSProperties;
}

const SchemaUnconfirmedBanner: React.FC<SchemaUnconfirmedBannerProps> = ({ style }) => (
  <div
    role="alert"
    aria-live="assertive"
    style={{
      background: 'var(--color-warning-bg)',
      color: 'var(--color-warning-text)',
      border: '1px solid var(--color-warning-border)',
      borderRadius: 6,
      padding: '10px 16px',
      margin: '12px 0 8px 0',
      fontWeight: 600,
      fontSize: 15,
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      ...style,
    }}
  >
    <svg width="20" height="20" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#b71c1c"/><text x="10" y="15" textAnchor="middle" fontSize="13" fill="#fff" fontWeight="bold">!</text></svg>
    <span>
      <strong>Schema not confirmed:</strong> Please confirm the file schema before running queries or using this cell.
    </span>
  </div>
);

export default SchemaUnconfirmedBanner;
