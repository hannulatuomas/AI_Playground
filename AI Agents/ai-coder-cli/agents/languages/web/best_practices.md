
# Web Development Best Practices (JavaScript/TypeScript/HTML/CSS)

## Code Organization and Structure

### Project Structure

#### React/Next.js
```
src/
├── components/          # Reusable UI components
│   ├── common/         # Shared components
│   ├── layout/         # Layout components
│   └── features/       # Feature-specific components
├── pages/              # Route pages (Next.js) or views
├── hooks/              # Custom React hooks
├── utils/              # Utility functions
├── services/           # API services
├── types/              # TypeScript type definitions
├── styles/             # Global styles and themes
├── context/            # React context providers
└── lib/                # Third-party library configurations
```

#### Vue/Nuxt
```
src/
├── components/         # Vue components
├── composables/        # Vue 3 composables
├── layouts/           # Layout components
├── pages/             # Route pages
├── stores/            # Pinia/Vuex stores
├── plugins/           # Vue plugins
├── middleware/        # Route middleware
├── utils/             # Utility functions
└── types/             # TypeScript definitions
```

### File Naming Conventions
- **Components**: PascalCase - `UserProfile.tsx`, `NavBar.vue`
- **Utilities/Hooks**: camelCase - `useAuth.ts`, `formatDate.ts`
- **Styles**: kebab-case - `user-profile.css`, `nav-bar.module.css`
- **Constants**: UPPER_SNAKE_CASE - `API_ENDPOINTS.ts`

### Module Organization
```typescript
// Group related imports
// 1. External libraries
import React, { useState, useEffect } from 'react';
import axios from 'axios';

// 2. Internal modules
import { UserService } from '@/services/user';
import { formatDate } from '@/utils/date';

// 3. Types
import type { User, UserProfile } from '@/types/user';

// 4. Styles
import styles from './UserProfile.module.css';

// 5. Assets
import defaultAvatar from '@/assets/avatar.png';
```

## Naming Conventions

### JavaScript/TypeScript
```typescript
// Variables and functions: camelCase
const userName = 'John';
function getUserData() {}

// Classes and Components: PascalCase
class UserService {}
function UserProfile() {}

// Constants: UPPER_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com';
const MAX_RETRY_ATTEMPTS = 3;

// Private properties: _camelCase (or use # for truly private)
class UserService {
  private _cache = new Map();
  #privateField = 'secret';
}

// Interfaces and Types: PascalCase with descriptive names
interface UserProfile {
  id: number;
  name: string;
}

type AsyncResult<T> = Promise<T | null>;

// Enums: PascalCase for enum, UPPER_CASE for values
enum UserRole {
  ADMIN = 'ADMIN',
  USER = 'USER',
  GUEST = 'GUEST'
}

// Boolean variables: use is/has/can prefix
const isLoading = true;
const hasPermission = false;
const canEdit = true;
```

### CSS/SCSS
```css
/* Use BEM methodology */
.block {}
.block__element {}
.block__element--modifier {}

/* Example */
.user-profile {}
.user-profile__avatar {}
.user-profile__avatar--large {}
.user-profile__name {}
.user-profile--premium {}

/* Or use CSS Modules for scoped styles */
/* UserProfile.module.css */
.container {}
.avatar {}
.name {}
```

## Error Handling Patterns

### Try-Catch with Async/Await
```typescript
// API calls
async function fetchUser(userId: string): Promise<User | null> {
  try {
    const response = await axios.get<User>(`/api/users/${userId}`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 404) {
        console.warn(`User ${userId} not found`);
        return null;
      }
      console.error('API error:', error.message);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
}

// With custom error types
class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) {
      throw new ApiError(
        'Failed to fetch data',
        response.status,
        await response.json()
      );
    }
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      // Handle API errors
      handleApiError(error);
    } else {
      // Handle other errors
      console.error('Unexpected error:', error);
    }
    throw error;
  }
}
```

### Error Boundaries (React)
```typescript
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error reporting service
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

### Form Validation
```typescript
// Use validation libraries like Zod, Yup, or joi
import { z } from 'zod';

const userSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  age: z.number().min(18, 'Must be 18 or older'),
});

type UserFormData = z.infer<typeof userSchema>;

