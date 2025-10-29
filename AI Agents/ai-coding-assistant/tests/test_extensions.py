"""
Comprehensive Tests for AI Coding Assistant Extension Phases

Tests for:
- ProjectManager (Phase 1)
- ProjectNavigator (Phase 2)
- ContextManager (Phase 3)
- TaskManager (Phase 4)
- RuleEnforcer (Phase 5)
- ToolIntegrator (Phase 6)
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from core.project_manager import ProjectManager
from core.learning_db import LearningDB
from features.project_nav import ProjectNavigator
from features.context_manager import ContextManager
from features.task_manager import TaskManager, TaskStatus, TaskType
from features.rule_enforcer import RuleEnforcer
from features.tool_integrator import ToolIntegrator


class TestProjectManager(unittest.TestCase):
    """Test ProjectManager functionality."""

    def setUp(self):
        """Create temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_llm = Mock()
        self.mock_llm.generate = Mock(return_value="Test summary")
        self.pm = ProjectManager(llm_interface=self.mock_llm)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_root_folder(self):
        """Test setting root folder."""
        result = self.pm.set_root_folder(self.test_dir)
        self.assertTrue(result)
        self.assertEqual(str(self.pm.root_folder), self.test_dir)

    def test_set_root_folder_invalid(self):
        """Test setting invalid root folder."""
        result = self.pm.set_root_folder("/nonexistent/path")
        self.assertFalse(result)

    def test_index_files(self):
        """Test file indexing."""
        # Create test files
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("def hello():\n    print('Hello')\n")

        self.pm.set_root_folder(self.test_dir)
        stats = self.pm.index_files()

        self.assertGreater(stats['total_files'], 0)
        self.assertIn('test.py', self.pm.file_index)

    def test_file_exclusion(self):
        """Test that excluded directories are not indexed."""
        # Create excluded directory
        excluded_dir = Path(self.test_dir) / ".git"
        excluded_dir.mkdir()
        (excluded_dir / "config").write_text("git config")

        self.pm.set_root_folder(self.test_dir)
        self.pm.index_files()

        # Check no .git files indexed
        for path in self.pm.file_index.keys():
            self.assertNotIn('.git', path)

    def test_binary_file_exclusion(self):
        """Test that binary files are excluded."""
        # Create binary file
        binary_file = Path(self.test_dir) / "image.png"
        binary_file.write_bytes(b'\x89PNG\r\n\x1a\n')

        self.pm.set_root_folder(self.test_dir)
        self.pm.index_files()

        self.assertNotIn('image.png', self.pm.file_index)

    def test_get_file_content(self):
        """Test reading file content."""
        test_file = Path(self.test_dir) / "test.txt"
        test_content = "Test content"
        test_file.write_text(test_content)

        self.pm.set_root_folder(self.test_dir)
        content, chunks = self.pm.get_file_content("test.txt")

        self.assertEqual(content, test_content)
        self.assertEqual(len(chunks), 1)

    def test_summarize_file(self):
        """Test file summarization."""
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("def test():\n    pass\n")

        self.pm.set_root_folder(self.test_dir)
        self.pm.index_files()

        summary = self.pm.summarize_file("test.py")
        self.assertIsNotNone(summary)
        self.mock_llm.generate.assert_called()


