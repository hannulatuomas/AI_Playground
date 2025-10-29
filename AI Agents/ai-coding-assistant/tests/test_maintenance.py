"""Tests for project maintenance system."""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from src.features.project_lifecycle import ProjectMaintainer


class TestProjectMaintainer(unittest.TestCase):
    """Test ProjectMaintainer functionality."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.maintainer = ProjectMaintainer(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_detect_project_type_python(self):
        """Test Python project type detection."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask==2.0.0")
        
        project_type = self.maintainer._detect_project_type(project)
        
        self.assertEqual(project_type, "python")
    
    def test_detect_project_type_node(self):
        """Test Node project type detection."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{"name": "test"}')
        
        project_type = self.maintainer._detect_project_type(project)
        
        self.assertEqual(project_type, "node")
    
    def test_detect_project_type_dotnet(self):
        """Test .NET project type detection."""
        project = self.temp_dir / "dotnet-project"
        project.mkdir()
        (project / "App.csproj").write_text('<Project>')
        
        project_type = self.maintainer._detect_project_type(project)
        
        self.assertEqual(project_type, "dotnet")
    
    def test_detect_project_type_none(self):
        """Test unknown project type."""
        project = self.temp_dir / "unknown"
        project.mkdir()
        
        project_type = self.maintainer._detect_project_type(project)
        
        self.assertIsNone(project_type)
    
    def test_check_outdated_deps_nonexistent_path(self):
        """Test outdated check with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        outdated = self.maintainer.check_outdated_deps(nonexistent)
        
        self.assertEqual(outdated, [])
    
    def test_check_outdated_deps_python(self):
        """Test checking outdated Python packages."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("requests")
        
        # This will call pip, which may or may not find outdated packages
        outdated = self.maintainer.check_outdated_deps(project, project_type="python")
        
        # Should return a list (may be empty if all up to date)
        self.assertIsInstance(outdated, list)
    
    def test_check_outdated_deps_unknown_type(self):
        """Test outdated check with unknown project type."""
        project = self.temp_dir / "unknown"
        project.mkdir()
        
        outdated = self.maintainer.check_outdated_deps(project, project_type="unknown")
        
        self.assertEqual(outdated, [])
    
    def test_scan_vulnerabilities_nonexistent_path(self):
        """Test vulnerability scan with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        vulns = self.maintainer.scan_vulnerabilities(nonexistent)
        
        self.assertEqual(vulns, [])
    
    def test_scan_vulnerabilities_python(self):
        """Test scanning Python vulnerabilities."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("requests")
        
        # This will attempt to run safety if available
        vulns = self.maintainer.scan_vulnerabilities(project, project_type="python")
        
        # Should return a list (may be empty if no vulns or safety not installed)
        self.assertIsInstance(vulns, list)
    
    def test_scan_vulnerabilities_unknown_type(self):
        """Test vulnerability scan with unknown project type."""
        project = self.temp_dir / "unknown"
        project.mkdir()
        
        vulns = self.maintainer.scan_vulnerabilities(project, project_type="unknown")
        
        self.assertEqual(vulns, [])
    
    def test_analyze_code_health_python(self):
        """Test code health analysis for Python project."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")
        
        # Create some Python files
        (project / "main.py").write_text("print('hello')\n")
        (project / "utils.py").write_text("def func():\n    pass\n")
        
        health = self.maintainer.analyze_code_health(project, project_type="python")
        
        self.assertIsInstance(health, dict)
        self.assertEqual(health["project_type"], "python")
        self.assertEqual(health["file_count"], 2)
        self.assertGreater(health["line_count"], 0)
    
    def test_analyze_code_health_node(self):
        """Test code health analysis for Node project."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{}')
        
        # Create some JS files
        (project / "index.js").write_text("console.log('hello');\n")
        
        health = self.maintainer.analyze_code_health(project, project_type="node")
        
        self.assertIsInstance(health, dict)
        self.assertEqual(health["project_type"], "node")
        self.assertEqual(health["file_count"], 1)
        self.assertGreater(health["line_count"], 0)
    
    def test_analyze_code_health_dotnet(self):
        """Test code health analysis for .NET project."""
        project = self.temp_dir / "dotnet-project"
        project.mkdir()
        (project / "App.csproj").write_text('<Project>')
        
        # Create some C# files
        (project / "Program.cs").write_text("class Program {}\n")
        
        health = self.maintainer.analyze_code_health(project, project_type="dotnet")
        
        self.assertIsInstance(health, dict)
        self.assertEqual(health["project_type"], "dotnet")
        self.assertEqual(health["file_count"], 1)
        self.assertGreater(health["line_count"], 0)
    
    def test_analyze_code_health_nonexistent(self):
        """Test code health with nonexistent path."""
        nonexistent = self.temp_dir / "nonexistent"
        
        health = self.maintainer.analyze_code_health(nonexistent)
        
        self.assertEqual(health, {})
    
    def test_generate_maintenance_report(self):
        """Test generating complete maintenance report."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "requirements.txt").write_text("requests")
        (project / "main.py").write_text("print('hello')\n")
        
        report = self.maintainer.generate_maintenance_report(project)
        
        self.assertIsInstance(report, dict)
        self.assertIn("project_path", report)
        self.assertIn("generated_at", report)
        self.assertIn("project_type", report)
        self.assertIn("summary", report)
        
        # Check summary structure
        summary = report["summary"]
        self.assertIn("outdated_count", summary)
        self.assertIn("vulnerability_count", summary)
        self.assertIn("critical_vulnerabilities", summary)
        self.assertIn("needs_attention", summary)
    
    def test_generate_maintenance_report_selective(self):
        """Test generating report with selective checks."""
        project = self.temp_dir / "test-project"
        project.mkdir()
        (project / "requirements.txt").write_text("requests")
        
        report = self.maintainer.generate_maintenance_report(
            project,
            include_outdated=False,
            include_vulnerabilities=False,
            include_health=True
        )
        
        self.assertIsInstance(report, dict)
        self.assertIn("code_health", report)
        self.assertNotIn("outdated_dependencies", report)
        self.assertNotIn("vulnerabilities", report)
    
    def test_get_update_commands_python(self):
        """Test getting update commands for Python."""
        project = self.temp_dir / "python-project"
        project.mkdir()
        (project / "requirements.txt").write_text("flask")
        
        commands = self.maintainer.get_update_commands(project, project_type="python")
        
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        self.assertTrue(any("pip" in cmd for cmd in commands))
    
    def test_get_update_commands_node(self):
        """Test getting update commands for Node."""
        project = self.temp_dir / "node-project"
        project.mkdir()
        (project / "package.json").write_text('{}')
        
        commands = self.maintainer.get_update_commands(project, project_type="node")
        
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        self.assertTrue(any("npm" in cmd for cmd in commands))
    
    def test_get_update_commands_dotnet(self):
        """Test getting update commands for .NET."""
        project = self.temp_dir / "dotnet-project"
        project.mkdir()
        (project / "App.csproj").write_text('<Project>')
        
        commands = self.maintainer.get_update_commands(project, project_type="dotnet")
        
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0)
        self.assertTrue(any("dotnet" in cmd for cmd in commands))


class TestProjectMaintainerIntegration(unittest.TestCase):
    """Integration tests for ProjectMaintainer."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.maintainer = ProjectMaintainer(verbose=False)
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Cleanup test files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_maintenance_workflow(self):
        """Test complete maintenance workflow."""
        # Create project
        project = self.temp_dir / "full-test"
        project.mkdir()
        (project / "requirements.txt").write_text("requests==2.28.0")
        (project / "main.py").write_text("""
def main():
    print('Hello, World!')

if __name__ == '__main__':
    main()
""")
        
        # Generate full report
        report = self.maintainer.generate_maintenance_report(project)
        
        # Verify report structure
        self.assertIsInstance(report, dict)
        self.assertEqual(report["project_type"], "python")
        self.assertIn("summary", report)
        self.assertIn("code_health", report)
        
        # Verify code health
        health = report["code_health"]
        self.assertEqual(health["file_count"], 1)
        self.assertGreater(health["line_count"], 0)
        
        # Get update commands
        commands = self.maintainer.get_update_commands(project)
        self.assertGreater(len(commands), 0)


if __name__ == "__main__":
    unittest.main()
