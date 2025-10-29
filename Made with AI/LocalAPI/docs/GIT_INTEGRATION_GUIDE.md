# Git Integration Guide

## Overview

LocalAPI includes built-in Git integration for version controlling your API collections, requests, and configurations. This allows you to track changes, maintain history, and collaborate using standard Git workflows.

## Features

### Core Git Operations

- ✅ **Repository Initialization** - Create Git repo in collections directory
- ✅ **Status Tracking** - View modified, created, deleted, and staged files
- ✅ **File Staging** - Stage individual files or all changes
- ✅ **Commits** - Commit with message and optional description
- ✅ **History** - View commit log with author and timestamps
- ✅ **Branch Management** - Create, switch, and manage branches
- ✅ **Diff Viewing** - See changes before committing
- ✅ **Configuration** - Set user name and email

### UI Features

- **Visual Status Panel** - See all changes at a glance
- **One-Click Staging** - Stage/unstage files with single click
- **Commit Dialog** - User-friendly commit interface
- **History Viewer** - Browse commit history
- **Status Indicators** - Color-coded file status badges
- **Branch Indicator** - Current branch displayed prominently

## Getting Started

### Initialize Repository

When you first open the Git panel, you'll see an option to initialize a repository:

1. Click **"Initialize Repository"** button
2. Git repo is created in your collections directory
3. A `.gitignore` file is automatically created

The default `.gitignore` includes:
```
node_modules/
dist/
release/
.DS_Store
Thumbs.db
*.log
.env
.env.local
data/*.db
data/*.db-*
```

### Configure User Information

Before making commits, set your name and email:

```typescript
await window.electronAPI.git.setConfig('user.name', 'Your Name');
await window.electronAPI.git.setConfig('user.email', 'your.email@example.com');
```

Or use the UI settings (if available).

## Using the Git Panel

### Viewing Status

The Git panel shows:

- **Branch name** - Current branch with icon
- **Change count** - Number of modified files
- **Staged count** - Number of files ready to commit
- **Ahead/Behind** - Commits ahead/behind remote (if configured)

### File Status Indicators

Files are marked with status badges:

- **M** - Modified (yellow)
- **C** - Created/New (green)
- **D** - Deleted (red)
- **R** - Renamed (blue)
- **S** - Staged (primary blue)

### Staging Files

**Stage Individual File:**
1. Find file in "Changes" list
2. Click the **+** button next to the file

**Stage All Files:**
1. Click **"Stage All"** button at top of changes list

**Unstage File:**
1. Find file in "Staged Changes" list
2. Click the **-** button next to the file

### Committing Changes

1. Stage the files you want to commit
2. Click **"Commit"** button
3. Enter commit message (required)
4. Optionally add detailed description
5. Click **"Commit"** to save changes

**Commit Message Guidelines:**
- First line: Brief summary (50 chars or less)
- Description: Detailed explanation (optional)
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise

### Viewing History

1. Click the **History** icon (clock) in panel header
2. Browse recent commits
3. See commit message, author, date, and hash

Each commit shows:
- **Message** - Commit summary
- **Author** - Who made the commit
- **Date** - When it was committed
- **Hash** - Short commit identifier (first 7 chars)

## API Reference

### Check Repository Status

```typescript
const isRepo = await window.electronAPI.git.isRepository();
```

### Initialize Repository

```typescript
await window.electronAPI.git.init();
```

### Get Status

```typescript
const status = await window.electronAPI.git.getStatus();
// Returns:
// {
//   isRepo: boolean,
//   branch: string,
//   modified: string[],
//   created: string[],
//   deleted: string[],
//   renamed: string[],
//   staged: string[],
//   conflicted: string[],
//   ahead: number,
//   behind: number
// }
```

### Stage Files

```typescript
// Stage single file
await window.electronAPI.git.add('collections/my-api.json');

// Stage multiple files
await window.electronAPI.git.add(['file1.json', 'file2.json']);

// Stage all files
await window.electronAPI.git.add('.');
```

### Unstage Files

```typescript
// Unstage specific files
await window.electronAPI.git.reset(['file1.json']);

// Unstage all
await window.electronAPI.git.reset();
```

### Commit Changes

```typescript
const hash = await window.electronAPI.git.commit({
  message: 'Add new API endpoints',
  description: 'Added user authentication and profile endpoints',
  addAll: false // Set true to stage all files before committing
});
```

### Get Commit History

```typescript
// Get last 20 commits
const commits = await window.electronAPI.git.getLog(20);

// Each commit has:
// {
//   hash: string,
//   date: string,
//   message: string,
//   author: string,
//   body?: string
// }
```

### View Diffs

```typescript
// Diff for unstaged changes
const diff = await window.electronAPI.git.getDiff();

// Diff for specific file
const fileDiff = await window.electronAPI.git.getDiff('file.json');

// Diff for staged changes
const stagedDiff = await window.electronAPI.git.getDiffStaged();
```

### Branch Operations

```typescript
// Get branches
const branches = await window.electronAPI.git.getBranches();
// Returns: { current: string, all: string[] }

// Create new branch
await window.electronAPI.git.createBranch('feature-branch', true); // true = checkout

// Switch branch
await window.electronAPI.git.checkout('main');
```

### Check for Changes

```typescript
const hasChanges = await window.electronAPI.git.hasChanges();
```

### Discard Changes

