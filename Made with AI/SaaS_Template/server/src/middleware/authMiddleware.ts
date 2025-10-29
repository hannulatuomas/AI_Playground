import jwt from 'jsonwebtoken';
import type { Request, Response, NextFunction } from 'express';

export interface AuthRequest extends Request {
  user?: { id: string; email: string; };
}

export function requireAuth(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.cookies?.token;
  if (!token) return res.status(401).json({ message: 'Not authenticated' });
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    if (typeof decoded === 'object' && decoded && 'id' in decoded && 'email' in decoded) {
      req.user = { id: (decoded as any).id, email: (decoded as any).email };
      return next();
    }
    return res.status(401).json({ message: 'Invalid token' });
  } catch {
    return res.status(401).json({ message: 'Invalid token' });
  }
}
