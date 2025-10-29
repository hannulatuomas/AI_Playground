
# Web Development Documentation Preferences

This document defines documentation standards for web development projects
(JavaScript, TypeScript, React, Vue, Angular, Node.js, HTML, CSS).
These preferences guide AI agents in maintaining consistent documentation.

---

## General Documentation Philosophy

**Core Principles:**
1. **Component-Based Documentation** - Document components and their props/API
2. **JSDoc for JavaScript/TypeScript** - Standard documentation format
3. **Living Style Guides** - Documentation should demo components
4. **API Endpoint Documentation** - Clear REST/GraphQL API docs
5. **Responsive Examples** - Show responsive behavior
6. **Accessibility Notes** - Document accessibility features

---

## Code Documentation Standards

### JSDoc Format (JavaScript/TypeScript)

**Function Documentation:**

```javascript
/**
 * Fetches user data from the API.
 * 
 * @async
 * @function fetchUserData
 * @param {string} userId - The unique identifier of the user
 * @param {Object} [options={}] - Optional configuration
 * @param {boolean} [options.includeProfile=false] - Include profile data
 * @param {number} [options.timeout=5000] - Request timeout in milliseconds
 * @returns {Promise<User>} Promise resolving to user object
 * @throws {NetworkError} When network request fails
 * @throws {ValidationError} When userId is invalid
 * 
 * @example
 * // Fetch basic user data
 * const user = await fetchUserData('user-123');
 * 
 * @example
 * // Fetch with profile data
 * const user = await fetchUserData('user-123', { includeProfile: true });
 */
async function fetchUserData(userId, options = {}) {
  // Implementation
}
```

**Class Documentation:**

```javascript
/**
 * Represents a data service for managing user information.
 * 
 * @class UserService
 * @classdesc Provides methods for CRUD operations on user data.
 * Handles caching and error recovery automatically.
 * 
 * @example
 * const service = new UserService();
 * const user = await service.getUser('123');
 */
class UserService {
  /**
   * Creates a new UserService instance.
   * 
   * @constructor
   * @param {Object} config - Configuration object
   * @param {string} config.apiUrl - Base API URL
   * @param {string} config.apiKey - API authentication key
   */
  constructor(config) {
    // Implementation
  }
  
  /**
   * Retrieves a user by ID.
   * 
   * @method
   * @param {string} id - User ID
   * @returns {Promise<User>} User object
   */
  async getUser(id) {
    // Implementation
  }
}
```

### TypeScript Documentation

```typescript
/**
 * User model representing a system user.
 */
interface User {
  /** Unique user identifier */
  id: string;
  
  /** User's display name */
  name: string;
  
  /** User's email address */
  email: string;
  
  /** Optional profile image URL */
  avatar?: string;
}

/**
 * Fetches user data from the API.
 * 
 * @param userId - The unique identifier of the user
 * @param options - Optional configuration
 * @returns Promise resolving to user object
 * @throws {NetworkError} When network request fails
 * 
 * @example
 * ```typescript
 * const user = await fetchUserData('user-123');
 * console.log(user.name);
 * ```
 */
async function fetchUserData(
  userId: string,
  options?: FetchOptions
): Promise<User> {
  // Implementation
}
```

### React Component Documentation

```typescript
/**
 * Button component with various styles and states.
 * 
 * @component
 * @example
 * ```tsx
 * <Button variant="primary" onClick={handleClick}>
 *   Click Me
 * </Button>
 * ```
 */
interface ButtonProps {
  /** Button content */
  children: React.ReactNode;
  
  /** Button style variant */
  variant?: 'primary' | 'secondary' | 'outline';
  
  /** Button size */
  size?: 'small' | 'medium' | 'large';
  
  /** Whether button is disabled */
  disabled?: boolean;
  
  /** Click handler */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  
  /** Additional CSS classes */
  className?: string;
  
  /** Accessible label for screen readers */
  'aria-label'?: string;
}

/**
 * Customizable button component.
 * 
 * @param props - Component props
 * @returns Button element
 */
export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
  className,
  ...rest
}) => {
  // Implementation
};

Button.displayName = 'Button';
```

### Vue Component Documentation