function validateForm(data: unknown): UserFormData {
  try {
    return userSchema.parse(data);
  } catch (error) {
    if (error instanceof z.ZodError) {
      // Handle validation errors
      const errorMessages = error.errors.map(e => e.message);
      throw new ValidationError(errorMessages);
    }
    throw error;
  }
}
```

## Performance Considerations

### React Performance
```typescript
// Use React.memo for expensive components
const ExpensiveComponent = React.memo(({ data }: Props) => {
  return <div>{/* Expensive rendering */}</div>;
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id;
});

// Use useMemo for expensive calculations
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);

// Use useCallback for stable function references
const handleClick = useCallback(() => {
  doSomething(value);
}, [value]);

// Code splitting with dynamic imports
const LazyComponent = React.lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}

// Virtualize long lists
import { FixedSizeList } from 'react-window';

function VirtualizedList({ items }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {({ index, style }) => (
        <div style={style}>{items[index]}</div>
      )}
    </FixedSizeList>
  );
}
```

### JavaScript Performance
```javascript
// Debounce expensive operations
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

const handleSearch = debounce((query) => {
  // Expensive search operation
}, 300);

// Throttle frequent events
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

const handleScroll = throttle(() => {
  // Handle scroll
}, 100);

// Use Web Workers for CPU-intensive tasks
const worker = new Worker('worker.js');
worker.postMessage({ data: largeDataset });
worker.onmessage = (e) => {
  console.log('Result from worker:', e.data);
};
```

### CSS Performance
```css
/* Use CSS containment */
.card {
  contain: layout style paint;
}

/* Avoid expensive selectors */
/* BAD: */
div > div > div > .nested {}

/* GOOD: */
.specific-class {}

/* Use will-change sparingly */
.animated-element {
  will-change: transform;
}

/* Remove will-change after animation */
.animated-element.done {
  will-change: auto;
}

/* Use CSS transforms instead of position changes */
/* GOOD: */
.element {
  transform: translateX(100px);
}

/* BAD: */
.element {
  left: 100px;
}
```

### Bundle Optimization
```javascript
// Tree shaking - import only what you need
// GOOD:
import { debounce } from 'lodash-es';

// BAD:
import _ from 'lodash';
const debounce = _.debounce;

// Dynamic imports for code splitting
const module = await import('./heavy-module.js');

// Lazy load images
<img 
  loading="lazy" 
  src="image.jpg" 
  alt="Description"
/>

// Use image formats like WebP
<picture>
  <source srcset="image.webp" type="image/webp" />
  <img src="image.jpg" alt="Fallback" />
</picture>
```

## Security Best Practices

### XSS Prevention
```typescript
// Always sanitize user input
import DOMPurify from 'dompurify';

const sanitizedHTML = DOMPurify.sanitize(userInput);

// In React, avoid dangerouslySetInnerHTML
// BAD:
<div dangerouslySetInnerHTML={{ __html: userInput }} />

// GOOD: React automatically escapes
<div>{userInput}</div>

// If you must use HTML, sanitize it
<div dangerouslySetInnerHTML={{ 
  __html: DOMPurify.sanitize(userInput) 
}} />
```

### CSRF Protection
```typescript
// Include CSRF token in requests
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

axios.defaults.headers.common['X-CSRF-Token'] = csrfToken;

// Use SameSite cookies
// Set in server:
// Set-Cookie: sessionId=abc123; SameSite=Strict; Secure; HttpOnly
```

### Content Security Policy
```html
<!-- Add CSP headers -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';">
```

### Authentication
```typescript
// Store tokens securely
// Use httpOnly cookies for refresh tokens
// Store access tokens in memory (not localStorage)

class AuthService {
  private accessToken: string | null = null;

  setAccessToken(token: string) {
    this.accessToken = token;
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }

  clearAccessToken() {
    this.accessToken = null;
  }
}

