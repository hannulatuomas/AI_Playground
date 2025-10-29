# Features Status

> **Feature status and documentation cross-references are up to date as of 2025-05-09. See [README.md](./README.md), [Next Steps.md](./Next%20Steps.md), and [UI_UX_Improvement_Checklist.md](./UI_UX_Improvement_Checklist.md) for details.**

**Architecture Summary:**
- Unique file IDs for all file references (no index- or filename-based logic)
- Centralized file/schema/cell state (React Context)
- Unified schema confirmation (no localStorage/filename-based logic)
- Modular, extensible logic for file handling, schema, export/import
- Collapsible sidebar with mobile/hamburger menu and overlay logic
- Resizable panels: persistent, responsive, accessible

See [README.md](./README.md) for architecture and [Next Steps.md](./Next%20Steps.md) for roadmap.


**Legend:**
- [x] Complete
- [~] Partial
- [ ] Not present

## Core Features
- [x] Unique file IDs and centralized file/schema/cell state (React Context)
- [x] Modular, extensible file logic and schema workflow
- [x] Multi-database support (PostgreSQL, MySQL, SQLite, SQL Server, Oracle, MongoDB, Neo4j)
- [x] Import/query CSV, JSON, XML as tables (full schema inference, override, validation, preview)
- [x] Notebook-style editor: SQL, MongoDB, Neo4j, Markdown, Chart, Schema cells
- [x] Results visualization: bar/line/pie charts, column selection, live preview, import from other cells/files
- [x] Export data: CSV, JSON, XML (unified, extensible export system)
- [x] Smart autocomplete for SQL/table/column names
- [x] Robust schema editor for all file types (validation, inference, override, live preview)
- [x] File preview/edit modal with React portal overlay
- [x] Sidebar/file panel: compact, accessible, consistent destructive actions
- [x] User guidance: tooltips, help text, collapsible help, ARIA/keyboard accessibility
- [x] Persistent, versioned notebook state
- [x] Modern, responsive, accessible UI (ARIA, tooltips, user guidance)

## Advanced & Planned
- [~] Plugin/registry architecture (core logic modularized, API/management UI planned)
- [~] Performance optimization for large datasets (backend streaming, frontend virtualized tables, ongoing)
- [~] UI improvements: theme toggle, resizable panels, mobile optimization (planned)
- [~] Collapsible/expandable results (cell outputs collapsible, result tables planned)
- [~] Advanced analytics (Python cell, graph/network visualizations, batch query execution, etc.)

## Documentation
- [x] All docs (README, FeatureStatus, Next Steps, Implementation Plan) kept in sync, cross-referenced, and up to date.

---

For architecture, see [README.md](./README.md). For roadmap, see [Next Steps.md](./Next%20Steps.md).


---

## Additional Features from Project Plan

### Python Cell Support & Analytics
- [ ] **Python code cells and execution**
  Planned: Add Python cell type to notebook, with backend execution and display of results (e.g., data analytics, matplotlib output).
  (should we support some other data analytic languages also?)

### Database & File Support
- [x] **Multi-database support (PostgreSQL, MySQL, SQLite, SQL Server, Oracle)**
- [x] **CSV file support** (full query, preview, robust schema override, import/export, and performant for large files)
- [x] **JSON file support** (full import, preview, query, schema inference/override, export, and UI parity with CSV/XML)
- [~] **XML file support** (partial: import, preview, schema override infrastructure ready, but not full UI/query/export parity with CSV/JSON) _(2025-05-09)_

### Notebook & Query UX
- [x] **Persistent cell/notebook state**  
  All cell, metadata, and group state is saved atomically with versioning and robust error handling. Extensible for future migration or backend sync.
- [x] **Notebook save/load as JSON**
- [x] **Saved Notebooks reliably load into editor**  
  Fixed state sync and update bugs; clicking a saved notebook now always loads it into the editor.
- [x] **Notebook export/import as JSON** _(2025-05-09)_
  - Fully implemented; notebooks can be saved/loaded as JSON files.
- [ ] **Notebook export/import as CSV/XML** _(2025-05-09)_
  - Not supported (notebooks are structured, not tabular; only query/chart results can be exported as CSV/XML).
- [~] **Execution time and row count display** _(2025-05-09)_
  - Complete in backend and API; UI display is planned.
- [ ] **Batch/multi-statement query execution**
- [ ] **Advanced SQL editor (Monaco/CodeMirror)**
- [ ] **Drag-and-drop for column reordering in results**

### Data Management & Export
- [x] **Run SQL queries against DBs or file-based tables**
- [x] **Export query results/tables as JSON/XML/CSV** _(2025-05-09)_
  - Fully implemented for all query/chart results via unified export system.
- [x] **Export query results/tables as CSV**
- [~] **Bulk export with progress indicators** _(2025-05-09)_
  - Export works for large datasets; progress indicators are limited or basic.
- [~] **Save query results as new tables in DB** _(2025-05-09)_
  - Supported for some DBs or via manual workflow; not universal or fully automated.
- [ ] **Cache results locally for offline access** _(2025-05-09)_
  - Not implemented.

### API & Integration
- [ ] **External API connectivity for data export**
- [ ] **API authentication (keys/OAuth/Basic Auth)**
- [ ] **Send data to APIs as JSON/XML**
- [ ] **Queue large API data transfers**
- [ ] **UI for configuring API endpoints/payloads**

### Security & Architecture
- [x] **Sanitize SQL queries / prevent injection (parameterized)**
- [ ] **Encrypt connection strings**
- [ ] **JWT authentication (optional)**

### Visualization & UI
- [x] **Basic visualizations (bar, line, pie charts)** _(2025-05-09)_
  - Implemented and available in results and chart cells (bar, line, pie) with Chart.js; fully integrated in the UI.
- [~] **Interactive tables (sortable, filterable)** _(2025-05-09)_
  - Partial: sorting/filtering present for some tables (virtualized/large tables), not all.
- [~] **Reorder table columns/rows** _(2025-05-09)_
  - Partial: drag-and-drop reordering in some contexts (notebook cells/groups), not full for all tables/results.

---

_Last updated: 2025-05-09_
