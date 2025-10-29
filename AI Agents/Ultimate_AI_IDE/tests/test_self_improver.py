"""
Tests for Self-Improver Module
"""

import pytest
import tempfile
from pathlib import Path
from src.modules.self_improver import (
    EventLogger, PatternAnalyzer, Learner, Adapter
)


class MockAIBackend:
    """Mock AI backend for testing."""
    
    def query(self, prompt, max_tokens=1000):
        """Mock query method."""
        return "Analysis result"


@pytest.fixture
def mock_ai():
    """Provide mock AI backend."""
    return MockAIBackend()


@pytest.fixture
def temp_log_file():
    """Create temporary log file."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    temp_file.close()
    yield temp_file.name
    Path(temp_file.name).unlink(missing_ok=True)


def test_event_logger_log_event(temp_log_file):
    """Test logging an event."""
    logger = EventLogger(temp_log_file)
    
    entry = logger.log_event(
        module='test_module',
        action='test_action',
        input_data={'input': 'test'},
        output_data={'output': 'result'},
        success=True
    )
    
    assert entry.module == 'test_module'
    assert entry.success is True


def test_event_logger_read_logs(temp_log_file):
    """Test reading logs."""
    logger = EventLogger(temp_log_file)
    
    logger.log_event('module1', 'action1', {}, {}, True)
    logger.log_event('module2', 'action2', {}, {}, False, error='Test error')
    
    logs = logger.read_logs()
    
    assert len(logs) == 2


def test_event_logger_get_errors(temp_log_file):
    """Test getting errors."""
    logger = EventLogger(temp_log_file)
    
    logger.log_event('module1', 'action1', {}, {}, True)
    logger.log_event('module2', 'action2', {}, {}, False, error='Error 1')
    logger.log_event('module3', 'action3', {}, {}, False, error='Error 2')
    
    errors = logger.get_recent_errors(limit=10)
    
    assert len(errors) == 2


def test_event_logger_success_rate(temp_log_file):
    """Test success rate calculation."""
    logger = EventLogger(temp_log_file)
    
    logger.log_event('module1', 'action1', {}, {}, True)
    logger.log_event('module1', 'action2', {}, {}, True)
    logger.log_event('module1', 'action3', {}, {}, False, error='Error')
    
    rate = logger.get_success_rate('module1')
    
    assert rate == pytest.approx(0.666, rel=0.01)


def test_pattern_analyzer():
    """Test pattern analyzer."""
    analyzer = PatternAnalyzer()
    
    from src.modules.self_improver.logger import LogEntry
    
    logs = [
        LogEntry('2025-01-01', 'module1', 'action1', {}, {}, False, 
                error='Import error', error_type='ImportError'),
        LogEntry('2025-01-01', 'module1', 'action2', {}, {}, False,
                error='Import error', error_type='ImportError'),
        LogEntry('2025-01-01', 'module2', 'action3', {}, {}, True)
    ]
    
    patterns = analyzer.analyze_errors(logs)
    
    assert len(patterns) > 0
    assert patterns[0].error_type == 'ImportError'
    assert patterns[0].frequency == 2


def test_pattern_analyzer_module_health():
    """Test module health analysis."""
    analyzer = PatternAnalyzer()
    
    from src.modules.self_improver.logger import LogEntry
    
    logs = [
        LogEntry('2025-01-01', 'module1', 'action1', {}, {}, True),
        LogEntry('2025-01-01', 'module1', 'action2', {}, {}, True),
        LogEntry('2025-01-01', 'module1', 'action3', {}, {}, False, error='Error'),
        LogEntry('2025-01-01', 'module2', 'action1', {}, {}, True)
    ]
    
    health = analyzer.get_module_health(logs)
    
    assert 'module1' in health
    assert 'module2' in health
    assert health['module1']['success_rate'] == pytest.approx(0.666, rel=0.01)


def test_learner(mock_ai):
    """Test learner."""
    learner = Learner(mock_ai)
    
    from src.modules.self_improver.analyzer import ErrorPattern
    
    patterns = [
        ErrorPattern(
            error_type='ImportError',
            frequency=5,
            common_contexts=[],
            affected_modules=['module1'],
            sample_errors=['Import failed']
        )
    ]
    
    insights = learner.learn_from_errors(patterns)
    
    assert len(insights) > 0
    assert insights[0].category == 'error_prevention'


def test_adapter():
    """Test adapter."""
    adapter = Adapter()
    
    from src.modules.self_improver.learner import Insight
    
    insights = [
        Insight(
            category='error_prevention',
            title='Recurring import error',
            description='Import errors occur frequently',
            recommendation='Add import checking',
            priority='high',
            evidence=[]
        )
    ]
    
    adaptations = adapter.adapt_from_insights(insights)
    
    assert len(adaptations) > 0
    assert adaptations[0].adaptation_type in ['prompt_update', 'rule_addition', 'parameter_change']