// Add auth token to requests
axios.interceptors.request.use((config) => {
  const token = authService.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Input Validation
```typescript
// Validate on both client and server
// Client-side validation for UX
// Server-side validation for security

// Sanitize URLs
function isSafeUrl(url: string): boolean {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

// Escape special characters
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}
```

## Testing Approaches

### Unit Testing
```typescript
// Use Jest + React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { UserProfile } from './UserProfile';

describe('UserProfile', () => {
  it('renders user information', () => {
    const user = { id: 1, name: 'John Doe', email: 'john@example.com' };
    render(<UserProfile user={user} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', async () => {
    const onEdit = jest.fn();
    const user = { id: 1, name: 'John Doe' };
    render(<UserProfile user={user} onEdit={onEdit} />);
    
    await userEvent.click(screen.getByRole('button', { name: /edit/i }));
    
    expect(onEdit).toHaveBeenCalledWith(user);
  });

  it('shows loading state while fetching', async () => {
    render(<UserProfile userId="1" />);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
    });
  });
});
```

### Integration Testing
```typescript
// Test component interactions
describe('LoginForm integration', () => {
  it('successfully logs in user', async () => {
    const mockLogin = jest.fn().mockResolvedValue({ success: true });
    render(<LoginForm onLogin={mockLogin} />);
    
    await userEvent.type(screen.getByLabelText(/email/i), 'user@example.com');
    await userEvent.type(screen.getByLabelText(/password/i), 'password123');
    await userEvent.click(screen.getByRole('button', { name: /login/i }));
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'user@example.com',
        password: 'password123'
      });
    });
  });
});
```

### E2E Testing
```typescript
// Use Playwright or Cypress
// Playwright example:
import { test, expect } from '@playwright/test';

test('user can create a new post', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=New Post');
  
  await page.fill('[name="title"]', 'My Test Post');
  await page.fill('[name="content"]', 'This is test content');
  await page.click('button:has-text("Publish")');
  
  await expect(page.locator('text=Post published')).toBeVisible();
  await expect(page.locator('h1:has-text("My Test Post")')).toBeVisible();
});
```

### Testing Hooks
```typescript
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('useCounter increments', () => {
  const { result } = renderHook(() => useCounter());
  
  expect(result.current.count).toBe(0);
  
  act(() => {
    result.current.increment();
  });
  
  expect(result.current.count).toBe(1);
});
```

## Documentation Standards

### JSDoc Comments
```typescript
/**
 * Fetches user data from the API.
 * 
 * @param userId - The unique identifier of the user
 * @param options - Optional configuration for the request
 * @param options.includeProfile - Whether to include profile data
 * @param options.cache - Whether to use cached data if available
 * @returns Promise resolving to user data or null if not found
 * @throws {ApiError} When the API request fails
 * 
 * @example
 * ```typescript
 * const user = await fetchUser('123', { includeProfile: true });
 * if (user) {
 *   console.log(user.name);
 * }
 * ```
 */
async function fetchUser(
  userId: string,
  options?: {
    includeProfile?: boolean;
    cache?: boolean;
  }
): Promise<User | null> {
  // Implementation
}
```

### Component Documentation
```typescript
/**
 * UserProfile displays user information and allows editing.
 * 
 * @component
 * @example
 * ```tsx
 * <UserProfile
 *   user={userData}
 *   onEdit={handleEdit}
 *   editable
 * />
 * ```
 */
interface UserProfileProps {
  /** User data to display */
  user: User;
  /** Callback when edit button is clicked */
  onEdit?: (user: User) => void;
  /** Whether the profile can be edited */
  editable?: boolean;
  /** Additional CSS class names */
  className?: string;
}

export function UserProfile({
  user,
  onEdit,
  editable = false,
  className
}: UserProfileProps) {
  // Implementation
}
```

### README Documentation
```markdown
# Component Name

## Description
Brief description of what the component does.

## Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| user | User | required | User data |
| onEdit | function | - | Edit callback |
| editable | boolean | false | Can edit |

## Usage
\`\`\`tsx
import { UserProfile } from './UserProfile';

<UserProfile user={user} onEdit={handleEdit} />
\`\`\`

## Examples
[Link to Storybook or examples]
```

## Common Pitfalls to Avoid

### 1. Mutating State Directly
```typescript
// BAD:
state.items.push(newItem);
setState(state);

// GOOD:
setState(prevState => ({
  ...prevState,
  items: [...prevState.items, newItem]
}));
```

### 2. Not Cleaning Up Effects
```typescript
// BAD:
useEffect(() => {
  const interval = setInterval(() => {}, 1000);
}, []);

// GOOD:
useEffect(() => {
  const interval = setInterval(() => {}, 1000);
  return () => clearInterval(interval);
}, []);
```

### 3. Using Index as Key
```typescript
// BAD:
{items.map((item, index) => (
  <div key={index}>{item.name}</div>
))}

// GOOD:
{items.map(item => (
  <div key={item.id}>{item.name}</div>
))}
```

### 4. Not Handling Async Errors
```typescript
// BAD:
async function loadData() {
  const data = await fetch('/api/data');
  setData(data);
}

// GOOD:
async function loadData() {
  try {
    const response = await fetch('/api/data');
    if (!response.ok) throw new Error('Failed to fetch');
    const data = await response.json();
    setData(data);
  } catch (error) {
    console.error('Error loading data:', error);
    setError(error.message);
  }
}
```

### 5. Creating Functions in Render
```typescript
// BAD:
function Component() {
  return <Child onClick={() => doSomething()} />;
}

// GOOD:
function Component() {
  const handleClick = useCallback(() => {
    doSomething();
  }, []);
  
  return <Child onClick={handleClick} />;
}
```

## Backend Development with Node.js and Express

### Express.js Server Setup
```typescript
// app.ts - Express application setup
import express, { Application, Request, Response, NextFunction } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';

const app: Application = express();

// Security middleware
app.use(helmet());

// CORS configuration
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
  credentials: true
}));

// Request parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression
app.use(compression());

// Logging
app.use(morgan('combined'));

// Routes
app.use('/api/users', userRoutes);
app.use('/api/posts', postRoutes);

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Error:', err);
  
  if (err instanceof ValidationError) {
    return res.status(400).json({ error: err.message });
  }
  
  if (err instanceof UnauthorizedError) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: 'Route not found' });
});

export default app;
```

### RESTful API Routes
```typescript
// routes/users.ts
import { Router, Request, Response } from 'express';
import { body, param, validationResult } from 'express-validator';
import { authenticate, authorize } from '../middleware/auth';
import * as userController from '../controllers/userController';

const router = Router();

// GET /api/users - List users (protected, admin only)
router.get(
  '/',
  authenticate,
  authorize(['admin']),
  userController.listUsers
);

// GET /api/users/:id - Get user by ID
router.get(
  '/:id',
  authenticate,
  param('id').isUUID(),
  userController.getUser
);

// POST /api/users - Create user
router.post(
  '/',
  [
    body('email').isEmail().normalizeEmail(),
    body('password').isLength({ min: 8 }),
    body('name').trim().isLength({ min: 2, max: 100 })
  ],
  userController.createUser
);

// PUT /api/users/:id - Update user
router.put(
  '/:id',
  authenticate,
  [
    param('id').isUUID(),
    body('name').optional().trim().isLength({ min: 2, max: 100 }),
    body('email').optional().isEmail().normalizeEmail()
  ],
  userController.updateUser
);

// DELETE /api/users/:id - Delete user
router.delete(
  '/:id',
  authenticate,
  authorize(['admin']),
  param('id').isUUID(),
  userController.deleteUser
);

export default router;
```

### Controllers Pattern
```typescript
// controllers/userController.ts
import { Request, Response, NextFunction } from 'express';
import { validationResult } from 'express-validator';
import * as userService from '../services/userService';
import { ApiError } from '../utils/errors';

export const listUsers = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const { page = 1, limit = 10, sort = 'createdAt' } = req.query;
    
    const result = await userService.listUsers({
      page: Number(page),
      limit: Number(limit),
      sort: String(sort)
    });
    
    res.json({
      success: true,
      data: result.users,
      pagination: {
        page: result.page,
        limit: result.limit,
        total: result.total,
        totalPages: result.totalPages
      }
    });
  } catch (error) {
    next(error);
  }
};

export const getUser = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ApiError('Validation failed', 400, errors.array());
    }
    
    const user = await userService.getUserById(req.params.id);
    
    if (!user) {
      throw new ApiError('User not found', 404);
    }
    
    res.json({ success: true, data: user });
  } catch (error) {
    next(error);
  }
};

export const createUser = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      throw new ApiError('Validation failed', 400, errors.array());
    }
    
    const user = await userService.createUser(req.body);
    
    res.status(201).json({ success: true, data: user });
  } catch (error) {
    next(error);
  }
};
```

### Middleware Patterns
```typescript
// middleware/auth.ts
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { ApiError } from '../utils/errors';

// Extend Express Request type to include user
declare global {
  namespace Express {
    interface Request {
      user?: {
        id: string;
        email: string;
        roles: string[];
      };
    }
  }
}

export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      throw new ApiError('No token provided', 401);
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;
    req.user = decoded;
    
    next();
  } catch (error) {
    next(new ApiError('Invalid token', 401));
  }
};

export const authorize = (roles: string[]) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    if (!req.user) {
      return next(new ApiError('Unauthorized', 401));
    }
    
    const hasRole = req.user.roles.some(role => roles.includes(role));
    
    if (!hasRole) {
      return next(new ApiError('Forbidden', 403));
    }
    
    next();
  };
};

// Rate limiting middleware
import rateLimit from 'express-rate-limit';

export const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP'
});

// Request validation middleware
export const validateRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    return next(new ApiError('Validation failed', 400, errors.array()));
  }
  
  next();
};
```

### Service Layer Pattern
```typescript
// services/userService.ts
import { User, UserCreateInput, UserUpdateInput } from '../types/user';
import { userRepository } from '../repositories/userRepository';
import { hashPassword, comparePassword } from '../utils/crypto';
import { ApiError } from '../utils/errors';

export const listUsers = async (options: {
  page: number;
  limit: number;
  sort: string;
}) => {
  const offset = (options.page - 1) * options.limit;
  
  const [users, total] = await Promise.all([
    userRepository.findMany({
      skip: offset,
      take: options.limit,
      orderBy: { [options.sort]: 'desc' }
    }),
    userRepository.count()
  ]);
  
  return {
    users,
    page: options.page,
    limit: options.limit,
    total,
    totalPages: Math.ceil(total / options.limit)
  };
};

export const getUserById = async (id: string): Promise<User | null> => {
  return await userRepository.findById(id);
};

export const createUser = async (input: UserCreateInput): Promise<User> => {
  // Check if user exists
  const existingUser = await userRepository.findByEmail(input.email);
  if (existingUser) {
    throw new ApiError('User already exists', 400);
  }
  
  // Hash password
  const hashedPassword = await hashPassword(input.password);
  
  // Create user
  const user = await userRepository.create({
    ...input,
    password: hashedPassword
  });
  
  return user;
};

export const updateUser = async (
  id: string,
  input: UserUpdateInput
): Promise<User> => {
  const user = await userRepository.findById(id);
  
  if (!user) {
    throw new ApiError('User not found', 404);
  }
  
  if (input.password) {
    input.password = await hashPassword(input.password);
  }
  
  return await userRepository.update(id, input);
};

export const deleteUser = async (id: string): Promise<void> => {
  const user = await userRepository.findById(id);
  
  if (!user) {
    throw new ApiError('User not found', 404);
  }
  
  await userRepository.delete(id);
};
```

### HTTP Client with Axios
```typescript
// utils/apiClient.ts
import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';

// Create axios instance with defaults
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.API_BASE_URL || 'http://localhost:3000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = generateRequestId();
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    
    // Handle 401 - Token expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post('/api/auth/refresh', { refreshToken });
        
        const { accessToken } = response.data;
        localStorage.setItem('authToken', accessToken);
        
        // Retry original request
        originalRequest.headers!.Authorization = `Bearer ${accessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other errors
    return Promise.reject(error);
  }
);

// API methods with type safety
export const api = {
  // GET request
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },
  
  // POST request
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.post<T>(url, data, config);
    return response.data;
  },
  
  // PUT request
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.put<T>(url, data, config);
    return response.data;
  },
  
  // PATCH request
  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.patch<T>(url, data, config);
    return response.data;
  },
  
  // DELETE request
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await apiClient.delete<T>(url, config);
    return response.data;
  }
};

