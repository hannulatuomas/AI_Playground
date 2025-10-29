"""
Project Manager Module

Handles project-level operations including:
- Setting and validating project root folder
- Indexing files recursively (with exclusions)
- Reading and chunking large files
- Summarizing files using LLM
- Managing project state and metadata

Addresses challenges:
- Large codebases: Index files with metadata for quick access
- Large files: Chunk reading to manage memory
- Context management: File summaries for selective inclusion
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class ProjectManager:
    """
    Manages project-level operations for the AI coding assistant.
    Handles file indexing, summarization, and project state.
    """

    # Common patterns to exclude from indexing
    DEFAULT_EXCLUDE_PATTERNS = {
        '.git', '.svn', '.hg',  # Version control
        '__pycache__', '.pytest_cache', '.mypy_cache',  # Python cache
        'node_modules', '.npm',  # Node.js
        'bin', 'obj',  # C#/.NET
        'build', 'dist', '.cache',  # Build outputs
        'target',  # Rust/Java
        '.vs', '.vscode', '.idea',  # IDE directories
        'venv', 'env', '.env',  # Python virtual environments
        'vendor',  # Go/PHP dependencies
        'coverage',  # Test coverage
    }

    # Binary file extensions to exclude
    BINARY_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib', '.a', '.lib',  # Executables and libraries
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',  # Images
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',  # Documents
        '.zip', '.tar', '.gz', '.rar', '.7z',  # Archives
        '.mp3', '.mp4', '.avi', '.mov',  # Media files
        '.db', '.sqlite', '.sqlite3',  # Databases
        '.pyc', '.pyo', '.pyd',  # Python compiled
        '.class', '.jar',  # Java compiled
        '.o', '.obj',  # Object files
    }

    # Text file extensions we explicitly support
    TEXT_EXTENSIONS = {
        '.py', '.pyw',  # Python
        '.cs',  # C#
        '.cpp', '.cxx', '.cc', '.c', '.h', '.hpp', '.hxx',  # C/C++
        '.js', '.jsx', '.mjs', '.cjs',  # JavaScript
        '.ts', '.tsx',  # TypeScript
        '.html', '.htm',  # HTML
        '.css', '.scss', '.sass', '.less',  # CSS
        '.ps1', '.psm1',  # PowerShell
        '.sh', '.bash', '.zsh',  # Shell scripts
        '.bat', '.cmd',  # Windows batch
        '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg',  # Config
        '.md', '.txt', '.rst',  # Documentation
        '.sql',  # SQL
        '.go',  # Go
        '.rs',  # Rust
        '.java',  # Java
        '.php',  # PHP
        '.rb',  # Ruby
        '.swift',  # Swift
        '.kt', '.kts',  # Kotlin
        '.vue',  # Vue
        '.r', '.R',  # R
        '.m',  # MATLAB/Objective-C
    }

    def __init__(
        self,
        llm_interface=None,
        index_path: str = "data/project_index.json"
    ):
        """
        Initialize the project manager.

        Args:
            llm_interface: Optional LLMInterface for file summarization
            index_path: Path to store the project index
        """
        self.llm_interface = llm_interface
        self.index_path = Path(index_path)
        self.root_folder: Optional[Path] = None
        self.file_index: Dict[str, Dict] = {}
        self.exclude_patterns = self.DEFAULT_EXCLUDE_PATTERNS.copy()
        
        # Ensure data directory exists
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def set_root_folder(self, path: str) -> bool:
        """
        Set and validate the project root folder.

        Args:
            path: Path to the project root folder

        Returns:
            True if valid and set successfully

        Raises:
            ValueError: If path is invalid
        """
        root_path = Path(path).resolve()

        if not root_path.exists():
            raise ValueError(f"Path does not exist: {path}")

        if not root_path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        self.root_folder = root_path
        print(f"✓ Project root set to: {self.root_folder}")
        return True

    def get_root_folder(self) -> Optional[str]:
        """
        Get the current project root folder.

        Returns:
            Root folder path as string or None
        """
        return str(self.root_folder) if self.root_folder else None

    def index_files(self, force_refresh: bool = False) -> Dict[str, Dict]:
        """
        Scan and recursively index all files in the project.
        
        Creates an index with metadata:
        - Relative path
        - File size
        - Last modified time
        - Language/extension
        - Summary hash (for change detection)

        Args:
            force_refresh: If True, rebuild index from scratch

        Returns:
            Dictionary mapping relative paths to file metadata

        Raises:
            ValueError: If root folder not set
        """
        if not self.root_folder:
            raise ValueError("Root folder not set. Call set_root_folder() first.")

        if not force_refresh:
            # Try to load existing index
            self._load_index()

        print(f"Indexing files in: {self.root_folder}")
        indexed_count = 0
        skipped_count = 0

        for root, dirs, files in os.walk(self.root_folder):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in self.exclude_patterns]

            for filename in files:
                file_path = Path(root) / filename
                
                # Skip binary files
                if file_path.suffix.lower() in self.BINARY_EXTENSIONS:
                    skipped_count += 1
                    continue

                # Get relative path from project root
                rel_path = file_path.relative_to(self.root_folder)
                rel_path_str = str(rel_path).replace('\\', '/')

                try:
                    # Get file metadata
                    stats = file_path.stat()
                    
                    # Determine language from extension
                    language = self._detect_language(file_path.suffix)

                    # Create metadata entry
                    metadata = {
                        'size': stats.st_size,
                        'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                        'extension': file_path.suffix.lower(),
                        'language': language,
                        'summary': None,  # Will be populated on demand
                        'summary_hash': None,  # For change detection
                    }

                    self.file_index[rel_path_str] = metadata
                    indexed_count += 1

                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not access {rel_path}: {e}")
                    skipped_count += 1
                    continue

        print(f"✓ Indexed {indexed_count} files (skipped {skipped_count} binary/inaccessible)")
        
        # Save index to disk
        self._save_index()

        return self.file_index

    def get_file_content(
        self,
        relative_path: str,
        chunk_size: int = 2000,
        start_line: int = 0,
        max_lines: Optional[int] = None
    ) -> Tuple[str, bool]:
        """
        Read file content with chunking support for large files.

        Args:
            relative_path: Path relative to project root
            chunk_size: Maximum number of lines to read in one chunk
            start_line: Starting line number (0-indexed)
            max_lines: Maximum number of lines to return (None for all)

        Returns:
            Tuple of (content, is_truncated)
            
        Raises:
            ValueError: If root folder not set
            FileNotFoundError: If file doesn't exist
        """
        if not self.root_folder:
            raise ValueError("Root folder not set")

        file_path = self.root_folder / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        is_truncated = False
        lines = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Skip to start line
                for _ in range(start_line):
                    next(f, None)

                # Read lines
                lines_to_read = max_lines if max_lines else chunk_size
                for i, line in enumerate(f):
                    if i >= lines_to_read:
                        is_truncated = True
                        break
                    lines.append(line.rstrip('\n\r'))

        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        for _ in range(start_line):
                            next(f, None)
                        lines_to_read = max_lines if max_lines else chunk_size
                        for i, line in enumerate(f):
                            if i >= lines_to_read:
                                is_truncated = True
                                break
                            lines.append(line.rstrip('\n\r'))
                    break
                except UnicodeDecodeError:
                    continue

        content = '\n'.join(lines)
        return content, is_truncated

    def get_file_chunks(
        self,
        relative_path: str,
        chunk_size: int = 2000
    ) -> List[Tuple[int, str]]:
        """
        Get file content as chunks for processing large files.

        Args:
            relative_path: Path relative to project root
            chunk_size: Lines per chunk

        Returns:
            List of (start_line, content) tuples

        Raises:
            ValueError: If root folder not set
            FileNotFoundError: If file doesn't exist
        """
        chunks = []
        start_line = 0
        
        while True:
            content, is_truncated = self.get_file_content(
                relative_path,
                chunk_size=chunk_size,
                start_line=start_line
            )
            
            if not content:
                break
            
            chunks.append((start_line, content))
            
            if not is_truncated:
                break
            
            start_line += chunk_size
        
        return chunks

    def summarize_file(self, relative_path: str, force: bool = False) -> Optional[str]:
        """
        Generate or retrieve a summary of the file using LLM.

        Args:
            relative_path: Path relative to project root
            force: Force regeneration even if summary exists

        Returns:
            Summary text or None if LLM not available

        Raises:
            ValueError: If root folder not set or file not in index
        """
        if not self.llm_interface:
            return None

        if relative_path not in self.file_index:
            raise ValueError(f"File not in index: {relative_path}")

        metadata = self.file_index[relative_path]
        
        # Check if summary already exists and file hasn't changed
        if not force and metadata.get('summary'):
            # Verify file hasn't been modified
            file_path = self.root_folder / relative_path
            current_hash = self._compute_file_hash(file_path)
            
            if current_hash == metadata.get('summary_hash'):
                return metadata['summary']

        # Generate new summary
        print(f"Generating summary for: {relative_path}")
        
        try:
            # Get file content (limit to reasonable size for summarization)
            content, is_truncated = self.get_file_content(
                relative_path,
                chunk_size=500  # Limit lines for summary
            )

            if not content.strip():
                return None

            # Build summarization prompt
            language = metadata.get('language', 'code')
            prompt = (
                f"Summarize this {language} file. "
                f"Focus on: structure, key functions/classes, imports/dependencies, main purpose.\n\n"
                f"File: {relative_path}\n\n"
                f"```{language}\n{content}\n```\n\n"
                f"Provide a concise 2-3 sentence summary."
            )

            if is_truncated:
                prompt += "\n\nNote: File is truncated, summarize visible content."

            # Generate summary using LLM
            summary = self.llm_interface.generate(
                prompt,
                max_tokens=150,
                use_cache=True
            )

            # Store summary in index
            file_path = self.root_folder / relative_path
            metadata['summary'] = summary.strip()
            metadata['summary_hash'] = self._compute_file_hash(file_path)
            
            # Save updated index
            self._save_index()

            return summary.strip()

        except Exception as e:
            print(f"Warning: Could not summarize {relative_path}: {e}")
            return None

    def get_file_list(
        self,
        language: Optional[str] = None,
        pattern: Optional[str] = None
    ) -> List[str]:
        """
        Get list of files from index with optional filtering.

        Args:
            language: Filter by language (e.g., 'python', 'cpp')
            pattern: Filter by filename pattern (case-insensitive substring)

        Returns:
            List of relative file paths
        """
        files = []

        for rel_path, metadata in self.file_index.items():
            # Apply language filter
            if language and metadata.get('language', '').lower() != language.lower():
                continue

            # Apply pattern filter
            if pattern and pattern.lower() not in rel_path.lower():
                continue

            files.append(rel_path)

        return sorted(files)

    def get_project_stats(self) -> Dict:
        """
        Get statistics about the indexed project.

        Returns:
            Dictionary with project statistics
        """
        if not self.file_index:
            return {
                'total_files': 0,
                'total_size': 0,
                'languages': {}
            }

        total_size = sum(meta['size'] for meta in self.file_index.values())
        
        # Count files by language
        languages = {}
        for metadata in self.file_index.values():
            lang = metadata.get('language', 'unknown')
            languages[lang] = languages.get(lang, 0) + 1

        return {
            'total_files': len(self.file_index),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'languages': dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))
        }

    def _detect_language(self, extension: str) -> str:
        """
        Detect language from file extension.

        Args:
            extension: File extension (with dot)

        Returns:
            Language name
        """
        ext_lower = extension.lower()
        
        # Direct mappings
        lang_map = {
            '.py': 'python', '.pyw': 'python',
            '.cs': 'csharp',
            '.cpp': 'cpp', '.cxx': 'cpp', '.cc': 'cpp', '.c': 'c',
            '.h': 'c', '.hpp': 'cpp', '.hxx': 'cpp',
            '.js': 'javascript', '.jsx': 'javascript', '.mjs': 'javascript',
            '.ts': 'typescript', '.tsx': 'typescript',
            '.html': 'html', '.htm': 'html',
            '.css': 'css', '.scss': 'css', '.sass': 'css',
            '.ps1': 'powershell', '.psm1': 'powershell',
            '.sh': 'bash', '.bash': 'bash', '.zsh': 'zsh',
            '.bat': 'batch', '.cmd': 'batch',
            '.json': 'json', '.xml': 'xml', '.yaml': 'yaml', '.yml': 'yaml',
            '.md': 'markdown', '.txt': 'text',
            '.go': 'go', '.rs': 'rust', '.java': 'java',
            '.php': 'php', '.rb': 'ruby', '.swift': 'swift',
            '.kt': 'kotlin', '.vue': 'vue', '.sql': 'sql',
        }

        return lang_map.get(ext_lower, 'unknown')

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute hash of file for change detection.

        Args:
            file_path: Path to the file

        Returns:
            SHA256 hash as hex string
        """
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            # If we can't compute hash, return timestamp as fallback
            return str(file_path.stat().st_mtime)

    def _save_index(self) -> None:
        """Save the file index to disk."""
        try:
            index_data = {
                'root_folder': str(self.root_folder) if self.root_folder else None,
                'last_updated': datetime.now().isoformat(),
                'files': self.file_index
            }

            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)

        except Exception as e:
            print(f"Warning: Could not save index: {e}")

    def _load_index(self) -> bool:
        """
        Load the file index from disk.

        Returns:
            True if loaded successfully
        """
        if not self.index_path.exists():
            return False

        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)

            # Restore root folder if it matches
            saved_root = index_data.get('root_folder')
            if saved_root and self.root_folder:
                if Path(saved_root) == self.root_folder:
                    self.file_index = index_data.get('files', {})
                    print(f"✓ Loaded index with {len(self.file_index)} files")
                    return True

            return False

        except Exception as e:
            print(f"Warning: Could not load index: {e}")
            return False

    def add_exclude_pattern(self, pattern: str) -> None:
        """
        Add a directory/file pattern to exclude from indexing.

        Args:
            pattern: Pattern to exclude (e.g., 'node_modules', '*.pyc')
        """
        self.exclude_patterns.add(pattern)

    def remove_exclude_pattern(self, pattern: str) -> None:
        """
        Remove a pattern from the exclusion list.

        Args:
            pattern: Pattern to remove
        """
        self.exclude_patterns.discard(pattern)

    def clear_index(self) -> None:
        """Clear the current file index."""
        self.file_index.clear()
        if self.index_path.exists():
            self.index_path.unlink()


if __name__ == "__main__":
    # Test the project manager
    print("Testing Project Manager...")

    pm = ProjectManager()

    # Test setting root folder
    try:
        pm.set_root_folder(".")
        print("✓ Root folder set")
    except ValueError as e:
        print(f"✗ Error: {e}")

    # Test indexing
    try:
        file_index = pm.index_files()
        print(f"✓ Indexed {len(file_index)} files")
    except Exception as e:
        print(f"✗ Error during indexing: {e}")

    # Test getting file list
    py_files = pm.get_file_list(language='python')
    print(f"✓ Found {len(py_files)} Python files")

    # Test project stats
    stats = pm.get_project_stats()
    print(f"✓ Project stats:")
    print(f"  Total files: {stats['total_files']}")
    print(f"  Total size: {stats['total_size_mb']} MB")
    print(f"  Languages: {list(stats['languages'].keys())[:5]}")

    print("\n✓ Project Manager tests complete")
