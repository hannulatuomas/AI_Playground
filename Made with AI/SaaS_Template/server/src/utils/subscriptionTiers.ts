import path from 'path';
import fs from 'fs';

export interface SubscriptionTier {
  key: string;
  label: string;
  priceId: string;
  features: string[];
  buttonText?: string;
  primary?: boolean;
}

export function getSubscriptionTiers(): SubscriptionTier[] {
  const configPath = path.resolve(__dirname, '../../config/subscriptionTiers.json');
  if (!fs.existsSync(configPath)) {
    throw new Error(`subscriptionTiers.json not found in server/config. Checked: ${configPath}`);
  }
  const raw = fs.readFileSync(configPath, 'utf-8');
  return JSON.parse(raw);
}

export function getTierByKey(key: string): SubscriptionTier | undefined {
  return getSubscriptionTiers().find(tier => tier.key === key);
}
