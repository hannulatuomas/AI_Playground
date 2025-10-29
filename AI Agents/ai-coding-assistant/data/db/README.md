# Database Directory

SQLite database files are stored here.

## Files:
- `learning.db` - Main learning database (auto-created on first run)

## Database Contents:
- User interactions
- Error patterns
- Best practices
- Success/failure statistics

## Backup:
It's recommended to backup this database regularly:
```bash
# Export learnings
# Use /stats command to see what's stored

# Manual backup
cp data/db/learning.db data/db/learning.db.backup
```

## Clear Data:
To reset all learning:
```bash
# Using CLI
/clear

# Or manually delete
rm data/db/learning.db
```

## Note:
.db files are gitignored by default
