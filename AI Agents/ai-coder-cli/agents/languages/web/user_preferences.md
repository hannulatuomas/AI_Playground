
# Web Development User Preferences (JavaScript/TypeScript/HTML/CSS)

## Framework and Library Preferences

### JavaScript Framework
```yaml
# Primary JavaScript/TypeScript framework
framework: react

# Options:
# - react: React
# - vue: Vue.js
# - angular: Angular
# - svelte: Svelte
# - solid: SolidJS
# - vanilla: Vanilla JavaScript
# - next: Next.js (React meta-framework)
# - nuxt: Nuxt.js (Vue meta-framework)
```

### Meta-Framework (React)
```yaml
# React meta-framework choice
react_metaframework: nextjs

# Options:
# - nextjs: Next.js (full-stack)
# - remix: Remix (full-stack)
# - gatsby: Gatsby (static)
# - create_react_app: Create React App (basic)
# - vite: Vite + React (fast dev)
```

### State Management
```yaml
# State management solution
state_management: zustand

# Options for React:
# - zustand: Zustand (lightweight)
# - redux_toolkit: Redux Toolkit
# - jotai: Jotai (atomic)
# - recoil: Recoil (atomic)
# - mobx: MobX (observable)
# - context_api: React Context API (built-in)

# Options for Vue:
# - pinia: Pinia (recommended for Vue 3)
# - vuex: Vuex (traditional)

# Options for Angular:
# - ngrx: NgRx
# - akita: Akita
```

### UI Component Library
```yaml
# UI component library
ui_library: material_ui

# Options for React:
# - material_ui: Material-UI (MUI)
# - ant_design: Ant Design
# - chakra_ui: Chakra UI
# - shadcn_ui: shadcn/ui
# - tailwind_components: Headless UI + Tailwind
# - react_bootstrap: React Bootstrap
# - none: Custom components

# Options for Vue:
# - vuetify: Vuetify
# - element_plus: Element Plus
# - primevue: PrimeVue
# - ant_design_vue: Ant Design Vue

# Options for Angular:
# - angular_material: Angular Material
# - ng_bootstrap: ng-bootstrap
# - primeng: PrimeNG
```

### CSS Framework/Approach
```yaml
# CSS styling approach
css_approach: tailwind

# Options:
# - tailwind: Tailwind CSS
# - styled_components: Styled Components (CSS-in-JS)
# - emotion: Emotion (CSS-in-JS)
# - css_modules: CSS Modules
# - sass: Sass/SCSS
# - less: Less
# - vanilla_css: Plain CSS
# - bootstrap: Bootstrap
```

## Code Style Preferences

### Language Choice
```yaml
# TypeScript vs JavaScript
language: typescript

# Options:
# - typescript: TypeScript (recommended)
# - javascript: JavaScript

# TypeScript strictness
typescript_strict: true

# Options:
# - true: Strict mode enabled
# - false: Standard mode
```

### Indentation and Formatting
```yaml
# Indentation
indent_style: spaces
indent_size: 2

# Line length
max_line_length: 100  # characters

# Quote style
quote_style: single

# Options:
# - single: 'string'
# - double: "string"

# Semicolons
semicolons: true

# Options:
# - true: Always use semicolons
# - false: No semicolons (ASI)

# Trailing commas
trailing_commas: es5

# Options:
# - none: No trailing commas
# - es5: Trailing commas where valid in ES5
# - all: Trailing commas everywhere possible

# Arrow function parentheses
arrow_parens: avoid

# Options:
# - avoid: x => x
# - always: (x) => x
```

### Naming Conventions
```yaml
# Component file naming
component_naming: PascalCase

# Options:
# - PascalCase: UserProfile.tsx
# - kebab-case: user-profile.tsx

# Function/variable naming
function_naming: camelCase

# Constant naming
constant_naming: UPPER_SNAKE_CASE

# CSS class naming
css_class_naming: kebab-case

# Options:
# - kebab-case: user-profile
# - camelCase: userProfile
# - BEM: block__element--modifier
```

