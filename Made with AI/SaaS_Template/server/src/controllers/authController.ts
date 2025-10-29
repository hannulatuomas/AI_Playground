import jwt from 'jsonwebtoken';
import { findUserByEmail, createUser, validatePassword, setResetPasswordToken, clearResetPasswordToken, setPassword } from '../services/userService';
import type { Request, Response } from 'express';
import { validationResult } from 'express-validator';
import { sendVerificationEmail, sendPasswordResetEmail } from '../services/emailService';

function issueToken(user: { id: string; email: string }) {
  return jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET!, { expiresIn: '7d' });
}

export async function register(req: Request, res: Response, next: Function) {
  try {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
    if (findUserByEmail(email)) return res.status(409).json({ error: 'User already exists' });
    const user = createUser(email, password, 'local');
    if (user.verificationToken) {
      try {
        await sendVerificationEmail(user.email, user.verificationToken);
      } catch (err) {
        return next({ status: 500, message: 'Failed to send verification email', details: String(err) });
      }
    }
    const token = issueToken(user);
    res.cookie('token', token, { httpOnly: true, sameSite: 'lax' });
    res.json({ id: user.id, email: user.email, emailVerified: user.emailVerified });
  } catch (err) {
    next(err);
  }
}

export async function login(req: Request, res: Response, next: Function) {
  try {
    const { email, password } = req.body;
    if (!email || !password) return res.status(400).json({ error: 'Email and password required' });
    const user = findUserByEmail(email);
    if (!user || !validatePassword(user, password)) return res.status(401).json({ error: 'Invalid credentials' });
    // Block login if user is not verified (for local accounts)
    if (user.provider === 'local' && !user.emailVerified) {
      return res.status(403).json({ error: 'Please verify your email before logging in.' });
    }
    const token = issueToken(user);
    res.cookie('token', token, { httpOnly: true, sameSite: 'lax' });
    res.json({ id: user.id, email: user.email, emailVerified: user.emailVerified });
  } catch (err) {
    next(err);
  }
}

export function logout(_req: Request, res: Response) {
  try {
    res.clearCookie('token');
    res.json({ message: 'Logged out' });
  } catch (err) {
    // Should never throw, but for completeness
    res.status(500).json({ error: 'Logout failed' });
  }
}


export function me(req: Request, res: Response, next: Function) {
  try {
    const token = req.cookies?.token;
    if (!token) return res.status(401).json({ error: 'Not authenticated' });
    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    if (typeof decoded === 'object' && decoded && 'id' in decoded && 'email' in decoded) {
      const user = findUserByEmail((decoded as any).email);
      return res.json({ id: (decoded as any).id, email: (decoded as any).email, emailVerified: user?.emailVerified });
    }
    return res.status(401).json({ error: 'Invalid token' });
  } catch (err) {
    next(err);
  }
}

export async function verifyEmail(req: Request, res: Response, next: Function) {
  try {
    const { token } = req.query;
    if (!token || typeof token !== 'string') {
      return res.status(400).json({ error: 'Invalid or already used token' });
    }
    const user = (require('../services/userService') as typeof import('../services/userService')).findUserByEmail(
      (require('../services/userService') as any).users?.find((u: any) => u.verificationToken === token)?.email
    );
    if (!user || user.emailVerified || user.verificationToken !== token) {
      return res.status(400).json({ error: 'Invalid or already used token' });
    }
    user.emailVerified = true;
    user.verificationToken = undefined;
    return res.json({ message: 'Email verified successfully' });
  } catch (err) {
    next(err);
  }
}

export async function requestPasswordReset(req: Request, res: Response, next: Function) {
  try {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email required' });
    const user = findUserByEmail(email);
    if (!user) return res.status(200).json({ message: 'If that email exists, a reset link has been sent.' }); // Always return 200 for security
    const token = require('uuid').v4();
    const expires = Date.now() + 1000 * 60 * 60; // 1 hour
    setResetPasswordToken(user, token, expires);
    try {
      await sendPasswordResetEmail(user.email, token);
      return res.json({ message: 'If that email exists, a reset link has been sent.' });
    } catch (err) {
      return next({ status: 500, message: 'Failed to send reset email', details: String(err) });
    }
  } catch (err) {
    next(err);
  }
}

export async function resetPassword(req: Request, res: Response, next: Function) {
  try {
    const { token, password } = req.body;
    if (!token || !password) return res.status(400).json({ error: 'Missing token or password' });
    const user = (require('../services/userService') as typeof import('../services/userService')).findUserByEmail(
      (require('../services/userService') as any).users?.find((u: any) => u.resetPasswordToken === token)?.email
    );
    if (!user || !user.resetPasswordToken || user.resetPasswordToken !== token) {
      return res.status(400).json({ error: 'Invalid or expired token' });
    }
    if (!user.resetPasswordExpires || user.resetPasswordExpires < Date.now()) {
      clearResetPasswordToken(user);
      return res.status(400).json({ error: 'Token expired' });
    }
    setPassword(user, password);
    clearResetPasswordToken(user);
    return res.json({ message: 'Password reset successful' });
  } catch (err) {
    next(err);
  }
}

export async function resendVerification(req: Request, res: Response, next: Function) {
  try {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email required' });
    const user = findUserByEmail(email);
    // Always return a generic message for privacy
    if (!user || user.emailVerified) {
      return res.status(200).json({ message: 'If that email exists, a verification email has been sent.' });
    }
    if (!user.verificationToken) {
      user.verificationToken = require('uuid').v4();
    }
    if (!user.verificationToken) {
      // This should never happen, but ensures type safety
      return next({ status: 500, message: 'Failed to generate verification token' });
    }
    try {
      await sendVerificationEmail(user.email, user.verificationToken);
      // TODO: Add rate limiting to prevent abuse
      return res.status(200).json({ message: 'If that email exists, a verification email has been sent.' });
    } catch (err) {
      return next({ status: 500, message: 'Failed to send verification email', details: String(err) });
    }
  } catch (err) {
    next(err);
  }
}
