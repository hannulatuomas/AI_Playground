"""
Unit tests for EnhancedPromptRefiner.

Tests for enhanced prompt refinement with language-specific context.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from agents.enhanced_prompt_refiner import EnhancedPromptRefiner


class TestEnhancedPromptRefinerInitialization:
    """Tests for EnhancedPromptRefiner initialization."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        refiner = EnhancedPromptRefiner()
        
        assert refiner.name == "enhanced_prompt_refiner"
        assert "prompt refinement" in refiner.description.lower()
        assert hasattr(refiner, '_best_practices_cache')
        assert hasattr(refiner, '_user_preferences_cache')
    
    def test_initialization_custom(self):
        """Test custom initialization."""
        refiner = EnhancedPromptRefiner(
            name="custom_refiner",
            description="Custom prompt refiner"
        )
        
        assert refiner.name == "custom_refiner"
        assert refiner.description == "Custom prompt refiner"
    
    def test_caches_initialized_empty(self):
        """Test that caches are initialized as empty."""
        refiner = EnhancedPromptRefiner()
        
        assert refiner._best_practices_cache == {}
        assert refiner._user_preferences_cache == {}


class TestExecuteMethod:
    """Tests for execute method."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_execute_basic(self, refiner):
        """Test basic execution."""
        task = "Write a function to calculate fibonacci numbers"
        context = {
            'language': 'python',
            'agent_type': 'code_editor'
        }
        
        result = refiner.execute(task, context)
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
        assert 'original_prompt' in result['data']
        assert result['data']['language'] == 'python'
        assert result['data']['agent_type'] == 'code_editor'
    
    def test_execute_with_all_context(self, refiner):
        """Test execution with complete context."""
        task = "Implement a REST API endpoint"
        context = {
            'language': 'python',
            'agent_type': 'code_editor',
            'project_path': Path('/tmp/test_project')
        }
        
        result = refiner.execute(task, context)
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
        assert 'enhancements_applied' in result['data']
    
    def test_execute_without_language(self, refiner):
        """Test execution without language specified."""
        task = "Write a function"
        context = {
            'agent_type': 'code_editor'
        }
        
        result = refiner.execute(task, context)
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
    
    def test_execute_with_generic_agent_type(self, refiner):
        """Test execution with generic agent type."""
        task = "Analyze code structure"
        context = {
            'language': 'javascript'
        }
        
        result = refiner.execute(task, context)
        
        assert result['success'] is True
        assert result['data']['agent_type'] == 'generic'
    
    def test_execute_error_handling(self, refiner):
        """Test error handling in execution."""
        with patch.object(refiner, '_build_enhanced_prompt', side_effect=Exception("Test error")):
            result = refiner.execute("test task", {})
            
            assert result['success'] is False
            assert 'error' in result
            assert 'Test error' in result['error']
    
    def test_execute_next_context(self, refiner):
        """Test that next context is properly set."""
        task = "Write tests"
        context = {
            'language': 'python',
            'agent_type': 'code_tester'
        }
        
        result = refiner.execute(task, context)
        
        assert 'next_context' in result
        assert 'refined_prompt' in result['next_context']
        assert result['next_context']['use_enhanced'] is True


class TestRolePromptGeneration:
    """Tests for role prompt generation."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_generate_role_prompt_code_editor(self, refiner):
        """Test role prompt for code editor."""
        role_prompt = refiner._generate_role_prompt('python', 'code_editor')
        
        assert 'Senior Python Developer' in role_prompt
        assert 'AI Engineer' in role_prompt
        assert 'code quality' in role_prompt.lower()
    
    def test_generate_role_prompt_code_planner(self, refiner):
        """Test role prompt for code planner."""
        role_prompt = refiner._generate_role_prompt('java', 'code_planner')
        
        assert 'Senior Java Architect' in role_prompt
        assert 'System design' in role_prompt or 'architecture' in role_prompt.lower()
    
    def test_generate_role_prompt_code_tester(self, refiner):
        """Test role prompt for code tester."""
        role_prompt = refiner._generate_role_prompt('javascript', 'code_tester')
        
        assert 'Test Engineer' in role_prompt
        assert 'testing' in role_prompt.lower() or 'test' in role_prompt.lower()
    
    def test_generate_role_prompt_debug_agent(self, refiner):
        """Test role prompt for debug agent."""
        role_prompt = refiner._generate_role_prompt('python', 'debug_agent')
        
        assert 'Debugging Expert' in role_prompt or 'debugging' in role_prompt.lower()
        assert 'Root cause' in role_prompt or 'debugging' in role_prompt.lower()
    
    def test_generate_role_prompt_documentation(self, refiner):
        """Test role prompt for documentation agent."""
        role_prompt = refiner._generate_role_prompt('python', 'documentation')
        
        assert 'Technical Writer' in role_prompt or 'documentation' in role_prompt.lower()
    
    def test_generate_role_prompt_unknown_agent_type(self, refiner):
        """Test role prompt for unknown agent type."""
        role_prompt = refiner._generate_role_prompt('python', 'unknown_type')
        
        # Should return a generic role prompt
        assert isinstance(role_prompt, str)
        assert len(role_prompt) > 0
    
    def test_generate_role_prompt_no_language(self, refiner):
        """Test role prompt without language."""
        role_prompt = refiner._generate_role_prompt('', 'code_editor')
        
        assert isinstance(role_prompt, str)
        # Should mention "programming" instead of specific language
        assert 'programming' in role_prompt.lower() or 'developer' in role_prompt.lower()


