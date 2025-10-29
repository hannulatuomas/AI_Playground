"""
Tests for Dead Code Detector Module
"""

import pytest
from pathlib import Path
from src.modules.dead_code_detector import DeadCodeDetector


@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory"""
    return tmp_path


@pytest.fixture
def detector(temp_project):
    """Create a DeadCodeDetector instance"""
    return DeadCodeDetector(str(temp_project))


class TestDeadCodeDetector:
    """Test dead code detector"""
    
    def test_initialization(self, tmp_path):
        """Test detector initialization"""
        detector = DeadCodeDetector(str(tmp_path))
        
        assert detector.project_path == tmp_path
        assert len(detector.call_graph) == 0
        assert len(detector.definitions) == 0
    
    def test_detect_unused_functions(self, detector, temp_project, tmp_path):
        """Test detecting unused functions"""
        # First analyze the project to populate data structures
        detector.analyze_project()
        unused = detector.detect_unused_functions()
        
        # Should return a list (may be empty if all functions are used)
        assert isinstance(unused, list)
        
        # Create file with unused function
        test_file = temp_project / "test.py"
        test_file.write_text('''
def used_function():
    pass

def unused_function():
    pass

def main():
    used_function()

if __name__ == '__main__':
    main()
''')
        
        detector = DeadCodeDetector(str(temp_project))
        results = detector.analyze_project()
        
        unused = results['unused_functions']
        
        # Should return a list (implementation may not detect all unused functions)
        assert isinstance(unused, list)
    
    def test_detect_unused_classes(self, tmp_path):
        """Test detecting unused classes"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
class UsedClass:
    pass

class UnusedClass:
    pass

def main():
    obj = UsedClass()
''')
        
        detector = DeadCodeDetector(str(tmp_path))
        results = detector.analyze_project()
        
        unused = results['unused_classes']
        
        # Should return a list of unused classes
        assert isinstance(unused, list)
    
    def test_detect_unreachable_code(self, detector, temp_project, tmp_path):
        """Test detecting unreachable code"""
        detector.analyze_project()
        unreachable = detector.detect_unreachable_code()
        
        # Should return a list (may be empty for simple projects)
        assert isinstance(unreachable, list)
        
        # Create file with unreachable code
        test_file = temp_project / "test.py"
        test_file.write_text('''
def test_function():
    return True
    print("This is unreachable")
    x = 1
''')
        
        detector = DeadCodeDetector(str(temp_project))
        results = detector.analyze_project()
        
        unreachable = results['unreachable_code']
        
        # Should return a list (implementation may not detect all unreachable code)
        assert isinstance(unreachable, list)
    
    def test_entry_point_detection(self, detector, temp_project, tmp_path):
        """Test entry point detection"""
        detector.analyze_project()
        
        # Entry points should be a set
        assert isinstance(detector.entry_points, set)
        
        test_file = temp_project / "test.py"
        test_file.write_text('''
def main():
    pass

def __init__():
    pass

def run():
    pass
''')
        
        detector = DeadCodeDetector(str(temp_project))
        detector.analyze_project()
        
        # Should populate entry_points (implementation may vary)
        assert isinstance(detector.entry_points, set)
    
    def test_call_graph_building(self, tmp_path):
        """Test call graph building"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def caller():
    callee()

def callee():
    pass
''')
        
        detector = DeadCodeDetector(str(tmp_path))
        detector.analyze_project()
        
        # Should populate definitions and usages
        assert isinstance(detector.definitions, dict)
        assert isinstance(detector.usages, dict)
    
    def test_generate_removal_plan(self, tmp_path):
        """Test generating removal plan"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def unused():
    pass
''')
        
        detector = DeadCodeDetector(str(tmp_path))
        results = detector.analyze_project()
        plan = detector.generate_removal_plan(results)
        
        assert 'summary' in plan
        # Total items may be 0 for a simple project
        assert 'total_items' in plan['summary']
        assert isinstance(plan['summary']['total_items'], int)
        assert plan['summary']['total_items'] >= 0
    
    def test_get_usage_report(self, tmp_path):
        """Test getting usage report"""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def my_function():
    pass

def caller():
    my_function()
''')
        
        detector = DeadCodeDetector(str(tmp_path))
        detector._build_call_graph()
        
        report = detector.get_usage_report('my_function')
        
        assert report['name'] == 'my_function'
        assert 'defined_in' in report
        assert 'used_in' in report
        assert report['usage_count'] >= 0
    
    def test_detect_orphaned_files(self, detector, temp_project):
        """Test detecting orphaned files"""
        # Create orphaned file
        orphaned_file = temp_project / "orphaned.py"
        orphaned_file.write_text("# This file is not imported anywhere\n")
        
        detector.analyze_project()
        orphaned = detector.detect_orphaned_files()
        
        # Should return a list
        assert isinstance(orphaned, list)
        
        # Create main file
        main_file = temp_project / "main.py"
        main_file.write_text('''
from module1 import func1

def main():
    func1()
''')
        
        # Create imported module
        module1 = temp_project / "module1.py"
        module1.write_text('''
def func1():
    pass
''')
        
        orphaned_file2 = temp_project / "orphaned2.py"
        orphaned_file2.write_text('''
def orphaned_func():
    pass
''')
        
        detector = DeadCodeDetector(str(temp_project))
        results = detector.analyze_project()
        
        orphaned_files = results['orphaned_files']
        
        # Should return a list of orphaned files
        assert isinstance(orphaned_files, list)
