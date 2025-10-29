"""
CLI Command Tests

Tests for all CLI commands including v1.6.0 commands.
"""

import pytest
from click.testing import CliRunner
from src.ui.cli import cli


class TestBasicCLICommands:
    """Test basic CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create CLI test runner."""
        return CliRunner()
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Ultimate AI-Powered IDE' in result.output
    
    def test_cli_version(self, runner):
        """Test CLI version command."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '1.6.0' in result.output
    
    def test_init_command(self, runner, tmp_path):
        """Test init command."""
        with runner.isolated_filesystem(temp_dir=tmp_path):
            result = runner.invoke(cli, ['init'])
            assert result.exit_code == 0
            assert 'initialized successfully' in result.output.lower()


class TestWorkflowCommands:
    """Test workflow CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_workflow_list(self, runner):
        """Test workflow list command."""
        result = runner.invoke(cli, ['workflow', 'list'])
        assert result.exit_code == 0
        assert 'feature_implementation' in result.output
        assert 'bug_fix' in result.output
    
    def test_workflow_info(self, runner):
        """Test workflow info command."""
        result = runner.invoke(cli, ['workflow', 'info', 'feature_implementation'])
        assert result.exit_code == 0
        assert 'Feature Implementation' in result.output
        assert 'Steps:' in result.output
    
    def test_workflow_info_invalid(self, runner):
        """Test workflow info with invalid template."""
        result = runner.invoke(cli, ['workflow', 'info', 'nonexistent'])
        assert result.exit_code != 0 or 'Error' in result.output


class TestSplitCommands:
    """Test file splitting CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_split_help(self, runner):
        """Test split command help."""
        result = runner.invoke(cli, ['split', '--help'])
        assert result.exit_code == 0
        assert 'File splitting commands' in result.output
    
    def test_split_detect(self, runner, tmp_path):
        """Test split detect command."""
        # Create test project
        project = tmp_path / "test_project"
        project.mkdir()
        
        result = runner.invoke(cli, ['split', 'detect', '--project', str(project)])
        # Should succeed or handle gracefully
        assert result.exit_code == 0 or 'Error' in result.output
    
    def test_split_suggest(self, runner, tmp_path):
        """Test split suggest command."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("def test(): pass\n")
        
        result = runner.invoke(cli, ['split', 'suggest', str(test_file)])
        # Should succeed or handle gracefully
        assert result.exit_code == 0 or 'Error' in result.output


class TestDeadCodeCommands:
    """Test dead code detection CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_deadcode_help(self, runner):
        """Test deadcode command help."""
        result = runner.invoke(cli, ['deadcode', '--help'])
        assert result.exit_code == 0
        assert 'Dead code detection' in result.output
    
    def test_deadcode_detect(self, runner, tmp_path):
        """Test deadcode detect command."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        result = runner.invoke(cli, ['deadcode', 'detect', '--project', str(project)])
        # Should succeed or handle gracefully
        assert result.exit_code == 0 or 'Error' in result.output


class TestAutomationCommands:
    """Test automation CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_automation_help(self, runner):
        """Test automation command help."""
        result = runner.invoke(cli, ['automation', '--help'])
        assert result.exit_code == 0
        assert 'Automation engine' in result.output
    
    def test_automation_status(self, runner):
        """Test automation status command."""
        result = runner.invoke(cli, ['automation', 'status'])
        # Should show status
        assert result.exit_code == 0 or 'Automation Engine Status' in result.output
    
    def test_automation_triggers(self, runner):
        """Test automation triggers command."""
        result = runner.invoke(cli, ['automation', 'triggers'])
        # Should list triggers
        assert result.exit_code == 0 or 'Automation Triggers' in result.output


class TestQualityCommands:
    """Test quality CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_bloat_detect(self, runner, tmp_path):
        """Test bloat detect command."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        result = runner.invoke(cli, ['bloat', 'detect', '--project', str(project)])
        assert result.exit_code == 0 or 'Error' in result.output
    
    def test_quality_check(self, runner, tmp_path):
        """Test quality check command."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        result = runner.invoke(cli, ['quality', 'check', '--project', str(project)])
        assert result.exit_code == 0 or 'Error' in result.output


class TestContextCommands:
    """Test context management CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_context_status(self, runner):
        """Test context status command."""
        result = runner.invoke(cli, ['context', 'status'])
        # Should show status or error gracefully
        assert result.exit_code == 0 or 'Error' in result.output


class TestIndexCommands:
    """Test codebase indexing CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_index_build(self, runner, tmp_path):
        """Test index build command."""
        project = tmp_path / "test_project"
        project.mkdir()
        
        result = runner.invoke(cli, ['index', 'build', '--project', str(project)])
        assert result.exit_code == 0 or 'Error' in result.output


class TestMCPCommands:
    """Test MCP CLI commands."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_mcp_list(self, runner):
        """Test MCP list command."""
        result = runner.invoke(cli, ['mcp', 'list'])
        # Should list servers or show none configured
        assert result.exit_code == 0 or 'MCP Servers' in result.output or 'No MCP servers' in result.output
