# Next Steps

> **Documentation is up to date as of 2025-05-09. Roadmap, priorities, and recently completed features are current and cross-referenced in [README.md](./README.md), [FeatureStatus.md](./FeatureStatus.md), and [UI_UX_Improvement_Checklist.md](./UI_UX_Improvement_Checklist.md).**

---

## Current Priorities

This roadmap reflects the current codebase and priorities. See [FeatureStatus.md](./FeatureStatus.md) for implementation status and [README.md](./README.md) for architecture.

**In Progress / Next:**
- Plugin/registry architecture: design API, implement minimal end-to-end example, expand plugin capabilities (panels, data sources), security & sandboxing
- UI/UX polish: continue accessibility and mobile responsiveness improvements, add keyboard resizing for panels, polish onboarding
- Advanced analytics: batch/multi-statement query execution, enhanced cell toolbar, execution time/row count display, chart/table improvements
- Documentation & Guides: keep all docs in sync ([README.md](./README.md), [FeatureStatus.md](./FeatureStatus.md), [UI_UX_Improvement_Checklist.md](./UI_UX_Improvement_Checklist.md))

---

1. **Performance Optimization for Large Datasets**
    - Backend: Further optimize query execution, streaming, and memory usage (CSV/XML, large DB queries)
    - Frontend: Continue refining virtualized tables and UI responsiveness

2. **Plugin Architecture**
   - Design plugin/registry API (frontend/backend)
   - Implement minimal end-to-end example (e.g., new cell type)
   - Expand plugin capabilities (panels, data sources)
   - Security & sandboxing

3. **UI/UX Polish**
   - Add theme toggle (dark/light)
   - Implement resizable panels and flexible workspace
   - Continue accessibility and mobile responsiveness improvements

4. **Documentation & Guides**
   - Keep README, FeatureStatus.md, and guides up to date
   - Add user-facing documentation as features stabilize
   - Audit all schema/query endpoints to ensure robust frontend/backend handling (always send all connection fields, never just uid)

---

## Roadmap

1. Continue refining file workflow, schema confirmation, and onboarding
2. Finalize plugin/registry system design and begin implementation
3. Polish schema editing and sample data UI (tooltips, import/export)
4. Optimize backend and frontend for large datasets
5. Expand export options (JSON/XML, bulk export)
6. Add advanced SQL editor (Monaco/CodeMirror)
7. Batch/multi-statement query execution
8. Drag-and-drop for column reordering in results
9. Persistent, versioned notebook state improvements
10. API integration for data export
11. Continue codebase audits for performance and maintainability

---

For implementation status, see [FeatureStatus.md](./FeatureStatus.md). For architecture and workflow, see [README.md](./README.md).

- Add notebook cell output export (CSV, JSON, etc.).
- Enable API integration for notebook queries.

---

## Recently Completed
- Modular, consistent export/import for notebooks, queries, and chart data
- Unified, extensible export system (CSV, JSON, XML)
- JSON file data source: import, preview, query, schema inference/override, export, UI parity with CSV/XML
- Robust schema editor for CSV/JSON/XML (frontend/backend)
- Virtualized tables for large result sets (react-window)
- Query parameter support (all DBs, CSV)
- Save and reuse query snippets
- Smart SQL/table/column autocomplete
- Grouped/collapsible notebook cells and drag-and-drop
- Chart visualization (bar, line, pie)
- Connection string support for all DBs
- Error highlighting and inline results
- Multi-database support (PostgreSQL, MySQL, SQLite, SQL Server, Oracle)
- MongoDB and Neo4j: Full backend/frontend support, advanced type inference, relationship schema, cell integration
- File panel and Saved Notebooks panel redesign: compact, accessible, consistent destructive action styling
- File preview/edit modal: React portal overlay, global modal styles
- Centralized, modular file workflow: unique file IDs, global file/schema state, unified schema confirmation, improved cell file selection, user guidance

---

## Roadmap

