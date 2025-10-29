import { Request, Response, NextFunction } from 'express';
import { ErrorCode, AppError } from '../utils/errors';

interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
}

interface RateLimitStore {
  [key: string]: {
    count: number;
    resetTime: number;
  };
}

export class RateLimiter {
  private store: RateLimitStore = {};
  private config: RateLimitConfig;
  private cleanupInterval: NodeJS.Timeout;

  constructor(config: RateLimitConfig) {
    this.config = config;
    this.cleanupInterval = setInterval(() => this.cleanup(), config.windowMs);
  }

  private cleanup(): void {
    const now = Date.now();
    for (const key in this.store) {
      if (this.store[key].resetTime < now) {
        delete this.store[key];
      }
    }
  }

  private getKey(req: Request): string {
    return `${req.ip}-${req.path}`;
  }

  public middleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      const key = this.getKey(req);
      const now = Date.now();

      if (!this.store[key] || this.store[key].resetTime < now) {
        this.store[key] = {
          count: 1,
          resetTime: now + this.config.windowMs
        };
      } else {
        this.store[key].count++;
      }

      if (this.store[key].count > this.config.maxRequests) {
        throw new AppError(
          ErrorCode.RATE_LIMIT_EXCEEDED,
          'Rate limit exceeded',
          {
            retryAfter: Math.ceil((this.store[key].resetTime - now) / 1000)
          }
        );
      }

      res.setHeader('X-RateLimit-Limit', this.config.maxRequests);
      res.setHeader('X-RateLimit-Remaining', this.config.maxRequests - this.store[key].count);
      res.setHeader('X-RateLimit-Reset', this.store[key].resetTime);

      next();
    };
  }

  public destroy(): void {
    clearInterval(this.cleanupInterval);
  }
} 