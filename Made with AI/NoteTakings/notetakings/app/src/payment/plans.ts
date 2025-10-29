import { requireNodeEnvVar } from '../server/utils';

export type SubscriptionStatus = 'past_due' | 'cancel_at_period_end' | 'active' | 'deleted';

export enum PaymentPlanId {
  Free = 'free',
  Basic = 'basic',
  Pro = 'pro',
  Ultimate = 'ultimate',
}

export interface PaymentPlan {
  // Returns the id under which this payment plan is identified on your payment processor. 
  // E.g. this might be price id on Stripe, or variant id on LemonSqueezy.
  getPaymentProcessorPlanId: () => string;
  effect: PaymentPlanEffect;
}

export type PaymentPlanEffect = { kind: 'subscription' } | { kind: 'credits'; amount: number };

export const paymentPlans: Record<PaymentPlanId, PaymentPlan> = {
  [PaymentPlanId.Free]: {
    getPaymentProcessorPlanId: () => requireNodeEnvVar('PAYMENTS_FREE_SUBSCRIPTION_PLAN_ID'),
    effect: { kind: 'subscription' },
  },
  [PaymentPlanId.Basic]: {
    getPaymentProcessorPlanId: () => requireNodeEnvVar('PAYMENTS_BASIC_SUBSCRIPTION_PLAN_ID'),
    effect: { kind: 'subscription' },
  },
  [PaymentPlanId.Pro]: {
    getPaymentProcessorPlanId: () => requireNodeEnvVar('PAYMENTS_PRO_SUBSCRIPTION_PLAN_ID'),
    effect: { kind: 'subscription' },
  },
  [PaymentPlanId.Ultimate]: {
    getPaymentProcessorPlanId: () => requireNodeEnvVar('PAYMENTS_ULTIMATE_PLAN_ID'),
    effect: { kind: 'subscription' },
  },
};

export function prettyPaymentPlanName(planId: PaymentPlanId): string {
  const planToName: Record<PaymentPlanId, string> = {
    [PaymentPlanId.Free]: 'Free',
    [PaymentPlanId.Basic]: 'Basic',
    [PaymentPlanId.Pro]: 'Pro',
    [PaymentPlanId.Ultimate]: 'Ultimate',
  };
  return planToName[planId];
}

export function parsePaymentPlanId(planId: string): PaymentPlanId {
  if ((Object.values(PaymentPlanId) as string[]).includes(planId)) {
    return planId as PaymentPlanId;
  } else {
    throw new Error(`Invalid PaymentPlanId: ${planId}`);
  }
}

export function getSubscriptionPaymentPlanIds(): PaymentPlanId[] {
  return Object.values(PaymentPlanId).filter((planId) => paymentPlans[planId].effect.kind === 'subscription');
}
