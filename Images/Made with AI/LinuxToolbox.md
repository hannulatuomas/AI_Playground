# LinuxToolbox — Linux Admin Tool

A Linux administration knowledge base and command explorer. Backend provides a FastAPI + MongoDB API with auth, command CRUD, advanced search, categories/tags, and saved commands. Frontend is a modern React app (CRACO + Tailwind + shadcn/ui).

## Overview
- Backend: FastAPI, Motor (MongoDB), pbkdf2_sha256 password hashing, JWT auth (Bearer)
- Domain: `Command` entries (name, description, syntax, examples, category, tags, visibility) and `SavedCommand`
- Features: Full-text-like search via regex across fields, filters by category/tags, categories-with-subcategories endpoint, unique tag listing
- Frontend: CRA + CRACO, TailwindCSS, shadcn/ui components

Repository paths:
- `backend/` — FastAPI app (`server.py`), requirements
- `frontend/` — CRA app with CRACO, Tailwind config, components and pages
- Root utilities: large datasets/population scripts (e.g., `populate_commands.py`, `comprehensive_linux_commands.py`, ...)

## Requirements
- Python 3.12+
- Node.js 18+ (Frontend)
- MongoDB instance

## Backend Setup
1. Create `.env` in `backend/`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=linux_toolbox
   CORS_ORIGINS=http://localhost:3000
   SECRET_KEY=change-me
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

## Core API (prefix `/api`)

### Auth
- `POST /auth/register` — register and receive `{ access_token, user }`
- `POST /auth/login` — login and receive `{ access_token, user }`
- `GET /auth/me` — get current user (requires `Authorization: Bearer <token>`)

### Commands
- `GET /commands?category=&tags=&limit=&offset=` — list commands (public or owned)
- `POST /commands/search` — body: `{ query?, category?, tags?, limit?, offset? }` advanced search across name, description, syntax, examples, tags
- `POST /commands` — create (auth required)
- `GET /commands/{id}` — get one
- `PUT /commands/{id}` — update (author only)
- `DELETE /commands/{id}` — delete (author only)

### Saved Commands
- `POST /saved-commands` — save a command for current user (body: `{ command_id }`)
- `GET /saved-commands` — list saved commands for current user
- `DELETE /saved-commands/{command_id}` — remove from saved

### Taxonomy
- `GET /categories` — list unique categories
- `GET /categories-with-subcategories` — categories with curated subcategories
- `GET /tags` — unique tags

### Basic
- `GET /` — `{ message: "Linux Admin Tool API" }`

### Models (selected)
- `CommandCreate`: `name`, `description`, `syntax`, `examples[]`, `category`, `tags[]`, `is_public?`
- `CommandResponse`: above plus ids, timestamps, author, visibility
- `SavedCommandCreate`: `command_id`

## Example Usage
Register and login:
```bash
curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@example.com\",\"username\":\"user\",\"password\":\"secret\"}"

curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"user@example.com\",\"password\":\"secret\"}"
```

Create a command:
```bash
set TOKEN=<JWT>
curl -X POST http://localhost:8000/api/commands ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"grep\",\"description\":\"Search text\",\"syntax\":\"grep [opts] pattern files\",\"examples\":[\"grep -R pattern .\"],\"category\":\"Text Processing\",\"tags\":[\"search\",\"regex\"]}"
```

Search commands:
```bash
curl -X POST http://localhost:8000/api/commands/search ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"network\",\"tags\":[\"scan\"]}"
```

Save a command:
```bash
curl -X POST http://localhost:8000/api/saved-commands ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"command_id\":\"<ID>\"}"
```

## Data Population Utilities
- Root contains multiple Python scripts to populate and enrich command databases: `comprehensive_linux_commands.py`, `populate_commands.py`, `kali_tools_database.py`, `ultimate_linux_database.py`, and expansions. Run these after backend is running to seed data (see script headers for usage).

## Tests
- API test suites under repo root: `backend_test.py`, `advanced_search_test.py`, etc.
- Run from repo root:
  ```bash
  pytest -q
  ```
- Artifacts: `test_reports/`, summary: `test_result.md`

## Project Structure (excerpt)
```
LinuxToolbox/
├── backend/
│   ├── server.py              # FastAPI app & endpoints (auth, commands, saved, taxonomy)
│   └── requirements.txt
├── frontend/
│   ├── package.json           # CRA + CRACO + Tailwind + shadcn/ui
│   ├── craco.config.js
│   └── src/
├── populate_commands.py       # Data seeding utilities (plus other expansion scripts)
├── backend_test.py            # API tests (+ specialized tests)
└── test_reports/              # Test artifacts
```

## Troubleshooting
- Ensure MongoDB is running and env vars (MONGO_URL, DB_NAME, SECRET_KEY, CORS_ORIGINS) are set
- Use a valid Bearer token for protected routes
- For search filters, verify category/tag values exist in the dataset
