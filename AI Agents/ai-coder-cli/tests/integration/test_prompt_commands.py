#!/usr/bin/env python3
"""
Integration tests for prompt management CLI commands.

Tests the complete workflows for:
1. Saving prompts and snippets
2. Listing and filtering prompts
3. Viewing prompt details
4. Editing prompts
5. Deleting prompts
6. Using prompts with variables
7. Import/Export functionality
8. Statistics generation
"""

import pytest
import tempfile
import shutil
import subprocess
import json
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.prompt_manager import PromptManager, PromptScope, PromptType


class TestPromptCommandsIntegration:
    """Integration tests for prompt management commands."""
    
    def setup_method(self):
        """Create temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp(prefix='aiagent_prompt_test_'))
        self.global_storage = self.test_dir / 'global_prompts'
        self.global_storage.mkdir(parents=True)
        
        # Set up environment to use test storage
        self.original_home = os.environ.get('HOME')
        os.environ['HOME'] = str(self.test_dir)
        
        # Create .ai-agent-console directory
        config_dir = self.test_dir / '.ai-agent-console' / 'prompts'
        config_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up temporary directory and restore environment."""
        if self.original_home:
            os.environ['HOME'] = self.original_home
        else:
            os.environ.pop('HOME', None)
        
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_save_and_list_prompt(self):
        """Test saving a prompt and listing it."""
        # Create manager directly
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a prompt
        prompt = manager.save_prompt(
            name="test-prompt",
            content="This is a test prompt",
            description="Test description",
            tags=["test"]
        )
        
        assert prompt is not None
        assert prompt.name == "test-prompt"
        
        # List prompts
        prompts = manager.list_prompts()
        
        assert len(prompts) == 1
        assert prompts[0].name == "test-prompt"
    
    def test_save_prompt_with_variables(self):
        """Test saving a prompt with variables."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a prompt with variables
        prompt = manager.save_prompt(
            name="variable-prompt",
            content="Hello {{name}}, welcome to {{project}}!",
            description="Prompt with variables"
        )
        
        assert "name" in prompt.variables
        assert "project" in prompt.variables
        
        # Use the prompt with variables
        result = manager.use_prompt(
            prompt.prompt_id,
            variables={"name": "Alice", "project": "MyApp"}
        )
        
        assert result == "Hello Alice, welcome to MyApp!"
    
    def test_filter_prompts_by_scope(self):
        """Test filtering prompts by scope."""
        # Create project directory
        project_dir = self.test_dir / 'test_project'
        project_dir.mkdir()
        
        manager = PromptManager(
            global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts',
            project_storage_dir=project_dir / '.project' / 'prompts'
        )
        
        # Save global and project prompts
        manager.save_prompt(
            name="global-prompt",
            content="Global content",
            scope=PromptScope.GLOBAL
        )
        manager.save_prompt(
            name="project-prompt",
            content="Project content",
            scope=PromptScope.PROJECT
        )
        
        # Filter by scope
        global_prompts = manager.list_prompts(scope=PromptScope.GLOBAL)
        project_prompts = manager.list_prompts(scope=PromptScope.PROJECT)
        
        assert len(global_prompts) == 1
        assert global_prompts[0].name == "global-prompt"
        assert len(project_prompts) == 1
        assert project_prompts[0].name == "project-prompt"
    
    def test_filter_prompts_by_type(self):
        """Test filtering prompts by type."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save different types
        manager.save_prompt(
            name="full-prompt",
            content="Full prompt content",
            prompt_type=PromptType.PROMPT
        )
        manager.save_prompt(
            name="code-snippet",
            content="def hello():\n    print('Hello')",
            prompt_type=PromptType.SNIPPET
        )
        
        # Filter by type
        prompts = manager.list_prompts(prompt_type=PromptType.PROMPT)
        snippets = manager.list_prompts(prompt_type=PromptType.SNIPPET)
        
        assert len(prompts) == 1
        assert prompts[0].name == "full-prompt"
        assert len(snippets) == 1
        assert snippets[0].name == "code-snippet"
    
    def test_filter_prompts_by_tags(self):
        """Test filtering prompts by tags."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save prompts with different tags
        manager.save_prompt(
            name="python-prompt",
            content="Python code review",
            tags=["python", "code-review"]
        )
        manager.save_prompt(
            name="javascript-prompt",
            content="JavaScript code review",
            tags=["javascript", "code-review"]
        )
        manager.save_prompt(
            name="docs-prompt",
            content="Generate documentation",
            tags=["documentation"]
        )
        
        # Filter by tags
        code_review = manager.list_prompts(tags=["code-review"])
        python = manager.list_prompts(tags=["python"])
        docs = manager.list_prompts(tags=["documentation"])
        
        assert len(code_review) == 2
        assert len(python) == 1
        assert len(docs) == 1
    
    def test_search_prompts(self):
        """Test searching prompts by term."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save prompts with different content
        manager.save_prompt(
            name="code-review",
            content="Review the code for best practices",
            description="Code review template"
        )
        manager.save_prompt(
            name="bug-fix",
            content="Fix the bug in the code",
            description="Bug fixing guide"
        )
        manager.save_prompt(
            name="documentation",
            content="Write documentation for the API",
            description="API documentation guide"
        )
        
        # Search by term
        code_prompts = manager.list_prompts(search_term="code")
        review_prompts = manager.list_prompts(search_term="review")
        api_prompts = manager.list_prompts(search_term="api")
        
        assert len(code_prompts) == 2  # code-review and bug-fix
        assert len(review_prompts) == 1  # code-review
        assert len(api_prompts) == 1  # documentation
    
    def test_edit_prompt(self):
        """Test editing an existing prompt."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a prompt
        prompt = manager.save_prompt(
            name="test-prompt",
            content="Original content",
            description="Original description",
            tags=["original"]
        )
        
        # Edit the prompt
        updated = manager.update_prompt(
            prompt_id=prompt.prompt_id,
            content="Updated content",
            description="Updated description",
            tags=["updated", "modified"]
        )
        
        assert updated.content == "Updated content"
        assert updated.description == "Updated description"
        assert updated.tags == ["updated", "modified"]
        assert updated.name == "test-prompt"  # Name unchanged
    
    def test_delete_prompt(self):
        """Test deleting a prompt."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a prompt
        prompt = manager.save_prompt(
            name="to-delete",
            content="This will be deleted"
        )
        
        # Verify it exists
        assert manager.get_prompt(prompt.prompt_id) is not None
        
        # Delete the prompt
        success = manager.delete_prompt(prompt.prompt_id)
        
        assert success is True
        assert manager.get_prompt(prompt.prompt_id) is None
        assert len(manager.list_prompts()) == 0
    
    def test_use_prompt_increments_usage(self):
        """Test that using a prompt increments its usage count."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a prompt
        prompt = manager.save_prompt(
            name="test-prompt",
            content="Test content"
        )
        
        assert prompt.usage_count == 0
        
        # Use the prompt multiple times
        for i in range(3):
            manager.use_prompt(prompt.prompt_id)
        
        # Check usage count
        updated_prompt = manager.get_prompt(prompt.prompt_id)
        assert updated_prompt.usage_count == 3
    
    def test_export_and_import_prompts(self):
        """Test exporting and importing prompts."""
        manager1 = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save some prompts
        manager1.save_prompt(
            name="prompt1",
            content="Content 1",
            description="Description 1",
            tags=["tag1"]
        )
        manager1.save_prompt(
            name="prompt2",
            content="Content 2",
            description="Description 2",
            tags=["tag2"]
        )
        
        # Export prompts
        export_file = self.test_dir / 'exported_prompts.json'
        count = manager1.export_prompts(export_file)
        
        assert count == 2
        assert export_file.exists()
        
        # Create new manager with different storage
        new_storage = self.test_dir / 'new_storage'
        new_storage.mkdir()
        manager2 = PromptManager(global_storage_dir=new_storage)
        
        # Import prompts
        imported_count = manager2.import_prompts(export_file)
        
        assert imported_count == 2
        
        # Verify imported prompts
        prompts = manager2.list_prompts()
        assert len(prompts) == 2
        assert any(p.name == "prompt1" for p in prompts)
        assert any(p.name == "prompt2" for p in prompts)
    
    def test_export_with_filters(self):
        """Test exporting prompts with filters."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save prompts with different tags
        manager.save_prompt(
            name="python-prompt",
            content="Python content",
            tags=["python", "code"]
        )
        manager.save_prompt(
            name="javascript-prompt",
            content="JavaScript content",
            tags=["javascript", "code"]
        )
        manager.save_prompt(
            name="docs-prompt",
            content="Docs content",
            tags=["documentation"]
        )
        
        # Export only python prompts
        export_file = self.test_dir / 'python_prompts.json'
        count = manager.export_prompts(export_file, tags=["python"])
        
        assert count == 1
        
        # Verify exported data
        with open(export_file, 'r') as f:
            data = json.load(f)
        
        assert len(data['prompts']) == 1
        assert data['prompts'][0]['name'] == "python-prompt"
    
    def test_import_with_overwrite(self):
        """Test importing prompts with overwrite option."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save existing prompt
        manager.save_prompt(
            name="existing",
            content="Original content",
            description="Original description"
        )
        
        # Export another prompt with same name
        export_data = {
            'version': '1.0',
            'prompts': [
                {
                    'prompt_id': 'new-id',
                    'name': 'existing',
                    'description': 'Updated description',
                    'content': 'Updated content',
                    'prompt_type': 'prompt',
                    'scope': 'global',
                    'tags': ['updated'],
                    'variables': [],
                    'created_at': '2025-10-14T10:00:00',
                    'updated_at': '2025-10-14T10:00:00',
                    'usage_count': 0,
                    'metadata': {}
                }
            ]
        }
        
        import_file = self.test_dir / 'import.json'
        with open(import_file, 'w') as f:
            json.dump(export_data, f)
        
        # Import without overwrite (should skip)
        count = manager.import_prompts(import_file, overwrite=False)
        assert count == 0
        
        prompt = manager.get_prompt_by_name("existing")
        assert prompt.content == "Original content"
        
        # Import with overwrite (should update)
        count = manager.import_prompts(import_file, overwrite=True)
        assert count == 1
        
        prompt = manager.get_prompt_by_name("existing")
        assert prompt.content == "Updated content"
        assert prompt.description == "Updated description"
    
    def test_prompt_statistics(self):
        """Test getting prompt statistics."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save various prompts
        manager.save_prompt(
            name="prompt1",
            content="Content 1",
            prompt_type=PromptType.PROMPT,
            scope=PromptScope.GLOBAL,
            tags=["python", "code"]
        )
        manager.save_prompt(
            name="snippet1",
            content="Content 2",
            prompt_type=PromptType.SNIPPET,
            scope=PromptScope.GLOBAL,
            tags=["javascript"]
        )
        
        # Use one prompt multiple times
        prompt = manager.get_prompt_by_name("prompt1")
        for _ in range(5):
            manager.use_prompt(prompt.prompt_id)
        
        # Get statistics
        stats = manager.get_stats()
        
        assert stats['total'] == 2
        assert stats['global'] == 2
        assert stats['project'] == 0
        assert stats['prompts'] == 1
        assert stats['snippets'] == 1
        assert 'python' in stats['tags']
        assert 'javascript' in stats['tags']
        assert len(stats['most_used']) > 0
        assert stats['most_used'][0]['name'] == 'prompt1'
        assert stats['most_used'][0]['usage_count'] == 5
    
    def test_persistence_across_sessions(self):
        """Test that prompts persist across manager instances."""
        storage_dir = self.test_dir / '.ai-agent-console' / 'prompts'
        
        # Create first manager and save prompts
        manager1 = PromptManager(global_storage_dir=storage_dir)
        manager1.save_prompt(
            name="persistent-prompt",
            content="This should persist",
            description="Persistence test",
            tags=["persistence"]
        )
        
        # Create second manager (simulating new session)
        manager2 = PromptManager(global_storage_dir=storage_dir)
        
        # Verify prompt exists
        prompt = manager2.get_prompt_by_name("persistent-prompt")
        
        assert prompt is not None
        assert prompt.name == "persistent-prompt"
        assert prompt.content == "This should persist"
        assert prompt.description == "Persistence test"
        assert "persistence" in prompt.tags
    
    def test_variable_substitution_workflow(self):
        """Test complete workflow with variable substitution."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save a template prompt
        template = manager.save_prompt(
            name="code-review-template",
            content="""Review the following {{language}} code:

