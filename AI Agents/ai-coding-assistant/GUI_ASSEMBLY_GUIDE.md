# GUI Lifecycle Assembly Guide

## Overview
The Phase 10 Project Lifecycle GUI has been created in 3 parts:
1. **Base + New Project section** (already in `gui_lifecycle.py`)
2. **Maintenance section** (in `MAINTENANCE_HANDLERS.txt`)
3. **Archiving section** (in `ARCHIVING_HANDLERS.txt`)

## Assembly Instructions

### Step 1: Open gui_lifecycle.py

The file currently has:
- ✅ Base GUI structure
- ✅ Code generation tab
- ✅ New Project section (complete)
- ⚠️ Maintenance section (placeholder only)
- ⚠️ Archiving section (placeholder only)

### Step 2: Replace Maintenance Section

Find this in `gui_lifecycle.py`:
```python
def create_maintenance_section(self, parent):
    """Placeholder for maintenance section."""
    ttk.Label(parent, text="Maintenance section - To be implemented", 
             font=('Arial', 12)).pack(pady=50)
```

Replace it with the content from `MAINTENANCE_HANDLERS.txt` (starting from `def create_maintenance_section`).

### Step 3: Replace Archiving Section

Find this in `gui_lifecycle.py`:
```python
def create_archiving_section(self, parent):
    """Placeholder for archiving section."""
    ttk.Label(parent, text="Archiving section - To be implemented", 
             font=('Arial', 12)).pack(pady=50)
```

Replace it with the content from `ARCHIVING_HANDLERS.txt` (starting from `def create_archiving_section`).

### Step 4: Add Handler Methods

At the end of the `ProjectLifecycleGUI` class (before the `def main():` function), add ALL the handler methods from both files:

**From MAINTENANCE_HANDLERS.txt:**
- `create_deps_tab()`
- `create_security_tab()`
- `create_health_tab()`
- `select_maint_project()`
- `gen_maint_report()`
- `check_deps()`
- `show_update_cmds()`
- `scan_vulns()`
- `analyze_health()`

**From ARCHIVING_HANDLERS.txt:**
- `select_arch_project()`
- `detect_version()`
- `bump_ver()`
- `gen_changelog()`
- `gen_docs()`
- `create_archive()`
- `arch_log()`

### Step 5: Verify Indentation

Make sure all methods are properly indented as part of the `ProjectLifecycleGUI` class (4 spaces).

### Step 6: Test

Run the GUI:
```bash
python -m src.ui.gui_lifecycle
```

## Final File Structure

