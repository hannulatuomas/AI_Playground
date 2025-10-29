# AI_Playground — Table of Contents

This repository contains 17 projects organized into two main folders.

## AI Agents (6)
- [DevGenius-AI](AI%20Agents/DevGenius-AI/)
  - AI-powered developer assistant with a FastAPI backend (multi-LLM routing, embeddings memory, progressive summarization) and a modern React frontend.
  - Tags: FastAPI, MongoDB, React, Tailwind, shadcn/ui, ChromaDB, Multi-LLM
- [Linux-MCP-systools-wsl](AI%20Agents/Linux-MCP-systools-wsl/)
  - Comprehensive Kali Linux MCP server offering 37 tools across 7 categories for shell, files, text, network, archives, and system operations; modular and secure.
  - Tags: Python, MCP, Kali Linux, Shell, Network, Archive, System Tools
- [Ultimate_AI_IDE](AI%20Agents/Ultimate_AI_IDE/)
  - Lightweight automated IDE using llama.cpp for local inference; self-improving workflows with scaffolding, auto-testing, refactoring, security scanning, and advanced RAG.
  - Tags: Python, llama.cpp, RAG, CodeBERT, CLI, GUI, pytest
- [Windsurf_Templates](AI%20Agents/Windsurf_Templates/)
  - Curated `.gitignore` and `.windsurfrules` templates for common stacks to quickly bootstrap clean repositories; minimal, composable, and cross-platform.
  - Tags: gitignore, templates, Windows, PowerShell, CMD
- [ai-coder-cli](AI%20Agents/ai-coder-cli/)
  - Production-ready AI agent console with multi-agent orchestration, llama.cpp/Ollama/OpenAI routing, persistent/vector memory, plugins, and automated task loops.
  - Tags: Python, Typer, Rich, Llama.cpp, Ollama, OpenAI, ChromaDB, Plugins
- [ai-coding-assistant](AI%20Agents/ai-coding-assistant/)
  - Project-aware development automation with advanced RAG, automated test generation, safety/rollback, and full CLI/GUI—powered by llama.cpp.
  - Tags: Python, llama.cpp, Advanced RAG, CodeBERT, CLI, GUI, Testing

## Made with AI (11)
- [ApiForge](Made%20with%20AI/ApiForge/)
  - Professional API testing and visual workflow platform supporting REST, SOAP, GraphQL, gRPC, and WebSocket, with spec import, variables, and enterprise features.
  - Tags: FastAPI, MongoDB, React, Tailwind, shadcn/ui, REST, SOAP, GraphQL, gRPC, WebSocket
- [DataForge](Made%20with%20AI/DataForge/)
  - Web-based database management tool inspired by Azure Data Studio: multi-DB connections, Monaco editor, notebooks, schema explorer, and modern React + FastAPI stack.
  - Tags: FastAPI, MongoDB, React, Monaco, Notebooks, Tailwind
- [EasyItAsset](Made%20with%20AI/EasyItAsset/)
  - Full-stack asset management app for containers, asset types, fields, and subtypes with a modern React frontend and Node.js backend, including hierarchical ID system.
  - Tags: React (TS), Node (TS), Asset Types, Hierarchical IDs
- [EmergentNexus](Made%20with%20AI/EmergentNexus/)
  - Knowledge graph workspace to create/link typed nodes with a FastAPI + MongoDB backend and a React graph UI powered by @antv/x6.
  - Tags: FastAPI, MongoDB, React, @antv/x6, Dexie, Zustand, Tailwind, shadcn/ui
- [FrostPeakSolutions_DataStudio](Made%20with%20AI/FrostPeakSolutions_DataStudio/)
  - Cross-platform database IDE: multi-database query, notebook-style editor, schema editing, visualization and export—modeled after Azure Data Studio.
  - Tags: Node/Express (TS), React (TS), MongoDB, Neo4j, CSV/JSON/XML, Notebooks
- [ItAssetManagement](Made%20with%20AI/ItAssetManagement/)
  - Modular ITAM platform with organizations, groups, types, and assets; FastAPI + MongoDB backend with JWT auth and a modern React frontend.
  - Tags: FastAPI, MongoDB, React, JWT, Tailwind, shadcn/ui
- [LinuxToolbox](Made%20with%20AI/LinuxToolbox/)
  - Linux admin knowledge base and command explorer with auth, command CRUD, advanced search/filters, and saved commands (FastAPI + MongoDB + React).
  - Tags: FastAPI, MongoDB, React, JWT, Search, Taxonomy
