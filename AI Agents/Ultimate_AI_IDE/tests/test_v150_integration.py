"""
Tests for v1.5.0 Integration

Comprehensive integration tests for Security Scanner, Dependency Manager,
and Template Validator features.
"""

import pytest
from pathlib import Path
from src.core.orchestrator import UAIDE
from src.modules.automation_engine import TriggerType, ActionType


class TestV150Integration:
    """Test v1.5.0 feature integration."""
    
    @pytest.fixture
    def uaide(self, tmp_path):
        """Create UAIDE instance for testing"""
        # Create minimal config
        config_file = tmp_path / "config.json"
        config_file.write_text('{"ai": {"model_path": "test"}, "database": {"path": ":memory:"}}')
        
        uaide = UAIDE(str(config_file))
        return uaide
    
    def test_all_v150_modules_initialized(self, uaide):
        """Test that all v1.5.0 modules are initialized"""
        # Security scanner should be lazy-initialized
        assert hasattr(uaide, 'scan_security')
        assert hasattr(uaide, 'scan_vulnerabilities')
        assert hasattr(uaide, 'check_dependencies')
        assert hasattr(uaide, 'detect_insecure_patterns')
        assert hasattr(uaide, 'scan_secrets')
        assert hasattr(uaide, 'generate_security_report')
        
        # Template validator methods
        assert hasattr(uaide, 'validate_template')
        assert hasattr(uaide, 'get_template_score')
    
    def test_security_scanner_orchestrator_integration(self, tmp_path, uaide):
        """Test security scanner integration with orchestrator"""
        # Create test project
        (tmp_path / "test.py").write_text('password = "secret123"\n')
        
        # Run security scan through orchestrator
        result = uaide.scan_security(str(tmp_path))
        
        assert result.success is True
        assert 'scan_result' in result.data
        assert 'risk_score' in result.data
    
    def test_dependency_manager_orchestrator_integration(self, tmp_path):
        """Test dependency manager through orchestrator"""
        from src.modules.dependency_manager import DependencyManager
        
        # Create test project
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        manager = DependencyManager(str(tmp_path))
        updates = manager.check_outdated()
        
        assert isinstance(updates, list)
    
    def test_template_validator_orchestrator_integration(self, tmp_path, uaide):
        """Test template validator integration with orchestrator"""
        # Create test project with issues
        (tmp_path / "test.py").write_text('# TODO: Implement\ndef func():\n    pass\n')
        
        # Validate through orchestrator
        result = uaide.validate_template(str(tmp_path))
        
        assert result.success is True
        assert 'score' in result.data
        assert 'result' in result.data
    
    def test_template_score_method(self, tmp_path, uaide):
        """Test get_template_score method"""
        result = uaide.get_template_score(str(tmp_path))
        
        assert result.success is True
        assert 'score' in result.data
        assert 0 <= result.data['score'] <= 100
    
    def test_automation_engine_v150_triggers(self, uaide):
        """Test that v1.5.0 triggers are registered"""
        # Check new trigger types exist
        assert TriggerType.SECURITY_ISSUE in TriggerType
        assert TriggerType.DEPENDENCY_OUTDATED in TriggerType
        assert TriggerType.TEMPLATE_ISSUE in TriggerType
    
    def test_automation_engine_v150_actions(self, uaide):
        """Test that v1.5.0 actions are registered"""
        # Check new action types exist
        assert ActionType.SECURITY_SCAN in ActionType
        assert ActionType.DEPENDENCY_UPDATE in ActionType
        assert ActionType.TEMPLATE_VALIDATE in ActionType
    
    def test_automation_handlers_registered(self, uaide):
        """Test that v1.5.0 automation handlers are registered"""
        # Check handlers are registered
        assert ActionType.SECURITY_SCAN in uaide.automation_engine.action_handlers
        assert ActionType.DEPENDENCY_UPDATE in uaide.automation_engine.action_handlers
        assert ActionType.TEMPLATE_VALIDATE in uaide.automation_engine.action_handlers
    
    def test_security_scan_automation(self, tmp_path, uaide):
        """Test automated security scanning"""
        context = {'project_path': str(tmp_path)}
        
        # Trigger automated security scan
        result = uaide._auto_security_scan(context)
        
        assert result is not None
        assert result.success is True
    
    def test_template_validation_automation(self, tmp_path, uaide):
        """Test automated template validation"""
        context = {'project_path': str(tmp_path)}
        
        # Trigger automated template validation
        result = uaide._auto_template_validate(context)
        
        assert result is not None
        assert result.success is True
    
    def test_event_bus_integration(self, tmp_path, uaide):
        """Test event bus integration for v1.5.0 features"""
        events_received = []
        
        def event_handler(event_data):
            events_received.append(event_data)
        
        # Subscribe to events
        uaide.event_bus.subscribe('security_scan_complete', event_handler)
        uaide.event_bus.subscribe('template_validated', event_handler)
        
        # Trigger actions
        uaide.scan_security(str(tmp_path))
        uaide.validate_template(str(tmp_path))
        
        # Check events were emitted
        assert len(events_received) >= 2
    
    def test_v150_features_dont_break_existing(self, uaide):
        """Test that v1.5.0 features don't break existing functionality"""
        # Test that existing orchestrator methods still work
        assert hasattr(uaide, 'project_manager')
        assert hasattr(uaide, 'code_generator')
        assert hasattr(uaide, 'test_generator')
        assert hasattr(uaide, 'doc_manager')
        assert hasattr(uaide, 'refactorer')
        
        # Test v1.4.0 features still work
        assert hasattr(uaide, 'workflow_engine')
        assert hasattr(uaide, 'file_splitter')
        assert hasattr(uaide, 'automation_engine')


