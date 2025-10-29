import Stripe from 'stripe';
import { setStripeCustomerId, getStripeCustomerId } from './userService';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2022-11-15' });

export async function createOrGetCustomer(userId: string, email: string): Promise<string> {
  let customerId = getStripeCustomerId(userId);
  if (customerId) return customerId;
  // Try to find by email (idempotent for template)
  const customers = await stripe.customers.list({ email, limit: 1 });
  if (customers.data.length > 0) {
    customerId = customers.data[0].id;
  } else {
    const customer = await stripe.customers.create({ email, metadata: { userId } });
    customerId = customer.id;
  }
  setStripeCustomerId(userId, customerId);
  return customerId;
}

import { getTierByKey } from '../utils/subscriptionTiers';

export async function createSubscriptionSession(userId: string, email: string, tierKey: string) {
  const tier = getTierByKey(tierKey);
  if (!tier || !tier.priceId) {
    throw new Error('Invalid subscription tier');
  }
  const priceId = tier.priceId;
  const customerId = await createOrGetCustomer(userId, email);
  const session = await stripe.checkout.sessions.create({
    payment_method_types: ['card'],
    mode: 'subscription',
    customer: customerId,
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.CLIENT_URL}/profile?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${process.env.CLIENT_URL}/buy`,
    metadata: { userId, tierKey },
  });
  return session.url;
}

export async function getSubscriptionStatus(userId: string) {
  const customerId = getStripeCustomerId(userId);
  if (!customerId) return { active: false };
  // Find active subscriptions for this customer
  const subs = await stripe.subscriptions.list({ customer: customerId, status: 'all', limit: 1 });
  const active = subs.data.some(s => s.status === 'active' || s.status === 'trialing');
  return { active };
}
