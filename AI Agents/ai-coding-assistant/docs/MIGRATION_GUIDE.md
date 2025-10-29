# 🔧 DATABASE MIGRATION GUIDE

## Quick Fix for "no such column: project_id" Error

**Error Message**:
```
✗ Initialization failed: no such column: project_id
```

---

## Solution: Run Migration

### Windows:
```batch
scripts\migrate_db.bat
```

### Linux/Mac:
```bash
python scripts/migrate_db.py
```

---

## What It Does

The migration script will:
1. ✅ Create a backup of your existing database
2. ✅ Add `project_id` column to interactions table
3. ✅ Add `file_path` column to interactions table
4. ✅ Create necessary indexes
5. ✅ Preserve all your existing data

**Backup Location**: `data/db/learning_backup_YYYYMMDD_HHMMSS.db`

---

## Alternative: Fresh Start

If you don't need to preserve your learning history:

### Windows:
```batch
scripts\reset_db.bat
```

### Linux/Mac:
```bash
python scripts/migrate_db.py --reset
```

This will:
1. ✅ Create a backup (just in case)
2. ✅ Delete old database
3. ✅ New database created automatically on next run

---

## After Migration

Run the application normally:

```bash
# CLI
scripts/run.bat      # Windows
scripts/run.sh       # Linux/Mac

# Enhanced GUI
python src/ui/gui_enhanced.py
```

---

## Troubleshooting

### Migration fails?
- Check the backup file in `data/db/`
- Try the reset option instead
- Contact support with error message

### Still getting errors?
1. Make sure you ran the migration
2. Check that Python can write to `data/db/` folder
3. Try deleting `data/db/learning.db` manually

---

## For Developers

The schema change adds two columns:
```sql
ALTER TABLE interactions ADD COLUMN project_id TEXT;
ALTER TABLE interactions ADD COLUMN file_path TEXT;
```

These columns enable:
- Project-specific learning
- File-level history tracking
- Better context management
- Rule enforcement per project

---

**Need Help?** See BUG_FIXES_COMPLETE.md for details.
