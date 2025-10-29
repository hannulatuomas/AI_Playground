# DevGenius-AI

An AI-powered developer assistant consisting of a FastAPI backend with conversation management, multi-LLM provider routing, progressive conversation summarization, embedding-based memory, and a React (CRACO + Tailwind + shadcn/ui) frontend.

## Overview
- Backend: FastAPI, Motor (MongoDB), uvicorn
- Memory: Embeddings (ChromaDB), progressive summaries with topic detection and importance scoring
- LLM Providers: OpenAI, Anthropic (Claude), Google Gemini, Local (llama.cpp HTTP endpoint)
- Frontend: Create React App + CRACO, TailwindCSS, shadcn/ui, React 19

Repository paths:
- `backend/` — FastAPI app (`server.py`), embeddings (`embedding_service.py`), memory (`agent_memory.py`), prompts (`system_prompts.py`)
- `frontend/` — CRA app with CRACO, Tailwind config, components and pages

## Features
- Multi-provider LLM routing with provider CRUD
- Conversation storage with message history in MongoDB
- Progressive conversation summarization with topic grouping and importance scoring
- Optional embedding storage/retrieval for semantic context (ChromaDB)
- Streaming responses for supported providers

## Requirements
- Python 3.12+
- Node.js 18+ (Frontend)
- MongoDB instance

## Backend Setup
1. Create `.env` in `backend/`:
   ```env
   MONGO_URL=mongodb://localhost:27017
   DB_NAME=devgenius
   # Optional provider API keys (set only the ones you use)
   OPENAI_API_KEY=
   ANTHROPIC_API_KEY=
   GOOGLE_API_KEY=
   ```
2. Install deps and run server:
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
yarn start    # or npm start (CRACO dev server at http://localhost:3000)
```

## Core API Endpoints (prefix `/api`)
- `POST /providers` — create provider
- `GET /providers` — list providers
- `PUT /providers/{provider_id}` — update provider
- `DELETE /providers/{provider_id}` — delete provider

- `POST /conversations` — create conversation
- `GET /conversations?agent_type=...` — list conversations (optional filter)
- `DELETE /conversations/{conversation_id}` — delete conversation (+ messages)
- `POST /conversations/{conversation_id}/summarize` — run progressive summarization now

- `POST /chat` — chat with a provider, persists messages, auto-summarizes over time

### Models (selected)
- `LLMProviderCreate`: `name`, `model`, `api_key`, `endpoint?`, `is_active?`
- `ConversationCreate`: `title`, `agent_type`, `provider_id`
- `ChatRequest`: `conversation_id?`, `message`, `provider_id`, `agent_type`, `title?`, `project_id?`

## Example Usage
Create a provider:
```bash
curl -X POST http://localhost:8000/api/providers ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"openai\",\"model\":\"gpt-4o-mini\",\"api_key\":\"$OPENAI_API_KEY\"}"
```

Start a chat:
```bash
curl -X POST http://localhost:8000/api/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"message\":\"Hello!\",\"provider_id\":\"<PROVIDER_ID>\",\"agent_type\":\"general\"}"
```

Summarize a conversation:
```bash
curl -X POST http://localhost:8000/api/conversations/<CONV_ID>/summarize
```

## Progressive Summarization Highlights
- Groups messages by topics: errors/fixes, code implementation, requirements, decisions, general
- Computes message importance (keywords, code indicators, length, role)
- Performs progressive updates when conversations grow
- Stores summary and metadata back to MongoDB

## Embeddings & Memory
- Optional embedding storage via `embedding_service`
- Stores user/assistant messages for semantic retrieval
- ChromaDB data under `backend/chroma_db/`

## Tests
- Root-level test: `backend_test.py`
- Run all (from repo root):
  ```bash
  pytest -q
  ```
  Or run the single file:
  ```bash
  pytest backend_test.py -q
  ```
  Reports: `test_reports/` and summary: `test_result.md`

## Project Structure (excerpt)
```
DevGenius-AI/
├── backend/
│   ├── server.py              # FastAPI app & endpoints
│   ├── embedding_service.py   # Embedding storage/retrieval
│   ├── agent_memory.py        # Long-term memory interface
│   ├── system_prompts.py      # System prompts registry
│   └── requirements.txt
├── frontend/
│   ├── package.json           # CRA + CRACO + Tailwind + shadcn/ui
│   ├── craco.config.js
│   └── src/
├── backend_test.py            # Backend API tests
├── tests/                     # Additional tests
└── test_reports/              # Test artifacts
```

## Troubleshooting
- Ensure MongoDB is running and `MONGO_URL`/`DB_NAME` are correct
- Only configure API keys for providers you use; others can remain unset
- If using local LLM, set a reachable `endpoint` (e.g., `http://localhost:8080`) when creating the provider
