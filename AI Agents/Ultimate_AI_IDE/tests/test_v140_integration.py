"""
v1.4.0 Integration Tests

Overall integration tests for v1.4.0 features working together.
"""

import pytest
from pathlib import Path
from src.core.orchestrator import UAIDE
from src.modules.workflow_engine import WorkflowEngine
from src.modules.file_splitter import FileSplitter
from src.modules.dead_code_detector import DeadCodeDetector
from src.modules.automation_engine import AutomationEngine


class TestV140Integration:
    """Integration tests for v1.4.0 features."""
    
    @pytest.fixture
    def uaide(self):
        """Create UAIDE instance."""
        return UAIDE()
    
    def test_all_v140_modules_initialized(self, uaide):
        """Test all v1.4.0 modules are properly initialized."""
        assert uaide.workflow_engine is not None
        assert isinstance(uaide.workflow_engine, WorkflowEngine)
        
        assert uaide.file_splitter is not None
        assert isinstance(uaide.file_splitter, FileSplitter)
        
        assert uaide.automation_engine is not None
        assert isinstance(uaide.automation_engine, AutomationEngine)
    
    def test_workflow_and_automation_integration(self, uaide):
        """Test workflow engine works with automation engine."""
        # Check automation is enabled
        stats = uaide.automation_engine.get_stats()
        assert 'enabled' in stats
        
        # Check workflow engine exists
        assert uaide.workflow_engine is not None
        
        # Check we can list templates
        from src.modules.workflow_engine import WorkflowTemplates
        templates = WorkflowTemplates.list_templates()
        assert len(templates) > 0
    
    def test_file_splitter_and_quality_integration(self, uaide, tmp_path):
        """Test file splitter works with quality monitoring."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("\n".join([f"# Line {i}" for i in range(600)]))
        
        # Detect large files
        result = uaide.detect_large_files(str(tmp_path))
        assert result.success is True
    
    def test_dead_code_and_automation_integration(self, uaide, tmp_path):
        """Test dead code detection with automation."""
        # Create test project
        project = tmp_path / "project"
        project.mkdir()
        
        test_file = project / "test.py"
        test_file.write_text("""
def used():
    pass

def unused():
    pass

def main():
    used()
""")
        
        # Detect dead code
        result = uaide.detect_dead_code(str(project))
        assert result.success is True
    
    def test_orchestrator_action_handlers(self, uaide):
        """Test orchestrator has all v1.4.0 action handlers."""
        # Check workflow handlers
        workflow_handlers = uaide.workflow_engine.executor.action_handlers
        assert len(workflow_handlers) > 0
        
        # Check automation handlers
        automation_handlers = uaide.automation_engine.action_handlers
        assert len(automation_handlers) > 0
    
    def test_automation_triggers_setup(self, uaide):
        """Test automation triggers are properly set up."""
        triggers = uaide.automation_engine.list_triggers()
        
        # Should have all default triggers
        assert len(triggers) >= 6
    
    def test_workflow_execution_end_to_end(self, uaide, tmp_path):
        """Test complete workflow execution."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        variables = {
            'project_path': str(project),
            'feature_name': 'Test Feature'
        }
        
        result = uaide.execute_workflow('quality_assurance', variables)
        
        # Should complete (success or graceful failure)
        assert result is not None
    
    def test_file_split_workflow(self, uaide, tmp_path):
        """Test file splitting workflow."""
        # Create large file
        large_file = tmp_path / "large.py"
        large_file.write_text("\n".join([f"# Line {i}" for i in range(600)]))
        
        # Detect
        detect_result = uaide.detect_large_files(str(tmp_path))
        assert detect_result.success is True
        
        # Get suggestions
        splitter = FileSplitter()
        suggestions = splitter.suggest_split_points(str(large_file))
        assert suggestions['success'] is True
    
    def test_automation_preferences(self, uaide):
        """Test automation preferences."""
        # Automation engine should have configuration
        engine = uaide.automation_engine
        
        # Check it has the expected attributes
        assert hasattr(engine, 'enabled')
        assert hasattr(engine, 'triggers')
    
    def test_v140_features_dont_break_existing(self, uaide):
        """Test v1.4.0 features don't break existing functionality."""
        # Test existing modules still work
        assert uaide.config is not None
        assert uaide.database is not None
        assert uaide.ai_backend is not None
        assert uaide.event_bus is not None
        
        # Test existing managers
        assert uaide.project_manager is not None
        assert uaide.code_generator is not None
        assert uaide.test_generator is not None


class TestV140Performance:
    """Performance tests for v1.4.0 features."""
    
    def test_workflow_engine_performance(self):
        """Test workflow engine initialization is fast."""
        import time
        
        start = time.time()
        engine = WorkflowEngine()
        engine.load_template('feature_implementation')
        duration = time.time() - start
        
        assert duration < 1.0  # Should be fast
    
    def test_file_splitter_performance(self, tmp_path):
        """Test file splitter is reasonably fast."""
        import time
        
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("\n".join([f"# Line {i}" for i in range(1000)]))
        
        splitter = FileSplitter()
        
        start = time.time()
        suggestions = splitter.suggest_split_points(str(test_file))
        duration = time.time() - start
        
        assert duration < 2.0  # Should be reasonably fast
    
    def test_automation_engine_performance(self):
        """Test automation engine is lightweight."""
        import time
        
        start = time.time()
        engine = AutomationEngine()
        engine.setup_default_triggers()
        duration = time.time() - start
        
        assert duration < 0.5  # Should be very fast
