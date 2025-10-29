import express from 'express';
import { updateProfile, deleteAccount } from '../controllers/profileController';
import { requireAuth } from '../middleware/authMiddleware';

const router = express.Router();

import { validatePassword, handleValidationErrors } from '../middleware/validation';

router.post('/update', requireAuth, validatePassword, handleValidationErrors, updateProfile);
router.post('/delete', requireAuth, deleteAccount);

export default router;
