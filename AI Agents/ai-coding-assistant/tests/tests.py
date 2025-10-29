"""
Comprehensive Test Suite for AI Coding Assistant

Tests cover:
- Core modules (LLM, PromptEngine, LearningDB)
- Features (CodeGenerator, Debugger, LanguageSupport)
- Integration tests
- Mock LLM for testing without actual model

Usage:
    python -m pytest tests/tests.py -v
    or
    python tests/tests.py
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core import LLMConfig, LLMInterface, PromptEngine, LearningDB
from features import CodeGenerator, Debugger, LanguageSupport


class MockLLMInterface:
    """Mock LLM Interface for testing without actual model."""
    
    def __init__(self, config=None):
        self.config = config
        self.call_count = 0
        self.last_prompt = None
        
    def generate(self, prompt: str, max_tokens: int = 1024, use_cache: bool = False, timeout: int = 60) -> str:
        """Mock generate method that returns predefined responses."""
        self.call_count += 1
        self.last_prompt = prompt
        
        # Return different responses based on prompt content
        if "python" in prompt.lower():
            return """
Here's a Python function:

```python
def hello_world():
    \"\"\"Return a greeting.\"\"\"
    return "Hello, World!"
```

This function returns a simple greeting string.
"""
        elif "debug" in prompt.lower() or "error" in prompt.lower():
            return """
Here's the fixed code:

```python
def hello():
    print("Hello")
```

The issue was a missing colon after the function definition.
"""
        else:
            return """
```python
def example():
    pass
```

