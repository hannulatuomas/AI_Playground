"""Tests for project archiving system."""

import unittest
import tempfile
import shutil
import zipfile
import tarfile
from pathlib import Path

from src.features.project_lifecycle import ProjectArchiver


class TestProjectArchiver(unittest.TestCase):
    """Test ProjectArchiver functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.archiver = ProjectArchiver(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_generate_full_docs(self):
        """Test documentation generation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "main.py").write_text("print('hello')")
        
        success, message = self.archiver.generate_full_docs(project)
        
        self.assertTrue(success)
        self.assertTrue((project / "docs").exists())
        self.assertTrue((project / "docs" / "API.md").exists())
        self.assertTrue((project / "docs" / "PROJECT_STRUCTURE.md").exists())
        self.assertTrue((project / "docs" / "USAGE.md").exists())
    
    def test_generate_full_docs_custom_output(self):
        """Test documentation with custom output path."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        output = self.temp_dir / "custom-docs"
        
        success, message = self.archiver.generate_full_docs(project, output)
        
        self.assertTrue(success)
        self.assertTrue(output.exists())
        self.assertTrue((output / "API.md").exists())
    
    def test_generate_full_docs_nonexistent_path(self):
        """Test documentation with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, message = self.archiver.generate_full_docs(nonexistent)
        
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_create_archive_zip(self):
        """Test ZIP archive creation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "file1.txt").write_text("content1")
        (project / "file2.txt").write_text("content2")
        
        success, archive_path, message = self.archiver.create_archive(
            project,
            format="zip"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(archive_path)
        self.assertTrue(archive_path.exists())
        self.assertTrue(archive_path.suffix == ".zip")
        
        # Verify archive contents
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            names = zipf.namelist()
            self.assertTrue(any("file1.txt" in name for name in names))
            self.assertTrue(any("file2.txt" in name for name in names))
    
    def test_create_archive_targz(self):
        """Test tar.gz archive creation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "file1.txt").write_text("content1")
        
        success, archive_path, message = self.archiver.create_archive(
            project,
            format="tar.gz"
        )
        
        self.assertTrue(success)
        self.assertIsNotNone(archive_path)
        self.assertTrue(archive_path.exists())
        self.assertTrue(str(archive_path).endswith(".tar.gz"))
        
        # Verify archive contents
        with tarfile.open(archive_path, 'r:gz') as tarf:
            names = tarf.getnames()
            self.assertTrue(any("file1.txt" in name for name in names))
    
    def test_create_archive_excludes(self):
        """Test archive creation with exclusions."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "include.txt").write_text("include")
        (project / "exclude.pyc").write_text("exclude")
        
        pycache = project / "__pycache__"
        pycache.mkdir()
        (pycache / "test.pyc").write_text("exclude")
        
        success, archive_path, message = self.archiver.create_archive(
            project,
            format="zip"
        )
        
        self.assertTrue(success)
        
        # Verify exclusions
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            names = zipf.namelist()
            self.assertTrue(any("include.txt" in name for name in names))
            self.assertFalse(any("exclude.pyc" in name for name in names))
            self.assertFalse(any("__pycache__" in name for name in names))
    
    def test_create_archive_invalid_format(self):
        """Test archive with invalid format."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, archive_path, message = self.archiver.create_archive(
            project,
            format="invalid"
        )
        
        self.assertFalse(success)
        self.assertIsNone(archive_path)
        self.assertIn("Unsupported format", message)
    
    def test_create_archive_nonexistent_path(self):
        """Test archive with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, archive_path, message = self.archiver.create_archive(nonexistent)
        
        self.assertFalse(success)
        self.assertIsNone(archive_path)
        self.assertIn("does not exist", message)
    
    def test_generate_changelog_no_git(self):
        """Test changelog generation without git."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, message = self.archiver.generate_changelog(project)
        
        self.assertFalse(success)
        self.assertIn("Not a git repository", message)
    
    def test_generate_changelog_nonexistent_path(self):
        """Test changelog with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, message = self.archiver.generate_changelog(nonexistent)
        
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_generate_release_notes(self):
        """Test release notes generation."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        highlights = ["New feature X", "Bug fix Y", "Performance improvement"]
        
        success, message = self.archiver.generate_release_notes(
            project,
            version="1.2.0",
            highlights=highlights
        )
        
        self.assertTrue(success)
        self.assertTrue((project / "RELEASE_NOTES.md").exists())
        
        # Verify content
        content = (project / "RELEASE_NOTES.md").read_text()
        self.assertIn("1.2.0", content)
        self.assertIn("New feature X", content)
        self.assertIn("Bug fix Y", content)
    
    def test_generate_release_notes_no_highlights(self):
        """Test release notes without highlights."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, message = self.archiver.generate_release_notes(
            project,
            version="1.0.0"
        )
        
        self.assertTrue(success)
        self.assertTrue((project / "RELEASE_NOTES.md").exists())
    
    def test_generate_release_notes_nonexistent_path(self):
        """Test release notes with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, message = self.archiver.generate_release_notes(
            nonexistent,
            version="1.0.0"
        )
        
        self.assertFalse(success)
        self.assertIn("does not exist", message)
    
    def test_bump_version_patch(self):
        """Test patch version bump."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "package.json").write_text('{"version": "1.2.3"}')
        
        success, new_version, message = self.archiver.bump_version(
            project,
            bump_type="patch"
        )
        
        self.assertTrue(success)
        self.assertEqual(new_version, "1.2.4")
        
        # Verify file updated
        content = (project / "package.json").read_text()
        self.assertIn('"version": "1.2.4"', content)
    
    def test_bump_version_minor(self):
        """Test minor version bump."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "package.json").write_text('{"version": "1.2.3"}')
        
        success, new_version, message = self.archiver.bump_version(
            project,
            bump_type="minor"
        )
        
        self.assertTrue(success)
        self.assertEqual(new_version, "1.3.0")
    
    def test_bump_version_major(self):
        """Test major version bump."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "package.json").write_text('{"version": "1.2.3"}')
        
        success, new_version, message = self.archiver.bump_version(
            project,
            bump_type="major"
        )
        
        self.assertTrue(success)
        self.assertEqual(new_version, "2.0.0")
    
    def test_bump_version_setup_py(self):
        """Test version bump in setup.py."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "setup.py").write_text('version="1.0.0"')
        
        success, new_version, message = self.archiver.bump_version(
            project,
            bump_type="patch"
        )
        
        self.assertTrue(success)
        self.assertEqual(new_version, "1.0.1")
        
        content = (project / "setup.py").read_text()
        self.assertIn('version="1.0.1"', content)
    
    def test_bump_version_invalid_type(self):
        """Test version bump with invalid type."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "package.json").write_text('{"version": "1.0.0"}')
        
        success, new_version, message = self.archiver.bump_version(
            project,
            bump_type="invalid"
        )
        
        self.assertFalse(success)
        self.assertIsNone(new_version)
        self.assertIn("Invalid bump type", message)
    
    def test_bump_version_no_version_file(self):
        """Test version bump without version file."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        
        success, new_version, message = self.archiver.bump_version(project)
        
        self.assertFalse(success)
        self.assertIsNone(new_version)
        self.assertIn("Could not detect", message)
    
    def test_bump_version_nonexistent_path(self):
        """Test version bump with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        success, new_version, message = self.archiver.bump_version(nonexistent)
        
        self.assertFalse(success)
        self.assertIsNone(new_version)
        self.assertIn("does not exist", message)


class TestProjectArchiverIntegration(unittest.TestCase):
    """Integration tests for ProjectArchiver."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.archiver = ProjectArchiver(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_archiving_workflow(self):
        """Test complete archiving workflow."""
        # Create project
        project = self.temp_dir / "my-project"
        project.mkdir()
        (project / "package.json").write_text('{"version": "1.0.0"}')
        (project / "main.js").write_text("console.log('hello');")
        (project / "README.md").write_text("# My Project")
        
        # Generate docs
        success, msg = self.archiver.generate_full_docs(project)
        self.assertTrue(success)
        
        # Generate release notes
        success, msg = self.archiver.generate_release_notes(
            project,
            version="1.0.0",
            highlights=["Initial release"]
        )
        self.assertTrue(success)
        
        # Bump version
        success, new_ver, msg = self.archiver.bump_version(project, "minor")
        self.assertTrue(success)
        self.assertEqual(new_ver, "1.1.0")
        
        # Create archive
        success, archive_path, msg = self.archiver.create_archive(project, "zip")
        self.assertTrue(success)
        self.assertIsNotNone(archive_path)
        self.assertTrue(archive_path.exists())
        
        # Verify archive contains everything
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            names = zipf.namelist()
            # Should contain main files and generated docs
            self.assertTrue(any("main.js" in name for name in names))
            self.assertTrue(any("README.md" in name for name in names))
            self.assertTrue(any("RELEASE_NOTES.md" in name for name in names))


if __name__ == "__main__":
    unittest.main()
