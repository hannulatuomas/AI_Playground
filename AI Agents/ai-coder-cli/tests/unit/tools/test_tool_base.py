
"""
Unit tests for Tool Base Class.

Tests the abstract base tool class and its core functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch
from tools.base import Tool


class ConcreteTool(Tool):
    """Concrete tool implementation for testing."""
    
    def invoke(self, params):
        """Implementation of invoke method."""
        return {
            'success': True,
            'result': params.get('input', 'default'),
            'params': params
        }


class FailingTool(Tool):
    """Tool that fails for testing retry logic."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attempt_count = 0
    
    def invoke(self, params):
        """Fails first N times, then succeeds."""
        self.attempt_count += 1
        if self.attempt_count < params.get('fail_times', 2):
            raise Exception(f"Attempt {self.attempt_count} failed")
        return {'success': True, 'attempt': self.attempt_count}


@pytest.mark.unit
class TestToolBase:
    """Test suite for Tool base class."""
    
    def test_tool_initialization(self):
        """Test tool initialization with all parameters."""
        config = {'timeout': 30, 'retry': 3}
        
        tool = ConcreteTool(
            name='test_tool',
            description='Test tool description',
            config=config
        )
        
        assert tool.name == 'test_tool'
        assert tool.description == 'Test tool description'
        assert tool.config == config
        assert tool.logger is not None
    
    def test_tool_initialization_without_config(self):
        """Test tool initialization without config."""
        tool = ConcreteTool(
            name='minimal_tool',
            description='Minimal tool'
        )
        
        assert tool.name == 'minimal_tool'
        assert tool.description == 'Minimal tool'
        assert tool.config == {}
    
    def test_invoke_method(self):
        """Test invoke method implementation."""
        tool = ConcreteTool(
            name='invoke_tool',
            description='Test invoke'
        )
        
        result = tool.invoke({'input': 'test_value'})
        
        assert result['success'] is True
        assert result['result'] == 'test_value'
        assert 'params' in result
    
    def test_abstract_invoke_method(self):
        """Test that Tool class is abstract and requires invoke implementation."""
        # Cannot instantiate Tool directly without implementing invoke
        with pytest.raises(TypeError):
            Tool(name='abstract', description='test')
    
    def test_invoke_with_retry_success_first_attempt(self):
        """Test invoke_with_retry succeeds on first attempt."""
        tool = ConcreteTool(
            name='retry_tool',
            description='Retry test'
        )
        
        result = tool.invoke_with_retry(
            {'input': 'retry_test'},
            max_retries=3,
            initial_delay=0.1
        )
        
        assert result['success'] is True
        assert result['result'] == 'retry_test'
    
    def test_invoke_with_retry_success_after_failures(self):
        """Test invoke_with_retry succeeds after initial failures."""
        tool = FailingTool(
            name='failing_tool',
            description='Tool that fails initially'
        )
        
        result = tool.invoke_with_retry(
            {'fail_times': 2},
            max_retries=3,
            initial_delay=0.1
        )
        
        assert result['success'] is True
        assert result['attempt'] == 2
        assert tool.attempt_count == 2
    
    def test_invoke_with_retry_exhausts_retries(self):
        """Test invoke_with_retry fails after exhausting retries."""
        tool = FailingTool(
            name='always_failing_tool',
            description='Tool that always fails'
        )
        
        with pytest.raises(Exception, match="failed"):
            tool.invoke_with_retry(
                {'fail_times': 10},  # Will never succeed
                max_retries=2,
                initial_delay=0.1
            )
    
    def test_invoke_with_retry_exponential_backoff(self):
        """Test that retry uses exponential backoff."""
        tool = FailingTool(
            name='backoff_tool',
            description='Test exponential backoff'
        )
        
        start_time = time.time()
        
        try:
            tool.invoke_with_retry(
                {'fail_times': 10},
                max_retries=2,
                initial_delay=0.1
            )
        except Exception:
            pass
        
        elapsed_time = time.time() - start_time
        
        # With exponential backoff: 0.1s + 0.2s = 0.3s minimum
        # Allow some margin for execution time
        assert elapsed_time >= 0.25, "Should use exponential backoff delays"
    
    def test_tool_logging(self, caplog):
        """Test that tool initialization logs correctly."""
        tool = ConcreteTool(
            name='log_test_tool',
            description='Logging test'
        )
        
        assert 'initialized' in caplog.text.lower()
        assert 'log_test_tool' in caplog.text
    
    def test_invoke_with_retry_logging(self, caplog):
        """Test that retry attempts are logged."""
        tool = FailingTool(
            name='retry_log_tool',
            description='Retry logging test'
        )
        
        try:
            tool.invoke_with_retry(
                {'fail_times': 3},
                max_retries=2,
                initial_delay=0.01
            )
        except Exception:
            pass
        
        # Should log retry attempts
        assert 'attempt' in caplog.text.lower() or 'retry' in caplog.text.lower()
