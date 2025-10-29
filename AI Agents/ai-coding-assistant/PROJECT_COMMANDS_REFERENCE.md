# Project Commands Quick Reference

## 📋 Command Overview

| Command | Description | Example |
|---------|-------------|---------|
| `project new` | Create new project from template | `project new web-react my-app` |
| `project templates` | List available templates | `project templates --search web` |
| `project init` | Initialize existing folder | `project init --git --license` |
| `project check-deps` | Check outdated dependencies | `project check-deps` |
| `project update-deps` | Show update commands | `project update-deps` |
| `project scan-security` | Scan for vulnerabilities | `project scan-security` |
| `project health` | Analyze code health | `project health` |
| `project archive` | Create project archive | `project archive --format zip` |
| `project changelog` | Generate changelog | `project changelog --from v1.0.0` |
| `project release` | Prepare release | `project release 1.2.0` |

---

## 🏗️ Creating Projects

### Basic Usage
```bash
project new <template> <name>
```

### With Options
```bash
project new web-react my-app \
  --author "John Doe" \
  --license MIT \
  --no-git
```

### Available Options
- `--author <name>` - Set author name
- `--license <type>` - Set license (MIT, Apache-2.0, GPL-3.0)
- `--no-git` - Don't initialize git
- `--no-install` - Don't install dependencies
- `--dest <path>` - Custom destination path

---

## 📚 Templates

### List All Templates
```bash
project templates
```

### Search Templates
```bash
project templates --search web
project templates --search python
project templates --search api
```

### Common Templates
- `web-react` - React web application
- `web-vue` - Vue.js web application
- `cli-python` - Python CLI tool
- `api-fastapi` - FastAPI REST API
- `api-express` - Express.js API
- `library-python` - Python library

---

## 🔧 Project Initialization

### Basic Init
```bash
cd my-existing-project
project init
```

### Init with Git
```bash
project init --git
```

### Init with License
```bash
project init --license
# Interactive: prompts for license type and author
```

---

## 📦 Dependency Management

### Check for Updates
```bash
project check-deps
```

**Output:**
```
Found 3 outdated dependencies:

  • react
    Current: 17.0.2
    Latest:  18.2.0

  • axios
    Current: 0.21.1
    Latest:  1.4.0
```

### Get Update Commands
```bash
project update-deps
```

**Output:**
```
# Update Node dependencies
npm outdated
npm update
# or for major updates:
npx npm-check-updates -u
npm install
```

---

## 🛡️ Security Scanning

### Scan for Vulnerabilities
```bash
project scan-security
```

**Output:**
```
Found 2 vulnerabilities:

  HIGH: lodash
    Prototype Pollution vulnerability

  CRITICAL: minimist
    Prototype Pollution allowing arbitrary code execution
```

---

## 📊 Health Analysis

### Analyze Project Health
```bash
project health
```

**Output:**
```
=== Code Health Metrics ===
  Project type: node
  Files: 42
  Lines of code: 3,547

  ✓ No major issues detected
```

---

## 📦 Archiving

### Create ZIP Archive
```bash
project archive
# or explicitly:
project archive --format zip
```

### Create TAR.GZ Archive
```bash
project archive --format tar.gz
```

**Output:**
```
✓ Archive created successfully!
  Location: C:\projects\my-app_20250119_143022.zip
  Size: 2.45 MB
```

---

## 📝 Changelog Management

### Generate Full Changelog
```bash
project changelog
```

### Generate Since Specific Tag
```bash
project changelog --from v1.0.0
```

**Output:**
```
✓ Changelog generated!
  C:\projects\my-app\CHANGELOG.md
```

---

## 🚀 Release Preparation

### Prepare Release
```bash
project release 1.2.0
```

**Interactive Workflow:**
```
→ Preparing release 1.2.0 for: C:\projects\my-app

  Key highlights (comma-separated, or Enter to skip): 
  > New dashboard, Performance improvements, Bug fixes

  Bump type (major/minor/patch) [patch]: 
  > minor

✓ Release notes generated!
✓ Version bumped: 1.1.0 -> 1.2.0
✓ Changelog updated!

✓ Release preparation complete!
  Version: 1.2.0

  Next steps:
  1. Review and commit changes
  2. Create git tag: git tag v1.2.0
  3. Push with tags: git push --tags
```

---

## 🎨 Output Color Guide

- **Green (✓)** - Success, completion
- **Red (✗)** - Errors, failures
- **Yellow (⚠)** - Warnings, important info
- **Cyan (→)** - Progress, processing
- **Bold** - Headings, emphasis

---

## 💡 Pro Tips

### Tip 1: Project Workflow
```bash
# Create project
project new web-react my-app --author "Me"
cd my-app

# Regular maintenance
project check-deps
project scan-security
project health

# Before release
project release 1.0.0
git tag v1.0.0
git push --tags

# Archive for distribution
project archive --format zip
```

### Tip 2: Automated Checks
```bash
# Add to pre-commit hook
project scan-security
project health
```

### Tip 3: Search Templates
```bash
# Find web templates
project templates --search web

# Find Python templates
project templates --search python
```

### Tip 4: Quick Health Check
```bash
# One-liner for project overview
project health && project check-deps
```

---

## 🔍 Troubleshooting

### Command Not Found
```bash
# Make sure you're in CLI
python src/ui/cli.py
```

### Template Not Found
```bash
# List available templates
project templates

# Use exact template name
project new web-react my-app  # ✓ Correct
project new react my-app      # ✗ Wrong
```

### Dependency Check Fails
```bash
# Install package managers:
# For Python: pip install --upgrade pip
# For Node: npm install -g npm
# For .NET: Install .NET SDK
```

### Security Scan No Results
```bash
# Install security tools:
pip install safety          # Python
npm install                 # Node (audit built-in)
# .NET (built-in)
```

---

## 📖 More Help

- Full command reference: `help` in CLI
- Detailed docs: `commits/PHASE_10_CLI_COMPLETE.md`
- Examples: `PHASE_10_INTEGRATION_SUMMARY.md`

---

**Quick Reference Version**: 1.0  
**Phase**: 10 - Project Lifecycle Management  
**Last Updated**: 2025-01-XX
