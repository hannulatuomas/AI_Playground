import React, { useEffect, useState } from 'react';
import SubscriptionTiers from '../components/SubscriptionTiers';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useAuth } from '../auth/useAuth';
import { useNavigate } from 'react-router-dom';

const UpgradeSubscription: React.FC = () => {
  const { user, loading } = useAuth();
  const [currentTier, setCurrentTier] = useState<string>('');
  const [tiersLoading, setTiersLoading] = useState(true);
  const [tiersError, setTiersError] = useState<string | null>(null);
  const [subscriptionTiers, setSubscriptionTiers] = useState<any[]>([]);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    async function fetchStatusAndTiers() {
      try {
        setTiersLoading(true);
        const [statusRes, tiersRes] = await Promise.all([
          fetch('/api/stripe/status', { credentials: 'include' }),
          import('../config/subscriptionTiers').then(mod => mod.fetchSubscriptionTiers()),
        ]);
        if (!cancelled) {
          let tierKey = 'free';
          if (statusRes.ok) {
            const data = await statusRes.json();
            if (data.tierKey) tierKey = data.tierKey;
            else if (data.active) tierKey = 'pro';
          }
          setCurrentTier(tierKey);
          setSubscriptionTiers(tiersRes);
          setTiersLoading(false);
        }
      } catch {
        if (!cancelled) {
          setTiersError('Failed to load subscription tiers');
          setTiersLoading(false);
        }
      }
    }
    fetchStatusAndTiers();
    return () => { cancelled = true; };
  }, []);

  const handleSelect = async (tierKey: string) => {
    setActionLoading(tierKey);
    setError(null);
    if (tierKey === 'free') {
      // Downgrade/cancel subscription
      try {
        const res = await fetch('/api/stripe/cancel-subscription', {
          method: 'POST',
          credentials: 'include',
        });
        const data = await res.json();
        if (res.ok) {
          setError(null);
          alert('Subscription cancelled. You are now on the Free tier.');
          window.location.reload();
        } else {
          setError(data.message || 'Failed to cancel subscription');
        }
      } catch (err) {
        setError('Network error');
      }
      setActionLoading(null);
      return;
    }
    try {
      const res = await fetch('/api/stripe/create-subscription', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ tierKey }),
      });
      const data = await res.json();
      if (res.ok && data.url) {
        window.location.href = data.url;
      } else {
        setError(data.message || 'Failed to create Stripe session');
      }
    } catch (err) {
      setError('Network error');
    }
    setActionLoading(null);
  };


  if (loading) return <div>Loading...</div>;
  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <main className="flex flex-col items-center justify-center min-h-screen gap-4 bg-gray-50 px-2">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-center">Manage Subscription</h1>
      {tiersLoading ? (
        <LoadingSpinner label="Loading subscription tiers..." />
      ) : tiersError ? (
        <EmptyState message={tiersError} />
      ) : (
        <SubscriptionTiers onSelect={handleSelect} currentTierKey={currentTier} />
      )}
      {actionLoading && <LoadingSpinner label="Processing..." />}
      {/* Only show one error: if tiersError, show above; otherwise show action error below */}
      {!tiersError && error && <EmptyState message={error} />}
    </main>
  );
};

export default UpgradeSubscription;
