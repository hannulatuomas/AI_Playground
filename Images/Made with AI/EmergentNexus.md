# EmergentNexus

A knowledge graph workspace for capturing ideas as nodes and linking them with typed relations. Backend provides a FastAPI + MongoDB graph API; frontend is a React app (CRACO + Tailwind + shadcn/ui) with graph visualization powered by @antv/x6 and state via Zustand.

## Overview
- Backend: FastAPI, Motor (MongoDB), uvicorn
- Domain: `Node` (markdown, kanban-card, evidence-item, etc.) and `NodeRelation` (links-to, parent-of, references, ...)
- Endpoints: CRUD for nodes and relations, health check
- Frontend: CRA + CRACO, TailwindCSS, shadcn/ui, @antv/x6 graph, Dexie (IndexedDB) for local data, Zustand store

Repository paths:
- `backend/` — FastAPI app (`server.py`), requirements
- `frontend/` — CRA app with CRACO, Tailwind config, components and pages

## Features
- Create, view, update, delete graph nodes with metadata, tags, and timestamps
- Create typed relations between nodes with optional color/label
- Fetch nodes by type and query relations by node
- CORS-enabled API for local frontend development

## Requirements
- Python 3.12+
- Node.js 18+ (Frontend)
- MongoDB instance

## Backend Setup
1. Create `.env` in `backend/`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=emergent_nexus
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
Nodes
- `POST /nodes` — create node (body: `NodeCreate`)
- `GET /nodes` — list nodes
- `GET /nodes/{node_id}` — get node by id
- `PUT /nodes/{node_id}` — update node
- `DELETE /nodes/{node_id}` — delete node (+ cascade delete of its relations)
- `GET /nodes/type/{node_type}` — list nodes of a given type

Relations
- `POST /relations` — create relation (body: `RelationCreate`)
- `GET /relations` — list all relations
- `GET /relations/node/{node_id}` — list relations involving a node
- `DELETE /relations/{from_id}/{to_id}` — delete relation

Basic
- `GET /` — `{ message: "Emergent Nexus API" }`
- `GET /health` — health status

### Models (selected)
- `NodeCreate`: `node_type`, `title`, `content {}`, `metadata {}`, `tags []`
- `Node`: same plus `id`, `relations []`, `created_at`, `updated_at`
- `RelationCreate`: `from_id`, `to_id`, `relation_type`, `color?`, `label?`

## Example Usage
Create a node:
```bash
curl -X POST http://localhost:8000/api/nodes ^
  -H "Content-Type: application/json" ^
  -d "{\"node_type\":\"markdown\",\"title\":\"Idea\",\"content\":{\"text\":\"...\"}}"
```

Link two nodes:
```bash
curl -X POST http://localhost:8000/api/relations ^
  -H "Content-Type: application/json" ^
  -d "{\"from_id\":\"<A>\",\"to_id\":\"<B>\",\"relation_type\":\"references\"}"
```

## Tests
- API tests: `backend_test.py`, additional under `tests/`
- Run from repo root:
  ```bash
  pytest -q
  ```
- Artifacts: `test_reports/`, summary: `test_result.md`

## Project Structure (excerpt)
```
EmergentNexus/
├── backend/
│   ├── server.py              # FastAPI app & endpoints
│   └── requirements.txt
├── frontend/
│   ├── package.json           # CRA + CRACO + Tailwind + shadcn/ui + @antv/x6
│   ├── craco.config.js
│   └── src/
├── backend_test.py            # Backend API tests
├── tests/                     # Additional tests
└── test_reports/              # Test artifacts
```

## Troubleshooting
- Ensure MongoDB is running and env vars are set correctly
- If CORS errors appear, verify `CORS_ORIGINS` includes the frontend origin
- Confirm API reachable at `http://localhost:8000/health`
