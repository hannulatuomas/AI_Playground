import React, { useEffect, useState } from 'react';
import { fetchSubscriptionTiers, SubscriptionTier } from '../config/subscriptionTiers';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';

import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

const UserProfile: React.FC = () => {
  const { user, refreshUser, logout } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [subscriptionTier, setSubscriptionTier] = useState<string>('');
  const [tiers, setTiers] = useState<SubscriptionTier[]>([]);
  const [tiersLoading, setTiersLoading] = useState<boolean>(true);
  const [tiersError, setTiersError] = useState<string | null>(null);

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const navigate = useNavigate();

  // Fetch profile/tier on mount and when window regains focus
  useEffect(() => {
    let cancelled = false;
    async function fetchProfileAndTier() {
      setError('');
      setLoading(true);
      try {
        // Removed refreshUser call to avoid redundant /api/auth/me requests.
        // User state is already refreshed by AuthProvider on app mount and after login/logout.
        setEmail(user?.email || '');
        setTiersLoading(true);
        const [statusRes, tiersRes] = await Promise.all([
          fetch('/api/stripe/status', { credentials: 'include' }),
          fetchSubscriptionTiers(),
        ]);
        if (!cancelled) {
          let tierLabel = 'Unknown';
          let tierKey = 'free';
          if (statusRes.ok) {
            const statusData = await statusRes.json();
            if (statusData.tierKey) {
              tierKey = statusData.tierKey;
            } else if (statusData.active) {
              tierKey = 'pro';
            } else {
              tierKey = 'free';
            }
          }
          setTiers(tiersRes as SubscriptionTier[]);
          const found = (tiersRes as SubscriptionTier[]).find(t => t.key === tierKey);
          tierLabel = found ? found.label : tierKey;
          setSubscriptionTier(tierLabel);
          setTiersLoading(false);
        }
      } catch {
        if (!cancelled) {
          setError('Network error');
          setTiersError('Failed to load subscription tiers');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    fetchProfileAndTier();
    function handleFocus() {
      setLoading(true);
      setError('');
      setTiersError(null);
      fetchProfileAndTier();
    }
    window.addEventListener('focus', handleFocus);
    return () => {
      cancelled = true;
      window.removeEventListener('focus', handleFocus);
    };
  }, [user?.email]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    // Client-side validation
    if (!password || password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    try {
      const res = await fetch('/api/profile/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ password }),
      });
      const data = await res.json();
      if (res.ok) {
        setMessage('Password updated successfully!');
        setPassword('');
        setConfirmPassword('');
      } else {
        setError(data.message || 'Failed to update profile');
      }
    } catch {
      setError('Network error');
    }
  };


  const handleDeleteAccount = async () => {
    setDeleteLoading(true);
    try {
      const res = await fetch('/api/profile/delete', {
        method: 'POST',
        credentials: 'include',
      });
      if (res.ok) {
        await logout();
        navigate('/');
      } else {
        setDeleteError('Failed to delete account');
      }
    } catch {
      setDeleteError('Network error');
    } finally {
      setDeleteLoading(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading profile..." />;

  return (
    <main className="flex items-center justify-center min-h-screen bg-gray-50 px-2">
      <div className="bg-white p-6 sm:p-8 rounded shadow w-full max-w-xs sm:max-w-md flex flex-col gap-4 mt-0 mb-0">

      <h2 className="text-2xl font-bold mb-4">User Profile</h2>
      {error && !loading && (
        <div id="profile-form-error" className="mb-4 text-red-700 bg-red-100 border border-red-300 rounded p-2" role="alert">
          {error}
        </div>
      )}
      <div className="mb-6">
        <label className="block text-sm font-medium mb-1">Email</label>
        <input
          type="email"
          value={user?.email || ''}
          readOnly
          className="w-full border rounded px-3 py-2 bg-gray-100 text-gray-700 cursor-not-allowed"
        />
      </div>
      <div className="mb-6">
        <label className="block text-sm font-medium mb-1">Subscription Tier</label>
        <div className="mt-1 p-2 border border-gray-300 rounded bg-gray-50 min-h-[40px] flex items-center">
          {tiersLoading ? (
            <LoadingSpinner label="Loading subscription tier..." className="py-2" />
          ) : tiersError ? (
            <EmptyState message={tiersError} />
          ) : (
            <span>{subscriptionTier}</span>
          )}
        </div>
        <button
          type="button"
          className="w-full bg-purple-600 text-white py-2 rounded hover:bg-purple-700 mt-3 mb-2 transition"
          title="Upgrade, downgrade, or cancel your subscription"
          onClick={() => navigate('/upgrade')}
        >
          Manage Subscription
        </button>
      </div>
      <form onSubmit={handleSave} className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium mb-1">Change Password</label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2 mb-2"
            value={password}
            onChange={e => { setPassword(e.target.value); setError(''); }}
            placeholder="New password"
            required
            minLength={6}
            aria-invalid={!!error && password.length < 6}
            aria-describedby={!!error && password.length < 6 ? 'profile-password-error' : undefined}
          />
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={confirmPassword}
            onChange={e => { setConfirmPassword(e.target.value); setError(''); }}
            placeholder="Confirm new password"
            required
            minLength={6}
            aria-invalid={!!error && password !== confirmPassword}
            aria-describedby={!!error && password !== confirmPassword ? 'profile-confirm-error' : undefined}
          />
        </div>
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? 'Updating...' : 'Update Password'}
        </button>
      </form>
      {message && <p className="mt-4 text-green-600">{message}</p>}
      <button
        type="button"
        className="w-full bg-gray-700 text-white py-2 rounded hover:bg-gray-800 mt-2"
        onClick={async () => {
          try {
            if (logout) {
              await logout();
              navigate('/');
            }
          } catch (e) {
            setError('Logout failed. Please try again.');
          }
        }}
        aria-label="Log out of your account"
      >
        Log Out
      </button>
      <button
        type="button"
        className="w-full bg-red-600 text-white py-2 rounded hover:bg-red-700 mt-2"
        onClick={() => setShowDeleteConfirm(true)}
      >
        Delete Account
      </button>
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded p-4 w-full max-w-sm">
            <h2 className="text-lg font-bold mb-2">Confirm Delete Account</h2>
            <p>Are you sure you want to delete your account?</p>
            <div className="flex justify-between mt-4">
              <button
                type="button"
                className="bg-gray-200 py-2 px-4 rounded hover:bg-gray-300"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
              <button
                type="button"
                className="bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
                onClick={handleDeleteAccount}
                disabled={deleteLoading}
              >
                {deleteLoading ? 'Deleting...' : 'Delete'}
              </button>
            </div>

          </div>
        </div>
      )}
    
    </div>
    </main>
  );
};

export default UserProfile;