```python
class ProjectLifecycleGUI:
    def __init__(self, root):
        # ... initialization ...
    
    def create_widgets(self):
        # ... widgets ...
    
    def create_code_tab(self):
        # ... code tab ...
    
    def create_project_tab(self):
        # ... project tab ...
    
    # NEW PROJECT SECTION
    def create_new_project_section(self, parent):
        # ... (already complete) ...
    
    # MAINTENANCE SECTION
    def create_maintenance_section(self, parent):
        # ... (from MAINTENANCE_HANDLERS.txt) ...
    
    def create_deps_tab(self, parent):
        # ... (from MAINTENANCE_HANDLERS.txt) ...
    
    def create_security_tab(self, parent):
        # ... (from MAINTENANCE_HANDLERS.txt) ...
    
    def create_health_tab(self, parent):
        # ... (from MAINTENANCE_HANDLERS.txt) ...
    
    # ARCHIVING SECTION
    def create_archiving_section(self, parent):
        # ... (from ARCHIVING_HANDLERS.txt) ...
    
    # CORE METHODS
    def initialize_components(self):
        # ... (already complete) ...
    
    def generate_code(self):
        # ... (already complete) ...
    
    # NEW PROJECT HANDLERS
    def refresh_templates(self):
        # ... (already complete) ...
    
    def on_template_selected(self, event):
        # ... (already complete) ...
    
    def browse_dest(self):
        # ... (already complete) ...
    
    def clear_project_form(self):
        # ... (already complete) ...
    
    def log_project(self, msg):
        # ... (already complete) ...
    
    def create_project(self):
        # ... (already complete) ...
    
    # MAINTENANCE HANDLERS (add these from MAINTENANCE_HANDLERS.txt)
    def select_maint_project(self):
        # ...
    
    def gen_maint_report(self):
        # ...
    
    def check_deps(self):
        # ...
    
    def show_update_cmds(self):
        # ...
    
    def scan_vulns(self):
        # ...
    
    def analyze_health(self):
        # ...
    
    # ARCHIVING HANDLERS (add these from ARCHIVING_HANDLERS.txt)
    def select_arch_project(self):
        # ...
    
    def detect_version(self):
        # ...
    
    def bump_ver(self, bump_type):
        # ...
    
    def gen_changelog(self):
        # ...
    
    def gen_docs(self):
        # ...
    
    def create_archive(self):
        # ...
    
    def arch_log(self, msg):
        # ...


def main():
    root = tk.Tk()
    app = ProjectLifecycleGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

## Features

### 📝 New Project Tab
- ✅ Template selection with preview
- ✅ Project configuration (name, author, email, description, license)
- ✅ Destination browser
- ✅ Options (Git init, install deps, create venv)
- ✅ Progress bar during creation
- ✅ Real-time log output

### 🔧 Maintenance Tab

**Dependencies Sub-tab:**
- ✅ Check for outdated packages
- ✅ Display current vs latest versions
- ✅ Color-coded status (green=up-to-date, orange=outdated)
- ✅ Show update commands

**Security Sub-tab:**
- ✅ Scan for vulnerabilities
- ✅ Display severity, package, and issue
- ✅ Color-coded by severity (red=critical, orange=high, yellow=medium, blue=low)
- ✅ Alert on critical vulnerabilities

**Health Sub-tab:**
- ✅ Analyze code health metrics
- ✅ Display project type, file count, line count
- ✅ List detected issues
- ✅ Visual metrics display

**General:**
- ✅ Project selector
- ✅ Generate maintenance report (JSON)

### 📦 Archiving Tab
- ✅ Project selector
- ✅ Current version display
- ✅ Version bumping (major, minor, patch)
- ✅ Changelog generation
- ✅ Documentation generation
- ✅ Archive creation (ZIP or TAR.GZ)
- ✅ Real-time output log

## Usage Examples

### Creating a New Project
1. Switch to "🏗️ Project Lifecycle" tab
2. Go to "📝 New Project" sub-tab
3. Select a template (e.g., "web-react")
4. Fill in project details
5. Choose destination folder
6. Select options (Git, venv, etc.)
7. Click "Create Project"
8. Watch the log for progress

### Checking Dependencies
1. Go to "🔧 Maintenance" sub-tab
2. Go to "📦 Dependencies" tab
3. Click "Select" to choose project
4. Click "Check Updates"
5. View outdated packages in the tree
6. Click "Show Commands" for update instructions

### Creating an Archive
1. Go to "📦 Archiving" sub-tab
2. Click "Select" to choose project
3. Bump version if needed (Major/Minor/Patch)
4. Click "Generate Changelog" for release notes
5. Click "Create Archive"
6. Select format (ZIP or TAR.GZ)
7. Archive is created with timestamped filename

## Requirements

- Python 3.12+
- tkinter (usually included)
- All Phase 10 components installed:
  - `features.project_lifecycle.TemplateManager`
  - `features.project_lifecycle.ProjectScaffolder`
  - `features.project_lifecycle.ProjectInitializer`
  - `features.project_lifecycle.ProjectMaintainer`
  - `features.project_lifecycle.ProjectArchiver`

## Troubleshooting

**"Project Lifecycle not installed" error:**
- Ensure Phase 10 components are in `src/features/project_lifecycle/`
- Check `__init__.py` exports all required classes

**Template not found:**
- Check `data/templates/` directory exists
- Ensure template JSON files are valid
- Click "↻" button to refresh template list

**Version detection fails:**
- Ensure project has `package.json` or `setup.py`
- Check file contains valid version string

**Archive creation fails:**
- Ensure project directory is accessible
- Check disk space for archive file
- Verify no files are locked/in-use

## Status

✅ **COMPLETE** - All three sections fully implemented
- Base structure ✅
- New Project section ✅
- Maintenance section ✅
- Archiving section ✅
- All handlers ✅

Ready for testing and integration!
