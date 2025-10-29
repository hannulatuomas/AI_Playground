import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Optionally log to an error reporting service
    if (import.meta.env.MODE === 'development') {
      // eslint-disable-next-line no-console
      console.error('ErrorBoundary caught:', error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4" role="alert" aria-live="assertive">
          <h1 className="text-3xl font-bold mb-4 text-red-700">Something went wrong</h1>
          <p className="mb-4 text-gray-700">An unexpected error occurred. Please try again.</p>
          <button onClick={this.handleRetry} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Try Again</button>
          {import.meta.env.MODE === 'development' && this.state.error && (
            <pre className="mt-4 text-xs text-left text-red-700 bg-red-50 p-2 rounded max-w-full overflow-x-auto">
              {this.state.error.message}
            </pre>
          )}
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
