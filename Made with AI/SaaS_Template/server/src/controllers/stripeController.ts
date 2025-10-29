import type { Request, Response } from 'express';
import Stripe from 'stripe';
import { createSubscriptionSession, getSubscriptionStatus } from '../services/stripeService';
import { getSubscriptionTiers } from '../utils/subscriptionTiers';
import { setSubscriptionStatus, findUserById } from '../services/userService';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, { apiVersion: '2022-11-15' });

// POST /api/stripe/create-subscription
export async function createSubscription(req: Request, res: Response, next: Function) {
  try {
    const user = (req as any).user; // set by auth middleware in real app
    // For template: accept email from body if no auth
    const email = user?.email || req.body.email;
    const userId = user?.id || 'anonymous';
    const tierKey = req.body.tierKey;
    if (!email) {
      return res.status(400).json({ error: 'Email required' });
    }
    if (!tierKey) {
      return res.status(400).json({ error: 'Subscription tier required' });
    }
    const url = await createSubscriptionSession(userId, email, tierKey);
    res.json({ url });
  } catch (err: any) {
    next({ status: 500, message: 'Stripe session error', details: String(err?.message || err) });
  }
}

// POST /api/stripe/webhook
export async function handleWebhook(req: Request, res: Response, next: Function) {
  const sig = req.headers['stripe-signature'] as string;
  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err: any) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  try {
    // Handle subscription events
    if (
      event.type === 'customer.subscription.created' ||
      event.type === 'customer.subscription.updated' ||
      event.type === 'customer.subscription.deleted'
    ) {
      const subscription = event.data.object as Stripe.Subscription;
      const customerId = subscription.customer as string;
      // Find user by stripeCustomerId
      const allUsers = require('../services/userService');
      const usersArr = allUsers && allUsers.findUserById ? Object.values(allUsers)[0] : [];
      const user = Array.isArray(usersArr)
        ? usersArr.find((u: any) => u.stripeCustomerId === customerId)
        : undefined;
      if (user) {
        setSubscriptionStatus(user.id, subscription.status as any);
      } else {
        // Not an error, just log
      }
    }
    res.json({ received: true });
  } catch (err: any) {
    next({ status: 500, message: 'Internal server error processing Stripe webhook', details: String(err?.message || err) });
  }
}

// GET /api/stripe/tiers
export function getTiers(req: Request, res: Response, next: Function) {
  try {
    const tiers = getSubscriptionTiers();
    res.json(tiers);
  } catch (err: any) {
    next({ status: 500, message: 'Failed to load subscription tiers', details: String(err?.message || err) });
  }
}

// GET /api/stripe/status
export async function subscriptionStatus(req: Request, res: Response, next: Function) {
  const user = (req as any).user;
  const userId = user?.id || 'anonymous';
  const status = await getSubscriptionStatus(userId);
  res.json(status);
}
