import { body, validationResult, ValidationChain } from 'express-validator';
import { Request, Response, NextFunction } from 'express';

export const validateRegister: ValidationChain[] = [
  body('email').isEmail().withMessage('Invalid email'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
];

export const validateLogin: ValidationChain[] = [
  body('email').isEmail().withMessage('Invalid email'),
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
];

export const validatePassword: ValidationChain[] = [
  body('password').isLength({ min: 6 }).withMessage('Password must be at least 6 characters'),
];

export const validateEmail: ValidationChain[] = [
  body('email').isEmail().withMessage('Invalid email'),
];

export const validateResetPassword: ValidationChain[] = [
  body('token').notEmpty().withMessage('Missing token'),
  ...validatePassword,
];

export function handleValidationErrors(req: Request, res: Response, next: NextFunction) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ error: 'Validation failed', details: errors.array() });
  }
  next();
}
