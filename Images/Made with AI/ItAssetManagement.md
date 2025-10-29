# IT Asset Management System

A modular IT Asset Management (ITAM) platform with a FastAPI + MongoDB backend and a modern React (CRACO + Tailwind + shadcn/ui) frontend. It supports organizations, asset groups, asset types, assets, custom fields, templates, and JWT-based authentication.

## Overview
- Backend: FastAPI, Motor (MongoDB), uvicorn, JWT auth (Bearer)
- Domain: Organization → Asset Groups → Asset Types → Assets
- Customization: Hierarchical custom fields with inheritance and defaults
- Security: JWT auth, per-organization access checks on all major routes
- Frontend: CRA + CRACO, TailwindCSS, shadcn/ui with rich UI components

Repository paths:
- `backend/` — FastAPI app (`server.py`), requirements
- `frontend/` — CRA app with CRACO, Tailwind config, components and pages

## Features
- User registration and login with JWT tokens
- Multi-organization support, per-user organization membership
- Asset groups and types with inherited/custom fields
- Asset CRUD with custom data, tags, relationships, and automatic defaults
- Secure per-organization authorization across all endpoints
- Built-in template endpoints for quick bootstraps (Hardware, Software, Network, Cloud)
- Detailed asset listing endpoint with enriched type/group info

## Requirements
- Python 3.12+
- Node.js 18+ (Frontend)
- MongoDB instance

## Backend Setup
1. Create `.env` in `backend/`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=itam
   JWT_SECRET_KEY=change-me-in-production
   CORS_ORIGINS=http://localhost:3000
   ```
2. Install and run:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   uvicorn server:app --reload --port 8000
   ```

## Frontend Setup
```bash
cd frontend
yarn install  # or npm install
yarn start    # CRACO dev server at http://localhost:3000
```

## Core API Endpoints (prefix `/api`)

### Auth
- `POST /auth/register` — create user (email, name, password, role?)
- `POST /auth/login` — returns `{ access_token, token_type, user }`
- `GET /auth/me` — current user (requires `Authorization: Bearer <token>`)

### Organizations
- `POST /organizations` — create (adds creator as member)
- `GET /organizations` — list organizations for current user
- `GET /organizations/{org_id}` — get single org
- `PUT /organizations/{org_id}` — update
- `DELETE /organizations/{org_id}` — delete (no asset groups present)

### Asset Groups
- `POST /asset-groups` — create (org-scoped)
- `GET /organizations/{org_id}/asset-groups` — list for org
- `PUT /asset-groups/{group_id}` — update
- `DELETE /asset-groups/{group_id}` — delete (no asset types present)

### Asset Types
- `POST /asset-types` — create (inherits fields from group)
- `GET /asset-groups/{group_id}/asset-types` — list types for a group
- `PUT /asset-types/{type_id}` — update
- `DELETE /asset-types/{type_id}` — delete (no assets present)

### Assets
- `POST /assets` — create asset (applies default values from type and group fields)
- `GET /organizations/{org_id}/assets` — list org assets
- `GET /asset-types/{type_id}/assets` — list assets by type
- `PUT /assets/{asset_id}` — update (handles type change propagation)
- `DELETE /assets/{asset_id}` — delete
- `GET /organizations/{org_id}/assets/detailed` — enriched assets with type/group names

### Templates
- `GET /templates/default-asset-groups` — built-in groups with suggested fields
  - Examples: Hardware, Software, Network Equipment, Cloud Services (date, currency, IP, MAC, dataset, etc.)

### Models (selected)
- `FieldDefinition`: flexible field system supporting types like `date`, `number`, `dataset`, `ip_address`, `mac_address`, `url`, `email`, `version`, `currency`, `password`, etc.
- `CustomTemplate`, `Organization`, `AssetGroup`, `AssetType`, `Asset`, plus `*Create` and `AssetUpdate` DTOs

## Example Usage (PowerShell/CMD style curl)
Register and login:
```bash
curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"name\":\"Admin\",\"password\":\"secret\",\"role\":\"admin\"}"

curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@example.com\",\"password\":\"secret\"}"
```

Create organization and group:
```bash
set TOKEN=<JWT_FROM_LOGIN>
curl -X POST http://localhost:8000/api/organizations ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Acme Corp\",\"description\":\"ITAM demo\"}"

curl -X POST http://localhost:8000/api/asset-groups ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Hardware\",\"organization_id\":\"<ORG_ID>\"}"
```

Create type and asset:
```bash
curl -X POST http://localhost:8000/api/asset-types ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Laptop\",\"asset_group_id\":\"<GROUP_ID>\",\"description\":\"Employee laptops\"}"

curl -X POST http://localhost:8000/api/assets ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Dell XPS\",\"asset_type_id\":\"<TYPE_ID>\",\"tags\":[\"critical\"]}"
```

## Tests
- Comprehensive API tests in repo root: `backend_test.py`, `focused_backend_test.py`, `review_focused_backend_test.py`, `enhanced_backend_test.py`, etc.
- Run from repo root:
  ```bash
  pytest -q
  ```
- Artifacts: `test_reports/`, summary: `test_result.md`

## Project Structure (excerpt)
```
ItAssetManagement/
├── backend/
│   ├── server.py              # FastAPI app & endpoints (auth, orgs, groups, types, assets, templates)
│   └── requirements.txt
├── frontend/
│   ├── package.json           # CRA + CRACO + Tailwind + shadcn/ui
│   ├── craco.config.js
│   └── src/
├── backend_test.py            # API tests (+ many focused tests)
├── tests/                     # Additional tests
└── test_reports/              # Test artifacts
```

## Troubleshooting
- Ensure MongoDB is running and `MONGO_URL`, `DB_NAME`, `JWT_SECRET_KEY` set correctly
- Include frontend origin in `CORS_ORIGINS` to avoid CORS errors during local dev
- 401 errors: confirm `Authorization: Bearer <token>` header and token freshness
- 400 on delete: ensure no dependent records (e.g., no types before deleting group)