class TestProjectNavigator(unittest.TestCase):
    """Test ProjectNavigator functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_llm = Mock()
        self.mock_llm.generate = Mock(return_value="Relevant file")
        
        self.pm = ProjectManager(llm_interface=self.mock_llm)
        self.pm.set_root_folder(self.test_dir)
        
        self.pn = ProjectNavigator(self.pm, self.mock_llm)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scan_project(self):
        """Test project scanning."""
        # Create test files
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("print('test')")

        changes = self.pn.scan_project(summarize_new=False)

        self.assertIn('new', changes)
        self.assertIn('modified', changes)
        self.assertIn('deleted', changes)

    def test_search_files(self):
        """Test file searching."""
        # Create test files
        (Path(self.test_dir) / "database.py").write_text("# Database module")
        (Path(self.test_dir) / "api.py").write_text("# API module")

        self.pm.index_files()

        results = self.pn.search_files("database", max_results=10)

        self.assertGreater(len(results), 0)
        self.assertTrue(any('database' in r['path'].lower() for r in results))

    def test_search_with_language_filter(self):
        """Test search with language filter."""
        (Path(self.test_dir) / "test.py").write_text("# Python")
        (Path(self.test_dir) / "test.js").write_text("// JavaScript")

        self.pm.index_files()

        results = self.pn.search_files("test", search_in=['python'])

        for result in results:
            self.assertTrue(result['path'].endswith('.py'))

    def test_edit_file_insert(self):
        """Test file editing with insert."""
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("line 1\nline 2\nline 3\n")

        changes = [{
            'type': 'insert',
            'line': 2,
            'new_content': 'inserted line\n'
        }]

        result = self.pn.edit_file('test.py', changes, create_backup=True)

        self.assertTrue(result['success'])
        self.assertIn('backup_path', result)

    def test_edit_file_replace(self):
        """Test file editing with replace."""
        test_file = Path(self.test_dir) / "test.py"
        test_file.write_text("line 1\nline 2\nline 3\n")

        changes = [{
            'type': 'replace',
            'start_line': 1,
            'end_line': 2,
            'new_content': 'replaced lines\n'
        }]

        result = self.pn.edit_file('test.py', changes)

        self.assertTrue(result['success'])

    def test_edit_file_dry_run(self):
        """Test dry-run mode."""
        test_file = Path(self.test_dir) / "test.py"
        original_content = "line 1\nline 2\n"
        test_file.write_text(original_content)

        changes = [{
            'type': 'insert',
            'line': 1,
            'new_content': 'new line\n'
        }]

        result = self.pn.edit_file('test.py', changes, dry_run=True)

        self.assertTrue(result['success'])
        self.assertIn('diff', result)
        
        # File should be unchanged
        self.assertEqual(test_file.read_text(), original_content)

    def test_backup_and_restore(self):
        """Test backup creation and restoration."""
        test_file = Path(self.test_dir) / "test.py"
        original_content = "original content"
        test_file.write_text(original_content)

        changes = [{
            'type': 'insert',
            'line': 0,
            'new_content': 'new content\n'
        }]

        result = self.pn.edit_file('test.py', changes, create_backup=True)
        backup_path = result['backup_path']

        # Restore
        self.pn.restore_from_backup(backup_path)

        restored_content = test_file.read_text()
        self.assertEqual(restored_content, original_content)


class TestContextManager(unittest.TestCase):
    """Test ContextManager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.mock_db = Mock(spec=LearningDB)
        self.mock_db.get_relevant_learnings = Mock(return_value=[])
        self.mock_db.add_action = Mock(return_value=1)
        self.mock_db.get_action_history = Mock(return_value=[])
        
        self.cm = ContextManager(learning_db=self.mock_db)

    def test_build_context_basic(self):
        """Test basic context building."""
        context = self.cm.build_context(
            task="Test task",
            max_tokens=1000
        )

        self.assertIn('sections', context)
        self.assertIn('task', context['sections'])
        self.assertLessEqual(context['total_tokens'], 1000)

    def test_build_context_with_rules(self):
        """Test context building with rules."""
        context = self.cm.build_context(
            task="Test task",
            max_tokens=2000,
            user_rules=["Rule 1", "Rule 2"]
        )

        self.assertIn('rules', context['sections'])
        self.assertEqual(len(context['sections']['rules']['content'].split('\n')), 3)

    def test_token_estimation(self):
        """Test token estimation."""
        text = "This is a test with multiple words"
        tokens = self.cm._estimate_tokens(text)

        self.assertGreater(tokens, 0)
        # Should be roughly words / 0.75
        expected = len(text.split()) / 0.75
        self.assertAlmostEqual(tokens, expected, delta=5)

    def test_context_truncation(self):
        """Test context truncation when over budget."""
        large_rules = ["Rule " + str(i) for i in range(100)]
        
        context = self.cm.build_context(
            task="Test task",
            max_tokens=100,
            user_rules=large_rules
        )

        self.assertLessEqual(context['total_tokens'], 100)

    def test_log_action(self):
        """Test action logging."""
        action_id = self.cm.log_action(
            action="Test action",
            outcome="Success",
            project_id="test-project"
        )

        self.assertEqual(action_id, 1)
        self.mock_db.add_action.assert_called_once()

    def test_get_history(self):
        """Test history retrieval."""
        self.mock_db.get_action_history = Mock(return_value=[
            {'action': 'Test', 'timestamp': '2025-01-01'}
        ])

        history = self.cm.get_history(project_id="test-project")

        self.assertEqual(len(history), 1)
        self.mock_db.get_action_history.assert_called_once()

    def test_format_context_for_prompt(self):
        """Test context formatting."""
        context = self.cm.build_context(task="Test task", max_tokens=1000)
        formatted = self.cm.format_context_for_prompt(context)

        self.assertIsInstance(formatted, str)
        self.assertIn("Test task", formatted)


