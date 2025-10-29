import React, { useEffect, useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

const VerifyEmail: React.FC = () => {
  const query = useQuery();
  const token = query.get('token');
  const [status, setStatus] = useState<'pending'|'success'|'error'>('pending');
  const [message, setMessage] = useState('');
  const navigate = useNavigate();
  const location = useLocation() as any;
  const { resendVerification } = useAuth();
  const registeredEmail = location.state?.email;
  const successMessage = location.state?.success;

  const hasVerified = useRef(false);
  useEffect(() => {
    if (!token || hasVerified.current) {
      return;
    }
    hasVerified.current = true;
    fetch(`/api/auth/verify-email?token=${token}`)
      .then(async res => {
        const data = await res.json();
        if (res.ok) {
          setStatus('success');
          setMessage('Your email has been verified! Redirecting to login...');
          setTimeout(() => navigate('/login'), 2000);
        } else {
          setStatus('error');
          setMessage(data.message || 'Verification failed.');
        }
      })
      .catch(() => {
        setStatus('error');
        setMessage('Network error during verification.');
      });
  }, [token, registeredEmail, navigate]);

  const [resendEmail, setResendEmail] = useState(registeredEmail || '');
  const [resendStatus, setResendStatus] = useState<'idle'|'sending'|'sent'|'error'>('idle');

  const handleResend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!resendEmail) return;
    setResendStatus('sending');
    const msg = await resendVerification(resendEmail);
    if (msg && msg.toLowerCase().includes('sent')) {
      setResendStatus('sent');
      setMessage('Verification email resent!');
    } else {
      setResendStatus('error');
      setMessage(msg || 'Failed to resend verification email.');
    }
  };


  return (
    <main className="flex flex-col items-center justify-center h-screen">
      <div className="bg-white p-8 rounded shadow w-96 flex flex-col gap-4 items-center">
        <h2 className="text-xl font-bold mb-2">Verify Your Email</h2>
        {successMessage && (
          <div className="text-green-700 bg-green-100 border border-green-300 rounded p-2 mb-2 text-center" role="alert">
            {successMessage}
          </div>
        )}
        <div className={`text-${status === 'success' ? 'green' : 'red'}-600 text-center`}>{message}</div>
        {(registeredEmail || status === 'error') && (
          <form onSubmit={handleResend} className="flex flex-col items-center gap-2 mt-2 w-full">
            <input
              type="email"
              placeholder="Enter your email to resend verification"
              value={resendEmail}
              onChange={e => setResendEmail(e.target.value)}
              className="border px-2 py-1 rounded w-full"
              required
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded"
              disabled={resendStatus==='sending'}
            >
              {resendStatus==='sending' ? 'Sending...' : 'Resend Verification Email'}
            </button>
          </form>
        )}
        <button onClick={() => navigate('/login')} className="mt-4 underline text-blue-600">Go to Login</button>
        <button onClick={() => navigate('/')} className="mt-2 underline text-blue-600">Back to Home</button>
      </div>
    </main>
  );
};

export default VerifyEmail;