### Import Organization
```yaml
# Import order
import_order:
  - react_first        # React/Vue/framework first
  - external_libraries # npm packages
  - internal_absolute  # @/components
  - internal_relative  # ./component
  - styles            # CSS imports last

# Path aliasing
use_path_aliases: true  # @/ for src/

# Named vs default exports
export_preference: named_exports

# Options:
# - named_exports: export const Component
# - default_exports: export default Component
# - mixed: Use both as appropriate
```

### Function Declaration Style
```yaml
# Function declaration preference
function_style: arrow_functions

# Options:
# - arrow_functions: const func = () => {}
# - function_keyword: function func() {}
# - mixed: Use both appropriately

# Component declaration (React)
component_style: function_components

# Options:
# - function_components: function Component() {}
# - arrow_components: const Component = () => {}
# - class_components: class Component extends React.Component
```

## Build Tool Preferences

### Bundler
```yaml
# Build tool / bundler
bundler: vite

# Options:
# - vite: Vite (fast, modern)
# - webpack: Webpack (mature, configurable)
# - parcel: Parcel (zero-config)
# - rollup: Rollup (library bundling)
# - esbuild: esbuild (extremely fast)
# - turbopack: Turbopack (experimental)
```

### Package Manager
```yaml
# Package manager
package_manager: pnpm

# Options:
# - pnpm: pnpm (fast, efficient)
# - npm: npm (default)
# - yarn: Yarn Classic
# - yarn_berry: Yarn Berry (v2+)
```

### Module System
```yaml
# Module system
module_system: esm

# Options:
# - esm: ES Modules (import/export)
# - commonjs: CommonJS (require/module.exports)
# - both: Dual module (ESM + CommonJS)
```

## Testing Preferences

### Unit Testing Framework
```yaml
# Unit test framework
test_framework: vitest

# Options:
# - vitest: Vitest (Vite-powered, modern)
# - jest: Jest (popular, mature)
# - mocha: Mocha (flexible)
# - jasmine: Jasmine (BDD-style)
```

### React Testing
```yaml
# React testing library
react_testing: testing_library

# Options:
# - testing_library: React Testing Library (recommended)
# - enzyme: Enzyme (legacy)

# Testing approach
testing_approach: integration

# Options:
# - integration: Integration/user-focused tests
# - unit: Pure unit tests
# - mixed: Combination
```

### E2E Testing
```yaml
# E2E testing framework
e2e_framework: playwright

# Options:
# - playwright: Playwright (modern, fast)
# - cypress: Cypress (developer-friendly)
# - puppeteer: Puppeteer (headless Chrome)
# - selenium: Selenium WebDriver (traditional)
```

### Code Coverage
```yaml
# Minimum coverage target
min_coverage: 80  # percentage

# Coverage tool
coverage_tool: vitest  # or jest, nyc, istanbul
```

## Tooling Preferences

### Linter
```yaml
# JavaScript/TypeScript linter
linter: eslint

# ESLint configuration
eslint_config: standard

# Options:
# - standard: JavaScript Standard Style
# - airbnb: Airbnb Style Guide
# - google: Google Style Guide
# - custom: Custom configuration

# Enable type-aware rules (TypeScript)
typescript_eslint_typed: true
```

### Formatter
```yaml
# Code formatter
formatter: prettier

# Format on save
format_on_save: true

# Prettier integration with ESLint
prettier_eslint_integration: true
```

### Type Checker
```yaml
# TypeScript type checking
type_checking: strict

# Run type check on build
type_check_on_build: true

# Use JSDoc for JS files
use_jsdoc: true  # For JavaScript projects
```

### Git Hooks
```yaml
# Git hooks tool
git_hooks: husky

# Options:
# - husky: Husky (popular)
# - simple_git_hooks: simple-git-hooks (lightweight)
# - none: No git hooks

# Pre-commit hooks
pre_commit_hooks:
  - lint_staged  # Lint staged files
  - type_check   # Run type checking
  - format       # Format code

# Commit message linting
commit_lint: true  # Use commitlint
```

## Project Structure Preferences

### Folder Organization
```yaml
# Project structure style
folder_structure: feature_based

# Options:
# - feature_based: Group by feature
# - type_based: Group by file type
# - atomic_design: Atomic design structure
# - modular: Modular/domain-based

# Example feature_based:
# /src
#   /features
#     /users
#       - UserList.tsx
#       - UserDetail.tsx
#       - userService.ts
#     /orders
#       - OrderList.tsx
#       - orderService.ts

# Example type_based:
# /src
#   /components
#   /services
#   /hooks
#   /utils
#   /types
```

