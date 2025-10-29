# SaaS Template (React, TypeScript, Vite, TailwindCSS, Express)

A minimal, production-ready SaaS starter template with full authentication (JWT, Google OAuth), robust Stripe subscription billing, and a modern React UI.

---

## Project Structure

```
/saas-template/
  /client/         # Frontend (React, TypeScript, Vite, TailwindCSS)
  /server/         # Backend (Express, TypeScript)
  /shared/         # (Optional) Shared types/interfaces
```

---

## Features
- **User Authentication**: Register/login with email & password (JWT in httpOnly cookie), plus Google OAuth. Email verification flow enforced (user must verify before login, handled via VerifyEmail page/flow). Password reset flow (ForgotPassword, ResetPassword pages, secure backend endpoints, MailerSend email).
- **Stripe Billing**: Subscription payments via Stripe Checkout, real-time status via webhooks, customer lookup.
- **User Dashboard**: See real subscription status after payment. Profile page with change password and delete account features.
- **Modern UI**: Vite, React, TailwindCSS. All forms, cards, and flows are fully responsive, visually consistent, and accessible.
- **Minimal, extensible codebase**: In-memory user store (swap for DB in production).
- **Error Handling**: Backend is robust and consistent (all major routes/controllers use centralized error handling and validation middleware). Frontend error handling/validation is improved (all major forms), but advanced error boundaries and some accessibility (a11y) are still missing.

---

## Codebase Audit & Template Notes

- **No legacy, dummy, or unused code:** As of the latest audit, the codebase contains no legacy, dummy, or unneeded code, and all files are actively used in the main flows.
- **In-memory user store:** The backend uses an in-memory user store for demonstration and template purposes. **This is a placeholder and must be replaced with a persistent database (e.g., PostgreSQL, MongoDB) in production deployments.**

> **Limitation:**
> Duplicate registration attempts (same email) are prevented at the API level and do not mutate or remove the existing user. However, the in-memory user store is not robust and may behave unexpectedly in concurrent or production-like scenarios (e.g., server restarts, race conditions, or memory leaks). For production, always use a persistent database with unique constraints to guarantee data integrity.
- **Verification email resend endpoint:** This endpoint now uses both per-IP and per-email (user/email) rate limiting (3 requests per hour per IP and 3 per hour per email). This provides robust, production-grade protection against abuse and spam. The implementation uses in-memory storage for template purposes; for distributed production deployments, swap to Redis or another shared store.

---

## Missing/Planned Features

- **Account Cleanup Policy:**
  - Unverified accounts (users who never verify their email) should be automatically deleted after a set period (e.g., 24-72 hours). Store a `verificationTokenExpires` timestamp and run a scheduled cleanup job to remove expired, unverified users.
  - Abandoned accounts (users who have not logged in for a long period, e.g., 12-24 months) should be identified using a `lastLoginAt` timestamp. Send a warning email before deletion, and remove accounts that remain inactive after the warning period. Prioritize this for free/unpaid accounts.
  - Make this policy clear in your Terms of Service/Privacy Policy.
  - These measures help keep the database clean and reduce spam/bot signups.

- Team management
- Notifications (email and/or in-app)
- Terms of Service and Privacy Policy pages
- Error boundaries and advanced frontend error handling (backend is complete)
- Automated and manual tests (unit, integration, E2E)
- Loading and empty states for all async content (all user-facing pages/components covered)
- Responsive design (partial)
- API key management
- Webhook endpoints (Stripe and others)
- Accessibility (a11y)
- Static asset optimization
- Invoice history
- Production deployment polish (monitoring, backups, CI/CD, logging, CDN/caching, etc.)

## Setup & Quickstart

### 1. Install dependencies
```sh
cd server && npm install
cd ../client && npm install
```

### 2. Environment Variables
Copy `/server/.env.example` to `/server/.env` and fill in:
- `JWT_SECRET` (random string)
- `GOOGLE_CLIENT_ID` & `GOOGLE_CLIENT_SECRET` (from Google Cloud)
- `STRIPE_SECRET_KEY` (from Stripe dashboard)
- `STRIPE_WEBHOOK_SECRET` (from Stripe CLI/dashboard)
- `STRIPE_PRICE_ID` (from your Stripe product)
- `CLIENT_URL` (usually http://localhost:5173)

### 3. Start backend
```sh
cd server
npm run dev
```
Server runs on [http://localhost:4000](http://localhost:4000)

### 4. Start frontend
```sh
cd client
npm run dev
```
Frontend runs on [http://localhost:5173](http://localhost:5173)

### 5. Stripe Webhooks (for local dev)
Install Stripe CLI and run:
```
stripe listen --forward-to localhost:4000/api/stripe/webhook
```
Copy the webhook secret into your `.env`.

---

## Authentication Flow
- **Register/Login**: POST to `/api/auth/register` or `/api/auth/login`, JWT set as httpOnly cookie. Users cannot log in until their email is verified.
- **Google Login**: Redirects to `/api/auth/google`, then callback sets JWT (only if email is verified).
- **Email Verification**: After registration, users are redirected to `/verify-email`, which handles verification and allows resending the verification email if needed. No banners or prompts after login.
- **User State**: Frontend fetches `/api/auth/me` to hydrate user context.
- **Logout**: `/api/auth/logout` clears auth cookie.
- **Forgot Password**: `/forgot-password` page lets users request a reset link (POST `/api/auth/request-password-reset`).
- **Reset Password**: `/reset-password?token=...` page lets users set a new password (POST `/api/auth/reset-password`).
- **Security**: All reset tokens are time-limited and single-use. No indication is given if an email does not exist.
- **Rate Limiting**: All endpoints are protected by centralized rate limiting middleware for security and abuse prevention.

---

## Stripe Subscription Flow
1. User clicks “Buy Subscription”, POSTs to `/api/stripe/create-subscription`.
2. Backend creates/fetches Stripe customer, starts Checkout session, returns URL.
3. User completes payment on Stripe, is redirected to `/profile`.
4. Stripe sends webhook to `/api/stripe/webhook`.
5. Backend updates user’s subscription status in memory.
6. Frontend fetches `/api/stripe/status` to show real subscription status.

---

## Extending & Production Notes
- Swap in-memory user store for a real database (Postgres, Mongo, etc).
- Secure your `.env` and secrets.
- Email verification is implemented (see EmailVerificationBanner and VerifyEmail page/flow). Add password reset, etc. as needed.
- Add more robust error handling (see code comments).

---

## Scripts
- `npm run dev` (dev server)
- `npm run build` (build for prod)
- `npm start` (start prod build)

---
