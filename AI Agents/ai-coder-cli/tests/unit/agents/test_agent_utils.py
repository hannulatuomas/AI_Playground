
"""
Unit tests for Agent Utility Modules.

Tests for clarification templates, codebase awareness, and context optimizer.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query.return_value = {
        'success': True,
        'response': 'Mock LLM response'
    }
    return router


@pytest.fixture
def sample_codebase_structure():
    """Sample codebase structure for testing."""
    return {
        'src/': {
            'main.py': 'def main(): pass',
            'utils.py': 'def helper(): pass',
            'models/': {
                'user.py': 'class User: pass',
                'product.py': 'class Product: pass'
            }
        },
        'tests/': {
            'test_main.py': 'def test_main(): pass'
        }
    }


# =============================================================================
# Clarification Templates Tests
# =============================================================================

class TestClarificationTemplates:
    """Tests for ClarificationTemplates module."""
    
    def test_import_clarification_templates(self):
        """Test importing clarification templates module."""
        from agents.utils import clarification_templates
        
        assert clarification_templates is not None
    
    def test_get_clarification_prompt(self):
        """Test getting clarification prompt template."""
        from agents.utils.clarification_templates import get_clarification_prompt
        
        prompt = get_clarification_prompt('ambiguous_requirement')
        
        assert prompt is not None
        assert isinstance(prompt, str)
        assert len(prompt) > 0
    
    def test_format_clarification_request(self):
        """Test formatting clarification request."""
        from agents.utils.clarification_templates import format_clarification_request
        
        request = format_clarification_request(
            question="What framework should I use?",
            context={'language': 'python', 'project_type': 'web'}
        )
        
        assert request is not None
        assert isinstance(request, str)
        assert 'python' in request.lower() or 'framework' in request.lower()
    
    def test_get_all_templates(self):
        """Test retrieving all available templates."""
        from agents.utils.clarification_templates import get_all_templates
        
        templates = get_all_templates()
        
        assert templates is not None
        assert isinstance(templates, dict)
        assert len(templates) > 0
    
    def test_template_categories(self):
        """Test different categories of templates."""
        from agents.utils.clarification_templates import get_template_by_category
        
        categories = ['technical', 'requirement', 'design', 'implementation']
        
        for category in categories:
            template = get_template_by_category(category)
            assert template is not None or template == {}  # Some categories may not exist


# =============================================================================
# Codebase Awareness Tests
# =============================================================================

class TestCodebaseAwareness:
    """Tests for CodebaseAwareness module."""
    
    def test_import_codebase_awareness(self):
        """Test importing codebase awareness module."""
        from agents.utils import codebase_awareness
        
        assert codebase_awareness is not None
    
    def test_analyze_codebase_structure(self, temp_dir):
        """Test analyzing codebase structure."""
        from agents.utils.codebase_awareness import analyze_codebase_structure
        
        # Create sample files
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("def main(): pass")
        (temp_dir / "tests").mkdir()
        (temp_dir / "tests" / "test_main.py").write_text("def test_main(): pass")
        
        result = analyze_codebase_structure(str(temp_dir))
        
        assert result is not None
        assert isinstance(result, dict)
    
    def test_get_file_dependencies(self, temp_dir):
        """Test extracting file dependencies."""
        from agents.utils.codebase_awareness import get_file_dependencies
        
        # Create a Python file with imports
        test_file = temp_dir / "main.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path

def main():
    pass
""")
        
        deps = get_file_dependencies(str(test_file))
        
        assert deps is not None
        assert isinstance(deps, (list, set))
    
    def test_identify_language(self, temp_dir):
        """Test identifying programming language."""
        from agents.utils.codebase_awareness import identify_language
        
        # Python file
        py_file = temp_dir / "test.py"
        py_file.write_text("def test(): pass")
        
        language = identify_language(str(py_file))
        
        assert language is not None
        assert 'python' in language.lower()
    
    def test_get_codebase_summary(self, temp_dir):
        """Test generating codebase summary."""
        from agents.utils.codebase_awareness import get_codebase_summary
        
        # Create sample structure
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("def main(): pass")
        (temp_dir / "tests").mkdir()
        (temp_dir / "README.md").write_text("# Test Project")
        
        summary = get_codebase_summary(str(temp_dir))
        
        assert summary is not None
        assert isinstance(summary, (dict, str))
    
    def test_find_entry_points(self, temp_dir):
        """Test finding entry points in codebase."""
        from agents.utils.codebase_awareness import find_entry_points
        
        # Create main file
        (temp_dir / "main.py").write_text("""
def main():
    pass

if __name__ == '__main__':
    main()
""")
        
        entry_points = find_entry_points(str(temp_dir))
        
        assert entry_points is not None
        assert isinstance(entry_points, list)
    
    def test_get_project_metadata(self, temp_dir):
        """Test extracting project metadata."""
        from agents.utils.codebase_awareness import get_project_metadata
        
        # Create setup.py or similar
        (temp_dir / "setup.py").write_text("""
from setuptools import setup

setup(
    name='test-project',
    version='1.0.0'
)
""")
        
        metadata = get_project_metadata(str(temp_dir))
        
        assert metadata is not None
        assert isinstance(metadata, dict)