### Component Organization
```yaml
# Component file structure
component_structure: folder_per_component

# Options:
# - folder_per_component: Each component in own folder
# - flat: All components in components folder
# - grouped: Group related components

# Example folder_per_component:
# /components
#   /Button
#     - Button.tsx
#     - Button.test.tsx
#     - Button.module.css
#     - index.ts
```

### Asset Management
```yaml
# Asset organization
asset_organization: colocated

# Options:
# - colocated: Assets near components that use them
# - centralized: All assets in /assets or /public
# - hybrid: Mix of both

# Image optimization
optimize_images: true

# SVG handling
svg_handling: svgr  # Convert SVG to React components

# Options:
# - svgr: @svgr/webpack
# - inline: Inline SVGs
# - url: Load as URL
```

## Design Pattern Preferences

### Component Patterns
```yaml
# Component composition pattern
composition_pattern: compound_components

# Options:
# - compound_components: Flexible compound components
# - render_props: Render props pattern
# - custom_hooks: Custom hooks for logic
# - hoc: Higher-Order Components (legacy)
# - mixed: Use appropriate pattern for each case
```

### Data Fetching
```yaml
# Data fetching approach
data_fetching: react_query

# Options for React:
# - react_query: TanStack Query (formerly React Query)
# - swr: SWR
# - rtk_query: RTK Query (Redux Toolkit)
# - apollo: Apollo Client (GraphQL)
# - fetch_api: Native fetch
# - axios: Axios

# Options for Vue:
# - vue_query: Vue Query
# - apollo: Apollo Client
# - axios: Axios
```

### Form Management
```yaml
# Form handling library
form_library: react_hook_form

# Options for React:
# - react_hook_form: React Hook Form (lightweight)
# - formik: Formik (feature-rich)
# - final_form: React Final Form
# - uncontrolled: Uncontrolled inputs
# - controlled: Controlled inputs

# Form validation
form_validation: zod

# Options:
# - zod: Zod (TypeScript-first)
# - yup: Yup (schema validation)
# - joi: Joi
# - custom: Custom validation
```

### Routing
```yaml
# Routing library
routing: react_router

# Options for React:
# - react_router: React Router
# - tanstack_router: TanStack Router
# - nextjs_router: Next.js Router (if using Next.js)

# Options for Vue:
# - vue_router: Vue Router
# - nuxt_router: Nuxt Router (if using Nuxt)

# Options for Angular:
# - angular_router: Angular Router (built-in)
```

## API and Backend Integration

### API Style
```yaml
# API communication style
api_style: rest

# Options:
# - rest: REST API
# - graphql: GraphQL
# - trpc: tRPC (type-safe RPC)
# - grpc: gRPC-Web
```

### API Client
```yaml
# HTTP client
http_client: axios

# Options:
# - axios: Axios (feature-rich)
# - fetch: Native Fetch API
# - ky: Ky (modern wrapper)
# - got: Got (Node.js)
```

### Type Safety for APIs
```yaml
# API type generation
api_types: openapi_codegen

# Options:
# - openapi_codegen: OpenAPI/Swagger codegen
# - graphql_codegen: GraphQL Code Generator
# - trpc: tRPC (runtime type safety)
# - manual: Manual type definitions
# - none: No type generation
```

## Performance Preferences

### Code Splitting
```yaml
# Code splitting strategy
code_splitting: route_based

# Options:
# - route_based: Split by route
# - component_based: Split by component
# - both: Aggressive splitting
# - minimal: Minimal splitting

# Dynamic imports
use_dynamic_imports: true
```

### Image Optimization
```yaml
# Image optimization tool
image_optimization: next_image

# Options:
# - next_image: Next.js Image component
# - custom: Custom solution
# - none: No optimization

# Image formats
preferred_image_formats:
  - webp
  - avif
  - jpg

# Lazy loading
lazy_load_images: true
```

### Bundle Optimization
```yaml
# Bundle analyzer
use_bundle_analyzer: true

# Tree shaking
enable_tree_shaking: true

# Minification
minify_code: true

# Source maps in production
source_maps_prod: false
```