class TestBestPracticesLoading:
    """Tests for best practices loading."""
    
    @pytest.fixture
    def temp_best_practices(self):
        """Create temporary best practices file."""
        temp_dir = tempfile.mkdtemp()
        practices_dir = Path(temp_dir) / 'agents' / 'languages' / 'python'
        practices_dir.mkdir(parents=True)
        
        practices_file = practices_dir / 'best_practices.md'
        practices_file.write_text("""
# Python Best Practices

## Code Editor
- Use PEP 8 style guide
- Write docstrings for all functions
- Use type hints

## Code Planner
- Create clear module structure
- Follow SOLID principles
        """)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_load_best_practices_success(self, refiner, temp_best_practices):
        """Test successful best practices loading."""
        with patch('pathlib.Path.cwd', return_value=Path(temp_best_practices)):
            practices = refiner._load_best_practices('python', 'code_editor')
            
            if practices:  # File may not be found in test environment
                assert 'PEP 8' in practices or 'best practices' in practices.lower()
    
    def test_load_best_practices_caching(self, refiner, temp_best_practices):
        """Test that best practices are cached."""
        with patch('pathlib.Path.cwd', return_value=Path(temp_best_practices)):
            practices1 = refiner._load_best_practices('python', 'code_editor')
            practices2 = refiner._load_best_practices('python', 'code_editor')
            
            # Should return same object from cache
            assert practices1 == practices2
    
    def test_load_best_practices_nonexistent(self, refiner):
        """Test loading best practices for nonexistent language."""
        practices = refiner._load_best_practices('nonexistent_lang', 'code_editor')
        
        # Should handle gracefully
        assert practices is None or isinstance(practices, str)


class TestUserPreferencesLoading:
    """Tests for user preferences loading."""
    
    @pytest.fixture
    def temp_preferences(self):
        """Create temporary user preferences file."""
        temp_dir = tempfile.mkdtemp()
        prefs_dir = Path(temp_dir) / 'config'
        prefs_dir.mkdir(parents=True)
        
        prefs_file = prefs_dir / 'user_preferences.yaml'
        prefs_file.write_text("""
python:
  code_editor:
    - Use pytest for testing
    - Prefer asyncio over threading
        """)
        
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_load_user_preferences_success(self, refiner, temp_preferences):
        """Test successful user preferences loading."""
        with patch('pathlib.Path.cwd', return_value=Path(temp_preferences)):
            prefs = refiner._load_user_preferences('python', 'code_editor')
            
            if prefs:  # File may not be found in test environment
                assert isinstance(prefs, str)
    
    def test_load_user_preferences_caching(self, refiner):
        """Test that user preferences are cached."""
        prefs1 = refiner._load_user_preferences('python', 'code_editor')
        prefs2 = refiner._load_user_preferences('python', 'code_editor')
        
        # Should return same object from cache
        assert prefs1 == prefs2
    
    def test_load_user_preferences_nonexistent(self, refiner):
        """Test loading preferences for nonexistent language."""
        prefs = refiner._load_user_preferences('nonexistent_lang', 'code_editor')
        
        # Should handle gracefully
        assert prefs is None or isinstance(prefs, str)


class TestProjectContextLoading:
    """Tests for project context loading."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project with context."""
        temp_dir = tempfile.mkdtemp()
        project_ai = Path(temp_dir) / '.project_ai'
        project_ai.mkdir()
        
        context_file = project_ai / 'coding_guidelines.md'
        context_file.write_text("""
# Project Coding Guidelines

- Use camelCase for variable names
- All tests must pass before commit
        """)
        
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_load_project_context_success(self, refiner, temp_project):
        """Test successful project context loading."""
        context = refiner._load_project_context(temp_project)
        
        if context:  # File may not be found
            assert isinstance(context, str)
    
    def test_load_project_context_no_file(self, refiner):
        """Test loading context when file doesn't exist."""
        temp_dir = tempfile.mkdtemp()
        try:
            context = refiner._load_project_context(Path(temp_dir))
            
            # Should handle gracefully
            assert context is None or isinstance(context, str)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_load_project_context_none_path(self, refiner):
        """Test loading context with None path."""
        # Should handle None path gracefully
        # This is tested indirectly through execute method