- [LocalAPI](Made%20with%20AI/LocalAPI/)
  - Fully local, offline-capable API development tool (Electron + React + TypeScript) covering multi-protocol clients, mock servers, security testing, caching, and plugins.
  - Tags: Electron, React, TypeScript, REST, GraphQL, SOAP, gRPC, WebSockets, OWASP ZAP
- [NoteTakings](Made%20with%20AI/NoteTakings/)
  - Wasp-based notes and knowledge app with whiteboards, docs/blog, and e2e tests; multi-project workspace centered on the `notetakings/app` web app.
  - Tags: Wasp, React, Tailwind, Prisma, Playwright, Astro
- [PentestPro](Made%20with%20AI/PentestPro/)
  - Penetration testing workflow and reporting suite: templates, guided assessments, and Markdown→PDF reports on a FastAPI + MongoDB backend with React UI.
  - Tags: FastAPI, MongoDB, React, JWT, Jinja2, WeasyPrint
- [SaaS_Template](Made%20with%20AI/SaaS_Template/)
  - Minimal SaaS starter with auth (JWT + Google OAuth), Stripe subscriptions, and a modern React (Vite/TS/Tailwind) frontend with Express/TS backend.
  - Tags: React (Vite/TS/Tailwind), Express (TS), Stripe, Google OAuth, JWT

---

Tip: Project-level README snapshots are under:
- `Images/AI Agents/` (e.g., DevGenius-AI.md)
- `Images/Made with AI/` (e.g., ApiForge.md)

---

# Project Details

## AI Agents

### DevGenius-AI
- AI-powered developer assistant with FastAPI backend and React frontend. Multi-provider LLM routing, embeddings memory, and progressive summaries.
- Key features:
  - Multi-LLM providers (OpenAI, Anthropic, Gemini, local llama.cpp HTTP)
  - Conversation storage with auto-summarization and topic grouping
  - Optional ChromaDB embeddings for semantic context
- Tech stack: FastAPI, MongoDB (Motor), React (CRA + CRACO), Tailwind, shadcn/ui.
- Quick start: backend with `uvicorn server:app`, frontend with `yarn start`.

### Linux-MCP-systools-wsl
- Comprehensive Kali Linux MCP server exposing 37 tools across 7 categories for shell, filesystem, text, network, archives, and system.
- Key features:
  - Secure shell/file/network/system operations with timeouts and validation
  - Modular tool registration and handlers per category
  - Command injection protection, extensive logging
- Tech stack: Python MCP server.
- Quick start: `python3 server.py`.

### Ultimate_AI_IDE
- Lightweight automated IDE using llama.cpp for local inference; self-improving workflows with scaffolding, testing, docs sync, refactoring, and advanced RAG.
- Key features:
  - Workflow engine, file splitter, dead code detection, automation
  - Security scanner and dependency manager
  - CodeBERT-powered retrieval, multi-modal search, graph-based retrieval
- Tech stack: Python 3.12.10, llama.cpp binaries, SQLite + vector store, pytest, CLI + tkinter GUI.
- Quick start: use scripts in `scripts/` to set up venv and run GUI/CLI.