```typescript
// Discard specific files
await window.electronAPI.git.discardChanges(['file1.json']);

// Discard all changes
await window.electronAPI.git.discardChanges();
```

### Configuration

```typescript
// Get config value
const userName = await window.electronAPI.git.getConfig('user.name');

// Set config value
await window.electronAPI.git.setConfig('user.name', 'John Doe');
await window.electronAPI.git.setConfig('user.email', 'john@example.com');
```

## Workflows

### Basic Workflow

1. **Make changes** to collections/requests
2. **Review changes** in Git panel
3. **Stage files** you want to commit
4. **Commit** with descriptive message
5. **View history** to see your commits

### Feature Branch Workflow

1. **Create feature branch**
   ```typescript
   await window.electronAPI.git.createBranch('feature-new-api', true);
   ```

2. **Make changes** and commit

3. **Switch back to main**
   ```typescript
   await window.electronAPI.git.checkout('main');
   ```

4. **Merge** (use external Git tools for merging)

### Backup Workflow

1. **Commit regularly** to track changes
2. **Add remote** repository (GitHub, GitLab, etc.)
3. **Push** commits to remote for backup
4. **Pull** to sync changes from other machines

## Best Practices

### Commit Messages

**Good:**
```
Add user authentication endpoints

- Added POST /auth/login endpoint
- Added POST /auth/register endpoint
- Added JWT token validation
```

**Bad:**
```
updated stuff
```

### When to Commit

- ✅ After completing a feature
- ✅ After fixing a bug
- ✅ Before making major changes
- ✅ At end of work session
- ❌ Don't commit broken code
- ❌ Don't commit half-finished work

### What to Commit

- ✅ Collection files
- ✅ Request configurations
- ✅ Environment files
- ✅ Documentation
- ❌ Don't commit secrets/passwords
- ❌ Don't commit temporary files
- ❌ Don't commit database files

### File Organization

Keep your collections organized:
```
collections/
  ├── user-api/
  │   ├── auth.json
  │   └── profile.json
  ├── payment-api/
  │   └── transactions.json
  └── README.md
```

## Troubleshooting

### "Not a Git repository"

**Solution:** Click "Initialize Repository" in the Git panel.

### "Please tell me who you are"

**Solution:** Configure your user name and email:
```typescript
await window.electronAPI.git.setConfig('user.name', 'Your Name');
await window.electronAPI.git.setConfig('user.email', 'your@email.com');
```

### "Nothing to commit"

**Solution:** Make sure you've staged files before committing. Click "Stage All" or stage individual files.

### Changes not showing

**Solution:** Click the refresh button in the Git panel header.

### Commit failed

**Possible causes:**
- No files staged
- Empty commit message
- Git configuration missing

**Solution:** Check error message and ensure all requirements are met.

## Advanced Usage

### Using with External Git Tools

LocalAPI's Git integration works with standard Git repositories. You can use external tools:

- **GitHub Desktop** - Visual Git client
- **GitKraken** - Advanced Git GUI
- **VS Code** - Built-in Git support
- **Command Line** - Full Git CLI access

The repository is located at:
```
{userData}/collections/
```

### Remote Repositories

While LocalAPI doesn't have built-in push/pull UI, you can:

1. **Add remote** using external tools or API:
   ```typescript
   // Not yet exposed in UI, but available in GitService
   ```

2. **Push/Pull** using external Git tools

3. **Collaborate** using standard Git workflows

### Branching Strategy

**Simple:**
- `main` - Production-ready collections
- `dev` - Development work

**Git Flow:**
- `main` - Stable releases
- `develop` - Integration branch
- `feature/*` - New features
- `hotfix/*` - Urgent fixes

## Integration with Other Features

### With Import/Export

1. Export collections to JSON
2. Commit the JSON files
3. Share via Git repository
4. Others can import the JSON

### With Collections

- Collections are automatically saved as files
- File changes trigger Git status updates
- Commit after organizing collections

### With Environments

- Environment files can be version controlled
- Commit environment templates
- Don't commit secrets (use .gitignore)

## Security Considerations

### What NOT to Commit

- ❌ API keys
- ❌ Passwords
- ❌ Access tokens
- ❌ Private keys
- ❌ Database credentials

### Use .gitignore

Add sensitive files to `.gitignore`:
```
.env
.env.local
secrets.json
*.key
*.pem
```

### Use Secrets Management

- Store secrets separately
- Use environment variables
- Use LocalAPI's secrets feature
- Never commit secrets to Git

## Performance

### Repository Size

- Git repos grow with history
- Large files increase repo size
- Consider cleaning old history periodically

### Optimization Tips

- Commit regularly but not too frequently
- Don't commit large binary files
- Use `.gitignore` effectively
- Clean up old branches

## Future Enhancements

### Planned Features

- Push/Pull UI
- Remote repository management
- Branch merging UI
- Conflict resolution
- Visual diff viewer
- Blame/history for specific files
- Tag management
- Stash support

## Related Documentation

- [User Guide](USER_GUIDE.md)
- [Import/Export Guide](IMPORT_EXPORT_GUIDE.md)
- [API Documentation](API.md)
- [Codebase Structure](CODEBASE_STRUCTURE.md)

## Support

For issues or questions:
1. Check this documentation
2. Review error messages
3. Check Git panel status
4. Verify Git configuration
5. Try external Git tools for advanced operations