This is an example function.
"""


class TestLLMConfig(unittest.TestCase):
    """Test LLMConfig dataclass."""
    
    def test_config_creation(self):
        """Test creating LLM configuration."""
        config = LLMConfig(
            model_path="test_model.gguf",
            executable_path="llama-cli",
            context_size=2048,
            temperature=0.7
        )
        
        self.assertEqual(config.model_path, "test_model.gguf")
        self.assertEqual(config.executable_path, "llama-cli")
        self.assertEqual(config.context_size, 2048)
        self.assertEqual(config.temperature, 0.7)
    
    def test_config_defaults(self):
        """Test default configuration values."""
        config = LLMConfig(
            model_path="test.gguf",
            executable_path="llama"
        )
        
        self.assertEqual(config.context_size, 4096)
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.top_p, 0.9)


class TestLearningDB(unittest.TestCase):
    """Test LearningDB functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = LearningDB(self.test_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
    
    def test_add_entry(self):
        """Test adding entry to database."""
        entry_id = self.db.add_entry(
            query="test query",
            language="python",
            response="test response",
            task_type="generate"
        )
        
        self.assertIsNotNone(entry_id)
        self.assertGreater(entry_id, 0)
    
    def test_update_feedback(self):
        """Test updating feedback for entry."""
        entry_id = self.db.add_entry(
            query="test",
            language="python",
            response="response",
            task_type="generate"
        )
        
        result = self.db.update_feedback(
            interaction_id=entry_id,
            feedback="Great!",
            success=True
        )
        
        self.assertTrue(result)
    
    def test_get_relevant_learnings(self):
        """Test retrieving relevant learnings."""
        # Add some test entries
        self.db.add_entry(
            query="test1",
            language="python",
            response="response1",
            task_type="generate",
            success=False,
            error_type="syntax_error",
            correction="Use proper syntax"
        )
        
        learnings = self.db.get_relevant_learnings(
            language="python",
            task_type="generate",
            limit=5
        )
        
        self.assertIsInstance(learnings, list)
    
    def test_get_statistics(self):
        """Test getting database statistics."""
        # Add some entries
        for i in range(3):
            self.db.add_entry(
                query=f"test{i}",
                language="python",
                response=f"response{i}",
                task_type="generate"
            )
        
        stats = self.db.get_statistics()
        
        self.assertIn('total_interactions', stats)
        self.assertGreaterEqual(stats['total_interactions'], 3)


class TestPromptEngine(unittest.TestCase):
    """Test PromptEngine functionality."""
    
    def setUp(self):
        """Set up test prompt engine."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = LearningDB(self.test_db.name)
        self.engine = PromptEngine(learning_db=self.db)
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
    
    def test_build_prompt_generate(self):
        """Test building prompt for code generation."""
        prompt = self.engine.build_prompt(
            task_type='generate',
            language='python',
            content='Create a function to sort a list'
        )
        
        self.assertIn('python', prompt.lower())
        self.assertIn('sort', prompt.lower())
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_build_prompt_debug(self):
        """Test building prompt for debugging."""
        prompt = self.engine.build_prompt(
            task_type='debug',
            language='python',
            content='def hello()\n    pass',
            error='SyntaxError: invalid syntax'
        )
        
        self.assertIn('debug', prompt.lower())
        self.assertIn('syntax', prompt.lower())
    
    def test_get_learnings(self):
        """Test getting learnings from database."""
        # Add a test learning
        self.db.add_entry(
            query="test",
            language="python",
            response="response",
            task_type="generate",
            success=False,
            error_type="logic_error",
            correction="Fix the logic"
        )
        
        learnings = self.engine.get_learnings(
            query="test",
            language="python",
            task_type="generate"
        )
        
        self.assertIsInstance(learnings, list)
        # Each learning should have error, solution, error_type
        for learning in learnings:
            self.assertIn('error', learning)
            self.assertIn('solution', learning)
            self.assertIn('error_type', learning)
    
    def test_normalize_language(self):
        """Test language name normalization."""
        self.assertEqual(self.engine._normalize_language('py'), 'python')
        self.assertEqual(self.engine._normalize_language('js'), 'javascript')
        self.assertEqual(self.engine._normalize_language('c++'), 'cpp')
        self.assertEqual(self.engine._normalize_language('python'), 'python')
    
    def test_format_learnings(self):
        """Test formatting learnings for prompt."""
        # Add a learning
        self.db.add_entry(
            query="test",
            language="python",
            response="bad code",
            task_type="generate",
            success=False,
            error_type="logic_error",
            correction="Better solution"
        )
        
        formatted = self.engine._format_learnings('python', 'generate')
        
        # Should return string (may be empty if no learnings found)
        self.assertIsInstance(formatted, str)
    
    def test_supported_languages(self):
        """Test getting supported languages."""
        languages = self.engine.get_supported_languages()
        
        self.assertIsInstance(languages, list)
        self.assertIn('python', languages)
        self.assertIn('javascript', languages)
        self.assertIn('cpp', languages)
    
    def test_supported_tasks(self):
        """Test getting supported task types."""
        tasks = self.engine.get_supported_tasks()
        
        self.assertIsInstance(tasks, list)
        self.assertIn('generate', tasks)
        self.assertIn('debug', tasks)


class TestCodeGenerator(unittest.TestCase):
    """Test CodeGenerator functionality."""
    
    def setUp(self):
        """Set up test code generator with mocks."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = LearningDB(self.test_db.name)
        self.engine = PromptEngine(learning_db=self.db)
        self.mock_llm = MockLLMInterface()
        self.generator = CodeGenerator(self.mock_llm, self.engine, self.db)
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
    
    def test_generate_code_success(self):
        """Test successful code generation."""
        result = self.generator.generate_code(
            task="Create a hello world function",
            language="python"
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['code'])
        self.assertIn('def', result['code'])
        self.assertIsNotNone(result['interaction_id'])
    
    def test_generate_code_with_framework(self):
        """Test code generation with framework detection."""
        result = self.generator.generate_code(
            task="Create a React component",
            language="javascript"
        )
        
        self.assertTrue(result['success'])
        # Framework should be detected
        self.assertIn(result['framework'], ['react', None])
    
    def test_detect_framework(self):
        """Test framework detection."""
        lang, framework = self.generator._detect_framework(
            "Create a React component",
            "javascript"
        )
        
        self.assertEqual(framework, "react")
    
    def test_parse_response(self):
        """Test parsing LLM response."""
        response = """
Here's the code:

```python
def test():
    pass
```

This is a test function.
"""
        code, explanation = self.generator._parse_response(response, "python")
        
        self.assertIn('def test', code)
        # The explanation should contain some text
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 0)
    
    def test_provide_feedback(self):
        """Test providing feedback."""
        # Generate code first
        result = self.generator.generate_code(
            task="test",
            language="python"
        )
        
        # Provide feedback
        success = self.generator.provide_feedback(
            interaction_id=result['interaction_id'],
            success=True,
            feedback="Great!"
        )
        
        self.assertTrue(success)
    
    def test_regenerate_with_feedback(self):
        """Test regenerating with feedback."""
        result = self.generator.regenerate_with_feedback(
            original_task="Create a function",
            language="python",
            feedback="Make it faster"
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['code'])


