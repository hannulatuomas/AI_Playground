"""
Tests for Workflow Engine Module
"""

import pytest
import yaml
from pathlib import Path
from src.modules.workflow_engine import (
    WorkflowEngine,
    WorkflowParser,
    WorkflowExecutor,
    WorkflowTemplates
)


class TestWorkflowParser:
    """Test workflow parser"""
    
    def test_parse_yaml_workflow(self):
        """Test parsing YAML workflow"""
        yaml_content = """
name: Test Workflow
description: A test workflow
steps:
  - name: step1
    action: test_action
    params:
      key: value
"""
        parser = WorkflowParser()
        workflow = parser.parse_string(yaml_content, 'yaml')
        
        assert workflow['name'] == 'Test Workflow'
        assert len(workflow['steps']) == 1
        assert workflow['steps'][0]['name'] == 'step1'
    
    def test_parse_json_workflow(self):
        """Test parsing JSON workflow"""
        json_content = '{"name": "Test", "steps": [{"name": "s1", "action": "act"}]}'
        parser = WorkflowParser()
        workflow = parser.parse_string(json_content, 'json')
        
        assert workflow['name'] == 'Test'
        assert len(workflow['steps']) == 1
    
    def test_validate_workflow_missing_name(self):
        """Test validation fails for missing name"""
        parser = WorkflowParser()
        
        with pytest.raises(ValueError, match="Missing required field: name"):
            parser._validate_workflow({'steps': []})
    
    def test_validate_workflow_missing_steps(self):
        """Test validation fails for missing steps"""
        parser = WorkflowParser()
        
        with pytest.raises(ValueError, match="Missing required field: steps"):
            parser._validate_workflow({'name': 'Test'})
    
    def test_validate_dependencies(self):
        """Test dependency validation"""
        parser = WorkflowParser()
        workflow = {
            'name': 'Test',
            'steps': [
                {'name': 'step1', 'action': 'act1'},
                {'name': 'step2', 'action': 'act2', 'depends_on': ['step1']}
            ]
        }
        
        assert parser.validate_dependencies(workflow) is True
    
    def test_detect_circular_dependency(self):
        """Test circular dependency detection"""
        parser = WorkflowParser()
        workflow = {
            'name': 'Test',
            'steps': [
                {'name': 'step1', 'action': 'act1', 'depends_on': ['step2']},
                {'name': 'step2', 'action': 'act2', 'depends_on': ['step1']}
            ]
        }
        
        with pytest.raises(ValueError, match="Circular dependency"):
            parser.validate_dependencies(workflow)


class TestWorkflowExecutor:
    """Test workflow executor"""
    
    def test_execute_simple_workflow(self):
        """Test executing simple workflow"""
        executed = []
        
        def test_handler(params, variables):
            executed.append(params.get('step'))
            return f"Executed {params.get('step')}"
        
        executor = WorkflowExecutor({'test_action': test_handler})
        
        workflow = {
            'name': 'Test',
            'steps': [
                {'name': 'step1', 'action': 'test_action', 'params': {'step': '1'}},
                {'name': 'step2', 'action': 'test_action', 'params': {'step': '2'}}
            ]
        }
        
        result = executor.execute(workflow)
        
        assert result['success'] is True
        assert len(executed) == 2
        assert executed == ['1', '2']
    
    def test_execute_with_dependencies(self):
        """Test execution order with dependencies"""
        execution_order = []
        
        def test_handler(params, variables):
            execution_order.append(params.get('step'))
            return True
        
        executor = WorkflowExecutor({'test_action': test_handler})
        
        workflow = {
            'name': 'Test',
            'steps': [
                {'name': 'step2', 'action': 'test_action', 'params': {'step': '2'}, 'depends_on': ['step1']},
                {'name': 'step1', 'action': 'test_action', 'params': {'step': '1'}}
            ]
        }
        
        result = executor.execute(workflow)
        
        assert result['success'] is True
        assert execution_order == ['1', '2']  # Should execute in dependency order
    
    def test_execute_with_failure(self):
        """Test handling step failure"""
        def failing_handler(params, variables):
            raise Exception("Test failure")
        
        executor = WorkflowExecutor({'failing_action': failing_handler})
        
        workflow = {
            'name': 'Test',
            'on_error': 'stop',
            'steps': [
                {'name': 'step1', 'action': 'failing_action'}
            ]
        }
        
        result = executor.execute(workflow)
        
        assert result['success'] is False
    
    def test_variable_substitution(self):
        """Test variable substitution in parameters"""
        captured_value = None
        
        def test_handler(params, variables):
            nonlocal captured_value
            captured_value = params.get('value')
            return True
        
        executor = WorkflowExecutor({'test_action': test_handler})
        
        workflow = {
            'name': 'Test',
            'variables': {'my_var': 'test_value'},
            'steps': [
                {'name': 'step1', 'action': 'test_action', 'params': {'value': '$my_var'}}
            ]
        }
        
        result = executor.execute(workflow)
        
        assert result['success'] is True
        assert captured_value == 'test_value'