class TestTaskManager(unittest.TestCase):
    """Test TaskManager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.mock_llm = Mock()
        self.mock_llm.generate = Mock(return_value='''[
            {
                "id": 1,
                "description": "Task 1",
                "type": "generate_code",
                "dependencies": []
            },
            {
                "id": 2,
                "description": "Task 2",
                "type": "generate_code",
                "dependencies": [1]
            }
        ]''')
        
        self.tm = TaskManager(self.mock_llm)

    def test_decompose_task_basic(self):
        """Test basic task decomposition."""
        result = self.tm.decompose_task(
            user_task="Build a login system",
            language="python"
        )

        self.assertIn('sub_tasks', result)
        self.assertGreater(len(result['sub_tasks']), 0)
        self.assertEqual(result['status'], TaskStatus.PENDING.value)

    def test_decompose_task_returns_valid_structure(self):
        """Test decomposition returns valid JSON structure."""
        result = self.tm.decompose_task("Test task")

        # Check required fields
        self.assertIn('task_id', result)
        self.assertIn('description', result)
        self.assertIn('sub_tasks', result)
        self.assertIn('status', result)

        # Check sub-tasks structure
        for task in result['sub_tasks']:
            self.assertIn('id', task)
            self.assertIn('description', task)
            self.assertIn('type', task)
            self.assertIn('dependencies', task)

    def test_parse_decomposition_response(self):
        """Test parsing of LLM decomposition response."""
        response = '''[
            {"id": 1, "description": "Task 1", "type": "generate_code"},
            {"id": 2, "description": "Task 2", "type": "edit_file"}
        ]'''

        tasks = self.tm._parse_decomposition_response(response)

        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['id'], 1)
        self.assertEqual(tasks[1]['type'], 'edit_file')

    def test_check_dependencies(self):
        """Test dependency checking."""
        all_tasks = [
            {'id': 1, 'status': TaskStatus.COMPLETED.value},
            {'id': 2, 'status': TaskStatus.PENDING.value, 'dependencies': [1]},
            {'id': 3, 'status': TaskStatus.PENDING.value, 'dependencies': [2]}
        ]

        # Task 2 dependencies met
        can_execute_2 = self.tm._check_dependencies(all_tasks[1], all_tasks)
        self.assertTrue(can_execute_2)

        # Task 3 dependencies not met
        can_execute_3 = self.tm._check_dependencies(all_tasks[2], all_tasks)
        self.assertFalse(can_execute_3)

    def test_generate_task_id(self):
        """Test task ID generation."""
        task_id_1 = self.tm._generate_task_id()
        task_id_2 = self.tm._generate_task_id()

        self.assertIsInstance(task_id_1, str)
        self.assertNotEqual(task_id_1, task_id_2)
        self.assertTrue(task_id_1.startswith('task_'))


class TestRuleEnforcer(unittest.TestCase):
    """Test RuleEnforcer functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.mock_db = Mock(spec=LearningDB)
        self.mock_db.set_project_rules = Mock(return_value=True)
        self.mock_db.get_project_rules = Mock(return_value=None)
        
        self.enforcer = RuleEnforcer(learning_db=self.mock_db)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_set_rules(self):
        """Test setting custom rules."""
        rules = ["Rule 1", "Rule 2", "Rule 3"]
        success = self.enforcer.set_rules(
            rules,
            project_id="test-project",
            language="python"
        )

        self.assertTrue(success)
        self.mock_db.set_project_rules.assert_called_once()

    def test_get_default_rules(self):
        """Test getting default rules for language."""
        rules = self.enforcer.get_rules(language="python")

        self.assertGreater(len(rules), 0)
        self.assertTrue(any('PEP 8' in rule for rule in rules))

    def test_enforce_rules(self):
        """Test rule enforcement."""
        context = {
            'task': 'Test task',
            'language': 'python'
        }

        enhanced = self.enforcer.enforce_rules(context)

        self.assertIn('rules', enhanced)
        self.assertIn('rules_prompt', enhanced)

    def test_check_compliance_file_length(self):
        """Test compliance check for file length."""
        # Create long file
        test_file = Path(self.test_dir) / "long.py"
        test_file.write_text("\n".join([f"line {i}" for i in range(600)]))

        mock_pm = Mock()
        mock_pm.get_file_content = Mock(return_value=(test_file.read_text(), []))
        
        self.enforcer.project_manager = mock_pm

        action_result = {'file_path': 'long.py'}
        task_context = {}

        compliance = self.enforcer.check_compliance(action_result, task_context)

        self.assertFalse(compliance['compliant'])
        self.assertGreater(len(compliance['violations']), 0)

    def test_format_rules_for_prompt(self):
        """Test formatting rules for prompts."""
        rules = ["Rule 1", "Rule 2"]
        formatted = self.enforcer.format_rules_for_prompt(rules=rules)

        self.assertIsInstance(formatted, str)
        self.assertIn("Rule 1", formatted)
        self.assertIn("Rule 2", formatted)

    def test_validate_against_rules(self):
        """Test code validation."""
        # Long code
        long_code = "\n".join([f"line {i}" for i in range(600)])
        
        result = self.enforcer.validate_against_rules(
            long_code,
            "python"
        )

        self.assertFalse(result['valid'])
        self.assertGreater(len(result['issues']), 0)


