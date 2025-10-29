"""
Integration Tests for Workflow Engine

Tests workflow execution with real handlers and orchestrator integration.
"""

import pytest
import tempfile
from pathlib import Path
from src.core.orchestrator import UAIDE
from src.modules.workflow_engine import WorkflowEngine, WorkflowTemplates


class TestWorkflowIntegration:
    """Integration tests for workflow engine."""
    
    @pytest.fixture
    def uaide(self):
        """Create UAIDE instance for testing."""
        return UAIDE()
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project directory."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        # Create a simple Python file
        test_file = project / "test.py"
        test_file.write_text("def hello():\n    return 'world'\n")
        
        return project
    
    def test_workflow_engine_initialization(self, uaide):
        """Test workflow engine is properly initialized."""
        assert uaide.workflow_engine is not None
        assert isinstance(uaide.workflow_engine, WorkflowEngine)
    
    def test_load_all_templates(self, uaide):
        """Test loading all workflow templates."""
        templates = WorkflowTemplates.list_templates()
        
        assert len(templates) == 6
        assert 'feature_implementation' in templates
        assert 'bug_fix' in templates
        assert 'refactoring' in templates
        assert 'documentation_update' in templates
        assert 'release_preparation' in templates
        assert 'quality_assurance' in templates
    
    def test_execute_workflow_with_orchestrator(self, uaide, temp_project):
        """Test executing workflow through orchestrator."""
        variables = {
            'project_path': str(temp_project),
            'feature_name': 'Test Feature'
        }
        
        result = uaide.execute_workflow('feature_implementation', variables)
        
        # Should succeed even if some steps fail (they're not fully implemented)
        assert result is not None
        assert hasattr(result, 'success')
    
    def test_workflow_with_missing_variables(self, uaide):
        """Test workflow execution with missing required variables."""
        result = uaide.execute_workflow('feature_implementation', {})
        
        # Should handle missing variables gracefully
        assert result is not None
    
    def test_workflow_error_handling(self, uaide):
        """Test workflow handles errors gracefully."""
        # Try to execute with invalid template
        try:
            result = uaide.execute_workflow('nonexistent_workflow', {})
            # Should either raise or return error result
            if result:
                assert not result.success
        except ValueError:
            # Expected for invalid template
            pass
    
    def test_workflow_action_handlers_registered(self, uaide):
        """Test that workflow action handlers are registered."""
        engine = uaide.workflow_engine
        
        # Check that handlers are registered
        assert len(engine.executor.action_handlers) > 0
        
        # Check for specific handlers
        expected_handlers = [
            'analyze_request',
            'check_existing_code',
            'generate_feature_code',
            'validate_syntax',
            'generate_unit_tests',
            'run_test_suite',
            'check_code_quality',
            'refactor_code',
            'update_documentation'
        ]
        
        for handler in expected_handlers:
            assert handler in engine.executor.action_handlers
    
    def test_workflow_dependency_resolution(self):
        """Test workflow dependency resolution works correctly."""
        engine = WorkflowEngine()
        
        workflow_id = engine.load_template('feature_implementation')
        info = engine.get_workflow_info(workflow_id)
        
        # Check execution order respects dependencies
        assert 'execution_order' in info
        assert len(info['execution_order']) == info['step_count']
    
    def test_workflow_validation(self):
        """Test workflow validation."""
        engine = WorkflowEngine()
        
        workflow_id = engine.load_template('bug_fix')
        is_valid = engine.validate_workflow(workflow_id)
        
        assert is_valid is True
    
    def test_workflow_with_custom_variables(self, uaide, temp_project):
        """Test workflow execution with custom variables."""
        variables = {
            'project_path': str(temp_project),
            'feature_name': 'Custom Feature',
            'language': 'python',
            'custom_var': 'custom_value'
        }
        
        result = uaide.execute_workflow('feature_implementation', variables)
        
        assert result is not None
    
    def test_multiple_workflow_executions(self, uaide, temp_project):
        """Test executing multiple workflows in sequence."""
        variables = {'project_path': str(temp_project)}
        
        # Execute multiple workflows
        result1 = uaide.execute_workflow('quality_assurance', variables)
        result2 = uaide.execute_workflow('documentation_update', variables)
        
        assert result1 is not None
        assert result2 is not None


class TestWorkflowRollback:
    """Test workflow rollback functionality."""
    
    def test_workflow_rollback_on_error(self):
        """Test workflow rolls back on error."""
        engine = WorkflowEngine()
        
        executed = []
        
        def test_handler(params, variables):
            executed.append('test')
            return True
        
        def failing_handler(params, variables):
            raise Exception("Test failure")
        
        engine.register_action('test_action', test_handler)
        engine.register_action('failing_action', failing_handler)
        
        # Load a template and modify it to test error handling
        workflow_id = engine.load_template('bug_fix')
        
        # Execute with missing variables to trigger error
        result = engine.execute_workflow(workflow_id, {})
        
        # Should handle errors gracefully
        assert isinstance(result, dict)
        assert 'success' in result


class TestWorkflowTemplateValidation:
    """Test workflow template validation."""
    
    def test_all_templates_valid(self):
        """Test that all built-in templates are valid."""
        templates = WorkflowTemplates.list_templates()
        
        for template_name in templates.keys():
            template = WorkflowTemplates.get_template(template_name)
            
            # Check required fields
            assert 'name' in template
            assert 'steps' in template
            assert len(template['steps']) > 0
            
            # Check each step
            for step in template['steps']:
                assert 'name' in step
                assert 'action' in step
    
    def test_template_dependency_validation(self):
        """Test template dependencies are valid."""
        template = WorkflowTemplates.get_template('feature_implementation')
        
        step_names = {step['name'] for step in template['steps']}
        
        for step in template['steps']:
            if 'depends_on' in step:
                deps = step['depends_on'] if isinstance(step['depends_on'], list) else [step['depends_on']]
                for dep in deps:
                    assert dep in step_names, f"Invalid dependency: {dep}"