class TestWorkflowTemplates:
    """Test workflow templates"""
    
    def test_list_templates(self):
        """Test listing available templates"""
        templates = WorkflowTemplates.list_templates()
        
        assert 'feature_implementation' in templates
        assert 'bug_fix' in templates
        assert 'refactoring' in templates
        assert 'documentation_update' in templates
        assert 'release_preparation' in templates
        assert 'quality_assurance' in templates
    
    def test_get_template(self):
        """Test getting a template"""
        template = WorkflowTemplates.get_template('feature_implementation')
        
        assert template['name'] == 'Feature Implementation'
        assert 'steps' in template
        assert len(template['steps']) > 0
    
    def test_get_invalid_template(self):
        """Test getting non-existent template"""
        with pytest.raises(ValueError, match="Unknown template"):
            WorkflowTemplates.get_template('nonexistent')
    
    def test_feature_implementation_template(self):
        """Test feature implementation template structure"""
        template = WorkflowTemplates.feature_implementation()
        
        assert template['name'] == 'Feature Implementation'
        assert 'analyze_feature' in [s['name'] for s in template['steps']]
        assert 'generate_code' in [s['name'] for s in template['steps']]
        assert 'run_tests' in [s['name'] for s in template['steps']]
    
    def test_bug_fix_template(self):
        """Test bug fix template structure"""
        template = WorkflowTemplates.bug_fix()
        
        assert template['name'] == 'Bug Fix'
        assert 'analyze_bug' in [s['name'] for s in template['steps']]
        assert 'generate_fix' in [s['name'] for s in template['steps']]


class TestWorkflowEngine:
    """Test workflow engine"""
    
    def test_load_template(self):
        """Test loading workflow template"""
        engine = WorkflowEngine()
        workflow_id = engine.load_template('feature_implementation')
        
        assert workflow_id == 'Feature Implementation'
        assert workflow_id in engine.list_workflows()
    
    def test_get_workflow_info(self):
        """Test getting workflow information"""
        engine = WorkflowEngine()
        workflow_id = engine.load_template('bug_fix')
        
        info = engine.get_workflow_info(workflow_id)
        
        assert info['name'] == 'Bug Fix'
        assert info['step_count'] > 0
        assert 'execution_order' in info
    
    def test_validate_workflow(self):
        """Test workflow validation"""
        engine = WorkflowEngine()
        workflow_id = engine.load_template('refactoring')
        
        assert engine.validate_workflow(workflow_id) is True
    
    def test_register_action(self):
        """Test registering action handler"""
        engine = WorkflowEngine()
        
        def test_handler(params, variables):
            return True
        
        engine.register_action('test_action', test_handler)
        
        assert 'test_action' in engine.executor.action_handlers
    
    def test_execute_workflow_with_variables(self):
        """Test executing workflow with variables"""
        engine = WorkflowEngine()
        
        executed = []
        
        def test_handler(params, variables):
            executed.append(True)
            return True
        
        # Register handlers for all actions in the template
        for action in ['analyze_request', 'check_existing_code', 'generate_feature_code',
                      'validate_syntax', 'generate_unit_tests', 'run_test_suite',
                      'check_code_quality', 'refactor_code', 'update_documentation']:
            engine.register_action(action, test_handler)
        
        workflow_id = engine.load_template('feature_implementation')
        
        variables = {
            'feature_name': 'Test Feature',
            'project_path': '/test/path'
        }
        
        result = engine.execute_workflow(workflow_id, variables)
        
        assert result['success'] is True
        assert len(executed) > 0
