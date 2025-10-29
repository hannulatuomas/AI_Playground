import rateLimit from 'express-rate-limit';
import type { Options as RateLimitOptions } from 'express-rate-limit';

// Factory for creating custom rate limiters
export const createRateLimiter = (options?: Partial<RateLimitOptions>) =>
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // default, override per use
    standardHeaders: true,
    legacyHeaders: false,
    message: 'Too many requests, please try again later.',
    ...options,
  });

// Global limiter: applies to all endpoints
export const globalLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per 15 min per IP
  message: 'Too many requests, please try again later.'
});

// Auth endpoints limiter: stricter for /api/auth
export const authLimiter = createRateLimiter({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10, // 10 requests per 15 min per IP
  message: 'Too many authentication attempts, please try again later.'
});

// Verification email resend limiter: strictest (per-IP)
export const resendVerificationLimiter = createRateLimiter({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3, // 3 requests per hour per IP
  message: 'Too many verification email requests, please try again in an hour.'
});

// Additional per-email limiter for resend verification endpoint
// Combine this with resendVerificationLimiter for best protection (per-IP + per-email)
export const resendVerificationPerEmailLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 3, // 3 requests per hour per email
  keyGenerator: (req) => {
    // Use email from body (lowercased); fallback to IP if not present
    return (req.body && req.body.email && typeof req.body.email === 'string')
      ? req.body.email.toLowerCase()
      : req.ip;
  },
  message: 'Too many verification email requests for this email. Please try again in an hour.',
  standardHeaders: true,
  legacyHeaders: false,
});