1. Cell Grouping with Drag-and-Drop
    - drag handles for cells?
2. Plugin Support (Frontend & Backend)
    - Design a plugin system that supports both frontend (JS/TS) and backend (Node/Python) plugins.
    - Plugins can register new cell types, data sources, UI panels, etc.
    - Provide a plugins management UI in the app.
    - Backend: Define a plugin API, dynamic loading, and safe sandboxing.
    - Frontend: Dynamic loading and registration of plugins, plugin lifecycle hooks.
3. Performance Optimization for Large Datasets
    - Frontend:
        - Replace result tables with a virtualized table component for smooth scrolling (e.g., react-window).
        - Support pagination and lazy loading for very large datasets.
    - Backend:
        - Stream query results to frontend, avoid loading entire datasets into memory.
        - Add chunked API endpoints and efficient DB/file reading.
        - Benchmarks and stress tests to validate improvements.
4. Override Inferred Types or Edit Schema Before Querying
    - Integrate schema editor directly into the notebook/query flow.
    - When querying CSV/XML, prompt for schema/type edits before executing.
    - Allow renaming columns, changing types, and saving schema presets.
5. Display Sample Data Rows in a Table for CSV/XML
    - Always show a “Sample Data” table in the notebook for CSV/XML cells.
    - Table updates live as schema/type changes are made.
    - Fetch and display the first N rows efficiently.

- Begin with cell grouping (data model, UI, DnD).
- Move to plugin architecture (API design, loading, UI).
- Integrate virtualized tables and backend streaming for performance.
- Refactor schema editing and sample data UI for CSV/XML.

---

_Last updated: 2025-04-30_

---

## File Workflow: Recommendations & Next Steps

### 4. Recommendations for Improvement

**A. Use File IDs Instead of Indexes**
- Assign a unique ID to each file (e.g., filename or a generated UUID).
- Cells should reference files by ID, not index, ensuring robustness if the file list changes.

**B. Centralize File State**
- Use a global context or state manager (React Context or Zustand, etc.) for files.
- All components (sidebar, notebook, cells) should read from/write to this single source of truth.

**C. Unify Schema Confirmation**
- Move schema confirmation to a single, clear flow (e.g., always confirm schema immediately after upload, or require confirmation before a file can be used in a cell).
- Store schema confirmation status in the centralized file state, not in local storage.

**D. Improve File Selection UX in Cells**
- Make file selection explicit in each cell (e.g., a dropdown with file names/IDs).
- Show current file and schema status clearly in the cell UI.

**E. Guide the User**
- Add tooltips, banners, or onboarding steps to guide users through the file workflow.
- Warn or prevent execution if a file’s schema is unconfirmed.

**F. Modularize File Logic**
- Move all file-related logic (upload, preview, schema, state) into a dedicated module or context.
- Ensure all file operations are handled consistently and are easy to extend.

### 5. Next Steps
- Refactor file handling to use unique IDs and centralized state.
- Redesign the cell UI to make file selection and schema status clear and robust.
- Unify and clarify the schema confirmation workflow.
- Remove duplicated file state and ensure all components use the same source.

---

## Recently Completed
- Robust schema editor for CSV/XML (frontend/backend)
- Virtualized tables for large result sets (react-window)
- Query parameter support (all DBs, CSV)
- Save and reuse query snippets
- Smart SQL/table/column autocomplete
- Grouped/collapsible notebook cells and drag-and-drop
- Chart visualization (bar, line, pie)
- Connection string support for all DBs
- Error highlighting and inline results
- Multi-database support (PostgreSQL, MySQL, SQLite, SQL Server, Oracle)
- **File panel and Saved Notebooks panel redesign:** Compact, accessible buttons and consistent destructive action styling
- **File preview/edit modal:** Now uses React portal and global modal styles for proper overlay
- **File workflow recommendations:** Actionable roadmap for unique file IDs, centralized state, unified schema confirmation, modular file logic, improved cell file selection, and user guidance

---