```vue
<!--
/**
 * UserCard component displays user information in a card format.
 * 
 * @component UserCard
 * @example
 * <UserCard :user="userData" @click="handleClick" />
 */
-->
<template>
  <div class="user-card">
    <!-- Template -->
  </div>
</template>

<script>
export default {
  name: 'UserCard',
  
  props: {
    /**
     * User object to display
     * @type {Object}
     * @property {string} id - User ID
     * @property {string} name - User name
     * @property {string} email - User email
     */
    user: {
      type: Object,
      required: true
    },
    
    /**
     * Whether to show detailed information
     * @type {boolean}
     * @default false
     */
    detailed: {
      type: Boolean,
      default: false
    }
  },
  
  emits: {
    /**
     * Emitted when card is clicked
     * @event click
     * @property {Object} user - The user object
     */
    click: (user) => true
  },
  
  /**
   * Formats the user's display name
   * @param {Object} user - User object
   * @returns {string} Formatted name
   */
  methods: {
    formatName(user) {
      // Implementation
    }
  }
}
</script>
```

### CSS/SCSS Documentation

```css
/**
 * Primary button styles
 * 
 * @section Buttons
 * @subsection Primary Buttons
 * 
 * @example
 * <button class="btn btn-primary">Click me</button>
 */
.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-white);
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s ease;
}

/**
 * Hover state for primary button
 */
.btn-primary:hover {
  background-color: var(--color-primary-dark);
}

/**
 * Responsive container
 * 
 * @responsive
 * - Mobile: Full width
 * - Tablet: 90% width, centered
 * - Desktop: Max 1200px width, centered
 */
.container {
  width: 100%;
  margin: 0 auto;
}

@media (min-width: 768px) {
  .container {
    width: 90%;
  }
}

@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
  }
}
```

---

## Project Documentation Structure

### Required Files

1. **README.md** - Project overview
2. **CONTRIBUTING.md** - Contribution guidelines
3. **CHANGELOG.md** - Version history
4. **package.json** - Dependencies and scripts (documented)
5. **docs/**
   - **API.md** - API documentation
   - **COMPONENTS.md** - Component library documentation
   - **STYLEGUIDE.md** - UI/style guide
   - **ARCHITECTURE.md** - Application architecture

### README.md Structure

```markdown
# Project Name

Brief project description.

[![Build Status](badge-url)](link)
[![npm version](badge-url)](link)
[![License](badge-url)](link)

## Features

- Feature 1
- Feature 2
- Feature 3

## Demo

[Live Demo](demo-url) | [Screenshots](screenshots-url)

## Prerequisites

- Node.js 16.x or later
- npm 8.x or yarn 1.22.x

## Installation

```bash
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
```

## Configuration

### Environment Variables

```env
# API Configuration
API_URL=https://api.example.com
API_KEY=your-api-key

# App Configuration
PORT=3000
NODE_ENV=development
```

## Development

```bash
# Start development server
npm run dev

# Run tests
npm test

# Run linter
npm run lint

# Build for production
npm run build
```

## Project Structure

```
src/
├── components/     # Reusable components
├── pages/          # Page components
├── hooks/          # Custom hooks
├── utils/          # Utility functions
├── styles/         # Global styles
├── api/            # API integration
└── types/          # TypeScript types
```

## Component Usage

### Button Component

```tsx
import { Button } from './components/Button';

<Button variant="primary" onClick={handleClick}>
  Click me
</Button>
```

## API Documentation

See [API.md](docs/API.md) for detailed API documentation.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE)
```

### Component Documentation (COMPONENTS.md)

```markdown
# Component Library

## Button

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `ReactNode` | - | Button content |
| `variant` | `'primary' \| 'secondary'` | `'primary'` | Button style |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Button size |
| `disabled` | `boolean` | `false` | Disabled state |
| `onClick` | `function` | - | Click handler |

### Examples

#### Primary Button

```tsx
<Button variant="primary" onClick={() => alert('Clicked')}>
  Primary Button
</Button>
```

#### Disabled Button

```tsx
<Button disabled>
  Disabled Button
</Button>
```

### Accessibility

- Supports keyboard navigation
- Includes ARIA attributes
- Works with screen readers

## Input

[Similar documentation for Input component]
```

---

## API Documentation

### REST API Documentation

```markdown
# API Reference

## Base URL

```
https://api.example.com/v1
```

## Authentication

All API requests require authentication via Bearer token:

```bash
Authorization: Bearer YOUR_TOKEN_HERE
```

## Endpoints

### Get Users

```
GET /users
```

Retrieves a list of users.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page` | `number` | No | Page number (default: 1) |
| `limit` | `number` | No | Items per page (default: 10) |
| `search` | `string` | No | Search query |

**Response:**

```json
{
  "data": [
    {
      "id": "user-123",
      "name": "John Doe",
      "email": "john@example.com"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100
  }
}
```

**Example:**

```bash
curl -X GET "https://api.example.com/v1/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

```javascript
// Using fetch
const response = await fetch('https://api.example.com/v1/users', {
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN'
  }
});
const data = await response.json();
```

### Create User

```
POST /users
```

Creates a new user.

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user"
}
```

**Response:**

```json
{
  "id": "user-123",
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "createdAt": "2025-10-12T10:00:00Z"
}
```

**Error Responses:**

- `400 Bad Request` - Validation error
- `401 Unauthorized` - Authentication required
- `409 Conflict` - User already exists
```

### GraphQL API Documentation

```markdown
# GraphQL API

## Endpoint

```
POST /graphql
```

## Schema

### Queries

#### getUser

Fetch a single user by ID.

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    profile {
      avatar
      bio
    }
  }
}
```

**Variables:**

```json
{
  "id": "user-123"
}
```

**Response:**

```json
{
  "data": {
    "user": {
      "id": "user-123",
      "name": "John Doe",
      "email": "john@example.com",
      "profile": {
        "avatar": "https://pbs.twimg.com/media/FVSphbFWAAAeORr?format=jpg&name=large",
        "bio": "Software developer"
      }
    }
  }
}
```

### Mutations

#### createUser

Create a new user.

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
  }
}
```

**Variables:**

```json
{
  "input": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```
```

---

## Documentation Tools

### Recommended Tools

1. **Storybook** - Component documentation and demos
   ```bash
   npx storybook init
   ```

2. **TypeDoc** - TypeScript API documentation
   ```bash
   npm install --save-dev typedoc
   typedoc --out docs src
   ```

3. **JSDoc** - JavaScript documentation
   ```bash
   npm install --save-dev jsdoc
   jsdoc -c jsdoc.json
   ```

4. **Swagger/OpenAPI** - REST API documentation
   ```yaml
   openapi: 3.0.0
   info:
     title: API Name
     version: 1.0.0
   ```

5. **GraphQL Playground/GraphiQL** - GraphQL API explorer

### Storybook Stories

```typescript
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

/**
 * Button component for user interactions.
 * 
 * Supports multiple variants and sizes.
 */
