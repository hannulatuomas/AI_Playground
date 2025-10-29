# User Preferences

**Version:** 0.7.0  
**Last Updated:** October 23, 2025

This document tracks user preferences and customizations for LocalAPI.

## Code Style Preferences

- **File Length**: Keep files under 500 lines
- **Code Style**: Clean, modular, well-structured
- **Testing**: Comprehensive tests for all features
- **Documentation**: Always keep up to date

## Project Organization

- **Scripts**: Organized in `scripts/` folder
- **Documentation**: Organized in `docs/` folder
- **Tests**: Organized in `tests/` folder
- **Code**: Organized in `src/` folder
- **Commits**: Scripts and summaries in `commits/` folder

## Important Documents

Always keep these documents up to date:
- README.md
- CHANGELOG.md
- TODO.md
- CODEBASE_STRUCTURE.md
- docs/API.md
- docs/STATUS.md
- docs/USER_PREFERENCES.md
- docs/AI_CONTEXT.md
- docs/EXTENDING_GUIDE.md
- docs/USER_GUIDE.md
- docs/QUICKSTART.md

## Application Settings (v0.6.0)

### Cache Settings

**Location**: Cache tab in main navigation

#### Default Configuration
- **Enable Caching**: `true`
- **Default TTL**: `5 minutes` (300 seconds)
- **Max Cache Size**: `100 MB`
- **Eviction Strategy**: LRU (Least Recently Used)

#### Configurable Options
- **TTL Range**: 1-60 minutes
- **Max Size Range**: 10-500 MB
- **Enable/Disable**: Toggle caching globally
- **Per-Request Override**: Can be set per request

#### Cache Statistics
- **Cache Hits**: Number of requests served from cache
- **Cache Misses**: Number of requests not in cache
- **Hit Rate**: Percentage (hits / total requests)
- **Current Size**: Cache size in MB
- **Entry Count**: Number of cached responses

#### Cache Operations
- **Clear All**: Remove all cached responses
- **Clean Expired**: Remove only expired entries
- **Invalidate by Pattern**: Remove entries matching regex pattern
- **Invalidate by Tags**: Remove entries with specific tags

### Git Settings

**Location**: Git tab in main navigation

#### Default Configuration
- **Working Directory**: `{userData}/collections`
- **Auto-initialize**: Creates .gitignore automatically
- **User Name**: From global git config
- **User Email**: From global git config

#### Features
- Repository initialization
- File staging/unstaging
- Commit with messages
- Branch management
- History viewing
- Diff generation

### Plugin Settings

**Location**: Plugins tab in main navigation

#### Default Configuration
- **Plugins Directory**: `{userData}/plugins`
- **Auto-discover**: On startup
- **Hot Reload**: Enabled

#### Plugin Management
- Enable/disable plugins
- Reload plugins
- View plugin info
- Check permissions

### Report Settings

**Location**: Reports tab in main navigation

#### Default Configuration
- **Output Directory**: User's Documents folder
- **Include Charts**: `true`
- **Include Summary**: `true`
- **Include Details**: `true`
- **Chart Type**: Auto-select based on data

#### Report Types
- Security Scan Reports
- Vulnerability Scan Reports
- Security Trends Reports
- Performance Trends Reports

## Commit Message Format

Git commit messages should be comprehensive and detailed, formatted as .bat files in `commits/` folder with proper multi-line syntax for Windows batch files.

---

**Version:** 0.7.0  
**Last Updated:** October 23, 2025
