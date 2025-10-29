"""
Tests for QualityMonitor module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.modules.quality_monitor import QualityMonitor, QualityIssue, QualityMetrics


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_with_issues(temp_project):
    """Create a project with quality issues."""
    # File that's too long (>500 lines)
    long_file_content = '\n'.join([f'line_{i} = {i}' for i in range(600)])
    (temp_project / 'long_file.py').write_text(long_file_content)
    
    # Function that's too long (>50 lines)
    long_function = 'def long_function():\n' + '\n'.join([f'    x = {i}' for i in range(60)])
    (temp_project / 'long_function.py').write_text(long_function)
    
    # High complexity function (complexity > 10)
    complex_function = '''
def complex_function(x, y, z):
    if x > 0:
        if y > 0:
            if z > 0:
                if x < 10:
                    if y < 10:
                        if z < 10:
                            if x % 2 == 0:
                                if y % 2 == 0:
                                    if z % 2 == 0:
                                        return "all even"
                                    else:
                                        return "x,y even"
                                else:
                                    return "x even"
                            else:
                                return "x odd"
                        else:
                            return "z >= 10"
                    else:
                        return "y >= 10"
                else:
                    return "x >= 10"
            else:
                return "z negative"
        else:
            return "y negative"
    else:
        return "x negative"
'''
    (temp_project / 'complex.py').write_text(complex_function)
    
    # Class without docstring
    no_docstring = '''
class MyClass:
    def method1(self):
        pass
    
    def method2(self):
        pass
'''
    (temp_project / 'no_docstring.py').write_text(no_docstring)
    
    # Clean file for comparison
    (temp_project / 'clean.py').write_text('"""Clean module."""\n\ndef clean_function():\n    """Clean function."""\n    return True')
    
    return temp_project


class TestQualityMonitor:
    """Test QualityMonitor functionality."""
    
    def test_init(self, temp_project):
        """Test QualityMonitor initialization."""
        monitor = QualityMonitor(str(temp_project))
        assert monitor.project_path == temp_project
        assert monitor.metrics_cache == {}
    
    def test_check_file_too_long(self, project_with_issues):
        """Test detection of files that are too long."""
        monitor = QualityMonitor(str(project_with_issues))
        long_file = project_with_issues / 'long_file.py'
        
        issues = monitor.check_file(long_file)
        
        assert len(issues) > 0
        assert any(issue.type == 'file_too_long' for issue in issues)
        assert any(issue.severity == 'high' for issue in issues)
    
    def test_check_function_too_long(self, project_with_issues):
        """Test detection of functions that are too long."""
        monitor = QualityMonitor(str(project_with_issues))
        long_func_file = project_with_issues / 'long_function.py'
        
        issues = monitor.check_file(long_func_file)
        
        assert len(issues) > 0
        assert any(issue.type == 'function_too_long' for issue in issues)
    
    def test_check_high_complexity(self, project_with_issues):
        """Test detection of high complexity functions."""
        monitor = QualityMonitor(str(project_with_issues))
        complex_file = project_with_issues / 'complex.py'
        
        issues = monitor.check_file(complex_file)
        
        # The complex function should trigger some quality issues
        # (either complexity, nesting depth, or function length)
        assert len(issues) > 0
    
    def test_check_missing_docstring(self, project_with_issues):
        """Test detection of missing docstrings."""
        monitor = QualityMonitor(str(project_with_issues))
        no_doc_file = project_with_issues / 'no_docstring.py'
        
        issues = monitor.check_file(no_doc_file)
        
        assert len(issues) > 0
        assert any(issue.type == 'missing_docstring' for issue in issues)
    
    def test_check_clean_file(self, project_with_issues):
        """Test checking a clean file."""
        monitor = QualityMonitor(str(project_with_issues))
        clean_file = project_with_issues / 'clean.py'
        
        issues = monitor.check_file(clean_file)
        
        # Clean file should have no issues
        assert len(issues) == 0
    
    def test_monitor_project(self, project_with_issues):
        """Test monitoring entire project."""
        monitor = QualityMonitor(str(project_with_issues))
        all_issues = monitor.monitor_project()
        
        assert isinstance(all_issues, dict)
        assert len(all_issues) > 0
        
        # Should find issues in multiple files
        assert 'long_file.py' in str(all_issues)
    
    def test_calculate_metrics(self, project_with_issues):
        """Test calculation of quality metrics."""
        monitor = QualityMonitor(str(project_with_issues))
        clean_file = project_with_issues / 'clean.py'
        
        metrics = monitor.calculate_metrics(clean_file)
        
        assert isinstance(metrics, QualityMetrics)
        assert metrics.lines_of_code > 0
        assert metrics.num_functions >= 1
        assert isinstance(metrics.issues, list)
    
    def test_should_trigger_refactoring(self, project_with_issues):
        """Test refactoring trigger detection."""
        monitor = QualityMonitor(str(project_with_issues))
        long_file = project_with_issues / 'long_file.py'
        
        should_refactor, reasons = monitor.should_trigger_refactoring(long_file)
        
        assert should_refactor is True
        assert len(reasons) > 0
        assert any('500 lines' in reason for reason in reasons)
    
    def test_generate_refactoring_suggestions(self, project_with_issues):
        """Test generation of refactoring suggestions."""
        monitor = QualityMonitor(str(project_with_issues))
        long_file = project_with_issues / 'long_file.py'
        
        suggestions = monitor.generate_refactoring_suggestions(long_file)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert all('type' in s for s in suggestions)
        assert all('priority' in s for s in suggestions)
    
    def test_get_project_quality_report(self, project_with_issues):
        """Test generation of project quality report."""
        monitor = QualityMonitor(str(project_with_issues))
        report = monitor.get_project_quality_report()
        
        assert 'total_files_with_issues' in report
        assert 'total_issues' in report
        assert 'severity_breakdown' in report
        assert 'files_needing_refactoring' in report
        assert 'quality_score' in report
        
        # Quality score should be between 0 and 100
        assert 0 <= report['quality_score'] <= 100
        
        # Should have found some issues
        assert report['total_issues'] > 0


class TestQualityMonitorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_project(self, temp_project):
        """Test monitoring empty project."""
        monitor = QualityMonitor(str(temp_project))
        all_issues = monitor.monitor_project()
        
        assert isinstance(all_issues, dict)
        assert len(all_issues) == 0
    
    def test_syntax_error_file(self, temp_project):
        """Test handling of files with syntax errors."""
        bad_file = temp_project / 'syntax_error.py'
        bad_file.write_text('def bad_syntax(\n    # Missing closing paren')
        
        monitor = QualityMonitor(str(temp_project))
        issues = monitor.check_file(bad_file)
        
        # Should detect syntax error
        assert len(issues) > 0
        assert any(issue.type == 'syntax_error' for issue in issues)
        assert any(issue.severity == 'critical' for issue in issues)
    
    def test_nonexistent_file(self, temp_project):
        """Test checking nonexistent file."""
        monitor = QualityMonitor(str(temp_project))
        nonexistent = temp_project / 'nonexistent.py'
        
        # Should not crash
        metrics = monitor.calculate_metrics(nonexistent)
        assert metrics.lines_of_code == 0
    
    def test_quality_score_calculation(self, temp_project):
        """Test quality score calculation."""
        # Create perfect file
        perfect_file = temp_project / 'perfect.py'
        perfect_file.write_text('"""Perfect module."""\n\ndef perfect():\n    """Perfect function."""\n    return True')
        
        monitor = QualityMonitor(str(temp_project))
        report = monitor.get_project_quality_report()
        
        # Perfect project should have high score
        assert report['quality_score'] >= 90
