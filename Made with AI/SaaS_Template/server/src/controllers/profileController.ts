import { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import { findUserByEmail, removeUserById } from '../services/userService';

export async function updateProfile(req: Request, res: Response, next: Function) {
  try {
    // Only allow updating password for now
    const { email } = (req as any).user || {};
    const { password } = req.body;
    if (!email) return res.status(401).json({ error: 'Not authenticated' });
    if (!password || password.length < 6) return res.status(400).json({ error: 'Password must be at least 6 characters' });
    const user = await findUserByEmail(email);
    if (!user) return res.status(404).json({ error: 'User not found' });
    user.passwordHash = bcrypt.hashSync(password, 10);
    return res.json({ message: 'Password updated' });
  } catch (err) {
    next(err);
  }
}

export async function deleteAccount(req: Request, res: Response, next: Function) {
  try {
    const { id } = (req as any).user || {};
    if (!id) return res.status(401).json({ error: 'Not authenticated' });
    const deleted = removeUserById(id);
    if (!deleted) return res.status(404).json({ error: 'User not found' });
    res.clearCookie && res.clearCookie('token');
    return res.json({ message: 'Account deleted' });
  } catch (err) {
    next(err);
  }
}