Focus Areas:
- {{focus_area_1}}
- {{focus_area_2}}

Project: {{project_name}}""",
            description="Code review template with variables",
            tags=["template", "code-review"]
        )
        
        # Verify variables detected
        assert "language" in template.variables
        assert "focus_area_1" in template.variables
        assert "focus_area_2" in template.variables
        assert "project_name" in template.variables
        
        # Use the template with variables
        result = manager.use_prompt(
            template.prompt_id,
            variables={
                "language": "Python",
                "focus_area_1": "Error handling",
                "focus_area_2": "Performance",
                "project_name": "MyApp"
            }
        )
        
        assert "Python" in result
        assert "Error handling" in result
        assert "Performance" in result
        assert "MyApp" in result
        assert "{{" not in result  # No unreplaced variables
    
    def test_complex_filtering(self):
        """Test combining multiple filters."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save various prompts
        manager.save_prompt(
            name="python-code-review",
            content="Python code review",
            prompt_type=PromptType.PROMPT,
            scope=PromptScope.GLOBAL,
            tags=["python", "code-review"]
        )
        manager.save_prompt(
            name="python-snippet",
            content="Python code snippet",
            prompt_type=PromptType.SNIPPET,
            scope=PromptScope.GLOBAL,
            tags=["python", "snippet"]
        )
        manager.save_prompt(
            name="javascript-code-review",
            content="JavaScript code review",
            prompt_type=PromptType.PROMPT,
            scope=PromptScope.GLOBAL,
            tags=["javascript", "code-review"]
        )
        
        # Filter by type and tags
        python_prompts = manager.list_prompts(
            prompt_type=PromptType.PROMPT,
            tags=["python"]
        )
        
        assert len(python_prompts) == 1
        assert python_prompts[0].name == "python-code-review"
        
        # Filter by tags and search
        code_review_prompts = manager.list_prompts(
            tags=["code-review"],
            search_term="code"
        )
        
        assert len(code_review_prompts) == 2


