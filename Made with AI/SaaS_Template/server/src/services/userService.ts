import bcrypt from 'bcryptjs';
import { v4 as uuidv4 } from 'uuid';

export interface User {
  id: string;
  email: string;
  passwordHash?: string; // Not present for Google users
  provider: 'local' | 'google';
  stripeCustomerId?: string;
  subscriptionStatus?: 'active' | 'inactive' | 'canceled' | 'past_due' | 'trialing' | 'unpaid';
  emailVerified?: boolean;
  verificationToken?: string;
  resetPasswordToken?: string;
  resetPasswordExpires?: number; // unix ms timestamp
}

// In-memory user store (for template)
export const users: User[] = [];

export function removeUserById(id: string): boolean {
  const idx = users.findIndex(u => u.id === id);
  if (idx !== -1) {
    users.splice(idx, 1);
    return true;
  }
  return false;
}

export function findUserByEmail(email: string): User | undefined {
  return users.find(u => u.email === email);
}

export function createUser(email: string, password?: string, provider: 'local' | 'google' = 'local'): User {
  const user: User = {
    id: uuidv4(),
    email,
    provider,
    passwordHash: provider === 'local' && password ? bcrypt.hashSync(password, 10) : undefined,
    emailVerified: provider === 'local' ? false : true,
    verificationToken: provider === 'local' ? uuidv4() : undefined,
  };
  users.push(user);
  return user;
}

export function validatePassword(user: User, password: string): boolean {
  if (!user.passwordHash) return false;
  return bcrypt.compareSync(password, user.passwordHash);
}

export function setResetPasswordToken(user: User, token: string, expires: number) {
  user.resetPasswordToken = token;
  user.resetPasswordExpires = expires;
}

export function clearResetPasswordToken(user: User) {
  user.resetPasswordToken = undefined;
  user.resetPasswordExpires = undefined;
}

export function setPassword(user: User, newPassword: string) {
  user.passwordHash = bcrypt.hashSync(newPassword, 10);
}

export function findUserById(id: string): User | undefined {
  return users.find(u => u.id === id);
}

export function setStripeCustomerId(userId: string, customerId: string) {
  const user = findUserById(userId);
  if (user) user.stripeCustomerId = customerId;
}

export function setSubscriptionStatus(userId: string, status: User['subscriptionStatus']) {
  const user = findUserById(userId);
  if (user) user.subscriptionStatus = status;
}

export function getStripeCustomerId(userId: string): string | undefined {
  const user = findUserById(userId);
  return user?.stripeCustomerId;
}

export function getSubscriptionStatus(userId: string): User['subscriptionStatus'] | undefined {
  const user = findUserById(userId);
  return user?.subscriptionStatus;
}