### Windsurf_Templates
- Curated `.gitignore` and `.windsurfrules` templates to bootstrap clean repos across stacks.
- Key features:
  - Minimal, composable templates (Python, Node, React, Next.js, C/C#, VS/JetBrains)
  - Simple copy/concat instructions for Windows shells
- Tech stack: Markdown templates.
- Quick start: copy desired templates into project `.gitignore`.

### ai-coder-cli
- Production-ready AI agent console with multi-agent orchestration, llama.cpp/Ollama/OpenAI routing, plugins, and persistent/vector memory.
- Key features:
  - Task orchestration with planning → code → tests → docs → commit
  - Saved prompts/snippets, versioning, Windows binaries
  - Development tools integration (linting/formatting/quality)
- Tech stack: Python, Typer CLI, Rich, ChromaDB, optional transformers.
- Quick start: create venv, install requirements, run CLI commands.

### ai-coding-assistant
- Project-aware automation platform with advanced RAG (8 features), automated test generation, and full CLI/GUI—powered by llama.cpp.
- Key features:
  - Code generation/debugging, task decomposition, rule enforcement
  - Phase 9 advanced RAG (query expansion, reranking, hybrid search, graphs)
  - Phase 11.1 multi-language test generation
- Tech stack: Python 3.12, sentence-transformers/CodeBERT (optional), tkinter GUI, CLI.
- Quick start: install requirements (optional transformers), launch via batch scripts.

## Made with AI

### ApiForge
- Professional API testing and visual workflow platform with REST/SOAP/GraphQL/gRPC/WebSocket, spec import, variables, and enterprise features.
- Key features:
  - Visual workflow designer with multiple node types
  - Global/collection variables with JSONPath extraction
  - Import from OpenAPI, WSDL, RAML, GraphQL, Postman, Insomnia
- Tech stack: FastAPI + MongoDB backend; React 18 + Tailwind + shadcn/ui frontend.
- Quick start: `pip install -r backend/requirements.txt` and `npm start` in frontend.

### DataForge
- Web-based database management inspired by Azure Data Studio with Monaco editor, notebooks, and schema explorer.
- Key features:
  - Multi-DB connectors, secure credential encryption
  - SQL editor, notebooks (SQL/Markdown/Python), export CSV/JSON
  - Azure Data Studio-like UX with themes and activity bar
- Tech stack: FastAPI, MongoDB; React + Tailwind + shadcn/ui.
- Quick start: run FastAPI backend and React frontend per README.

### EasyItAsset
- Full-stack asset management for containers, asset types, fields, and subtypes with hierarchical IDs.
- Key features:
  - Type-specific validation, cascading operations, real-time preview
  - Strong ID utilities and validation
- Tech stack: React (TS) frontend; Node backend (TypeScript).
- Quick start: `npm install` and `npm run dev` in frontend; backend per project setup.

### EmergentNexus
- Knowledge graph workspace to capture nodes and typed relations; React graph UI with @antv/x6.
- Key features:
  - CRUD for nodes/relations, tags, timestamps
  - IndexedDB (Dexie) support on frontend
- Tech stack: FastAPI + MongoDB; React + Tailwind + shadcn/ui + @antv/x6.
- Quick start: start FastAPI and CRA dev server.

### FrostPeakSolutions_DataStudio
- Cross-platform database IDE: multi-DB query, notebook editor, schema editing, visualization/export.
- Key features:
  - CSV/JSON/XML import with schema inference/override
  - MongoDB/Neo4j drivers with advanced type inference
  - Virtualized tables and modular services
- Tech stack: Node/Express (TypeScript) backend; React (TypeScript) frontend.
- Quick start: `npm install && npm run dev` in backend and frontend.

### ItAssetManagement
- Modular ITAM platform with orgs, groups, types, assets, templates, and JWT-secured APIs.
- Key features:
  - Inherited/custom fields, enriched listings, per-org authorization
  - Built-in templates (Hardware/Software/Network/Cloud)
- Tech stack: FastAPI + MongoDB; React + Tailwind + shadcn/ui.
- Quick start: configure `.env`, run `uvicorn`, start frontend.

### LinuxToolbox
- Linux admin knowledge base and command explorer with advanced search and saved commands.
- Key features:
  - Auth, command CRUD, taxonomy endpoints (categories/tags)
  - Data seeding utilities and test suites
- Tech stack: FastAPI + MongoDB; React + Tailwind + shadcn/ui.
- Quick start: run backend (`uvicorn`) and frontend (`yarn start`).

### LocalAPI
- Fully local, offline-capable API development tool (Electron + React + TypeScript) with multi-protocol clients and rich tooling.
- Key features:
  - REST/GraphQL/SOAP/gRPC/WebSockets/SSE/JMS/MQTT
  - Mock servers, scripting, security testing (OWASP/ZAP, fuzzing), caching
  - Git integration and plugin system
- Tech stack: Electron, React, TypeScript; tests and scripts included.
- Quick start: `npm install`, `npm run dev`; packaging via `npm run package:<platform>`.

### NoteTakings
- Wasp-based notes and knowledge app with supporting projects (whiteboards, blog/docs, e2e tests).
- Key features:
  - Markdown editor, whiteboard integration (tldraw), tags/links/search
  - Prisma-backed backend with migrations via Wasp
- Tech stack: Wasp (full-stack TS), React, Tailwind, Prisma.
- Quick start: `wasp start db` then `wasp start` in `notetakings/app`.

### PentestPro
- Penetration testing workflow and reporting suite with templates, guided assessments, and Markdown→PDF reporting.
- Key features:
  - Template builder (steps/fields/sections), assessment lifecycle
  - PDF reports via Jinja2 + markdown2 + WeasyPrint
- Tech stack: FastAPI + MongoDB; React + Tailwind + shadcn/ui.
- Quick start: configure `.env`, run backend and frontend.

### SaaS_Template
- Minimal SaaS starter: JWT + Google OAuth auth, Stripe subscriptions, modern React UI.
- Key features:
  - Email verification, password reset, webhook handling
  - Centralized rate limiting and robust error handling
- Tech stack: React (Vite/TS/Tailwind) frontend; Express (TypeScript) backend.
- Quick start: install server/client deps, start `npm run dev` in both; set Stripe webhook.
