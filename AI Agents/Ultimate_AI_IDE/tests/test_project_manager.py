"""
Tests for Project Manager Module
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.modules.project_manager import ProjectManager, ProjectDetector, ProjectScaffolder


class TestProjectDetector:
    """Test ProjectDetector class."""
    
    def test_detect_python_project(self, tmp_path):
        """Test detecting Python project."""
        # Create a simple Python project
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "requirements.txt").write_text("pytest>=7.0.0")
        
        detector = ProjectDetector()
        project_info = detector.detect_project(str(tmp_path))
        
        assert project_info is not None
        assert project_info.language == 'python'
        assert 'requirements.txt' in project_info.config_files
    
    def test_detect_javascript_project(self, tmp_path):
        """Test detecting JavaScript project."""
        # Create a JavaScript project
        (tmp_path / "index.js").write_text("console.log('hello');")
        (tmp_path / "package.json").write_text('{"name": "test"}')
        
        detector = ProjectDetector()
        project_info = detector.detect_project(str(tmp_path))
        
        assert project_info is not None
        assert project_info.language == 'javascript'
        assert 'package.json' in project_info.config_files
    
    def test_detect_react_framework(self, tmp_path):
        """Test detecting React framework."""
        (tmp_path / "App.jsx").write_text("export default function App() {}")
        pkg_json = {
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            }
        }
        import json
        (tmp_path / "package.json").write_text(json.dumps(pkg_json))
        
        detector = ProjectDetector()
        project_info = detector.detect_project(str(tmp_path))
        
        assert project_info is not None
        assert project_info.framework == 'react'
    
    def test_detect_nonexistent_path(self):
        """Test detecting nonexistent path."""
        detector = ProjectDetector()
        project_info = detector.detect_project("/nonexistent/path")
        
        assert project_info is None


class TestProjectScaffolder:
    """Test ProjectScaffolder class."""
    
    def test_create_python_project(self, tmp_path):
        """Test creating Python project."""
        scaffolder = ProjectScaffolder()
        
        success = scaffolder.create_project(
            name="test_project",
            language="python",
            framework=None,
            path=str(tmp_path),
            git_init=False
        )
        
        assert success is True
        
        project_path = tmp_path / "test_project"
        assert project_path.exists()
        assert (project_path / "src").exists()
        assert (project_path / "tests").exists()
        assert (project_path / "requirements.txt").exists()
        assert (project_path / "README.md").exists()
    
    def test_create_fastapi_project(self, tmp_path):
        """Test creating FastAPI project."""
        scaffolder = ProjectScaffolder()
        
        success = scaffolder.create_project(
            name="api_project",
            language="python",
            framework="fastapi",
            path=str(tmp_path),
            git_init=False
        )
        
        assert success is True
        
        project_path = tmp_path / "api_project"
        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "src" / "api").exists()
        
        # Check FastAPI in requirements
        req_content = (project_path / "requirements.txt").read_text()
        assert "fastapi" in req_content
    
    def test_create_react_project(self, tmp_path):
        """Test creating React project."""
        scaffolder = ProjectScaffolder()
        
        success = scaffolder.create_project(
            name="react_app",
            language="javascript",
            framework="react",
            path=str(tmp_path),
            git_init=False
        )
        
        assert success is True
        
        project_path = tmp_path / "react_app"
        assert (project_path / "src").exists()
        assert (project_path / "public").exists()
        assert (project_path / "package.json").exists()
    
    def test_create_duplicate_project(self, tmp_path):
        """Test creating duplicate project raises error."""
        scaffolder = ProjectScaffolder()
        
        # Create first project
        scaffolder.create_project(
            name="duplicate",
            language="python",
            framework=None,
            path=str(tmp_path),
            git_init=False
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError):
            scaffolder.create_project(
                name="duplicate",
                language="python",
                framework=None,
                path=str(tmp_path),
                git_init=False
            )


class TestProjectManager:
    """Test ProjectManager class."""
    
    def test_create_project(self, tmp_path):
        """Test creating project through manager."""
        manager = ProjectManager()
        
        project_info = manager.create_project(
            name="managed_project",
            language="python",
            framework=None,
            path=str(tmp_path),
            git_init=False
        )
        
        assert project_info is not None
        assert project_info.name == "managed_project"
        assert project_info.language == "python"
    
    def test_detect_project(self, tmp_path):
        """Test detecting project through manager."""
        # Create a project first
        (tmp_path / "main.py").write_text("print('test')")
        
        manager = ProjectManager()
        project_info = manager.detect_project(str(tmp_path))
        
        assert project_info is not None
        assert project_info.language == "python"
    
    def test_maintain_project(self, tmp_path):
        """Test project maintenance."""
        # Create a project
        (tmp_path / "main.py").write_text("print('test')")
        
        manager = ProjectManager()
        report = manager.maintain_project(str(tmp_path))
        
        assert report['success'] is True
        assert 'issues' in report
        assert 'suggestions' in report
        
        # Should have issues (missing README, etc.)
        assert len(report['issues']) > 0
    
    def test_maintain_invalid_project(self):
        """Test maintaining invalid project."""
        manager = ProjectManager()
        report = manager.maintain_project("/nonexistent")
        
        assert report['success'] is False
        assert 'error' in report