// Usage example
interface User {
  id: string;
  name: string;
  email: string;
}

export const userApi = {
  getUsers: () => api.get<User[]>('/users'),
  getUser: (id: string) => api.get<User>(`/users/${id}`),
  createUser: (data: Omit<User, 'id'>) => api.post<User>('/users', data),
  updateUser: (id: string, data: Partial<User>) => api.put<User>(`/users/${id}`, data),
  deleteUser: (id: string) => api.delete<void>(`/users/${id}`)
};
```

### Environment Configuration
```typescript
// config/env.ts
import { z } from 'zod';

// Define environment schema
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  PORT: z.string().transform(Number).default('3000'),
  
  // Database
  DATABASE_URL: z.string().url(),
  
  // JWT
  JWT_SECRET: z.string().min(32),
  JWT_EXPIRES_IN: z.string().default('1h'),
  REFRESH_TOKEN_EXPIRES_IN: z.string().default('7d'),
  
  // CORS
  ALLOWED_ORIGINS: z.string().default('http://localhost:3000'),
  
  // External APIs
  API_KEY: z.string().optional(),
  
  // Redis (optional)
  REDIS_URL: z.string().url().optional(),
  
  // Logging
  LOG_LEVEL: z.enum(['error', 'warn', 'info', 'debug']).default('info')
});

