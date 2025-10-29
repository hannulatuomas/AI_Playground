#!/usr/bin/env python3
"""
Script to update version numbers and dates in documentation files.
"""
import re
from pathlib import Path
from datetime import datetime

# Current version and date
CURRENT_VERSION = "2.4.1"
CURRENT_DATE = "October 13, 2025"
CURRENT_DATE_SHORT = "2025-10-13"

def update_file_versions(file_path: Path) -> bool:
    """Update version and date in a file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Update "Version:" patterns
        # Match: **Version:** X.X.X
        content = re.sub(
            r'\*\*Version:\*\* \d+\.\d+(\.\d+)?',
            f'**Version:** {CURRENT_VERSION}',
            content
        )
        
        # Update "Last Updated:" patterns
        # Match: **Last Updated:** Month Day, Year
        content = re.sub(
            r'\*\*Last Updated:\*\* [A-Za-z]+ \d+, \d{4}',
            f'**Last Updated:** {CURRENT_DATE}',
            content
        )
        
        # Match: **Last Updated:** YYYY-MM-DD
        content = re.sub(
            r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}',
            f'**Last Updated:** {CURRENT_DATE_SHORT}',
            content
        )
        
        # Special case for docs/README.md - has different formatting
        if file_path.name == 'README.md' and 'Documentation Status' in content:
            content = re.sub(
                r'\*\*Last Updated:\*\* [A-Za-z]+ \d+, \d{4}\s+',
                f'**Last Updated:** {CURRENT_DATE}  \n',
                content
            )
            content = re.sub(
                r'\*\*Version:\*\* \d+\.\d+(\.\d+)?',
                f'**Version:** {CURRENT_VERSION}',
                content
            )
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    root_dir = Path('/home/ubuntu/ai-agent-console')
    
    # Key documentation files to update
    key_docs = [
        'docs/README.md',
        'docs/TODO.md',
        'docs/development/STATUS.md',
        'docs/development/FUTURE_IMPROVEMENTS.md',
        'docs/guides/EXTENDING_GUIDE.md',
        'docs/guides/BENCHMARKS.md',
        'docs/guides/TESTING.md',
        'PROJECT_STRUCTURE.md',
    ]
    
    print(f"Updating documentation to version {CURRENT_VERSION} ({CURRENT_DATE})\n")
    print("=" * 80)
    
    updated_count = 0
    
    # Update key documentation files
    for doc_file in key_docs:
        file_path = root_dir / doc_file
        if file_path.exists():
            if update_file_versions(file_path):
                print(f"✓ Updated {doc_file}")
                updated_count += 1
    
    print("\n" + "=" * 80)
    print(f"\n✅ Updated {updated_count} files to version {CURRENT_VERSION}")

if __name__ == "__main__":
    main()
