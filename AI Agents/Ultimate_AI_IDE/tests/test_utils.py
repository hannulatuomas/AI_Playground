"""
Tests for Utility Functions
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.utils.file_ops import (
    ensure_dir, read_file, write_file, copy_file, delete_file,
    list_files, get_file_size, file_exists, dir_exists
)
from src.utils.path_utils import (
    normalize_path, get_relative_path, join_paths, get_parent_dir,
    get_filename, get_extension, change_extension, is_subpath,
    sanitize_filename, get_size_str
)
from src.utils.validators import (
    validate_project_name, validate_path, validate_language,
    validate_email, validate_url, validate_version, validate_identifier
)


class TestFileOps:
    """Test file operations."""
    
    def test_ensure_dir(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "test", "nested", "dir")
            result = ensure_dir(test_dir)
            assert result.exists()
            assert result.is_dir()
    
    def test_read_write_file(self):
        """Test reading and writing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            content = "Hello, World!"
            
            # Write
            assert write_file(file_path, content)
            
            # Read
            read_content = read_file(file_path)
            assert read_content == content
    
    def test_copy_file(self):
        """Test file copying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "source.txt")
            dst = os.path.join(tmpdir, "dest.txt")
            
            write_file(src, "test content")
            assert copy_file(src, dst)
            assert file_exists(dst)
            assert read_file(dst) == "test content"
    
    def test_delete_file(self):
        """Test file deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            write_file(file_path, "test")
            
            assert file_exists(file_path)
            assert delete_file(file_path)
            assert not file_exists(file_path)
    
    def test_list_files(self):
        """Test listing files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            for i in range(3):
                write_file(os.path.join(tmpdir, f"test{i}.txt"), "content")
            
            files = list_files(tmpdir, "*.txt")
            assert len(files) == 3
    
    def test_get_file_size(self):
        """Test getting file size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.txt")
            content = "Hello"
            write_file(file_path, content)
            
            size = get_file_size(file_path)
            assert size == len(content)


class TestPathUtils:
    """Test path utilities."""
    
    def test_normalize_path(self):
        """Test path normalization."""
        path = normalize_path("./test/../file.txt")
        assert Path(path).is_absolute()
    
    def test_join_paths(self):
        """Test joining paths."""
        result = join_paths("dir1", "dir2", "file.txt")
        assert "dir1" in result
        assert "file.txt" in result
    
    def test_get_parent_dir(self):
        """Test getting parent directory."""
        path = "/path/to/file.txt"
        parent = get_parent_dir(path)
        assert parent.endswith("to")
        
        grandparent = get_parent_dir(path, levels=2)
        assert grandparent.endswith("path")
    
    def test_get_filename(self):
        """Test getting filename."""
        path = "/path/to/file.txt"
        
        with_ext = get_filename(path, with_extension=True)
        assert with_ext == "file.txt"
        
        without_ext = get_filename(path, with_extension=False)
        assert without_ext == "file"
    
    def test_get_extension(self):
        """Test getting file extension."""
        assert get_extension("file.txt") == ".txt"
        assert get_extension("file.tar.gz") == ".gz"
        assert get_extension("file") == ""
    
    def test_change_extension(self):
        """Test changing file extension."""
        result = change_extension("file.txt", ".md")
        assert result.endswith(".md")
        
        result = change_extension("file.txt", "py")
        assert result.endswith(".py")
    
    def test_is_subpath(self):
        """Test checking if path is subpath."""
        with tempfile.TemporaryDirectory() as tmpdir:
            parent = tmpdir
            child = os.path.join(tmpdir, "subdir", "file.txt")
            
            assert is_subpath(child, parent)
            assert not is_subpath(parent, child)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        dirty = "file<name>:with|bad*chars?.txt"
        clean = sanitize_filename(dirty)
        
        assert "<" not in clean
        assert ">" not in clean
        assert ":" not in clean
        assert "|" not in clean
        assert "*" not in clean
        assert "?" not in clean
    
    def test_get_size_str(self):
        """Test human-readable size string."""
        assert "B" in get_size_str(100)
        assert "KB" in get_size_str(2048)
        assert "MB" in get_size_str(2 * 1024 * 1024)


class TestValidators:
    """Test validation functions."""
    
    def test_validate_project_name(self):
        """Test project name validation."""
        assert validate_project_name("my_project")
        assert validate_project_name("project-123")
        assert not validate_project_name("")
        assert not validate_project_name("project with spaces")
        assert not validate_project_name("project@#$")
    
    def test_validate_path(self):
        """Test path validation."""
        assert validate_path("/some/path")
        assert validate_path("relative/path")
        assert not validate_path("")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            assert validate_path(tmpdir, must_exist=True)
            assert not validate_path("/nonexistent/path", must_exist=True)
    
    def test_validate_language(self):
        """Test language validation."""
        assert validate_language("python")
        assert validate_language("javascript")
        assert validate_language("PYTHON")  # Case insensitive
        assert not validate_language("invalid_lang")
    
    def test_validate_email(self):
        """Test email validation."""
        assert validate_email("user@example.com")
        assert validate_email("test.user@domain.co.uk")
        assert not validate_email("invalid.email")
        assert not validate_email("@example.com")
        assert not validate_email("user@")
    
    def test_validate_url(self):
        """Test URL validation."""
        assert validate_url("http://example.com")
        assert validate_url("https://example.com/path")
        assert not validate_url("not a url")
        assert not validate_url("ftp://example.com")
    
    def test_validate_version(self):
        """Test version validation."""
        assert validate_version("1.0.0")
        assert validate_version("2.3.4")
        assert validate_version("1.0.0-alpha")
        assert not validate_version("1.0")
        assert not validate_version("v1.0.0")
    
    def test_validate_identifier(self):
        """Test identifier validation."""
        assert validate_identifier("valid_name")
        assert validate_identifier("_private")
        assert validate_identifier("name123")
        assert not validate_identifier("123name")
        assert not validate_identifier("invalid-name")
        assert not validate_identifier("invalid name")
