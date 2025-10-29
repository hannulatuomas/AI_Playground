import { Request, Response, NextFunction } from 'express';
import { ErrorCode, AppError } from '../utils/errors';

export class InputSanitizer {
  private static readonly XSS_REGEX = /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi;
  private static readonly SQL_INJECTION_REGEX = /('|"|;|--|union|select|insert|update|delete|drop|exec|execute|truncate)/gi;
  private static readonly PATH_TRAVERSAL_REGEX = /(\.\.\/|\.\.\\|\.\/|\.\\)/g;

  public static sanitizeString(value: string): string {
    if (typeof value !== 'string') {
      return value;
    }

    // Remove XSS
    value = value.replace(this.XSS_REGEX, '');
    
    // Remove SQL injection attempts
    value = value.replace(this.SQL_INJECTION_REGEX, '');
    
    // Remove path traversal attempts
    value = value.replace(this.PATH_TRAVERSAL_REGEX, '');
    
    // Trim whitespace
    value = value.trim();
    
    return value;
  }

  public static sanitizeObject(obj: any): any {
    if (obj === null || obj === undefined) {
      return obj;
    }

    if (typeof obj === 'string') {
      return this.sanitizeString(obj);
    }

    if (Array.isArray(obj)) {
      return obj.map(item => this.sanitizeObject(item));
    }

    if (typeof obj === 'object') {
      const sanitized: any = {};
      for (const key in obj) {
        sanitized[key] = this.sanitizeObject(obj[key]);
      }
      return sanitized;
    }

    return obj;
  }

  public static middleware() {
    return (req: Request, res: Response, next: NextFunction) => {
      try {
        // Sanitize request body
        if (req.body) {
          req.body = this.sanitizeObject(req.body);
        }

        // Sanitize query parameters
        if (req.query) {
          req.query = this.sanitizeObject(req.query);
        }

        // Sanitize URL parameters
        if (req.params) {
          req.params = this.sanitizeObject(req.params);
        }

        next();
      } catch (error) {
        throw new AppError(
          ErrorCode.INVALID_INPUT,
          'Invalid input data',
          { error: error.message }
        );
      }
    };
  }
} 