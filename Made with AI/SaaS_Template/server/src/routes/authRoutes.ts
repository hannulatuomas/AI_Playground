const express = require('express');
import type { Request, Response } from 'express';
const router = express.Router();

import { register, login, logout, me, verifyEmail, resendVerification } from '../controllers/authController';
import { resendVerificationLimiter, resendVerificationPerEmailLimiter } from '../middleware/rateLimiter';
import {
  validateRegister,
  validateLogin,
  validateEmail,
  validateResetPassword,
  handleValidationErrors
} from '../middleware/validation';

// POST /api/auth/register
router.post(
  '/register',
  validateRegister,
  handleValidationErrors,
  register
);

// POST /api/auth/login
router.post(
  '/login',
  validateLogin,
  handleValidationErrors,
  login
);

// GET /api/auth/google
import { googleAuthRedirect, googleAuthCallback } from '../controllers/googleOAuth';

router.get('/google', googleAuthRedirect);
router.get('/google/callback', googleAuthCallback);

// Email verification endpoints
router.get('/verify-email', verifyEmail);
// Apply both per-IP and per-email limiter for robust protection
router.post(
  '/resend-verification',
  resendVerificationLimiter,           // per-IP
  resendVerificationPerEmailLimiter,   // per-email
  validateEmail,
  handleValidationErrors,
  resendVerification
);

// Password reset endpoints
import { requestPasswordReset, resetPassword } from '../controllers/authController';
router.post('/request-password-reset', validateEmail, handleValidationErrors, requestPasswordReset);
router.post('/reset-password', validateResetPassword, handleValidationErrors, resetPassword);

// GET /api/auth/me
router.get('/me', me);

// GET /api/auth/logout
router.get('/logout', logout);

export default router;