# =============================================================================
# Context Optimizer Tests
# =============================================================================

class TestContextOptimizer:
    """Tests for ContextOptimizer module."""
    
    def test_import_context_optimizer(self):
        """Test importing context optimizer module."""
        from agents.utils import context_optimizer
        
        assert context_optimizer is not None
    
    def test_optimize_context(self, mock_llm_router):
        """Test optimizing context for LLM."""
        from agents.utils.context_optimizer import optimize_context
        
        context = {
            'code': 'def test(): pass' * 1000,  # Large code
            'history': ['msg1', 'msg2', 'msg3'] * 100,  # Long history
            'metadata': {'key': 'value'}
        }
        
        optimized = optimize_context(context, max_tokens=1000)
        
        assert optimized is not None
        assert isinstance(optimized, dict)
    
    def test_truncate_code_context(self):
        """Test truncating code context."""
        from agents.utils.context_optimizer import truncate_code_context
        
        long_code = "def function(): pass\n" * 100
        
        truncated = truncate_code_context(long_code, max_lines=10)
        
        assert truncated is not None
        assert len(truncated.split('\n')) <= 10
    
    def test_compress_history(self):
        """Test compressing conversation history."""
        from agents.utils.context_optimizer import compress_history
        
        history = [
            {'role': 'user', 'content': 'Message 1'},
            {'role': 'assistant', 'content': 'Response 1'},
            {'role': 'user', 'content': 'Message 2'},
            {'role': 'assistant', 'content': 'Response 2'}
        ] * 50
        
        compressed = compress_history(history, max_messages=10)
        
        assert compressed is not None
        assert isinstance(compressed, list)
        assert len(compressed) <= 10
    
    def test_prioritize_context_elements(self):
        """Test prioritizing context elements."""
        from agents.utils.context_optimizer import prioritize_context_elements
        
        elements = [
            {'type': 'recent_code', 'content': 'code1', 'priority': 'high'},
            {'type': 'history', 'content': 'msg1', 'priority': 'low'},
            {'type': 'current_task', 'content': 'task1', 'priority': 'high'}
        ]
        
        prioritized = prioritize_context_elements(elements)
        
        assert prioritized is not None
        assert isinstance(prioritized, list)
    
    def test_estimate_token_count(self):
        """Test estimating token count."""
        from agents.utils.context_optimizer import estimate_token_count
        
        text = "This is a test message with several tokens."
        
        count = estimate_token_count(text)
        
        assert count is not None
        assert isinstance(count, int)
        assert count > 0
    
    def test_smart_context_window(self):
        """Test smart context window management."""
        from agents.utils.context_optimizer import smart_context_window
        
        messages = [
            "Message 1",
            "Message 2",
            "Message 3",
            "Message 4",
            "Message 5"
        ]
        
        window = smart_context_window(messages, window_size=3)
        
        assert window is not None
        assert isinstance(window, list)
        assert len(window) <= 3


# =============================================================================
# Integration Tests for Utils
# =============================================================================

class TestUtilsIntegration:
    """Integration tests combining multiple utils."""
    
    def test_codebase_aware_clarification(self, temp_dir):
        """Test generating clarifications aware of codebase."""
        from agents.utils.codebase_awareness import analyze_codebase_structure
        from agents.utils.clarification_templates import format_clarification_request
        
        # Create sample codebase
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("def main(): pass")
        
        # Analyze codebase
        structure = analyze_codebase_structure(str(temp_dir))
        
        # Generate clarification with context
        clarification = format_clarification_request(
            question="How should I organize this code?",
            context={'structure': structure}
        )
        
        assert clarification is not None
        assert isinstance(clarification, str)
    
    def test_optimized_codebase_context(self, temp_dir):
        """Test optimizing codebase context."""
        from agents.utils.codebase_awareness import get_codebase_summary
        from agents.utils.context_optimizer import optimize_context
        
        # Create sample codebase
        (temp_dir / "src").mkdir()
        (temp_dir / "src" / "main.py").write_text("def main(): pass\n" * 100)
        
        # Get summary
        summary = get_codebase_summary(str(temp_dir))
        
        # Optimize for LLM
        optimized = optimize_context(
            {'codebase': summary},
            max_tokens=500
        )
        
        assert optimized is not None
        assert isinstance(optimized, dict)