// Validate and export environment variables
export const env = envSchema.parse(process.env);

// Type-safe environment access
export type Env = z.infer<typeof envSchema>;
```

## Package Management

### package.json Structure
```json
{
  "name": "my-fullstack-app",
  "version": "1.0.0",
  "description": "Full-stack web application",
  "main": "dist/index.js",
  "scripts": {
    "dev": "nodemon src/index.ts",
    "build": "tsc && vite build",
    "start": "node dist/index.js",
    "test": "jest --coverage",
    "test:watch": "jest --watch",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,json}\"",
    "type-check": "tsc --noEmit",
    "prepare": "husky install"
  },
  "dependencies": {
    "express": "^4.18.2",
    "axios": "^1.6.0",
    "cors": "^2.8.5",
    "helmet": "^7.1.0",
    "compression": "^1.7.4",
    "morgan": "^1.10.0",
    "jsonwebtoken": "^9.0.2",
    "bcrypt": "^5.1.1",
    "zod": "^3.22.4",
    "express-validator": "^7.0.1",
    "express-rate-limit": "^7.1.5"
  },
  "devDependencies": {
    "@types/express": "^4.17.21",
    "@types/node": "^20.10.0",
    "@types/cors": "^2.8.17",
    "@types/compression": "^1.7.5",
    "@types/morgan": "^1.9.9",
    "@types/jsonwebtoken": "^9.0.5",
    "@types/bcrypt": "^5.0.2",
    "typescript": "^5.3.3",
    "nodemon": "^3.0.2",
    "ts-node": "^10.9.2",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.1",
    "@types/jest": "^29.5.11",
    "supertest": "^6.3.3",
    "@types/supertest": "^6.0.2",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1",
    "husky": "^8.0.3",
    "lint-staged": "^15.2.0"
  },
  "engines": {
    "node": ">=18.0.0",
    "npm": ">=9.0.0"
  }
}
```

### Using npm vs yarn vs pnpm
```bash
# npm (traditional)
npm install
npm run dev
npm test

