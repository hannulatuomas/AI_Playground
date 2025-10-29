"""
Tests for Prompt Manager Module
"""

import pytest
from pathlib import Path
import tempfile
from src.modules.prompt_manager import (
    PromptManager, TemplateEngine, DefaultPrompts, Prompt
)


@pytest.fixture
def temp_prompts_file():
    """Create temporary prompts file."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


def test_prompt_manager_add(temp_prompts_file):
    """Test adding a prompt."""
    manager = PromptManager(temp_prompts_file)
    
    prompt = manager.add_prompt(
        name="test_prompt",
        template="Generate {language} code for {task}",
        category="testing"
    )
    
    assert prompt.name == "test_prompt"
    assert len(prompt.variables) == 2
    assert "language" in prompt.variables
    assert "task" in prompt.variables


def test_prompt_manager_get(temp_prompts_file):
    """Test getting and rendering a prompt."""
    manager = PromptManager(temp_prompts_file)
    
    manager.add_prompt(
        name="code_gen",
        template="Generate {language} code for {purpose}"
    )
    
    rendered = manager.get_prompt(
        "code_gen",
        language="Python",
        purpose="testing"
    )
    
    assert rendered == "Generate Python code for testing"


def test_prompt_manager_update(temp_prompts_file):
    """Test updating a prompt."""
    manager = PromptManager(temp_prompts_file)
    
    manager.add_prompt(
        name="test",
        template="Old template"
    )
    
    success = manager.update_prompt(
        name="test",
        template="New template"
    )
    
    assert success is True
    assert manager.prompts["test"].template == "New template"


def test_prompt_manager_delete(temp_prompts_file):
    """Test deleting a prompt."""
    manager = PromptManager(temp_prompts_file)
    
    manager.add_prompt(name="test", template="Test")
    success = manager.delete_prompt("test")
    
    assert success is True
    assert "test" not in manager.prompts


def test_prompt_manager_list(temp_prompts_file):
    """Test listing prompts."""
    manager = PromptManager(temp_prompts_file)
    
    manager.add_prompt(name="test1", template="Test 1", category="cat1")
    manager.add_prompt(name="test2", template="Test 2", category="cat2")
    manager.add_prompt(name="test3", template="Test 3", category="cat1")
    
    all_prompts = manager.list_prompts()
    assert len(all_prompts) == 3
    
    cat1_prompts = manager.list_prompts(category="cat1")
    assert len(cat1_prompts) == 2


def test_template_engine_simple():
    """Test simple variable substitution."""
    engine = TemplateEngine()
    
    template = "Hello {name}, you are {age} years old"
    result = engine.render(template, {"name": "Alice", "age": 30})
    
    assert result == "Hello Alice, you are 30 years old"


def test_template_engine_conditional():
    """Test conditional rendering."""
    engine = TemplateEngine()
    
    template = "{% if premium %}Premium user{% endif %}"
    
    result1 = engine.render(template, {"premium": True})
    assert "Premium user" in result1
    
    result2 = engine.render(template, {"premium": False})
    assert "Premium user" not in result2


def test_template_engine_loop():
    """Test loop rendering."""
    engine = TemplateEngine()
    
    template = "{% for item in items %}{item}, {% endfor %}"
    result = engine.render(template, {"items": ["a", "b", "c"]})
    
    assert "a" in result
    assert "b" in result
    assert "c" in result


def test_template_engine_validate():
    """Test template validation."""
    engine = TemplateEngine()
    
    valid_template = "Hello {name}"
    is_valid, errors = engine.validate_template(valid_template)
    assert is_valid is True
    assert len(errors) == 0
    
    invalid_template = "{% if test %}No endif"
    is_valid, errors = engine.validate_template(invalid_template)
    assert is_valid is False
    assert len(errors) > 0


def test_template_engine_extract_variables():
    """Test variable extraction."""
    engine = TemplateEngine()
    
    template = "Generate {language} code for {task} with {framework}"
    variables = engine.extract_variables(template)
    
    assert "language" in variables
    assert "task" in variables
    assert "framework" in variables


def test_default_prompts_get_all():
    """Test getting all default prompts."""
    prompts = DefaultPrompts.get_all_defaults()
    
    assert len(prompts) > 0
    assert "generate_function" in prompts
    assert "generate_tests" in prompts


def test_default_prompts_get_specific():
    """Test getting specific default prompt."""
    prompt = DefaultPrompts.get_prompt("generate_function")
    
    assert "template" in prompt
    assert "category" in prompt
    assert prompt["category"] == "code_generation"


def test_default_prompts_by_category():
    """Test getting prompts by category."""
    code_gen_prompts = DefaultPrompts.get_by_category("code_generation")
    
    assert len(code_gen_prompts) > 0
    assert all(p["category"] == "code_generation" for p in code_gen_prompts.values())


def test_prompt_persistence(temp_prompts_file):
    """Test that prompts persist across instances."""
    # Create and add prompt
    manager1 = PromptManager(temp_prompts_file)
    manager1.add_prompt(name="persistent", template="Test template")
    
    # Create new instance and check prompt exists
    manager2 = PromptManager(temp_prompts_file)
    assert "persistent" in manager2.prompts
    assert manager2.prompts["persistent"].template == "Test template"
