import React from 'react';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  fullScreen?: boolean;
  color?: string;
  className?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'medium',
  fullScreen = false,
  color = 'blue',
  className = ''
}) => {
  const sizeClasses = {
    small: 'h-6 w-6 border-2',
    medium: 'h-12 w-12 border-3',
    large: 'h-16 w-16 border-4'
  };

  const containerClasses = fullScreen
    ? 'min-h-screen flex items-center justify-center bg-gray-50'
    : 'flex items-center justify-center';

  return (
    <div className={containerClasses}>
      <div
        className={`animate-spin rounded-full border-t-current border-r-transparent border-b-current border-l-transparent text-${color}-500 ${sizeClasses[size]} ${className}`}
      ></div>
    </div>
  );
}; 