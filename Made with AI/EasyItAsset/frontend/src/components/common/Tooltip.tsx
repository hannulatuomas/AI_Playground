import React from 'react';

interface TooltipProps {
  content: string;
  disabled?: boolean;
  children: React.ReactNode;
}

export const Tooltip: React.FC<TooltipProps> = ({ content, disabled = false, children }) => {
  // Don't render tooltip if disabled or content is empty
  if (disabled || !content.trim()) {
    return <>{children}</>;
  }

  return (
    <div className="relative group">
      {children}
      <div className="absolute invisible group-hover:visible bg-gray-800 text-white text-xs rounded p-2 bottom-full mb-2 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
        {content}
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-1/2 rotate-45 w-2 h-2 bg-gray-800"></div>
      </div>
    </div>
  );
}; 