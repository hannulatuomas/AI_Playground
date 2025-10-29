import React, { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

const ForgotPassword: React.FC = () => {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validateEmail = (value: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    // Client-side validation
    if (!validateEmail(email)) {
      setError('Please enter a valid email address');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/request-password-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      const data = await res.json();
      if (res.ok) {
        setSent(true);
      } else {
        setError(data.message || 'Something went wrong');
      }
    } catch {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-sm flex flex-col gap-4">
        <h2 className="text-xl font-bold mb-2 text-center">Forgot Password</h2>
        {sent ? (
          <div className="text-green-600 mb-4">If that email exists, a reset link has been sent.</div>
        ) : (
          <>
            <label className="block text-sm font-medium mb-2" htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              className="w-full p-2 border border-gray-300 rounded mb-4"
              value={email}
              onChange={e => { setEmail(e.target.value); setError(''); }}
              required
              autoFocus
              aria-invalid={!!error && !validateEmail(email)}
              aria-describedby={!!error && !validateEmail(email) ? 'forgot-email-error' : undefined}
            />
            {error && (
              <div id="forgot-form-error" className="text-red-700 bg-red-100 border border-red-300 rounded p-2 mb-2" role="alert">
                {error}
              </div>
            )}
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? <LoadingSpinner label="Sending..." /> : 'Send Reset Link'}
            </button>
          </>
        )}
      </form>
    </main>
  );
};

export default ForgotPassword;