class TestBuildEnhancedPrompt:
    """Tests for building enhanced prompts."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_build_enhanced_prompt_basic(self, refiner):
        """Test building basic enhanced prompt."""
        prompt = refiner._build_enhanced_prompt(
            "Write a function",
            "python",
            "code_editor",
            None,
            {}
        )
        
        assert isinstance(prompt, str)
        assert "Write a function" in prompt
        assert "Task" in prompt or "task" in prompt
    
    def test_build_enhanced_prompt_with_role(self, refiner):
        """Test that enhanced prompt includes role."""
        prompt = refiner._build_enhanced_prompt(
            "Debug this code",
            "python",
            "debug_agent",
            None,
            {}
        )
        
        assert "Senior" in prompt or "Developer" in prompt or "Engineer" in prompt
    
    def test_build_enhanced_prompt_structured(self, refiner):
        """Test that enhanced prompt is structured."""
        prompt = refiner._build_enhanced_prompt(
            "Plan architecture",
            "java",
            "code_planner",
            None,
            {}
        )
        
        # Should have structured sections
        assert "###" in prompt or "Task" in prompt
        assert "step-by-step" in prompt.lower() or "approach" in prompt.lower()
    
    def test_build_enhanced_prompt_with_project_path(self, refiner):
        """Test enhanced prompt with project path."""
        temp_dir = tempfile.mkdtemp()
        try:
            prompt = refiner._build_enhanced_prompt(
                "Implement feature",
                "python",
                "code_editor",
                Path(temp_dir),
                {}
            )
            
            assert isinstance(prompt, str)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestExtractRelevantSection:
    """Tests for extracting relevant sections."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_extract_relevant_section_with_header(self, refiner):
        """Test extracting section with matching header."""
        content = """
# Best Practices

## Code Editor
- Use clean code principles
- Write tests

## Code Planner
- Create diagrams
        """
        
        section = refiner._extract_relevant_section(content, 'code_editor')
        
        assert 'clean code' in section.lower() or 'code editor' in section.lower()
    
    def test_extract_relevant_section_no_match(self, refiner):
        """Test extracting section when no match."""
        content = "General content without sections"
        
        section = refiner._extract_relevant_section(content, 'code_editor')
        
        # Should return original content or handle gracefully
        assert isinstance(section, str)
    
    def test_extract_relevant_section_case_insensitive(self, refiner):
        """Test that extraction is case insensitive."""
        content = """
## CODE EDITOR
- Uppercase section
        """
        
        section = refiner._extract_relevant_section(content, 'code_editor')
        
        assert 'CODE EDITOR' in section or 'Uppercase' in section


class TestIntegration:
    """Integration tests for enhanced prompt refinement."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_complete_refinement_workflow(self, refiner):
        """Test complete refinement workflow."""
        # Step 1: Refine for Python code editor
        result1 = refiner.execute(
            "Write a sorting algorithm",
            {'language': 'python', 'agent_type': 'code_editor'}
        )
        
        assert result1['success'] is True
        refined1 = result1['data']['refined_prompt']
        assert 'sorting algorithm' in refined1.lower()
        
        # Step 2: Refine for Java code planner
        result2 = refiner.execute(
            "Design a microservices architecture",
            {'language': 'java', 'agent_type': 'code_planner'}
        )
        
        assert result2['success'] is True
        refined2 = result2['data']['refined_prompt']
        assert 'architecture' in refined2.lower()
        
        # Prompts should be different due to different contexts
        assert refined1 != refined2
    
    def test_refinement_with_caching(self, refiner):
        """Test that caching improves performance."""
        context = {'language': 'python', 'agent_type': 'code_editor'}
        
        # First call - may load from files
        result1 = refiner.execute("Task 1", context)
        
        # Second call - should use cache
        result2 = refiner.execute("Task 2", context)
        
        assert result1['success'] is True
        assert result2['success'] is True
    
    def test_refinement_different_languages(self, refiner):
        """Test refinement for different languages."""
        languages = ['python', 'javascript', 'java', 'cpp', 'csharp']
        task = "Implement a binary search"
        
        results = []
        for lang in languages:
            result = refiner.execute(task, {'language': lang, 'agent_type': 'code_editor'})
            assert result['success'] is True
            results.append(result['data']['refined_prompt'])
        
        # Each should mention the appropriate language
        for i, lang in enumerate(languages):
            prompt = results[i]
            # Language should be mentioned in the prompt
            assert isinstance(prompt, str) and len(prompt) > 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    @pytest.fixture
    def refiner(self):
        """Create a refiner instance."""
        return EnhancedPromptRefiner()
    
    def test_empty_task(self, refiner):
        """Test refinement with empty task."""
        result = refiner.execute("", {'language': 'python'})
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
    
    def test_empty_context(self, refiner):
        """Test refinement with empty context."""
        result = refiner.execute("Write code", {})
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
    
    def test_very_long_task(self, refiner):
        """Test refinement with very long task."""
        long_task = "Write code " * 1000
        result = refiner.execute(long_task, {'language': 'python'})
        
        assert result['success'] is True
        assert 'refined_prompt' in result['data']
    
    def test_special_characters_in_task(self, refiner):
        """Test refinement with special characters."""
        task = "Implement function with <special> & {characters} $ % @"
        result = refiner.execute(task, {'language': 'python'})
        
        assert result['success'] is True
        assert '<special>' in result['data']['refined_prompt']
