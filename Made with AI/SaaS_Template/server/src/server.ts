import express from 'express';
import cors from 'cors';
import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';

import helmet from 'helmet';
import authRoutes from './routes/authRoutes';
import stripeRoutes from './routes/stripeRoutes';
import profileRoutes from './routes/profileRoutes';


// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  credentials: true,
}));
app.use(helmet());
app.use(express.json());
app.use(cookieParser());

// Global rate limit (all endpoints)
import { globalLimiter, authLimiter } from './middleware/rateLimiter';

app.use(globalLimiter);

// Stricter rate limit for auth endpoints
app.use('/api/auth', authLimiter);

app.use('/api/auth', authRoutes);
app.use('/api/stripe', stripeRoutes);
app.use('/api/profile', profileRoutes);

/** @type {import('express').RequestHandler} */
app.get('/api/health', (_req: import('express').Request, res: import('express').Response) => res.json({ status: 'ok' }));

// Centralized error handler
app.use((err: any, _req: import('express').Request, res: import('express').Response, _next: import('express').NextFunction) => {
  const isDev = process.env.NODE_ENV !== 'production';
  const status = err.status || 500;
  const errorResponse: any = {
    error: err.message || 'Internal Server Error',
    code: err.code || undefined,
  };
  if (isDev && err.stack) {
    errorResponse.stack = err.stack;
  }
  if (err.details) {
    errorResponse.details = err.details;
  }
  // Never leak sensitive info
  if (status >= 500 && !isDev) {
    errorResponse.error = 'Internal Server Error';
    delete errorResponse.stack;
    delete errorResponse.details;
  }
  console.error('Unhandled error:', err);
  res.status(status).json(errorResponse);
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
