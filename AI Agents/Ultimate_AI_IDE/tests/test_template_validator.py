"""
Tests for Template Validator Module

Comprehensive tests for template validation functionality.
"""

import pytest
from pathlib import Path
from src.modules.template_validator import TemplateValidator, ValidationIssue


class TestTemplateValidator:
    """Test template validator."""
    
    def test_validator_initialization(self, tmp_path):
        """Test validator initializes correctly"""
        validator = TemplateValidator(str(tmp_path))
        assert validator.project_path == tmp_path
        assert validator.issues == []
    
    def test_clean_project(self, tmp_path):
        """Test validation of clean project"""
        # Create clean file
        (tmp_path / "app.py").write_text('def hello():\n    return "Hello"\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['is_clean'] is True
        assert result['total_issues'] == 0
        assert validator.get_clean_score() == 100.0
    
    def test_example_code_detection(self, tmp_path):
        """Test detection of example code"""
        (tmp_path / "app.py").write_text('example_data = {"test": "example"}\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
        assert result['summary']['example_code'] > 0
    
    def test_todo_detection(self, tmp_path):
        """Test detection of TODO comments"""
        (tmp_path / "app.py").write_text('# TODO: Implement this function\ndef func():\n    pass\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
        assert result['summary']['todo'] > 0
    
    def test_fixme_detection(self, tmp_path):
        """Test detection of FIXME comments"""
        (tmp_path / "app.py").write_text('# FIXME: This is broken\ndef func():\n    return None\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
        assert result['summary']['todo'] > 0
    
    def test_placeholder_detection(self, tmp_path):
        """Test detection of placeholder implementations"""
        (tmp_path / "app.py").write_text('def func():\n    raise NotImplementedError\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
        assert result['summary']['placeholder'] > 0
    
    def test_pass_placeholder_detection(self, tmp_path):
        """Test detection of pass placeholders"""
        (tmp_path / "app.py").write_text('def func():\n    pass\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
    
    def test_ellipsis_placeholder_detection(self, tmp_path):
        """Test detection of ellipsis placeholders"""
        (tmp_path / "app.py").write_text('def func():\n    ...\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
    
    def test_unnecessary_dependency_detection(self, tmp_path):
        """Test detection of unnecessary dependencies"""
        (tmp_path / "requirements.txt").write_text('requests==2.28.0\nfaker==18.0.0\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] > 0
        assert result['summary']['unused_dependency'] > 0
    
    def test_multiple_issues(self, tmp_path):
        """Test detection of multiple issue types"""
        (tmp_path / "app.py").write_text('''
# TODO: Implement this
def example_function():
    pass

# FIXME: This is broken
def demo_function():
    raise NotImplementedError
''')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        assert result['total_issues'] >= 4  # At least 4 issues
        assert result['summary']['todo'] >= 2
        assert result['summary']['placeholder'] >= 2
    
    def test_cleanliness_score(self, tmp_path):
        """Test cleanliness score calculation"""
        # Clean project
        validator1 = TemplateValidator(str(tmp_path))
        result1 = validator1.validate_project()
        assert validator1.get_clean_score() == 100.0
        
        # Project with issues
        (tmp_path / "app.py").write_text('# TODO: Fix this\ndef func():\n    pass\n')
        validator2 = TemplateValidator(str(tmp_path))
        result2 = validator2.validate_project()
        assert validator2.get_clean_score() < 100.0
    
    def test_severity_levels(self, tmp_path):
        """Test severity classification"""
        (tmp_path / "app.py").write_text('example_data = "test"\n# TODO: implement\ndef func():\n    pass\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        summary = result['summary']
        assert summary['high'] + summary['medium'] + summary['low'] == result['total_issues']
    
    def test_skip_test_directories(self, tmp_path):
        """Test that test directories are skipped"""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_app.py").write_text('# TODO: Write tests\nexample_test = True\n')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        # Should not find issues in test directory
        assert result['is_clean'] is True
    
    def test_valid_pass_usage(self, tmp_path):
        """Test that valid pass usage is not flagged"""
        (tmp_path / "app.py").write_text('''
try:
    do_something()
except Exception:
    pass  # Intentionally ignore
''')
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        # Should not flag pass in except block
        assert result['is_clean'] is True


class TestValidationIssue:
    """Test ValidationIssue dataclass."""
    
    def test_issue_creation(self):
        """Test creating validation issue"""
        issue = ValidationIssue(
            file_path="app.py",
            line_number=10,
            issue_type="todo",
            description="TODO found",
            severity="medium",
            suggestion="Complete the implementation"
        )
        
        assert issue.file_path == "app.py"
        assert issue.line_number == 10
        assert issue.issue_type == "todo"
        assert issue.severity == "medium"
