# Minimal SaaS Template Essentials Checklist

## 1. Authentication & Security
- [x] Email/password authentication (JWT, secure cookies)
- [x] Google OAuth login
- [x] Email verification flow
- [x] Password reset (Forgot/Reset Password, MailerSend integration)
- [x] Secure password hashing (bcrypt/argon2)
- [x] CSRF, XSS, and CORS protections
- [x] Rate limiting (especially on auth endpoints)
- [x] Centralized error handling (backend & frontend)
- [x] Minimal, accessible ErrorBoundary in React

## 2. Billing & Subscription
- [x] Stripe integration: checkout, webhooks, plan management
- [x] 3 subscription tiers (free, basic, pro)
- [x] Profile page shows current tier, allows upgrade/downgrade

## 3. User Management
- [x] User profile page (change password, delete account, see email)
- [x] Logout functionality

## 4. Frontend
- [x] Responsive, minimal, modern UI (React, Vite, TailwindCSS)
- [x] Robust client-side validation and user-friendly error messages on all forms
- [x] Accessible forms and error messages (a11y basics)
- [x] Clean navigation (register, login, profile, subscription, etc.)

## 5. Backend
- [x] Modular Express structure (routes, controllers, middleware, services)
- [x] Input validation middleware (e.g., express-validator)
- [x] Secure environment variable handling

## 6. Documentation
- [x] Up-to-date README, checklist, folder structure, and summary table
- [x] Clear setup instructions (env vars, Stripe/MailerSend/Google setup)
- [x] Minimal, clean code with no dummy/unused code

---

### Strongly Recommended (not strictly mandatory)
- [ ] CI/CD workflow (e.g., GitHub Actions for lint/build/test)
- [ ] Basic monitoring/uptime check (even just a doc suggestion)
- [ ] CDN/static asset caching hint (for frontend assets)
- [ ] Script or doc note for regular database backups (if DB is used)
- [ ] Example unit tests (Jest for backend, React Testing Library for frontend)
- [ ] Simple integration/E2E test (e.g., register/login flow)
- [x] Accessibility: forms/buttons are keyboard accessible, proper aria-labels/roles
- [ ] Basic OpenAPI/Swagger doc or markdown API overview
- [ ] Stub/static pages for Terms of Service and Privacy Policy
- [ ] Placeholder for invoice history (optional, can be stubbed)