## Accessibility Preferences

### A11Y Standards
```yaml
# Accessibility compliance target
a11y_target: wcag_aa

# Options:
# - wcag_aa: WCAG 2.1 AA (recommended)
# - wcag_aaa: WCAG 2.1 AAA (stricter)
# - section_508: Section 508
```

### A11Y Linting
```yaml
# Accessibility linting
a11y_linting: eslint_plugin_jsx_a11y

# Enable A11Y testing
a11y_testing: true  # axe-core, jest-axe

# Semantic HTML preference
prefer_semantic_html: true
```

## SEO Preferences

### Meta Tags
```yaml
# SEO meta tag management
seo_management: next_seo

# Options:
# - next_seo: next-seo (Next.js)
# - react_helmet: React Helmet
# - vue_meta: vue-meta (Vue)
# - manual: Manual meta tags
```

### Sitemap Generation
```yaml
# Generate sitemap
generate_sitemap: true

# robots.txt
generate_robots_txt: true
```

## Internationalization (i18n)

### i18n Library
```yaml
# Internationalization library
i18n_library: react_i18next

# Options for React:
# - react_i18next: react-i18next
# - format_js: FormatJS (React Intl)
# - lingui: Lingui

# Options for Vue:
# - vue_i18n: Vue I18n

# Options for Angular:
# - ngx_translate: ngx-translate
# - angular_i18n: Angular i18n (built-in)

# Default locale
default_locale: en-US

# Supported locales
supported_locales:
  - en-US
  - es-ES
  - fr-FR
  - de-DE
```

## PWA and Mobile

### Progressive Web App
```yaml
# PWA support
enable_pwa: true

# Service worker
service_worker: workbox

# Options:
# - workbox: Workbox (Google)
# - custom: Custom service worker
# - none: No service worker
```

### Mobile Development
```yaml
# Mobile framework (if applicable)
mobile_framework: react_native

# Options:
# - react_native: React Native
# - ionic: Ionic
# - nativescript: NativeScript
# - capacitor: Capacitor
# - none: Web only
```

## Documentation Preferences

### Component Documentation
```yaml
# Component documentation tool
component_docs: storybook

# Options:
# - storybook: Storybook
# - styleguidist: React Styleguidist
# - docz: Docz
# - none: No component docs

# Generate prop types documentation
document_prop_types: true
```

### API Documentation
```yaml
# API documentation format
api_docs_format: jsdoc

# Options:
# - jsdoc: JSDoc comments
# - tsdoc: TSDoc (TypeScript)
# - markdown: Markdown files
```

## Environment Configuration

### Environment Variables
```yaml
# Environment variable prefix
env_prefix: VITE_  # or REACT_APP_, NEXT_PUBLIC_, etc.

# Use .env files
use_env_files: true

# Environment-specific configs
env_configs:
  - .env.development
  - .env.production
  - .env.test
```

### Configuration Management
```yaml
# Configuration approach
config_management: environment_variables

# Options:
# - environment_variables: .env files
# - config_files: config.js files
# - runtime_config: Fetch config at runtime
```

## Backend Framework Preferences

### Server Framework
```yaml
# Backend framework choice
backend_framework: express

# Options:
# - express: Express.js (Node.js)
# - fastify: Fastify (faster alternative)
# - koa: Koa.js (modern Express)
# - nestjs: NestJS (TypeScript-first)
# - hapi: Hapi.js (enterprise)
# - nextjs_api: Next.js API Routes
```

### Architecture Pattern
```yaml
# Backend architecture
backend_architecture: layered

# Options:
# - layered: Layered (controller -> service -> repository)
# - clean: Clean Architecture
# - mvc: Model-View-Controller
# - modular: Modular/Domain-based
```

### ORM/Database Client
```yaml
# Database ORM/Client
orm: prisma

# Options:
# - prisma: Prisma ORM
# - typeorm: TypeORM
# - sequelize: Sequelize
# - mongoose: Mongoose (MongoDB)
# - knex: Knex.js (SQL query builder)
# - raw: Raw SQL queries
```

### Database Type
```yaml
# Primary database
database: postgresql

# Options:
# - postgresql: PostgreSQL
# - mysql: MySQL/MariaDB
# - mongodb: MongoDB
# - sqlite: SQLite
# - redis: Redis (cache/session)
```

