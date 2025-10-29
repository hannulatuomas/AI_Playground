import React, { useState } from 'react';
import { useAuth } from '../auth/useAuth';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { Link, useNavigate, useLocation } from 'react-router-dom';

const Login: React.FC = () => {
  const { login, error, googleLogin, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const location = useLocation() as any;
  const [successMsg, setSuccessMsg] = useState(location.state?.success || '');
  const [pageError, setPageError] = useState(location.state?.error || '');

  // Sync pageError with AuthProvider error
  React.useEffect(() => {
    if (error) setPageError(error);
  }, [error]);

  // Navigate to profile if login succeeded
  React.useEffect(() => {
    if (user) navigate('/profile');
  }, [user, navigate]);

  // Clear state after displaying
  React.useEffect(() => {
    if (location.state?.success || location.state?.error) {
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, []);

  const validateEmail = (value: string) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg('');
    setPageError('');
    // Client-side validation
    if (!validateEmail(email)) {
      setPageError('Please enter a valid email address');
      return;
    }
    if (!password || password.length < 6) {
      setPageError('Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    await login(email, password);
    setLoading(false);
    // Navigation now handled in useEffect when user is set
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-sm flex flex-col gap-4">
        <h2 className="text-xl font-bold mb-2 text-center">Login</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => { setEmail(e.target.value); setPageError(''); }}
          className="border px-2 py-1 rounded"
          required
          aria-invalid={!!pageError && !validateEmail(email)}
          aria-describedby={!!pageError && !validateEmail(email) ? 'login-email-error' : undefined}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => { setPassword(e.target.value); setPageError(''); }}
          className="border px-2 py-1 rounded"
          required
          minLength={6}
          aria-invalid={!!pageError && password.length < 6}
          aria-describedby={!!pageError && password.length < 6 ? 'login-password-error' : undefined}
        />
        {pageError && <EmptyState message={pageError} />}

        <button
          type="submit"
          className="bg-blue-600 text-white py-2 rounded disabled:opacity-50 min-w-[120px] relative flex items-center justify-center"
          disabled={loading}
        >
          <span className={loading ? 'invisible' : 'block'}>Login</span>
          {loading && (
            <span className="absolute inset-0 flex items-center justify-center">
              <LoadingSpinner label="Logging in..." />
            </span>
          )}
        </button>
        <button
          type="button"
          onClick={googleLogin}
          className="bg-red-500 text-white py-2 rounded min-w-[160px]"
        >
          Login with Google
        </button>
        {successMsg && <div className="text-green-700 text-base font-semibold border border-green-400 rounded p-2 bg-green-50 mb-2">{successMsg}</div>}
        <div className="text-sm mt-2">
          <Link to="/forgot-password" className="text-blue-600">Forgot your password?</Link>
        </div>
        <div className="text-sm mt-2">Don't have an account? <Link to="/register" className="text-blue-600">Register</Link></div>
      </form>
    </main>
  );
};

export default Login;