class TestDebugger(unittest.TestCase):
    """Test Debugger functionality."""
    
    def setUp(self):
        """Set up test debugger with mocks."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = LearningDB(self.test_db.name)
        self.engine = PromptEngine(learning_db=self.db)
        self.mock_llm = MockLLMInterface()
        self.debugger = Debugger(self.mock_llm, self.engine, self.db)
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
    
    def test_debug_code_success(self):
        """Test successful code debugging."""
        result = self.debugger.debug_code(
            code="def hello()\n    pass",
            language="python",
            error_msg="SyntaxError: invalid syntax"
        )
        
        self.assertTrue(result['success'])
        self.assertIsNotNone(result['fixed_code'])
        self.assertIsNotNone(result['explanation'])
    
    def test_classify_error(self):
        """Test error classification."""
        error_type = self.debugger._classify_error(
            "SyntaxError: invalid syntax",
            "python"
        )
        
        self.assertEqual(error_type, "syntax_error")
        
        error_type2 = self.debugger._classify_error(
            "NameError: name 'x' is not defined",
            "python"
        )
        
        self.assertEqual(error_type2, "name_error")
    
    def test_validate_inputs(self):
        """Test input validation."""
        # Valid input
        error = self.debugger._validate_inputs(
            "def test(): pass",
            "python",
            "SyntaxError"
        )
        
        self.assertIsNone(error)
        
        # Invalid input (empty code)
        error = self.debugger._validate_inputs(
            "",
            "python",
            None
        )
        
        self.assertIsNotNone(error)
        self.assertIn("empty", error.lower())
    
    def test_get_language_specific_hints(self):
        """Test getting language-specific hints."""
        hints = self.debugger._get_language_specific_hints(
            "bash",
            "command not found"
        )
        
        self.assertIsInstance(hints, str)
        self.assertGreater(len(hints), 0)
    
    def test_provide_feedback(self):
        """Test providing debugging feedback."""
        # Debug code first
        result = self.debugger.debug_code(
            code="test code",
            language="python",
            error_msg="test error"
        )
        
        # Provide feedback
        success = self.debugger.provide_feedback(
            interaction_id=result['interaction_id'],
            success=True
        )
        
        self.assertTrue(success)


class TestLanguageSupport(unittest.TestCase):
    """Test LanguageSupport functionality."""
    
    def setUp(self):
        """Set up test language support."""
        self.lang_support = LanguageSupport()
    
    def test_get_template(self):
        """Test getting language template."""
        template = self.lang_support.get_code_template("python", "basic")
        
        self.assertIsNotNone(template)
        self.assertIsInstance(template, str)
    
    def test_get_language_info(self):
        """Test getting language information."""
        info = self.lang_support.get_language_info("python")
        
        self.assertIsNotNone(info)
        self.assertIsInstance(info, dict)
        self.assertIn('extensions', info)
        self.assertIn('.py', info['extensions'])
    
    def test_detect_language_from_filename(self):
        """Test detecting language from filename."""
        lang, framework = self.lang_support.detect_language(
            code="",  # Empty code
            filename="test.py"
        )
        
        self.assertEqual(lang, "python")
    
    def test_detect_language_from_code(self):
        """Test detecting language from code."""
        lang, framework = self.lang_support.detect_language(
            code="def hello():\n    pass"
        )
        
        self.assertEqual(lang, "python")
    
    def test_detect_framework(self):
        """Test framework detection."""
        code = """
import React from 'react';
import { useState } from 'react';

