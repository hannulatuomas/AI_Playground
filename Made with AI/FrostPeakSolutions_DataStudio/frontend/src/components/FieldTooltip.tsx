import React from 'react';

interface FieldTooltipProps {
  text: string;
  id: string;
}

/**
 * Accessible info icon + tooltip for form fields.
 * Uses native title attribute for simplicity and accessibility.
 */
export const FieldTooltip: React.FC<FieldTooltipProps> = ({ text, id }) => (
  <span
    tabIndex={0}
    aria-label={text}
    aria-describedby={id}
    style={{ display: 'inline-flex', alignItems: 'center', marginLeft: 6, cursor: 'pointer', color: 'var(--color-primary)' }}
    title={text}
    role="img"
  >
    <svg
      width="16"
      height="16"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      style={{ marginRight: 0, verticalAlign: 'middle' }}
    >
      <circle cx="12" cy="12" r="10" stroke="var(--color-primary)" strokeWidth="2" fill="var(--color-primary-light)" />
      <text x="12" y="16" textAnchor="middle" fontSize="12" fill="var(--color-primary)" fontFamily="Arial, sans-serif">i</text>
    </svg>
  </span>
);