# yarn (faster, deterministic)
yarn install
yarn dev
yarn test

# pnpm (most efficient, disk-space saving)
pnpm install
pnpm dev
pnpm test

# Lock files importance
# Always commit: package-lock.json (npm), yarn.lock (yarn), or pnpm-lock.yaml (pnpm)
```

## Build Tools and Module Bundlers

### Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@types': path.resolve(__dirname, './src/types')
    }
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@mui/material']
        }
      }
    }
  },
  
  optimizeDeps: {
    include: ['react', 'react-dom']
  }
});
```

### Webpack Configuration (Alternative)
```javascript
// webpack.config.js
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === 'development';
  
  return {
    entry: './src/index.tsx',
    
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isDevelopment ? '[name].js' : '[name].[contenthash].js',
      clean: true
    },
    
    resolve: {
      extensions: ['.tsx', '.ts', '.jsx', '.js'],
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/
        },
        {
          test: /\.css$/,
          use: [
            isDevelopment ? 'style-loader' : MiniCssExtractPlugin.loader,
            'css-loader',
            'postcss-loader'
          ]
        },
        {
          test: /\.(png|svg|jpg|jpeg|gif)$/i,
          type: 'asset/resource'
        }
      ]
    },
    
    plugins: [
      new HtmlWebpackPlugin({
        template: './public/index.html'
      }),
      !isDevelopment && new MiniCssExtractPlugin({
        filename: '[name].[contenthash].css'
      }),
      process.env.ANALYZE && new BundleAnalyzerPlugin()
    ].filter(Boolean),
    
    optimization: {
      minimize: !isDevelopment,
      minimizer: [new TerserPlugin()],
      splitChunks: {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            priority: 10
          }
        }
      }
    },
    
    devServer: {
      port: 3000,
      hot: true,
      historyApiFallback: true,
      proxy: {
        '/api': 'http://localhost:5000'
      }
    }
  };
};
```