class TestCLIIntegration:
    """Test CLI integration for v1.5.0 features."""
    
    def test_security_commands_registered(self):
        """Test security CLI commands are registered"""
        from src.ui.cli import cli
        
        # Check security command group exists
        assert 'security' in [cmd.name for cmd in cli.commands.values()]
    
    def test_deps_commands_registered(self):
        """Test dependency CLI commands are registered"""
        from src.ui.cli import cli
        
        # Check deps command group exists
        assert 'deps' in [cmd.name for cmd in cli.commands.values()]
    
    def test_template_commands_registered(self):
        """Test template CLI commands are registered"""
        from src.ui.cli import cli
        
        # Check template command group exists
        assert 'template' in [cmd.name for cmd in cli.commands.values()]


class TestGUIIntegration:
    """Test GUI integration for v1.5.0 features."""
    
    @pytest.mark.skipif(not pytest.importorskip("tkinter", reason="tkinter not available"), reason="GUI tests require tkinter")
    def test_security_tab_exists(self):
        """Test security tab is integrated"""
        try:
            from src.ui.gui.tab_security import SecurityTab
            assert SecurityTab is not None
        except ImportError as e:
            if "tkinter" in str(e).lower():
                pytest.skip("tkinter not available")
            raise
    
    @pytest.mark.skipif(not pytest.importorskip("tkinter", reason="tkinter not available"), reason="GUI tests require tkinter")
    def test_dependencies_tab_exists(self):
        """Test dependencies tab is integrated"""
        try:
            from src.ui.gui.tab_dependencies import DependenciesTab
            assert DependenciesTab is not None
        except ImportError as e:
            if "tkinter" in str(e).lower():
                pytest.skip("tkinter not available")
            raise
    
    @pytest.mark.skipif(not pytest.importorskip("tkinter", reason="tkinter not available"), reason="GUI tests require tkinter")
    def test_template_tab_exists(self):
        """Test template tab is integrated"""
        try:
            from src.ui.gui.tab_template import TemplateTab
            assert TemplateTab is not None
        except ImportError as e:
            if "tkinter" in str(e).lower():
                pytest.skip("tkinter not available")
            raise


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_security_workflow(self, tmp_path):
        """Test complete security scanning workflow"""
        # Create project with security issues
        (tmp_path / "app.py").write_text('''
password = "hardcoded123"
api_key = "sk_live_abcdefghijklmnop"

def query_db(user_id):
    cursor.execute("SELECT * FROM users WHERE id=" + user_id)
''')
        
        from src.modules.security_scanner import SecurityScanner
        
        scanner = SecurityScanner(str(tmp_path))
        result = scanner.scan_project()
        
        # Should detect multiple issues
        assert result.summary['total'] > 0
        assert result.risk_score > 0
        
        # Generate report
        from src.modules.security_scanner import SecurityReporter
        reporter = SecurityReporter()
        report = reporter.generate(result, 'text')
        
        assert len(report) > 0
    
    def test_full_dependency_workflow(self, tmp_path):
        """Test complete dependency management workflow"""
        # Create project
        (tmp_path / "requirements.txt").write_text("requests==2.0.0\n")
        
        from src.modules.dependency_manager import DependencyManager
        
        manager = DependencyManager(str(tmp_path))
        
        # Check outdated
        updates = manager.check_outdated()
        assert isinstance(updates, list)
        
        # Get safe updates
        safe_updates = manager.suggest_safe_updates()
        assert isinstance(safe_updates, list)
    
    def test_full_template_workflow(self, tmp_path):
        """Test complete template validation workflow"""
        # Create project with template issues
        (tmp_path / "app.py").write_text('''
# TODO: Implement this
def example_function():
    pass

# FIXME: This is broken
def demo_function():
    raise NotImplementedError
''')
        
        from src.modules.template_validator import TemplateValidator
        
        validator = TemplateValidator(str(tmp_path))
        result = validator.validate_project()
        
        # Should detect issues
        assert result['total_issues'] > 0
        assert result['summary']['todo'] > 0
        assert result['summary']['placeholder'] > 0
        
        # Get score
        score = validator.get_clean_score()
        assert 0 <= score <= 100