### Authentication Strategy
```yaml
# Authentication method
auth_strategy: jwt

# Options:
# - jwt: JSON Web Tokens
# - session: Express sessions
# - oauth: OAuth 2.0
# - passport: Passport.js
# - auth0: Auth0
# - firebase_auth: Firebase Authentication
```

### API Documentation
```yaml
# API documentation tool
api_docs: swagger

# Options:
# - swagger: Swagger/OpenAPI
# - postman: Postman collections
# - api_blueprint: API Blueprint
# - none: No API docs
```

### Logging Framework
```yaml
# Logging library
logging: winston

# Options:
# - winston: Winston
# - pino: Pino (fast)
# - bunyan: Bunyan
# - morgan: Morgan (HTTP logging)
# - console: Console.log only
```

### Validation Library
```yaml
# Request validation
validation: zod

# Options:
# - zod: Zod (TypeScript-first)
# - joi: Joi
# - yup: Yup
# - class_validator: class-validator (NestJS)
# - express_validator: express-validator
```

## Full-Stack Deployment

### Monorepo vs Polyrepo
```yaml
# Repository structure
repo_structure: monorepo

# Options:
# - monorepo: Monorepo (all in one)
# - polyrepo: Separate repos
```

### Monorepo Tool
```yaml
# Monorepo management (if monorepo)
monorepo_tool: turborepo

# Options:
# - turborepo: Turborepo
# - nx: Nx
# - lerna: Lerna
# - pnpm_workspaces: pnpm workspaces
# - yarn_workspaces: Yarn workspaces
```

### Deployment Preferences

### Hosting Platform
```yaml
# Preferred hosting platform
hosting: vercel

# Options:
# - vercel: Vercel (Next.js optimal)
# - netlify: Netlify
# - aws_amplify: AWS Amplify
# - azure_static_web_apps: Azure Static Web Apps
# - github_pages: GitHub Pages
# - cloudflare_pages: Cloudflare Pages
# - railway: Railway
# - render: Render
# - heroku: Heroku
# - digitalocean: DigitalOcean App Platform
# - self_hosted: Self-hosted
```

### Containerization
```yaml
# Use Docker
use_docker: true

# Docker compose for local dev
docker_compose: true

# Kubernetes deployment
use_kubernetes: false
```

### CI/CD
```yaml
# CI/CD platform
cicd_platform: github_actions

# Options:
# - github_actions: GitHub Actions
# - gitlab_ci: GitLab CI
# - jenkins: Jenkins
# - circleci: CircleCI
# - travis: Travis CI
# - azure_devops: Azure DevOps
```

### Build Output
```yaml
# Output directory
output_directory: dist  # or build, out

# Generate static export
static_export: false  # true for SSG

# Server-side rendering
ssr: true  # For Next.js, Nuxt, etc.
```

## Development Environment

### Runtime Version Management
```yaml
# Node version manager
node_version_manager: nvm

# Options:
# - nvm: Node Version Manager
# - fnm: Fast Node Manager
# - n: n (simple)
# - volta: Volta
# - asdf: asdf-vm

# Preferred Node version
node_version: "20.x"  # LTS version
```

### IDE/Editor
```yaml
# Primary code editor
editor: vscode

# Options:
# - vscode: Visual Studio Code
# - webstorm: WebStorm
# - vim: Vim/Neovim
# - sublime: Sublime Text
# - atom: Atom
```

### Code Quality Tools
```yaml
# Pre-commit hooks
use_pre_commit_hooks: true

# Tools to run on commit
pre_commit_tools:
  - lint
  - format
  - type_check
  - test

# Auto-fix on save
auto_fix_on_save: true
```

## IMPORTANT: User Preferences Override

**This configuration file serves as the LAST SOURCE OF TRUTH and will override any conflicting settings in best_practices.md.**

When generating code, the agent should:
1. First consult best_practices.md for general guidelines
2. Then apply user_preferences.md settings to override specific choices
3. Always prioritize user preferences over best practices when conflicts arise

Example: If best_practices.md suggests React with Redux, but user_preferences.md specifies Vue with Pinia, the agent MUST use Vue with Pinia.
