import React, { useState } from 'react';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useSearchParams, useNavigate } from 'react-router-dom';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token') || '';
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    // Client-side validation
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, password }),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess(true);
        setTimeout(() => navigate('/login'), 2500);
      } else {
        setError(data.message || 'Something went wrong');
      }
    } catch {
      setError('Network error');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-50 px-2"><div className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-sm text-center text-red-600">Invalid or missing token.</div></div>;
  }

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-sm flex flex-col gap-4">
        <h2 className="text-xl font-bold mb-2 text-center">Reset Password</h2>
        {success ? (
          <div className="text-green-600 mb-4">Password reset! Redirecting to login...</div>
        ) : (
          <>
            <label className="block text-sm font-medium mb-2" htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              className="w-full p-2 border border-gray-300 rounded mb-4"
              value={password}
              onChange={e => { setPassword(e.target.value); setError(''); }}
              required
              minLength={6}
              aria-invalid={!!error && password.length < 6}
              aria-describedby={!!error && password.length < 6 ? 'reset-password-error' : undefined}
            />
            <label className="block text-sm font-medium mb-2" htmlFor="confirm">Confirm Password</label>
            <input
              id="confirm"
              type="password"
              className="w-full p-2 border border-gray-300 rounded mb-4"
              value={confirm}
              onChange={e => { setConfirm(e.target.value); setError(''); }}
              required
              minLength={6}
              aria-invalid={!!error && password !== confirm}
              aria-describedby={!!error && password !== confirm ? 'reset-confirm-error' : undefined}
            />
            {error && (
              <div id="reset-form-error" className="text-red-700 bg-red-100 border border-red-300 rounded p-2 mb-2" role="alert">
                {error}
              </div>
            )}
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
              disabled={loading}
            >
              {loading ? <LoadingSpinner label="Resetting..." /> : 'Reset Password'}
            </button>
          </>
        )}
      </form>
    </main>
  );
};

export default ResetPassword;