class TestPromptCommandsErrorHandling:
    """Integration tests for error handling in prompt commands."""
    
    def setup_method(self):
        """Create temporary directory for testing."""
        self.test_dir = Path(tempfile.mkdtemp(prefix='aiagent_prompt_err_test_'))
        os.environ['HOME'] = str(self.test_dir)
        
        config_dir = self.test_dir / '.ai-agent-console' / 'prompts'
        config_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up temporary directory."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_save_duplicate_name_error(self):
        """Test that saving duplicate name raises error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        # Save first prompt
        manager.save_prompt(name="duplicate", content="First")
        
        # Try to save with same name
        with pytest.raises(ValueError, match="already exists"):
            manager.save_prompt(name="duplicate", content="Second")
    
    def test_use_nonexistent_prompt_error(self):
        """Test that using non-existent prompt raises error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        with pytest.raises(ValueError, match="not found"):
            manager.use_prompt("nonexistent-id")
    
    def test_update_nonexistent_prompt_error(self):
        """Test that updating non-existent prompt raises error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        with pytest.raises(ValueError, match="not found"):
            manager.update_prompt("nonexistent-id", content="New content")
    
    def test_missing_variables_error(self):
        """Test that missing variables raise error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        prompt = manager.save_prompt(
            name="template",
            content="Hello {{name}}, you are {{age}} years old."
        )
        
        with pytest.raises(ValueError, match="Missing required variables"):
            manager.use_prompt(prompt.prompt_id, variables={"name": "Alice"})
    
    def test_empty_name_error(self):
        """Test that empty name raises error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        with pytest.raises(ValueError, match="cannot be empty"):
            manager.save_prompt(name="", content="Content")
    
    def test_project_scope_without_project_error(self):
        """Test that project scope without project raises error."""
        manager = PromptManager(global_storage_dir=self.test_dir / '.ai-agent-console' / 'prompts')
        
        with pytest.raises(ValueError, match="no active project"):
            manager.save_prompt(
                name="test",
                content="content",
                scope=PromptScope.PROJECT
            )


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
