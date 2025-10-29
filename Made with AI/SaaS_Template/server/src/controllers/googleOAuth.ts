import { OAuth2Client } from 'google-auth-library';
import { findUserByEmail, createUser } from '../services/userService';
import jwt from 'jsonwebtoken';
import type { Request, Response } from 'express';

const client = new OAuth2Client({
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  redirectUri: process.env.GOOGLE_CALLBACK_URL,
});

function issueToken(user: { id: string; email: string }) {
  return jwt.sign({ id: user.id, email: user.email }, process.env.JWT_SECRET!, { expiresIn: '7d' });
}

export function googleAuthRedirect(_req: Request, res: Response) {
  const url = client.generateAuthUrl({
    access_type: 'offline',
    scope: ['openid', 'email', 'profile'],
    prompt: 'select_account',
  });
  res.redirect(url);
}

export async function googleAuthCallback(req: Request, res: Response) {
  const code = req.query.code as string;
  if (!code) return res.status(400).json({ message: 'No code provided' });
  try {
    const { tokens } = await client.getToken(code);
    const ticket = await client.verifyIdToken({
      idToken: tokens.id_token!,
      audience: process.env.GOOGLE_CLIENT_ID,
    });
    const payload = ticket.getPayload();
    if (!payload?.email) return res.status(400).json({ message: 'No email from Google' });
    let user = findUserByEmail(payload.email);
    if (!user) user = createUser(payload.email, undefined, 'google');
    const token = issueToken(user);
    res.cookie('token', token, { httpOnly: true, sameSite: 'lax' });
    // Redirect to client app after login
    res.redirect(process.env.CLIENT_URL || '/');
  } catch (err) {
    res.status(500).json({ message: 'Google login failed', error: String(err) });
  }
}
