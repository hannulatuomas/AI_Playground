# FrostPeakSolutions DataStudio

A modern, extensible, cross-platform IDE for database management, data visualization, and querying. Inspired by Azure Data Studio, designed for usability, modularity, and future extensibility.

---

## Contents
- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Schema & File Workflow](#schema--file-workflow)
- [Plugin & Extensibility](#plugin--extensibility)
- [Current Status](#current-status)
- [Next Steps](#next-steps)
- [Feature Status](./FeatureStatus.md)
- [Implementation Plan](./Connection_And_Notebook_Implementation_Plan.md)

---

> **Documentation is current as of 2025-05-09. All major features, architecture, and workflow are described below. For detailed UI/UX, workflow, and implementation checklists, see [UI_UX_Improvement_Checklist.md](./UI_UX_Improvement_Checklist.md), [FeatureStatus.md](./FeatureStatus.md), [Next Steps.md](./Next%20Steps.md), and [Database IDE Plan.md](./Database%20IDE%20Plan.md). All documentation is systematically updated after each major change. If you find any outdated information, please open an issue or PR.**

## Features
- Multi-database support:
  - PostgreSQL, MySQL, SQLite, SQL Server, Oracle (**Complete**)
  - MongoDB, Neo4j (**Complete**) — advanced type inference, robust schema/query endpoints, full frontend cell integration
- Import/query CSV, JSON, and XML as tables (full schema inference, override, validation, and preview)
- Notebook-style editor: SQL, MongoDB, Neo4j, Markdown, Chart, Schema cells
- Robust connection property handling: Frontend always sends all connection fields for `/tables` and `/columns` endpoints, ensuring backend reliability
- Table dropdown in Schema Cell is always sorted alphabetically (locale/case/numeric aware) for improved UX
- Results visualization: bar/line/pie charts, column selection, live preview, import from other cells/files
- Export data: CSV, JSON, XML for notebooks, query results, chart data (unified, extensible export system)
- Modular, extensible UI and backend (plugin/registry pattern in progress)
- Virtualized tables for large result sets (react-window)
- Save and reuse query snippets
- Smart autocomplete for SQL, table, and column names
- Robust schema editor for all file types (CSV, JSON, XML, MongoDB, Neo4j): validation, inference, override, live preview
- File preview/edit modal with React portal overlay
- Compact, accessible sidebar, notebook delete buttons, and consistent destructive action styling
- File workflow: unique file IDs, fully centralized file/schema/cell state (React Context), unified schema confirmation, modular file logic (no legacy filename/localStorage schema logic), improved file selection UX, and user guidance (see Next Steps.md and UI_UX_Improvement_Checklist.md)
- Sidebar: collapsible, mobile/hamburger menu support, overlay logic, and accessibility improvements
- Resizable panels: dependency-free, persistent sizing, visual cues, responsive on all devices
- Modern, responsive, accessible UI with ARIA, tooltips, keyboard navigation, and user guidance throughout

---

## Getting Started

### Prerequisites
- Node.js (18+)
- Docker (optional, for dev/prod parity)

### Setup
#### Backend
```sh
cd backend
npm install
npm run dev
```
#### Frontend
```sh
cd frontend
npm install
npm start
```
#### Docker Compose (optional)
```sh
docker-compose up --build
```

---

## Project Structure
```
FrostPeakSolutions_DataStudio/
├── backend/
│   ├── src/
│   │   ├── connections.ts         # DB connection logic (multi-DB, MongoDB/Neo4j supported)
│   │   ├── filePreview.ts         # CSV/JSON/XML/JSON preview/sample logic
│   │   ├── fileUpload.ts          # File upload endpoints (CSV, JSON, XML)
│   │   ├── query.ts               # Query execution (SQL, CSV/JSON/XML, MongoDB, Neo4j)
│   │   ├── schema.ts              # Schema inference/override (CSV, JSON, XML, advanced type inference for MongoDB/Neo4j, relationship schema)
│   │   ├── utils/
│   │   │   └── typeInference.ts   # Advanced type inference utility (modular, used by MongoDB/Neo4j)
│   │   └── index.ts               # Express app entry
│   └── package.json               # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/            # React components (cells, panels, notebook, file/JSON/CSV/XML preview, etc.)
│   │   ├── hooks/                 # Custom hooks (file schema, context, etc.)
│   │   ├── services/              # Modularized logic (exportService, importService, dataSourceService, etc.)
│   │   ├── App.tsx                # Main app entry
│   │   └── index.tsx              # ReactDOM entry
│   └── package.json               # Frontend dependencies
├── FeatureStatus.md               # Feature checklist (current status)
├── Next Steps.md                  # Roadmap and priorities
├── README.md                      # Project documentation
└── ...
```

---

# notebookEditor Subdirectory

This directory contains logic and UI components extracted from `NotebookEditor.tsx` for improved modularity and maintainability.

- `NotebookEditorOps.ts`: Pure logic for notebook group/cell operations (add, move, duplicate, delete, group/ungroup, etc.).
- `NotebookMetaModal.tsx`: UI for the Edit Notebook Info modal.
- (Future) Other subcomponents and helpers for the notebook editor UI.
- **Planned:** Modularization of file logic (upload, preview, schema, state) for maintainability and extensibility (see Next Steps.md).

---

# Export Functionality Architecture

- **Unified Export Service:** All export actions (notebook, query results, chart data) use a single, modular service layer (`frontend/src/services/exportService.ts`).
- **Backend Endpoints:** `/notebook/export`, `/query/export`, `/chart/export` endpoints serialize and stream data in the selected format (JSON, CSV, XML).
- **Frontend Controls:** Modern dropdowns and export buttons are provided in all relevant UI components, supporting format selection and robust error handling.
- **Extensibility:** Adding new export formats or targets is straightforward due to the modular design on both frontend and backend.

All code here is TypeScript and follows project conventions for type safety and minimal dependencies.

---

## Codebase Overview
- **Backend:** Node.js + Express (TypeScript). Modular drivers for multiple databases. MongoDB and Neo4j support is fully implemented (official drivers, advanced type inference, robust schema/query endpoints, relationship schema for Neo4j). CSV, JSON, and XML handled as tables. Secure, extensible API.
- **Frontend:** React (TypeScript). Modular components for notebook cells, file/connection panels, results, and charting. Virtualized tables for performance.
- **Chart Import Modal:** All chart data import logic is encapsulated in `ChartImportModal.tsx`, which provides a reusable, maintainable modal for importing and mapping chart data from files or other cells. `NotebookCell.tsx` only manages when to show the modal and passes required props; no chart import logic remains in NotebookCell.
- **Schema Editing:** Robust schema override for CSV, JSON, and XML, with live validation and backend enforcement.
- **File Workflow:** Sidebar/file panel and notebook delete buttons redesigned for compactness and accessibility. File preview/edit modal uses React portal overlay. Roadmap for modularizing all file logic and centralizing file state (see Next Steps.md).

---

## Schema & File Workflow
- **Centralized file state:** All file and schema state is managed via a global context (React Context) using unique file IDs. No legacy localStorage or index-based references remain.
- **Unified schema confirmation:** Schema status (unconfirmed/confirmed/editing) is tracked centrally and required before file-backed cells can execute queries.
- **Schema editing:**
  - CSV, JSON, and XML: Schema is inferred and can be overridden in the UI before querying.
  - JSON: Treated as tables (array of objects); schema is inferred automatically and can be edited in the notebook cell UI with live validation.
  - All overrides are validated and respected backend-side.
- **File selection UX:**
  - Notebook cells use dropdowns for explicit file selection, with schema status displayed and tooltips/guidance provided.
- **Modular file logic:**
  - All file/schema logic is encapsulated in custom hooks and services for maintainability and extensibility.

See [Next Steps.md](./Next%20Steps.md) for actionable workflow recommendations and roadmap.
---

## Architecture Overview

---

## Theme Support

FrostPeakSolutions DataStudio supports both light and dark themes for improved accessibility and user comfort.

- **Theme Toggle:** Easily switch between light and dark mode using the toggle button (🌞/🌙) in the sidebar.
- **Persistence:** Your theme preference is saved in your browser and automatically restored on future visits.
- **Accessibility:** All color variables for both themes are designed for strong contrast (WCAG AA/AAA for text and status colors). The theme toggle is keyboard accessible. A manual audit with browser tools and screen readers is recommended for final verification.
- **Best Practices:** No hardcoded color values are used in main styles; all colors are managed with CSS variables for full themeability and maintainability.

See the [UI/UX Improvement Checklist](./UI_UX_Improvement_Checklist.md) for ongoing accessibility work and future improvements.


- **Centralized state:** All file, schema, and cell state is managed centrally for robustness and extensibility.
- **Unique file IDs:** All file references use unique IDs for reliability; no index- or filename-based logic remains.
- **Plugin/registry pattern:** Extensible architecture for new file/data/cell types, with modular logic for file handling, schema, and export/import.
- **Modern UI/UX:** Responsive, accessible, and consistent design throughout the application.
- **Performance:** Virtualized tables, backend streaming/pagination (CSV/XML), and further optimizations planned.
- **Security:** Input validation, sanitized queries, password exclusion from responses.

## Plugin & Extensibility
- **Plugin/registry architecture:**
  - New file/data types, cell types, and export formats can be added via a registry or plugin system (frontend/backend).
  - All core logic is modularized for future plugin support.
- **Planned:** End-to-end plugin API, plugin management UI, and example plugin implementations.

## Current Status
- See [FeatureStatus.md](./FeatureStatus.md) for the full status checklist.
- See [Next Steps.md](./Next%20Steps.md) for the prioritized roadmap.
---

## Next Steps
See `Next Steps.md` for the prioritized roadmap, including:
- JSON file support: Fully implemented (import, preview, query, schema inference/override, export, and UI parity with CSV/XML)
- MongoDB/Neo4j: Full query support, schema inference, relationship schema (Neo4j), and frontend cell integration
- Plugin system (frontend/backend)
- UI polish (themes, accessibility, panel resizing)
- Documentation and user guides
- Performance optimization
- Feature completion (see FeatureStatus.md)

---

For full feature status and roadmap, see `FeatureStatus.md` and `Next Steps.md`.
│   ├── package.json, tsconfig.json
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── NotebookEditor.tsx               # Main notebook UI and state
│   │   │   ├── NotebookCell.tsx                 # Notebook cell logic (SQL/Markdown/Chart)
│   │   │   ├── ChartImportModal.tsx             # Encapsulated chart data import modal logic
│   │   │   ├── NotebookCellFileSchemaPreview.tsx# Schema editor for file-based cells
│   │   │   ├── FilePreview.tsx                  # File preview/sample table
│   │   │   ├── Sidebar.tsx, SnippetsPanel.tsx   # UI panels
│   │   │   └── ...
│   │   ├── App.tsx, index.tsx
│   │   └── ...
│   ├── package.json, tsconfig.json
│   └── ...
├── README.md
├── FeatureStatus.md
├── Next Steps.md
└── ...
```

## Next Steps
- Implement database connection logic in backend
- Build connection panel and query editor in frontend
- Add file upload and parsing endpoints
- Add results visualization and export features

---

## Schema Editing Flow

The application provides a robust schema editing experience for CSV and XML files, tightly integrated with the notebook query flow:

- **Inline Schema Editor:**
  - When adding a CSV/XML file as a cell, an inline schema editor appears above the query area.
  - Users can edit column names and types, with real-time validation (no duplicates, no empty names, all types required).
  - Tooltips and inline help are provided for clarity.

- **Import/Export Schema:**
  - Users can export the current schema as a JSON file for backup or sharing.
  - Users can import a schema JSON to override the current schema.

- **Persistence:**
  - All schema overrides are saved to localStorage and automatically restored when the file is used again.

- **Backend Integration:**
  - When a query is run on a CSV/XML file, the schema override is sent to the backend and used to define the table structure for the query.
  - If no override is present, the backend infers the schema from the file.

- **Validation & Security:**
  - All schema overrides are validated on both frontend and backend for type/name correctness.
  - User input is sanitized to prevent injection or malformed state.

---

See `Database IDE Plan.md` for full documentation and roadmap.

---

## File Workflow: Recommendations & Next Steps

See `Next Steps.md` for a detailed roadmap and actionable recommendations on improving file workflow, including:

- Using unique file IDs instead of indexes for robust referencing
- Centralizing file state via a global context or state manager
- Unifying schema confirmation flow and storing status centrally
- Improving file selection UX in notebook cells
- Guiding users with tooltips, banners, and onboarding
- Modularizing all file-related logic for maintainability

**Next Steps:**
- Refactor file handling to use unique IDs and centralized state
- Redesign cell UI for clear file selection and schema status
- Unify schema confirmation workflow
- Remove duplicated file state and ensure all components use the same source
