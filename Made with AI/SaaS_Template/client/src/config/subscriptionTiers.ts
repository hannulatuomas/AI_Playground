export interface SubscriptionTier {
  key: string;
  label: string;
  priceId: string;
  features: string[];
  buttonText?: string;
  primary?: boolean;
}

// Helper to fetch tiers from backend
export async function fetchSubscriptionTiers(): Promise<SubscriptionTier[]> {
  const res = await fetch('/api/stripe/tiers');
  if (!res.ok) throw new Error('Failed to fetch subscription tiers');
  return res.json();
}