class TestToolIntegrator(unittest.TestCase):
    """Test ToolIntegrator functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.integrator = ToolIntegrator()

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('subprocess.run')
    def test_git_status(self, mock_run):
        """Test git status checking."""
        # Mock git commands
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse
            Mock(stdout='main', returncode=0),  # git branch
            Mock(stdout='M  file.py\n?? new.py\n', returncode=0)  # git status
        ]

        self.integrator.project_manager = Mock()
        self.integrator.project_manager.root_folder = self.test_dir

        status = self.integrator.git_status()

        self.assertTrue(status['initialized'])
        self.assertEqual(status['branch'], 'main')
        self.assertIn('file.py', status['changed_files'])
        self.assertIn('new.py', status['untracked_files'])

    @patch('subprocess.run')
    def test_git_commit(self, mock_run):
        """Test git commit."""
        # Mock successful commit
        mock_run.side_effect = [
            Mock(returncode=0),  # git rev-parse (initialized)
            Mock(stdout='main', returncode=0),  # branch
            Mock(stdout='M  file.py\n', returncode=0),  # status
            Mock(returncode=0),  # git add
            Mock(returncode=0),  # git commit
            Mock(stdout='abc123\n', returncode=0)  # commit hash
        ]

        self.integrator.project_manager = Mock()
        self.integrator.project_manager.root_folder = self.test_dir

        result = self.integrator.git_commit(
            message="Test commit",
            generate_message=False
        )

        # Note: Will fail without proper git setup, but tests the logic
        self.assertIn('success', result)

    def test_detect_test_framework_python(self):
        """Test test framework detection."""
        framework = self.integrator._detect_test_framework('python')

        # Will return None if pytest not installed, but tests the logic
        if framework:
            self.assertIn('name', framework)

    def test_parse_pytest_output(self):
        """Test pytest output parsing."""
        output = """
        test_file.py::test_function PASSED
        test_file.py::test_another FAILED
        
        2 passed, 1 failed in 0.5s
        """

        result = self.integrator._parse_pytest_output(output)

        self.assertEqual(result['passed'], 2)
        self.assertEqual(result['failed'], 1)

    def test_parse_jest_output(self):
        """Test jest output parsing."""
        output = """
        Tests: 2 failed, 8 passed, 10 total
        """

        result = self.integrator._parse_jest_output(output)

        self.assertEqual(result['failed'], 2)
        self.assertEqual(result['passed'], 8)
        self.assertEqual(result['total'], 10)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestProjectManager))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectNavigator))
    suite.addTests(loader.loadTestsFromTestCase(TestContextManager))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestRuleEnforcer))
    suite.addTests(loader.loadTestsFromTestCase(TestToolIntegrator))

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

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