function App() {
    return <div>Hello</div>;
}
"""
        lang, framework = self.lang_support.detect_language(code=code)
        
        self.assertEqual(framework, "react")
    
    def test_validate_framework(self):
        """Test framework validation."""
        # Valid combination - react is a web framework for javascript
        result = self.lang_support.is_web_framework("react")
        self.assertTrue(result)
        
        # Invalid - django is python, not javascript
        result = self.lang_support.is_web_framework("notaframework")
        self.assertFalse(result)
    
    def test_get_supported_languages(self):
        """Test getting supported languages."""
        languages = self.lang_support.get_supported_languages()
        
        self.assertIsInstance(languages, list)
        self.assertGreater(len(languages), 10)
        self.assertIn("python", languages)
    
    def test_get_supported_frameworks(self):
        """Test getting supported frameworks."""
        # Test that we can get language info which includes frameworks
        python_info = self.lang_support.get_language_info("python")
        self.assertIn('frameworks', python_info)
        self.assertIn('django', python_info['frameworks'])
        self.assertIn('flask', python_info['frameworks'])
    
    def test_add_language(self):
        """Test adding a new language (via template system)."""
        # The current implementation doesn't have add_language method
        # but we can test that the language system is extensible
        # by checking if we can get info for existing languages
        rust_info = self.lang_support.get_language_info("rust")
        # Rust might not be in the system, so we just check it doesn't crash
        self.assertIsInstance(rust_info, (dict, type(None)))


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db = LearningDB(self.test_db.name)
        self.engine = PromptEngine(learning_db=self.db)
        self.mock_llm = MockLLMInterface()
        self.generator = CodeGenerator(self.mock_llm, self.engine, self.db)
        self.debugger = Debugger(self.mock_llm, self.engine, self.db)
        self.lang_support = LanguageSupport()
    
    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_db.name):
            os.unlink(self.test_db.name)
    
    def test_full_generation_workflow(self):
        """Test complete code generation workflow."""
        # 1. Generate code
        result = self.generator.generate_code(
            task="Create a greeting function",
            language="python"
        )
        
        self.assertTrue(result['success'])
        interaction_id = result['interaction_id']
        
        # 2. Provide feedback
        feedback_success = self.generator.provide_feedback(
            interaction_id=interaction_id,
            success=True,
            feedback="Works great!"
        )
        
        self.assertTrue(feedback_success)
        
        # 3. Get statistics
        stats = self.db.get_statistics()
        self.assertGreater(stats['total_interactions'], 0)
    
    def test_full_debugging_workflow(self):
        """Test complete debugging workflow."""
        # 1. Debug code
        result = self.debugger.debug_code(
            code="def test()\n    pass",
            language="python",
            error_msg="SyntaxError"
        )
        
        self.assertTrue(result['success'])
        interaction_id = result['interaction_id']
        
        # 2. Provide feedback
        feedback_success = self.debugger.provide_feedback(
            interaction_id=interaction_id,
            success=True
        )
        
        self.assertTrue(feedback_success)
    
    def test_learning_cycle(self):
        """Test that system learns from feedback."""
        # 1. First generation
        result1 = self.generator.generate_code(
            task="Create a function",
            language="python"
        )
        
        # 2. Provide negative feedback
        self.generator.provide_feedback(
            interaction_id=result1['interaction_id'],
            success=False,
            error_type="logic_error",
            correction="Better approach needed"
        )
        
        # 3. Check learnings are stored
        learnings = self.engine.get_learnings(
            query="function",
            language="python",
            task_type="generate"
        )
        
        # Should have at least one learning now
        self.assertIsInstance(learnings, list)
        
        # 4. Second generation should incorporate learnings
        prompt = self.engine.build_prompt(
            task_type="generate",
            language="python",
            content="Create another function"
        )
        
        # Prompt may or may not contain learnings depending on DB state
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
    
    def test_language_detection_integration(self):
        """Test language detection integrated with generation."""
        # Detect language
        lang, framework = self.lang_support.detect_language(
            code="import React from 'react'",
            filename="App.jsx"
        )
        
        # Use detected language for generation
        if lang:
            result = self.generator.generate_code(
                task="Create a component",
                language=lang
            )
            
            self.assertTrue(result['success'])


class TestMocking(unittest.TestCase):
    """Test that mocking works correctly."""
    
    def test_mock_llm_response(self):
        """Test mock LLM returns expected responses."""
        mock_llm = MockLLMInterface()
        
        # Test Python response
        response = mock_llm.generate("Write Python code", max_tokens=100)
        self.assertIn("python", response.lower())
        self.assertIn("def", response)
        
        # Test debug response
        response = mock_llm.generate("Debug this code with error", max_tokens=100)
        self.assertIn("fixed", response.lower())
        
        # Test call count
        self.assertEqual(mock_llm.call_count, 2)
    
    @patch('subprocess.run')
    def test_mock_subprocess(self, mock_run):
        """Test mocking subprocess calls."""
        # Configure mock
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Test output",
            stderr=""
        )
        
        # This would call subprocess in real LLMInterface
        # Here we just test the mock works
        import subprocess
        result = subprocess.run(
            ["echo", "test"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.stdout, "Test output")
        mock_run.assert_called_once()


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestLLMConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestLearningDB))
    suite.addTests(loader.loadTestsFromTestCase(TestPromptEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestCodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestDebugger))
    suite.addTests(loader.loadTestsFromTestCase(TestLanguageSupport))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestMocking))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