## Testing with Jest and Mocha

### Jest Configuration
```typescript
// jest.config.ts
import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  
  roots: ['<rootDir>/src'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/?(*.)+(spec|test).+(ts|tsx|js)'
  ],
  
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest'
  },
  
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.test.{ts,tsx}',
    '!src/**/__tests__/**'
  ],
  
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  
  setupFilesAfterEnv: ['<rootDir>/src/test/setup.ts'],
  
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};

export default config;
```

### Backend API Testing
```typescript
// __tests__/api/users.test.ts
import request from 'supertest';
import app from '../../app';
import { userRepository } from '../../repositories/userRepository';

describe('User API', () => {
  beforeEach(async () => {
    await userRepository.clear();
  });
  
  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const userData = {
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      };
      
      const response = await request(app)
        .post('/api/users')
        .send(userData)
        .expect(201);
      
      expect(response.body.success).toBe(true);
      expect(response.body.data).toHaveProperty('id');
      expect(response.body.data.email).toBe(userData.email);
      expect(response.body.data).not.toHaveProperty('password');
    });
    
    it('should return 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          name: 'John Doe',
          email: 'invalid-email',
          password: 'password123'
        })
        .expect(400);
      
      expect(response.body.success).toBe(false);
    });
  });
  
  describe('GET /api/users/:id', () => {
    it('should return user by id', async () => {
      const user = await userRepository.create({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'hashedpassword'
      });
      
      const response = await request(app)
        .get(`/api/users/${user.id}`)
        .set('Authorization', `Bearer ${generateToken(user)}`)
        .expect(200);
      
      expect(response.body.data.id).toBe(user.id);
    });
    
    it('should return 404 for non-existent user', async () => {
      const response = await request(app)
        .get('/api/users/non-existent-id')
        .set('Authorization', `Bearer ${generateToken()}`)
        .expect(404);
      
      expect(response.body.success).toBe(false);
    });
  });
});
```

### Mocha + Chai Alternative
```typescript
// test/api/users.test.ts
import { expect } from 'chai';
import request from 'supertest';
import app from '../../src/app';

describe('User API', () => {
  describe('POST /api/users', () => {
    it('should create a new user', (done) => {
      request(app)
        .post('/api/users')
        .send({
          name: 'John Doe',
          email: 'john@example.com',
          password: 'password123'
        })
        .expect(201)
        .end((err, res) => {
          if (err) return done(err);
          
          expect(res.body).to.have.property('success', true);
          expect(res.body.data).to.have.property('id');
          expect(res.body.data.email).to.equal('john@example.com');
          
          done();
        });
    });
  });
});
```

### Service Unit Tests
```typescript
// services/__tests__/userService.test.ts
import { userService } from '../userService';
import { userRepository } from '../../repositories/userRepository';

jest.mock('../../repositories/userRepository');

describe('UserService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  describe('createUser', () => {
    it('should create user with hashed password', async () => {
      const mockUser = {
        id: '1',
        name: 'John Doe',
        email: 'john@example.com',
        password: 'hashedpassword'
      };
      
      (userRepository.findByEmail as jest.Mock).mockResolvedValue(null);
      (userRepository.create as jest.Mock).mockResolvedValue(mockUser);
      
      const result = await userService.createUser({
        name: 'John Doe',
        email: 'john@example.com',
        password: 'password123'
      });
      
      expect(result).toEqual(mockUser);
      expect(userRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'John Doe',
          email: 'john@example.com',
          password: expect.not.stringMatching('password123')
        })
      );
    });
    
    it('should throw error if user exists', async () => {
      (userRepository.findByEmail as jest.Mock).mockResolvedValue({ id: '1' });
      
      await expect(
        userService.createUser({
          name: 'John Doe',
          email: 'john@example.com',
          password: 'password123'
        })
      ).rejects.toThrow('User already exists');
    });
  });
});
```

