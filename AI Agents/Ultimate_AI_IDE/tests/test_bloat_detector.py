"""
Tests for BloatDetector module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from src.modules.bloat_detector import BloatDetector


@pytest.fixture
def temp_project():
    """Create a temporary project directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def project_with_bloat(temp_project):
    """Create a project with various types of bloat."""
    # Create unnecessary files
    (temp_project / '.DS_Store').touch()
    (temp_project / 'Thumbs.db').touch()
    
    # Create example code
    (temp_project / 'example_code.py').write_text('# Example code\nprint("example")')
    (temp_project / 'sample_test.py').write_text('# Sample test\npass')
    
    # Create empty file
    (temp_project / 'empty.py').touch()
    
    # Create file with bloat comment
    (temp_project / 'bloat_comment.py').write_text('# TODO: Remove this example\nprint("test")')
    
    # Create requirements.txt with unused dependency
    (temp_project / 'requirements.txt').write_text('requests==2.28.0\nunused-package==1.0.0')
    
    # Create actual code that uses requests
    (temp_project / 'main.py').write_text('import requests\nprint("main")')
    
    return temp_project


class TestBloatDetector:
    """Test BloatDetector functionality."""
    
    def test_init(self, temp_project):
        """Test BloatDetector initialization."""
        detector = BloatDetector(str(temp_project))
        assert detector.project_path == temp_project
        assert detector.bloat_items == []
    
    def test_detect_unnecessary_files(self, project_with_bloat):
        """Test detection of unnecessary files."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_unnecessary_files()
        
        assert len(results) == 2  # .DS_Store and Thumbs.db
        file_names = [r['path'] for r in results]
        assert any('.DS_Store' in f for f in file_names)
        assert any('Thumbs.db' in f for f in file_names)
    
    def test_detect_example_code(self, project_with_bloat):
        """Test detection of example code."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_example_code()
        
        assert len(results) >= 2  # example_code.py and sample_test.py
        file_names = [r['path'] for r in results]
        assert any('example_code.py' in f for f in file_names)
        assert any('sample_test.py' in f for f in file_names)
    
    def test_detect_empty_files(self, project_with_bloat):
        """Test detection of empty files."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_empty_files()
        
        assert len(results) >= 1
        assert any('empty.py' in r['path'] for r in results)
    
    def test_detect_bloat_comments(self, project_with_bloat):
        """Test detection of bloat comments."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_bloat_comments()
        
        assert len(results) >= 1
        assert any('bloat_comment.py' in r['path'] for r in results)
        assert any('TODO: Remove this example' in r['comment'] for r in results)
    
    def test_detect_unused_dependencies(self, project_with_bloat):
        """Test detection of unused dependencies."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_unused_dependencies()
        
        # Should detect unused-package but not requests
        assert len(results) >= 1
        assert any('unused-package' in r['name'] for r in results)
        assert not any('requests' in r['name'] for r in results)
    
    def test_detect_all(self, project_with_bloat):
        """Test comprehensive bloat detection."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_all()
        
        assert 'unnecessary_files' in results
        assert 'example_code' in results
        assert 'unused_dependencies' in results
        assert 'empty_files' in results
        assert 'bloat_comments' in results
        
        total_items = sum(len(items) for items in results.values())
        assert total_items > 0
    
    def test_generate_cleanup_plan(self, project_with_bloat):
        """Test cleanup plan generation."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_all()
        plan = detector.generate_cleanup_plan(results)
        
        assert 'summary' in plan
        assert 'actions' in plan
        assert plan['summary']['total_items'] > 0
        assert len(plan['actions']) > 0
        
        # Check risk assessment
        for action in plan['actions']:
            assert 'risk' in action
            assert action['risk'] in ['low', 'medium', 'high']
    
    def test_execute_cleanup_low_risk(self, project_with_bloat):
        """Test execution of low-risk cleanup."""
        detector = BloatDetector(str(project_with_bloat))
        results = detector.detect_all()
        plan = detector.generate_cleanup_plan(results)
        
        # Execute only low-risk items
        execution_results = detector.execute_cleanup(plan, auto_approve_low_risk=True)
        
        assert 'executed' in execution_results
        assert 'skipped' in execution_results
        assert 'failed' in execution_results
        
        # Should have executed some low-risk items
        assert execution_results['executed'] > 0
    
    def test_no_bloat_detection(self, temp_project):
        """Test detection on clean project."""
        # Create a clean project
        (temp_project / 'clean.py').write_text('import os\nprint("clean")')
        
        detector = BloatDetector(str(temp_project))
        results = detector.detect_all()
        
        # Should find minimal or no bloat
        total_items = sum(len(items) for items in results.values())
        assert total_items == 0 or total_items < 3  # Allow for minor detections


class TestBloatDetectorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_nonexistent_project(self):
        """Test with nonexistent project path."""
        detector = BloatDetector('/nonexistent/path')
        # Should not crash, just return empty results
        results = detector.detect_all()
        assert isinstance(results, dict)
    
    def test_empty_project(self, temp_project):
        """Test with empty project."""
        detector = BloatDetector(str(temp_project))
        results = detector.detect_all()
        
        total_items = sum(len(items) for items in results.values())
        assert total_items == 0
    
    def test_nested_directories(self, temp_project):
        """Test detection in nested directories."""
        nested = temp_project / 'src' / 'nested'
        nested.mkdir(parents=True)
        (nested / 'example.py').write_text('# Example\npass')
        
        detector = BloatDetector(str(temp_project))
        results = detector.detect_example_code()
        
        assert len(results) >= 1
        assert any('example.py' in r['path'] for r in results)
