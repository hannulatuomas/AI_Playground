# Windsurf_Templates

Curated starter resources for bootstrapping projects with proper `.gitignore` presets across common stacks. Use these templates to quickly set up clean repositories without committing build artifacts, IDE folders, logs, caches, or other transient files.

## Overview
- Purpose-built `.gitignore` templates for popular ecosystems
- Minimal footprint, drop-in usage
- Easy to combine multiple templates per project

## Repository Layout
```
Windsurf_Templates/
├── gitignores/                 # All ignore templates
│   ├── .gitignore.python       # Python (venv, __pycache__, builds, coverage, etc.)
│   ├── .gitignore.node         # Node/NPM (node_modules, logs, caches)
│   ├── .gitignore.nodejs       # Alias of node-style ignores
│   ├── .gitignore.react        # React/CRA build artifacts
│   ├── .gitignore.nextjs       # Next.js .next/, out/
│   ├── .gitignore.cpp          # C/C++ build outputs
│   ├── .gitignore.csharp       # C#/.NET (bin/, obj/, user files)
│   ├── .gitignore.net          # .NET general template
│   ├── .gitignore.visualstudio # VS solution caches
│   ├── .gitignore.jetbrains    # JetBrains IDEs (IntelliJ, Rider, PyCharm, etc.)
│   ├── .gitignore.vscode       # VS Code workspace artifacts
│   ├── .gitignore.aspnet       # ASP.NET specifics
│   └── gitignore.io.txt        # Reference notes
└── .windsurf/                  # Reserved for Windsurf workflows (empty)
```

## Quick Start
Pick one or more templates and copy their content into your project's root `.gitignore`.

### Option 1: PowerShell (Windows)
```powershell
# Example: Node + VS Code
Get-Content "gitignores/.gitignore.node" , "gitignores/.gitignore.vscode" | Set-Content ".gitignore"
```

### Option 2: CMD (Windows)
```cmd
type gitignores\.gitignore.node gitignores\.gitignore.vscode > .gitignore
```

### Option 3: Manual copy-paste
Open the desired template(s) and paste into `.gitignore`.

## Combining Templates Safely
- You can concatenate multiple templates (e.g., Python + VSCode + JetBrains)
- Duplicates are harmless; Git ignores duplicate patterns
- Keep project-specific rules at the bottom (e.g., build/, dist/, coverage reports)

## Recommended Combos
- Node/React: `.gitignore.node` + `.gitignore.vscode` (+ `.gitignore.jetbrains` if applicable)
- Next.js: `.gitignore.nextjs` + `.gitignore.vscode`
- Python: `.gitignore.python` + `.gitignore.vscode` (+ `.gitignore.jetbrains`)
- .NET/C#: `.gitignore.net` or `.gitignore.csharp` + `.gitignore.visualstudio`
- C/C++: `.gitignore.cpp` + IDE of choice

## Tips for Custom Rules
- Add environment files: `.env`, `.env.*`
- Add OS files: `Thumbs.db`, `.DS_Store`
- Add tooling caches: `.pytest_cache/`, `.mypy_cache/`, `.tox/`, `.ruff_cache/`, `.eslintcache`
- Add build outputs: `build/`, `dist/`, `out/`, `coverage/`, `reports/`

## Contributing a New Template
1. Add a new file under `gitignores/` named `.gitignore.<stack>` (lowercase)
2. Keep entries minimal and widely applicable
3. Include comments only where necessary
4. Avoid project-specific or secret files (handled by local `.gitignore` or `.git/info/exclude`)

## Notes
- `.windsurf/` is reserved for Windsurf workflows; currently empty for future automation
- These templates are compatible with Git across platforms