## Language-Specific Idioms and Patterns

### TypeScript Patterns

#### Type Guards
```typescript
function isUser(value: unknown): value is User {
  return (
    typeof value === 'object' &&
    value !== null &&
    'id' in value &&
    'name' in value
  );
}

if (isUser(data)) {
  console.log(data.name); // TypeScript knows this is User
}
```

#### Discriminated Unions
```typescript
type Result<T> =
  | { success: true; data: T }
  | { success: false; error: string };

function handleResult<T>(result: Result<T>) {
  if (result.success) {
    console.log(result.data);
  } else {
    console.error(result.error);
  }
}
```

#### Utility Types
```typescript
// Partial - make all properties optional
type PartialUser = Partial<User>;

// Pick - select specific properties
type UserPreview = Pick<User, 'id' | 'name'>;

// Omit - exclude specific properties
type UserWithoutEmail = Omit<User, 'email'>;

// Record - create object type with specific keys
type UserMap = Record<string, User>;
```

### Modern JavaScript Patterns

#### Optional Chaining
```javascript
const userName = user?.profile?.name ?? 'Guest';
```

#### Nullish Coalescing
```javascript
const port = config.port ?? 3000;
```

#### Destructuring
```javascript
// Object destructuring with defaults
const { name = 'Guest', age = 0 } = user;

// Array destructuring
const [first, second, ...rest] = array;

// Function parameter destructuring
function greet({ name, age }: User) {
  console.log(`Hello ${name}, you are ${age}`);
}
```

#### Spread Operators
```javascript
// Merge objects
const merged = { ...defaults, ...userSettings };

// Clone array
const clone = [...original];

// Add to array immutably
const newArray = [...items, newItem];
```

### React Patterns

#### Compound Components
```typescript
function Tabs({ children }: { children: React.ReactNode }) {
  const [activeIndex, setActiveIndex] = useState(0);
  
  return (
    <TabsContext.Provider value={{ activeIndex, setActiveIndex }}>
      {children}
    </TabsContext.Provider>
  );
}

Tabs.List = function TabsList({ children }: { children: React.ReactNode }) {
  return <div role="tablist">{children}</div>;
};

Tabs.Tab = function Tab({ index, children }: { index: number; children: React.ReactNode }) {
  const { activeIndex, setActiveIndex } = useContext(TabsContext);
  return (
    <button
      role="tab"
      aria-selected={activeIndex === index}
      onClick={() => setActiveIndex(index)}
    >
      {children}
    </button>
  );
};

// Usage:
<Tabs>
  <Tabs.List>
    <Tabs.Tab index={0}>Tab 1</Tabs.Tab>
    <Tabs.Tab index={1}>Tab 2</Tabs.Tab>
  </Tabs.List>
</Tabs>
```

#### Render Props
```typescript
interface DataLoaderProps<T> {
  url: string;
  render: (data: T, loading: boolean, error?: Error) => React.ReactNode;
}

function DataLoader<T>({ url, render }: DataLoaderProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error>();

  useEffect(() => {
    fetchData(url).then(setData).catch(setError).finally(() => setLoading(false));
  }, [url]);

  return <>{render(data!, loading, error)}</>;
}
```

#### Custom Hooks
```typescript
function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error(error);
    }
  };

  return [storedValue, setValue] as const;
}
```

### Accessibility (A11Y)

```typescript
// Semantic HTML
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/">Home</a></li>
  </ul>
</nav>

// ARIA labels
<button aria-label="Close dialog" onClick={onClose}>
  <CloseIcon />
</button>

// Keyboard navigation
<div
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyPress={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleClick();
    }
  }}
>
  Click me
</div>

// Focus management
const inputRef = useRef<HTMLInputElement>(null);

useEffect(() => {
  inputRef.current?.focus();
}, []);

// Screen reader support
<img src="image.jpg" alt="Descriptive text" />
<div role="status" aria-live="polite">
  {message}
</div>
```
