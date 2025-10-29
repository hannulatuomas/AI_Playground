import React, { useState } from 'react';
import { useAuth } from '../auth/useAuth';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { Link, useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const { register, error, googleLogin } = useAuth();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const navigate = useNavigate();

  const validateEmail = (value: string) => {
    // Simple email regex
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setFormError(null);
    setSuccess(null);
    // Client-side validation
    if (!validateEmail(email)) {
      setFormError('Please enter a valid email address');
      return;
    }
    if (password.length < 6) {
      setFormError('Password must be at least 6 characters');
      return;
    }
    if (password !== confirmPassword) {
      setFormError('Passwords do not match');
      return;
    }
    setLoading(true);
    const result = await register(email, password);
    setLoading(false);
    if (result) {
      navigate('/verify-email', { state: { email, success: 'Registration successful! Please check your email to verify your account.' } });
    } else {
      setFormError(error || 'Registration failed. Please check your details or try a different email.');
    }
  };


  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
      <form onSubmit={handleSubmit} className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-sm flex flex-col gap-4">
        <h2 className="text-xl font-bold mb-2 text-center">Register</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => { setEmail(e.target.value); setFormError(null); }}
          className="border px-2 py-1 rounded"
          required
          aria-invalid={!!formError && !validateEmail(email)}
          aria-describedby={!!formError && !validateEmail(email) ? 'register-email-error' : undefined}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => { setPassword(e.target.value); setFormError(null); }}
          className="border px-2 py-1 rounded"
          required
          minLength={6}
          aria-invalid={!!formError && password.length < 6}
          aria-describedby={!!formError && password.length < 6 ? 'register-password-error' : undefined}
        />
        <input
          type="password"
          placeholder="Confirm Password"
          value={confirmPassword}
          onChange={e => { setConfirmPassword(e.target.value); setFormError(null); }}
          className="border px-2 py-1 rounded"
          required
          minLength={6}
          aria-invalid={!!formError && password !== confirmPassword}
          aria-describedby={!!formError && password !== confirmPassword ? 'register-confirm-error' : undefined}
        />
        {formError && (
          <div id="register-form-error" className="text-red-700 bg-red-100 border border-red-300 rounded p-2 mb-2" role="alert">
            {formError}
          </div>
        )}
        <button
          type="submit"
          className="bg-blue-600 text-white py-2 rounded disabled:opacity-50 min-w-[120px] relative flex items-center justify-center"
          disabled={loading}
        >
          <span className={loading ? 'invisible' : 'block'}>Register</span>
          {loading && (
            <span className="absolute inset-0 flex items-center justify-center">
              <LoadingSpinner label="Registering..." />
            </span>
          )}
        </button>
        <button
          type="button"
          onClick={googleLogin}
          className="bg-red-500 text-white py-2 rounded min-w-[160px]"
        >
          Register with Google
        </button>
        {success && (
          <div className="text-green-700 text-base font-semibold border border-green-400 rounded p-2 bg-green-50 flex flex-col items-center gap-2">
            {success}
            <button
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              onClick={() => navigate('/verify-email', { state: { email, registered: true } })}
              type="button"
            >
              Go to Verify Email
            </button>
          </div>
        )}

        <div className="text-sm mt-2">Already have an account? <Link to="/login" className="text-blue-600">Login</Link></div>
      </form>
    </main>
  );
};

export default Register;
