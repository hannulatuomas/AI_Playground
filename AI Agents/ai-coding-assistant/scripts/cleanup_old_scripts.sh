#!/bin/bash
# Cleanup Script - Remove old scripts from project root

cd "$(dirname "$0")/.."

echo ""
echo "========================================"
echo "Cleanup Old Scripts from Root"
echo "========================================"
echo ""
echo "This will DELETE the following files from project root:"
echo "- setup.bat"
echo "- setup.sh"
echo "- run.bat"
echo "- run.sh"
echo "- run_tests.bat"
echo "- run_tests.sh"
echo "- migrate_db.bat"
echo "- migrate_db.py"
echo "- reset_db.bat"
echo "- verify_fixes.bat"
echo ""
echo "These files have been moved to scripts/ folder."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "Removing old scripts..."
echo ""

# Remove old scripts
for file in setup.bat setup.sh run.bat run.sh run_tests.bat run_tests.sh migrate_db.bat migrate_db.py reset_db.bat verify_fixes.bat; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "✓ Removed $file"
    fi
done

echo ""
echo "========================================"
echo "Cleanup Complete!"
echo "========================================"
echo ""
echo "All old scripts have been removed from project root."
echo ""
echo "Use the new scripts in scripts/ folder:"
echo "- scripts/setup.sh"
echo "- scripts/run.sh"
echo "- scripts/run_tests.sh"
echo "- scripts/migrate_db.py"
echo ""
