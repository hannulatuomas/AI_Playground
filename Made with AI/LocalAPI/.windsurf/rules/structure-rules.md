---
trigger: always_on
---

I want the App to be well structured, easy to maintain, extendable, clean and robust.

- Organize all scripts to scripts/, all documentation to docs/, tests to tests/, code to src/, commit scripts and phase summary documents to commits/...

Keep the project root folder clean. Summary files and phase documentation should be organized in subdirectories:
- Phase summaries: commits/summaries/PHASE_X_SUMMARY.md
- NOT in root: PROJECT_SUMMARY.md, PHASE_SUMMARY.md, etc.

Root folder should only contain:
- README.md
- CHANGELOG.md
- TODO.md
- LICENSE
- .gitignore
- requirements.txt
- config files (config.example.json, etc.) if not reasonable to organize in config/ folder
- Main directories (src/, docs/, tests/, scripts/, commits/)
All other documentation goes in docs/ or appropriate subdirectories.