import React, { useEffect, useState } from 'react';
import SubscriptionTiers from '../components/SubscriptionTiers';
import LoadingSpinner from '../components/LoadingSpinner';
import EmptyState from '../components/EmptyState';
import { useAuth } from '../auth/useAuth';
import { useNavigate } from 'react-router-dom';

const BuySubscription: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && user) {
      navigate('/upgrade');
    }
  }, [user, authLoading, navigate]);

  const handleSelect = async (tierKey: string) => {
    setLoading(tierKey);
    setError(null);
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
    setLoading(null);
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen gap-4 bg-gray-50 px-2">
      <h1 className="text-2xl sm:text-3xl font-bold mb-6 text-center">Choose a Subscription Plan</h1>
      <SubscriptionTiers onSelect={handleSelect} onFreeTier={() => window.location.href = '/register'} />
      {loading && <LoadingSpinner label="Redirecting to Stripe..." />}
      {error && <EmptyState message={error} />}
    </main>
  );
};

export default BuySubscription;
