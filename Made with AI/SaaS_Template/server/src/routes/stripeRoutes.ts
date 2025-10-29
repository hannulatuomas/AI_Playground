const express = require('express');
import type { Request, Response } from 'express';
const router = express.Router();

import { createSubscription, handleWebhook, subscriptionStatus, getTiers } from '../controllers/stripeController';

import { validateEmail, handleValidationErrors } from '../middleware/validation';

// You may want to add a custom validator for tierKey if needed
router.post('/create-subscription', validateEmail, handleValidationErrors, createSubscription);
router.post('/webhook', handleWebhook);
router.get('/tiers', getTiers);
router.get('/status', subscriptionStatus);

export default router;
