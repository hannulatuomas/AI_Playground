"""
Unit tests for PromptManager.

Tests the prompt and snippet management system including CRUD operations,
variable substitution, persistence, and filtering functionality.
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from core.prompt_manager import (
    PromptManager,
    Prompt,
    PromptScope,
    PromptType,
    create_prompt_manager
)


class TestPrompt:
    """Tests for the Prompt dataclass."""
    
    def test_prompt_creation(self):
        """Test creating a prompt with default values."""
        prompt = Prompt(
            name="test-prompt",
            content="This is a test prompt"
        )
        
        assert prompt.name == "test-prompt"
        assert prompt.content == "This is a test prompt"
        assert prompt.description == ""
        assert prompt.prompt_type == PromptType.PROMPT
        assert prompt.scope == PromptScope.GLOBAL
        assert prompt.tags == []
        assert prompt.variables == []
        assert isinstance(prompt.prompt_id, str)
        assert len(prompt.prompt_id) > 0
        assert isinstance(prompt.created_at, datetime)
        assert isinstance(prompt.updated_at, datetime)
        assert prompt.usage_count == 0
        assert prompt.metadata == {}
    
    def test_prompt_with_custom_values(self):
        """Test creating a prompt with custom values."""
        prompt = Prompt(
            prompt_id="custom-id",
            name="Custom Prompt",
            description="Test description",
            content="Test content",
            prompt_type=PromptType.SNIPPET,
            scope=PromptScope.PROJECT,
            tags=["test", "example"],
            usage_count=5,
            metadata={"key": "value"}
        )
        
        assert prompt.prompt_id == "custom-id"
        assert prompt.name == "Custom Prompt"
        assert prompt.description == "Test description"
        assert prompt.content == "Test content"
        assert prompt.prompt_type == PromptType.SNIPPET
        assert prompt.scope == PromptScope.PROJECT
        assert prompt.tags == ["test", "example"]
        assert prompt.usage_count == 5
        assert prompt.metadata == {"key": "value"}
    
    def test_variable_extraction(self):
        """Test automatic variable extraction from content."""
        prompt = Prompt(
            name="test",
            content="Hello {{name}}, welcome to {{project}}!"
        )
        
        assert "name" in prompt.variables
        assert "project" in prompt.variables
        assert len(prompt.variables) == 2
    
    def test_variable_extraction_duplicates(self):
        """Test that duplicate variables are removed."""
        prompt = Prompt(
            name="test",
            content="{{var1}} and {{var2}} and {{var1}} again"
        )
        
        assert len(prompt.variables) == 2
        assert "var1" in prompt.variables
        assert "var2" in prompt.variables
    
    def test_variable_substitution(self):
        """Test variable substitution in content."""
        prompt = Prompt(
            name="test",
            content="Hello {{name}}, you are {{age}} years old."
        )
        
        result = prompt.substitute_variables({
            "name": "Alice",
            "age": "30"
        })
        
        assert result == "Hello Alice, you are 30 years old."
    
    def test_variable_substitution_missing_vars(self):
        """Test that missing variables raise an error."""
        prompt = Prompt(
            name="test",
            content="Hello {{name}}, you are {{age}} years old."
        )
        
        with pytest.raises(ValueError, match="Missing required variables"):
            prompt.substitute_variables({"name": "Alice"})
    
    def test_increment_usage(self):
        """Test incrementing usage count."""
        prompt = Prompt(name="test", content="test")
        
        assert prompt.usage_count == 0
        initial_update = prompt.updated_at
        
        prompt.increment_usage()
        
        assert prompt.usage_count == 1
        assert prompt.updated_at >= initial_update
    
    def test_prompt_to_dict(self):
        """Test converting prompt to dictionary."""
        prompt = Prompt(
            name="Test Prompt",
            description="Test description",
            content="Test content",
            tags=["test"]
        )
        
        data = prompt.to_dict()
        
        assert isinstance(data, dict)
        assert data['name'] == "Test Prompt"
        assert data['description'] == "Test description"
        assert data['content'] == "Test content"
        assert data['tags'] == ["test"]
        assert 'prompt_id' in data
        assert 'created_at' in data
        assert 'updated_at' in data
        assert 'prompt_type' in data
        assert 'scope' in data
        assert 'variables' in data
        assert 'usage_count' in data
        assert 'metadata' in data
    
    def test_prompt_from_dict(self):
        """Test creating prompt from dictionary."""
        data = {
            'prompt_id': 'test-id',
            'name': 'Test Prompt',
            'description': 'Test description',
            'content': 'Hello {{name}}',
            'prompt_type': 'prompt',
            'scope': 'global',
            'tags': ['test'],
            'variables': ['name'],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'usage_count': 3,
            'metadata': {'key': 'value'}
        }
        
        prompt = Prompt.from_dict(data)
        
        assert prompt.prompt_id == 'test-id'
        assert prompt.name == 'Test Prompt'
        assert prompt.description == 'Test description'
        assert prompt.content == 'Hello {{name}}'
        assert prompt.prompt_type == PromptType.PROMPT
        assert prompt.scope == PromptScope.GLOBAL
        assert prompt.tags == ['test']
        assert prompt.variables == ['name']
        assert prompt.usage_count == 3
        assert prompt.metadata == {'key': 'value'}


class TestPromptManager:
    """Tests for the PromptManager class."""
    
    @pytest.fixture
    def temp_global_dir(self):
        """Create a temporary directory for global storage."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary directory for project storage."""
        temp_path = Path(tempfile.mkdtemp())
        yield temp_path
        shutil.rmtree(temp_path)
    
    @pytest.fixture
    def manager(self, temp_global_dir, temp_project_dir):
        """Create a PromptManager instance for testing."""
        return PromptManager(
            global_storage_dir=temp_global_dir,
            project_storage_dir=temp_project_dir
        )
    
    def test_manager_initialization(self, temp_global_dir):
        """Test PromptManager initialization."""
        manager = PromptManager(global_storage_dir=temp_global_dir)
        
        assert manager.global_storage_dir == temp_global_dir
        assert manager.global_storage_file == temp_global_dir / 'prompts.json'
        assert manager.global_storage_dir.exists()
        assert isinstance(manager._prompts, dict)
    
    def test_manager_initialization_with_project(self, temp_global_dir, temp_project_dir):
        """Test PromptManager initialization with project storage."""
        manager = PromptManager(
            global_storage_dir=temp_global_dir,
            project_storage_dir=temp_project_dir
        )
        
        assert manager.project_storage_dir == temp_project_dir
        assert manager.project_storage_dir.exists()
    
    def test_save_prompt_global(self, manager):
        """Test saving a global prompt."""
        prompt = manager.save_prompt(
            name="test-prompt",
            content="Test content",
            description="Test description",
            tags=["test"]
        )
        
        assert prompt.name == "test-prompt"
        assert prompt.content == "Test content"
        assert prompt.description == "Test description"
        assert prompt.scope == PromptScope.GLOBAL
        assert prompt.tags == ["test"]
        assert prompt.prompt_id in manager._prompts
    
    def test_save_prompt_project(self, manager):
        """Test saving a project-scoped prompt."""
        prompt = manager.save_prompt(
            name="project-prompt",
            content="Project content",
            scope=PromptScope.PROJECT
        )
        
        assert prompt.name == "project-prompt"
        assert prompt.scope == PromptScope.PROJECT
        assert prompt.prompt_id in manager._prompts
    
    def test_save_prompt_duplicate_name(self, manager):
        """Test that saving a prompt with duplicate name raises error."""
        manager.save_prompt(
            name="duplicate",
            content="Content 1"
        )
        
        with pytest.raises(ValueError, match="already exists"):
            manager.save_prompt(
                name="duplicate",
                content="Content 2"
            )
    
    def test_save_prompt_empty_name(self, manager):
        """Test that saving a prompt with empty name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.save_prompt(
                name="",
                content="Content"
            )
    
    def test_save_prompt_project_scope_without_project_dir(self, temp_global_dir):
        """Test that project-scoped prompt fails without project directory."""
        manager = PromptManager(global_storage_dir=temp_global_dir)
        
        with pytest.raises(ValueError, match="no active project"):
            manager.save_prompt(
                name="test",
                content="content",
                scope=PromptScope.PROJECT
            )
    
    def test_get_prompt(self, manager):
        """Test retrieving a prompt by ID."""
        saved_prompt = manager.save_prompt(
            name="test",
            content="content"
        )
        
        retrieved = manager.get_prompt(saved_prompt.prompt_id)
        
        assert retrieved is not None
        assert retrieved.prompt_id == saved_prompt.prompt_id
        assert retrieved.name == saved_prompt.name
    
    def test_get_prompt_not_found(self, manager):
        """Test retrieving a non-existent prompt."""
        result = manager.get_prompt("non-existent-id")
        
        assert result is None
    
    def test_get_prompt_by_name(self, manager):
        """Test retrieving a prompt by name."""
        manager.save_prompt(
            name="test-prompt",
            content="content"
        )
        
        prompt = manager.get_prompt_by_name("test-prompt")
        
        assert prompt is not None
        assert prompt.name == "test-prompt"
    
    def test_get_prompt_by_name_with_scope(self, manager):
        """Test retrieving a prompt by name with scope filter."""
        manager.save_prompt(
            name="global-prompt",
            content="global content",
            scope=PromptScope.GLOBAL
        )
        manager.save_prompt(
            name="project-prompt",
            content="project content",
            scope=PromptScope.PROJECT
        )
        
        global_prompt = manager.get_prompt_by_name("global-prompt", PromptScope.GLOBAL)
        project_prompt = manager.get_prompt_by_name("project-prompt", PromptScope.PROJECT)
        
        assert global_prompt is not None
        assert global_prompt.scope == PromptScope.GLOBAL
        assert project_prompt is not None
        assert project_prompt.scope == PromptScope.PROJECT
    
    def test_list_prompts_empty(self, manager):
        """Test listing prompts when none exist."""
        prompts = manager.list_prompts()
        
        assert prompts == []
    
    def test_list_prompts(self, manager):
        """Test listing all prompts."""
        manager.save_prompt(name="prompt1", content="content1")
        manager.save_prompt(name="prompt2", content="content2")
        
        prompts = manager.list_prompts()
        
        assert len(prompts) == 2
        assert any(p.name == "prompt1" for p in prompts)
        assert any(p.name == "prompt2" for p in prompts)
    
    def test_list_prompts_by_scope(self, manager):
        """Test filtering prompts by scope."""
        manager.save_prompt(
            name="global1",
            content="content",
            scope=PromptScope.GLOBAL
        )
        manager.save_prompt(
            name="project1",
            content="content",
            scope=PromptScope.PROJECT
        )
        
        global_prompts = manager.list_prompts(scope=PromptScope.GLOBAL)
        project_prompts = manager.list_prompts(scope=PromptScope.PROJECT)
        
        assert len(global_prompts) == 1
        assert global_prompts[0].name == "global1"
        assert len(project_prompts) == 1
        assert project_prompts[0].name == "project1"
    
    def test_list_prompts_by_type(self, manager):
        """Test filtering prompts by type."""
        manager.save_prompt(
            name="prompt1",
            content="content",
            prompt_type=PromptType.PROMPT
        )
        manager.save_prompt(
            name="snippet1",
            content="content",
            prompt_type=PromptType.SNIPPET
        )
        
        prompts = manager.list_prompts(prompt_type=PromptType.PROMPT)
        snippets = manager.list_prompts(prompt_type=PromptType.SNIPPET)
        
        assert len(prompts) == 1
        assert prompts[0].name == "prompt1"
        assert len(snippets) == 1
        assert snippets[0].name == "snippet1"
    
    def test_list_prompts_by_tags(self, manager):
        """Test filtering prompts by tags."""
        manager.save_prompt(
            name="prompt1",
            content="content",
            tags=["python", "code"]
        )
        manager.save_prompt(
            name="prompt2",
            content="content",
            tags=["javascript", "code"]
        )
        manager.save_prompt(
            name="prompt3",
            content="content",
            tags=["documentation"]
        )
        
        python_prompts = manager.list_prompts(tags=["python"])
        code_prompts = manager.list_prompts(tags=["code"])
        
        assert len(python_prompts) == 1
        assert python_prompts[0].name == "prompt1"
        assert len(code_prompts) == 2
    
    def test_list_prompts_by_search_term(self, manager):
        """Test searching prompts by term."""
        manager.save_prompt(
            name="code-review",
            content="Review the code",
            description="Code review template"
        )
        manager.save_prompt(
            name="bug-fix",
            content="Fix the bug",
            description="Bug fixing guide"
        )
        
        review_prompts = manager.list_prompts(search_term="review")
        code_prompts = manager.list_prompts(search_term="code")
        
        assert len(review_prompts) == 1
        assert review_prompts[0].name == "code-review"
        assert len(code_prompts) == 1
    
    def test_update_prompt(self, manager):
        """Test updating an existing prompt."""
        prompt = manager.save_prompt(
            name="test",
            content="original content",
            description="original description"
        )
        
        updated = manager.update_prompt(
            prompt_id=prompt.prompt_id,
            content="updated content",
            description="updated description"
        )
        
        assert updated.content == "updated content"
        assert updated.description == "updated description"
        assert updated.name == "test"  # Unchanged
    
    def test_update_prompt_not_found(self, manager):
        """Test updating a non-existent prompt."""
        with pytest.raises(ValueError, match="not found"):
            manager.update_prompt(
                prompt_id="non-existent",
                content="content"
            )
    
    def test_update_prompt_name(self, manager):
        """Test updating prompt name."""
        prompt = manager.save_prompt(name="old-name", content="content")
        
        updated = manager.update_prompt(
            prompt_id=prompt.prompt_id,
            name="new-name"
        )
        
        assert updated.name == "new-name"
    
    def test_update_prompt_tags(self, manager):
        """Test updating prompt tags."""
        prompt = manager.save_prompt(
            name="test",
            content="content",
            tags=["old"]
        )
        
        updated = manager.update_prompt(
            prompt_id=prompt.prompt_id,
            tags=["new", "tags"]
        )
        
        assert updated.tags == ["new", "tags"]
    
    def test_delete_prompt(self, manager):
        """Test deleting a prompt."""
        prompt = manager.save_prompt(name="test", content="content")
        
        success = manager.delete_prompt(prompt.prompt_id)
        
        assert success is True
        assert manager.get_prompt(prompt.prompt_id) is None
    
    def test_delete_prompt_not_found(self, manager):
        """Test deleting a non-existent prompt."""
        success = manager.delete_prompt("non-existent")
        
        assert success is False
    
    def test_use_prompt(self, manager):
        """Test using a prompt."""
        prompt = manager.save_prompt(
            name="test",
            content="Hello {{name}}!"
        )
        
        result = manager.use_prompt(
            prompt_id=prompt.prompt_id,
            variables={"name": "World"}
        )
        
        assert result == "Hello World!"
        
        # Check usage count incremented
        updated_prompt = manager.get_prompt(prompt.prompt_id)
        assert updated_prompt.usage_count == 1
    
    def test_use_prompt_without_variables(self, manager):
        """Test using a prompt without variables."""
        prompt = manager.save_prompt(
            name="test",
            content="Hello World!"
        )
        
        result = manager.use_prompt(prompt_id=prompt.prompt_id)
        
        assert result == "Hello World!"
    
    def test_use_prompt_not_found(self, manager):
        """Test using a non-existent prompt."""
        with pytest.raises(ValueError, match="not found"):
            manager.use_prompt(prompt_id="non-existent")
    
    def test_use_prompt_missing_variables(self, manager):
        """Test using a prompt with missing variables."""
        prompt = manager.save_prompt(
            name="test",
            content="Hello {{name}}!"
        )
        
        # When variables dict is provided but incomplete, should raise error
        with pytest.raises(ValueError, match="Missing required variables"):
            manager.use_prompt(prompt_id=prompt.prompt_id, variables={"wrong_var": "value"})
    
    def test_persistence_global(self, temp_global_dir):
        """Test that global prompts persist across manager instances."""
        # Create first manager and save prompt
        manager1 = PromptManager(global_storage_dir=temp_global_dir)
        manager1.save_prompt(name="test", content="content")
        
        # Create second manager and verify prompt exists
        manager2 = PromptManager(global_storage_dir=temp_global_dir)
        prompt = manager2.get_prompt_by_name("test")
        
        assert prompt is not None
        assert prompt.name == "test"
        assert prompt.content == "content"
    
    def test_persistence_project(self, temp_global_dir, temp_project_dir):
        """Test that project prompts persist across manager instances."""
        # Create first manager and save prompt
        manager1 = PromptManager(
            global_storage_dir=temp_global_dir,
            project_storage_dir=temp_project_dir
        )
        manager1.save_prompt(
            name="test",
            content="content",
            scope=PromptScope.PROJECT
        )
        
        # Create second manager and verify prompt exists
        manager2 = PromptManager(
            global_storage_dir=temp_global_dir,
            project_storage_dir=temp_project_dir
        )
        prompt = manager2.get_prompt_by_name("test")
        
        assert prompt is not None
        assert prompt.name == "test"
        assert prompt.scope == PromptScope.PROJECT
    
    def test_export_prompts(self, manager, tmp_path):
        """Test exporting prompts to a file."""
        manager.save_prompt(name="prompt1", content="content1")
        manager.save_prompt(name="prompt2", content="content2")
        
        output_file = tmp_path / "export.json"
        count = manager.export_prompts(output_file)
        
        assert count == 2
        assert output_file.exists()
        
        # Verify exported data
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        assert 'prompts' in data
        assert len(data['prompts']) == 2
    
    def test_export_prompts_by_scope(self, manager, tmp_path):
        """Test exporting prompts filtered by scope."""
        manager.save_prompt(
            name="global1",
            content="content",
            scope=PromptScope.GLOBAL
        )
        manager.save_prompt(
            name="project1",
            content="content",
            scope=PromptScope.PROJECT
        )
        
        output_file = tmp_path / "export.json"
        count = manager.export_prompts(output_file, scope=PromptScope.GLOBAL)
        
        assert count == 1
    
    def test_import_prompts(self, manager, tmp_path):
        """Test importing prompts from a file."""
        # Create export data
        export_data = {
            'version': '1.0',
            'prompts': [
                {
                    'prompt_id': 'id1',
                    'name': 'imported1',
                    'description': 'desc1',
                    'content': 'content1',
                    'prompt_type': 'prompt',
                    'scope': 'global',
                    'tags': ['test'],
                    'variables': [],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'usage_count': 0,
                    'metadata': {}
                }
            ]
        }
        
        import_file = tmp_path / "import.json"
        with open(import_file, 'w') as f:
            json.dump(export_data, f)
        
        # Import
        count = manager.import_prompts(import_file)
        
        assert count == 1
        prompt = manager.get_prompt_by_name("imported1")
        assert prompt is not None
        assert prompt.name == "imported1"
    
    def test_import_prompts_with_overwrite(self, manager, tmp_path):
        """Test importing prompts with overwrite option."""
        # Save existing prompt
        manager.save_prompt(
            name="existing",
            content="original content"
        )
        
        # Create import data with same name
        export_data = {
            'version': '1.0',
            'prompts': [
                {
                    'prompt_id': 'new-id',
                    'name': 'existing',
                    'description': 'updated',
                    'content': 'updated content',
                    'prompt_type': 'prompt',
                    'scope': 'global',
                    'tags': [],
                    'variables': [],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat(),
                    'usage_count': 0,
                    'metadata': {}
                }
            ]
        }
        
        import_file = tmp_path / "import.json"
        with open(import_file, 'w') as f:
            json.dump(export_data, f)
        
        # Import with overwrite
        count = manager.import_prompts(import_file, overwrite=True)
        
        assert count == 1
        prompt = manager.get_prompt_by_name("existing")
        assert prompt.content == "updated content"
        assert prompt.description == "updated"
    
    def test_get_stats(self, manager):
        """Test getting statistics about prompts."""
        # Create various prompts
        manager.save_prompt(
            name="global1",
            content="content",
            scope=PromptScope.GLOBAL,
            prompt_type=PromptType.PROMPT,
            tags=["python"]
        )
        manager.save_prompt(
            name="project1",
            content="content",
            scope=PromptScope.PROJECT,
            prompt_type=PromptType.SNIPPET,
            tags=["javascript"]
        )
        
        # Use one prompt to increment usage
        prompt = manager.get_prompt_by_name("global1")
        manager.use_prompt(prompt.prompt_id)
        
        stats = manager.get_stats()
        
        assert stats['total'] == 2
        assert stats['global'] == 1
        assert stats['project'] == 1
        assert stats['prompts'] == 1
        assert stats['snippets'] == 1
        assert 'python' in stats['tags']
        assert 'javascript' in stats['tags']
        assert len(stats['most_used']) > 0


class TestCreatePromptManager:
    """Tests for the create_prompt_manager convenience function."""
    
    def test_create_without_project(self):
        """Test creating a manager without project directory."""
        manager = create_prompt_manager()
        
        assert manager is not None
        assert manager.global_storage_dir is not None
        assert manager.project_storage_dir is None
    
    def test_create_with_project(self, tmp_path):
        """Test creating a manager with project directory."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()
        
        manager = create_prompt_manager(project_dir)
        
        assert manager is not None
        assert manager.global_storage_dir is not None
        assert manager.project_storage_dir is not None
        assert manager.project_storage_dir == project_dir / '.project' / 'prompts'
