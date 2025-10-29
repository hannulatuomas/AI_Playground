import React from 'react';
import { fetchSubscriptionTiers, SubscriptionTier } from '../config/subscriptionTiers';
import LoadingSpinner from './LoadingSpinner';
import EmptyState from './EmptyState';

interface Props {
  onSelect: (tierKey: string) => void;
  currentTierKey?: string;
  onFreeTier?: () => void;
}

const SubscriptionTiers: React.FC<Props> = ({ onSelect, currentTierKey, onFreeTier }) => {
  const [tiers, setTiers] = React.useState<SubscriptionTier[]>([]);
  const [loading, setLoading] = React.useState<boolean>(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    fetchSubscriptionTiers()
      .then(data => { if (!cancelled) { setTiers(data); setLoading(false); } })
      .catch(err => { if (!cancelled) { setError('Failed to load subscription tiers'); setLoading(false); } });
    return () => { cancelled = true; };
  }, []);

  if (loading) return <LoadingSpinner label="Loading subscription tiers..." />;
  if (error) return <EmptyState message={error} />;
  if (!tiers.length) return <EmptyState message="No subscription tiers available." />;

  return (
    <div className="w-full max-w-screen-xl mx-auto px-2 sm:px-4 md:px-8 pb-8">
      <div className="flex flex-col md:flex-row gap-6 md:gap-8 justify-center items-center md:items-stretch w-full">
        {tiers.map((tier: SubscriptionTier) => {
          const isPrimary = !!tier.primary;
          const isFree = tier.key === 'free';
          return (
            <div
              key={tier.key}
              className={`relative border rounded-lg shadow-lg flex flex-col justify-between items-stretch transition-transform duration-200 w-full max-w-xs sm:max-w-sm md:max-w-[360px] ${isPrimary ? 'p-6 sm:p-8 scale-105 hover:scale-110 focus-within:scale-110 md:w-[400px] md:p-8 md:scale-105 md:hover:scale-110 md:focus-within:scale-110 border-green-500 ring-2 ring-green-400 bg-green-50 focus-visible:ring-green-300' : 'p-4 sm:p-6 md:w-[360px] md:p-6 border-gray-200 bg-white focus-visible:ring-blue-300'} hover:scale-105 focus-within:scale-105 focus-visible:ring-4 z-10`}
            >
              {isPrimary && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-green-500 text-white text-xs font-semibold uppercase tracking-wide shadow-md z-20">
                  Most Popular
                </div>
              )}
              <div className="flex flex-col items-center pt-8 min-h-[120px] justify-start">
                <h3 className={`text-xl font-bold mb-2 ${isPrimary ? 'text-green-700' : ''}`}>{tier.label}</h3>
                <ul className="mb-4 list-disc list-inside text-sm text-gray-700 text-left w-full">
                  {tier.features.map((f: string, i: number) => (
                    <li key={i}>{f}</li>
                  ))}
                </ul>
              </div>
              <div className="flex flex-row w-full gap-2 mt-auto">
                {currentTierKey === tier.key ? (
                  <button
                    className="w-full py-2 rounded font-semibold bg-gray-300 text-gray-700 cursor-not-allowed border border-gray-400"
                    disabled
                  >
                    Current Plan
                  </button>
                ) : (
                  <button
                    className={`w-full py-2 rounded font-semibold transition-colors duration-150
                      ${isPrimary ? 'bg-green-500 text-white hover:bg-green-600' :
                        isFree ? 'bg-gray-200 text-gray-800 hover:bg-gray-300' :
                        'bg-blue-600 text-white hover:bg-blue-700'}
                    `}
                    onClick={() => {
                      if (isFree && typeof onFreeTier === 'function') {
                        onFreeTier();
                      } else {
                        onSelect(tier.key);
                      }
                    }}
                  >
                    {tier.buttonText || (isFree ? 'Start Free' : 'Buy Now')}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SubscriptionTiers;
