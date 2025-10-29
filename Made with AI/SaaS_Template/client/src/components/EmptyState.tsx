import React from 'react';

const EmptyState: React.FC<{ icon?: React.ReactNode; message?: string; className?: string }> = ({
  icon,
  message = 'Nothing to display.',
  className = '',
}) => (
  <div className={`flex flex-col items-center justify-center py-8 text-gray-500 ${className}`}
    aria-live="polite"
  >
    {icon || (
      <svg
        className="h-10 w-10 mb-2 text-gray-300"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3" />
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      </svg>
    )}
    <span className="text-base font-medium">{message}</span>
  </div>
);

export default EmptyState;
