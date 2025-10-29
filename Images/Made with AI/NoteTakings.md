# NoteTakings — Knowledge + Notes Workspace

A multi-project workspace centered around a Wasp-based web app for notes and knowledge management, accompanied by e2e tests, a docs/blog site, and UI experiments (tldraw whiteboards, editors, React bases).

## Repository Layout
```
NoteTakings/
├── notetakings/
│   ├── app/                # Main Wasp app (web app)
│   ├── e2e-tests/          # Playwright tests for the app
│   ├── blog/               # Astro (Starlight) docs/blog
│   └── README.md           # High-level overview
├── tldraw/                 # Whiteboard experiments and kit
├── mxd-editor/             # Editor experiments
├── react-base/             # React base project
├── react-typescript-todo/  # TS sample project
├── Whiteboard-1/           # Additional whiteboard assets
└── Docker/                 # Containerization assets
```

The core deliverable is the Wasp app in `notetakings/app`.

## Tech Stack (App)
- Framework: Wasp (full-stack TypeScript)
- Frontend: React, TailwindCSS, Headless UI
- Backend: Wasp server (Node), Prisma ORM
- Database: Prisma (configure via env)
- Tooling: Vite, TypeScript, Zod

## Getting Started (App)
1. Install Wasp (see Wasp docs) and ensure Node 18+ is available.
2. Prepare environment files in `notetakings/app`:
   - Copy `.env.client.example` to `.env.client` and set values
   - Copy `.env.server.example` to `.env.server` and set values (DB, secrets, providers)
3. Run database and app:
   ```bash
   # in notetakings/app
   wasp start db   # starts the database service
   wasp start      # runs app (dev)
   ```
4. First-time or after schema changes:
   ```bash
   wasp db migrate-dev
   # optional: wasp db studio
   ```

## Scripts (App)
- Local dev database: `wasp start db`
- Start app (dev): `wasp start`
- Apply migrations: `wasp db migrate-dev`
- Prisma studio: `wasp db studio`

## Features and Roadmap (from project README)
- Markdown editor (colors, templates, PDF/HTML export, Mermaid)
- Whiteboard integration (tldraw), notes, relations, network assets
- File manager (paths), graph view, offline mode
- Download MD files, Kanban board, tags, links, search

## Blog/Docs (Astro Starlight)
- Located at `notetakings/blog`
- Use Astro’s commands to develop and build documentation

## E2E Tests (Playwright)
- Located at `notetakings/e2e-tests`
- Configure base URL to match `wasp start` output and run tests with Playwright CLI

## Notes on Other Folders
- `tldraw/` and `Whiteboard-1/`: Whiteboard kits, example boards, assets (.tldr files)
- `mxd-editor/`: Editor experiments (MDX/editor tech)
- `react-base/`, `react-typescript-todo/`: React starter bases

## Troubleshooting
- Ensure both `.env.client` and `.env.server` exist with correct values
- If Prisma entities change, re-run `wasp db migrate-dev`
- Verify Node 18+ and Wasp CLI are installed
- For e2e tests, confirm the dev server address and auth/seed steps if required