const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'outline']
    },
    size: {
      control: 'select',
      options: ['small', 'medium', 'large']
    }
  }
};

export default meta;
type Story = StoryObj<typeof Button>;

/**
 * Primary button style
 */
export const Primary: Story = {
  args: {
    children: 'Button',
    variant: 'primary'
  }
};

/**
 * Secondary button style
 */
export const Secondary: Story = {
  args: {
    children: 'Button',
    variant: 'secondary'
  }
};
```

---

## Package.json Documentation

```json
{
  "name": "project-name",
  "version": "1.0.0",
  "description": "Project description",
  "scripts": {
    "dev": "Development server - starts app in development mode",
    "build": "Production build - creates optimized build",
    "test": "Run test suite - executes all unit and integration tests",
    "lint": "Code linting - checks code quality with ESLint",
    "format": "Code formatting - formats code with Prettier",
    "storybook": "Component docs - starts Storybook dev server",
    "docs": "Generate documentation - creates API docs with TypeDoc"
  }
}
```

---

## Documentation Maintenance

### Maintenance Schedule

1. **On Every PR**: Update component docs, README if needed
2. **Weekly**: Review TODO comments, update project status
3. **Sprint End**: Update CHANGELOG, regenerate documentation
4. **Release**: Full documentation review and update

### Documentation Checklist

- [ ] All components have JSDoc/TSDoc comments
- [ ] Props/parameters documented
- [ ] Examples provided
- [ ] Storybook stories created
- [ ] API endpoints documented
- [ ] README.md current
- [ ] CHANGELOG.md updated
- [ ] Environment variables documented
- [ ] Accessibility notes included

---

## AI Agent Guidelines

**For AI Agents Maintaining Documentation:**

1. **Use JSDoc/TSDoc** - Standard format for web projects
2. **Document Props/Parameters** - Especially for components
3. **Include Examples** - Live, working examples
4. **API Documentation** - Keep REST/GraphQL docs current
5. **Component Demos** - Update Storybook stories
6. **Accessibility** - Document ARIA attributes
7. **Responsive Behavior** - Note mobile/tablet/desktop differences
8. **Browser Compatibility** - Document browser requirements

**Priority Order:**
1. Component documentation (JSDoc + Storybook)
2. API documentation
3. README.md
4. COMPONENTS.md
5. CHANGELOG.md

---

**Last Updated:** 2025-10-12
**Version:** 1.0
