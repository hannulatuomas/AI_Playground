# Versioning System Guide

**Version:** 2.5.0  
**Last Updated:** October 13, 2025  
**Status:** ✅ Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Semantic Versioning](#semantic-versioning)
3. [Versioning Tool](#versioning-tool)
4. [Git Agent Integration](#git-agent-integration)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Automated Workflows](#automated-workflows)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Agent Console includes a comprehensive automated versioning management system that follows semantic versioning principles. The system can automatically detect changes, determine appropriate version bumps, update version files across the project, and integrate with git workflows.

### Key Features

- **Semantic Versioning**: Full support for MAJOR.MINOR.PATCH versioning
- **Automatic Detection**: Analyzes git commits to suggest version bumps
- **Multi-File Updates**: Updates version strings across all project files
- **Git Integration**: Creates git tags for versions and integrates with commit workflows
- **Agent Integration**: Works seamlessly with the git agent for automated version management
- **Changelog Generation**: Can generate structured changelog entries
- **Flexible Control**: Supports both manual and automatic version management

---

## Semantic Versioning

The versioning system follows [Semantic Versioning 2.0.0](https://semver.org/) principles:

### Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Breaking changes that are backward incompatible
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes and minor changes
- **PRERELEASE** (optional): Pre-release identifier (e.g., alpha, beta, rc.1)
- **BUILD** (optional): Build metadata

### Version Bump Rules

The system automatically determines version bumps based on commit messages:

#### MAJOR Version Bump (X.0.0)

Triggered by keywords indicating breaking changes:
- `breaking`, `breaking change`, `breaking changes`
- `backward incompatible`, `incompatible`
- `removed` (when removing features)

**Example commits:**
```
BREAKING: Remove deprecated API endpoints
feat: Add new authentication system (backward incompatible)
```

#### MINOR Version Bump (0.X.0)

Triggered by keywords indicating new features:
- `feat`, `feature`, `add`, `added`, `new`
- `implement`, `implemented`, `enhancement`
- `enhance`, `improved`, `improvement`

**Example commits:**
```
feat: Add versioning system with semantic versioning support
feature: Implement virtual environment setup scripts
add: New versioning tool for automated version management
```

#### PATCH Version Bump (0.0.X)

Triggered by keywords indicating bug fixes:
- `fix`, `fixed`, `bug`, `bugfix`, `patch`
- `hotfix`, `repair`, `resolve`, `resolved`
- `correct`, `corrected`

**Example commits:**
```
fix: Correct version file reading in core module
bugfix: Resolve issue with git tag creation
patch: Fix typo in documentation
```

### Deprecation Handling

The system also tracks deprecations:
- `deprecate`, `deprecated`, `deprecation`

Deprecations typically trigger MINOR version bumps but are tracked separately for changelog generation.

---

## Versioning Tool

The `VersioningTool` is a reusable tool that agents can use for version management.

### Tool Actions

The tool supports the following actions:

#### 1. Get Current Version

Get the current version from the VERSION file.

```python
result = versioning_tool.invoke({'action': 'get_version'})
# Returns:
# {
#     'success': True,
#     'action': 'get_version',
#     'version': '2.5.0',
#     'version_parts': {
#         'major': 2,
#         'minor': 5,
#         'patch': 0,
#         'prerelease': None,
#         'build': None
#     }
# }
```

#### 2. Manual Version Bump

Manually bump the version by specifying the bump type.

```python
result = versioning_tool.invoke({
    'action': 'bump',
    'bump_type': 'minor'  # 'major', 'minor', or 'patch'
})
# Returns:
# {
#     'success': True,
#     'action': 'bump',
#     'bump_type': 'minor',
#     'old_version': '2.5.0',
#     'new_version': '2.6.0',
#     'message': 'Version bumped from 2.5.0 to 2.6.0'
# }
```

#### 3. Automatic Version Bump

Automatically analyze changes and bump the version.

```python
result = versioning_tool.invoke({
    'action': 'auto_bump',
    'use_git': True  # Analyze git commits
})
# Returns:
# {
#     'success': True,
#     'action': 'auto_bump',
#     'bump_type': 'minor',
#     'old_version': '2.5.0',
#     'new_version': '2.6.0',
#     'analysis': {
#         'has_breaking_changes': False,
#         'has_new_features': True,
#         'has_bug_fixes': True,
#         'has_deprecations': False,
#         'commits_analyzed': 15,
#         'files_changed': 8
#     },
#     'message': 'Version auto-bumped from 2.5.0 to 2.6.0 (minor)'
# }
```

#### 4. Analyze Changes

Analyze changes without bumping the version.

```python
result = versioning_tool.invoke({
    'action': 'analyze',
    'use_git': True
})
# Returns:
# {
#     'success': True,
#     'action': 'analyze',
#     'current_version': '2.5.0',
#     'suggested_bump': 'minor',
#     'analysis': {
#         'has_breaking_changes': False,
#         'has_new_features': True,
#         'has_bug_fixes': False,
#         'has_deprecations': False,
#         'commit_messages': [...],
#         'file_changes': [...]
#     }
# }
```

#### 5. Update Version in Files

Update version strings across project files.

```python
result = versioning_tool.invoke({
    'action': 'update_files',
    'version': '2.6.0'  # Optional, uses current if not specified
})
# Returns:
# {
#     'success': True,
#     'action': 'update_files',
#     'version': '2.6.0',
#     'updated_files': ['README.md', 'docs/README.md', ...],
#     'skipped_files': ['setup.py'],  # Files that don't exist
#     'message': 'Updated version to 2.6.0 in 5 files'
# }
```

#### 6. Create Git Tag

Create a git tag for the version.

```python
result = versioning_tool.invoke({
    'action': 'create_tag',
    'version': '2.6.0',  # Optional
    'message': 'Release 2.6.0 with new features'  # Optional
})
# Returns:
# {
#     'success': True,
#     'action': 'create_tag',
#     'version': '2.6.0',
#     'tag_name': 'v2.6.0',
#     'message': 'Created tag v2.6.0'
# }
```

#### 7. Full Release Workflow

Execute the complete release workflow.

```python
result = versioning_tool.invoke({
    'action': 'full_release',
    'bump_type': 'minor',  # Optional, uses auto if not specified
    'create_tag': True,  # Default: True
    'tag_message': 'Release 2.6.0'  # Optional
})
# Returns:
# {
#     'success': True,
#     'action': 'full_release',
#     'new_version': '2.6.0',
#     'steps': [
#         ('analyze', {...}),
#         ('bump', {...}),
#         ('update_files', {...}),
#         ('create_tag', {...})
#     ],
#     'message': 'Successfully released version 2.6.0'
# }
```

### Files Updated by Versioning Tool

The tool automatically updates version strings in the following files:

1. **VERSION** - Main version file
2. **core/__init__.py** - Python package version
3. **main.py** - Application version (if __version__ exists)
4. **setup.py** - Package distribution version (if exists)
5. **README.md** - Documentation version
6. **docs/README.md** - Documentation index version
7. **PROJECT_STRUCTURE.md** - Project structure documentation
8. **CONTRIBUTING.md** - Contributing guide version

---

## Git Agent Integration

The `GitAgent` has been enhanced to support automatic versioning on commits.

### Versioning-Enabled Commits

#### Method 1: Using Context

```python
context = {
    'enable_versioning': True,
    'version_bump_type': 'minor',  # Optional: 'major', 'minor', 'patch', or None for auto
    'create_version_tag': True  # Optional: default True
}

result = git_agent.execute('commit with message "Add new features"', context)
```

#### Method 2: Using Convenience Method

```python
result = git_agent.commit_with_versioning(
    message="Add new features",
    bump_type='minor',  # Optional: None for auto-detection
    create_tag=True  # Optional: default True
)
```

### What Happens During a Versioning Commit

1. **Change Analysis**: Analyzes git commits since last tag
2. **Version Bump**: Bumps version based on analysis or specified type
3. **File Updates**: Updates VERSION file and all version strings in project files
4. **Staging**: Automatically stages the updated version files
5. **Commit**: Creates the commit with your message
6. **Tagging**: Creates a git tag (e.g., `v2.6.0`) if enabled

### Configuration

Enable versioning by default in `config.yaml`:

```yaml
agents:
  git_agent:
    enable_git_versioning: true  # Enable automatic versioning on commits
    require_git_confirmation: true  # Require confirmation for git operations
```

---

## Usage Examples

### Example 1: Check Current Version

```python
from tools import VersioningTool

# Initialize tool
versioning = VersioningTool(config={'project_root': '/path/to/project'})

# Get current version
result = versioning.invoke({'action': 'get_version'})
print(f"Current version: {result['version']}")
```

### Example 2: Manual Version Bump

```python
# Bump minor version (2.5.0 -> 2.6.0)
result = versioning.invoke({
    'action': 'bump',
    'bump_type': 'minor'
})

if result['success']:
    print(f"Version bumped from {result['old_version']} to {result['new_version']}")
```

### Example 3: Automatic Version Bump with Analysis

```python
# Analyze git commits and bump version automatically
result = versioning.invoke({
    'action': 'auto_bump',
    'use_git': True
})

if result['success']:
    analysis = result['analysis']
    print(f"Version: {result['new_version']}")
    print(f"Bump type: {result['bump_type']}")
    print(f"New features: {analysis['has_new_features']}")
    print(f"Bug fixes: {analysis['has_bug_fixes']}")
    print(f"Breaking changes: {analysis['has_breaking_changes']}")
```

### Example 4: Full Release Workflow

```python
# Complete release with automatic bump
result = versioning.invoke({
    'action': 'full_release',
    'create_tag': True,
    'tag_message': 'Release with new features and bug fixes'
})

if result['success']:
    print(f"Released version {result['new_version']}")
    for step_name, step_result in result['steps']:
        print(f"  {step_name}: {'✓' if step_result.get('success') else '✗'}")
```

### Example 5: Commit with Automatic Versioning (Git Agent)

```python
from agents import GitAgent

git_agent = GitAgent(config={...})

# Commit with automatic version detection
result = git_agent.commit_with_versioning(
    message="feat: Add versioning system with semantic versioning support",
    bump_type=None,  # Auto-detect from commit message
    create_tag=True
)

if result['success']:
    print("Commit and version bump successful!")
```

### Example 6: Manual Version Control

```python
# Step-by-step manual control
versioning = VersioningTool()

# 1. Analyze changes
analysis = versioning.invoke({'action': 'analyze', 'use_git': True})
print(f"Suggested bump: {analysis['suggested_bump']}")

# 2. Decide on bump type (can override suggestion)
bump_type = 'minor'  # or use analysis['suggested_bump']

# 3. Bump version
bump_result = versioning.invoke({'action': 'bump', 'bump_type': bump_type})
new_version = bump_result['new_version']

# 4. Update files
versioning.invoke({'action': 'update_files', 'version': new_version})

# 5. Create tag
versioning.invoke({
    'action': 'create_tag',
    'version': new_version,
    'message': f'Release {new_version}'
})
```

---

## Configuration

### Tool Configuration

```python
versioning_tool = VersioningTool(config={
    'project_root': '/path/to/project'  # Root directory of the project
})
```

### Agent Configuration (config.yaml)

```yaml
tools:
  versioning:
    enabled: true

agents:
  git_agent:
    enable_git_versioning: false  # Set to true to enable by default
    require_git_confirmation: true
    tools:
      - git
      - versioning  # Add versioning tool to git agent
```

### VERSION File Location

The VERSION file should be in the project root:

```
project-root/
├── VERSION              # Contains version string (e.g., "2.5.0")
├── core/
│   └── __init__.py      # Reads from VERSION file
├── README.md            # Contains version documentation
└── ...
```

---

## Automated Workflows

### Workflow 1: Feature Development

1. Develop new features
2. Commit with feature description: `feat: Add new feature`
3. System automatically:
   - Detects "feat" keyword
   - Bumps MINOR version
   - Updates all version files
   - Creates git tag

### Workflow 2: Bug Fix

1. Fix a bug
2. Commit with fix description: `fix: Resolve issue with X`
3. System automatically:
   - Detects "fix" keyword
   - Bumps PATCH version
   - Updates all version files
   - Creates git tag

### Workflow 3: Breaking Change

1. Make breaking changes
2. Commit with breaking change notice: `BREAKING: Change API signature`
3. System automatically:
   - Detects "BREAKING" keyword
   - Bumps MAJOR version
   - Updates all version files
   - Creates git tag

### Workflow 4: Manual Release

```bash
# 1. Analyze current changes
python -c "
from tools import VersioningTool
v = VersioningTool()
result = v.invoke({'action': 'analyze', 'use_git': True})
print(f'Suggested: {result[\"suggested_bump\"]}')
"

# 2. Perform full release
python -c "
from tools import VersioningTool
v = VersioningTool()
result = v.invoke({'action': 'full_release', 'bump_type': 'minor'})
print(f'Released: {result[\"new_version\"]}')
"
```

---

## Best Practices

### 1. Commit Message Conventions

Use clear, descriptive commit messages with keywords:

**Good:**
```
feat: Add automated versioning system
fix: Correct version file reading
BREAKING: Remove deprecated API endpoints
```

**Avoid:**
```
update stuff
changes
wip
```

### 2. Version Bumping Strategy

- **Patch (0.0.X)**: Bug fixes, documentation updates, minor improvements
- **Minor (0.X.0)**: New features, non-breaking changes, enhancements
- **Major (X.0.0)**: Breaking changes, major refactors, API changes

### 3. Pre-Release Versioning

For alpha/beta releases, use prerelease tags:
```
2.6.0-alpha.1
2.6.0-beta.1
2.6.0-rc.1
2.6.0  (final release)
```

### 4. Tagging Strategy

Always create tags for releases:
- Makes it easy to track release history
- Enables rollback to specific versions
- Integrates with CI/CD pipelines

### 5. Changelog Maintenance

Keep a CHANGELOG.md file updated:
```markdown
## [2.6.0] - 2025-10-13

### Added
- Automated versioning system
- Virtual environment setup scripts

### Fixed
- Version file reading in core module

### Changed
- Git agent now supports versioning integration
```

### 6. Testing Before Release

Always test before bumping major versions:
```python
# Analyze first
result = versioning.invoke({'action': 'analyze'})
print(f"Suggested: {result['suggested_bump']}")

# Review and decide
# Then release
```

---

## Troubleshooting

### Issue 1: VERSION File Not Found

**Problem**: `FileNotFoundError: VERSION file not found`

**Solution**:
```python
# The tool will create VERSION file automatically with default version 0.1.0
# Or create it manually:
echo "2.5.0" > VERSION
```

### Issue 2: Invalid Version Format

**Problem**: `ValueError: Invalid version format`

**Solution**:
Ensure VERSION file contains valid semantic version:
```bash
# Valid formats
echo "2.5.0" > VERSION
echo "2.5.0-alpha.1" > VERSION
echo "2.5.0+build.123" > VERSION

# Invalid formats
echo "v2.5.0" > VERSION  # Don't include 'v' prefix
echo "2.5" > VERSION     # Must have three parts (MAJOR.MINOR.PATCH)
```

### Issue 3: Git Tag Already Exists

**Problem**: Tag already exists for the version

**Solution**:
```bash
# Option 1: Delete existing tag
git tag -d v2.5.0
git push origin :refs/tags/v2.5.0

# Option 2: Use a different version
# Bump to next version
```

### Issue 4: No Changes Detected

**Problem**: Auto-bump fails with "No changes detected"

**Solution**:
```bash
# Ensure there are git commits since last tag
git log --oneline

# If no commits, make changes first
# Or use manual bump
```

### Issue 5: Versioning Tool Not Available in Agent

**Problem**: Agent can't find versioning tool

**Solution**:
```yaml
# Ensure versioning tool is registered in config.yaml
tools:
  versioning:
    enabled: true

agents:
  git_agent:
    tools:
      - git
      - versioning  # Add this
```

### Issue 6: File Updates Fail

**Problem**: Some files not updated with new version

**Solution**:
- Check if files exist in project
- Verify file permissions
- Check file contains version patterns that can be updated
- Review tool logs for specific errors

---

## Advanced Topics

### Custom Version Patterns

To update custom files, extend the `version_manager.py`:

```python
# Add to update_version_in_files() in tools/lib/version_manager.py
updates = [
    # ... existing updates ...
    {
        'file': 'your_custom_file.txt',
        'pattern': r'Version: \d+\.\d+\.\d+',
        'replacement': f'Version: {version_str}'
    }
]
```

### Integration with CI/CD

```yaml
# Example GitHub Actions workflow
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Auto-version and release
        run: |
          python -c "
          from tools import VersioningTool
          v = VersioningTool()
          result = v.invoke({'action': 'full_release'})
          print(f'Released: {result[\"new_version\"]}')
          "
      - name: Push changes
        run: |
          git push origin main --tags
```

---

## Summary

The automated versioning management system provides:

1. ✅ **Semantic Versioning** - Full MAJOR.MINOR.PATCH support
2. ✅ **Automatic Detection** - Analyzes commits to suggest version bumps
3. ✅ **Multi-File Updates** - Updates version across all project files
4. ✅ **Git Integration** - Creates tags and integrates with commits
5. ✅ **Agent Integration** - Works seamlessly with git agent
6. ✅ **Flexible Control** - Supports both manual and automatic workflows
7. ✅ **Best Practices** - Follows semantic versioning standards

For more information, see:
- [Semantic Versioning Specification](https://semver.org/)
- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Conventional Commits](https://www.conventionalcommits.org/)
