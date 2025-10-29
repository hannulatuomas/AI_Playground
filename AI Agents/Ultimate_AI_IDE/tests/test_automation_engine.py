"""
Tests for Automation Engine Module
"""

import pytest
from src.modules.automation_engine import (
    AutomationEngine,
    TriggerType,
    ActionType,
    AutomationPreferences
)


class TestAutomationEngine:
    """Test automation engine"""
    
    def test_initialization(self):
        """Test engine initialization"""
        engine = AutomationEngine()
        assert engine.enabled is True
        assert len(engine.triggers) == 0
    
    def test_register_and_fire_trigger(self):
        """Test registering and firing trigger"""
        engine = AutomationEngine()
        executed = []
        
        def condition(ctx):
            return ctx.get('should_execute', False)
        
        def handler(ctx):
            executed.append(True)
            return {'success': True}
        
        engine.register_trigger(TriggerType.FILE_SAVE, condition, ActionType.QUALITY_CHECK)
        engine.register_action_handler(ActionType.QUALITY_CHECK, handler)
        
        results = engine.fire_trigger(TriggerType.FILE_SAVE, {'should_execute': True})
        
        assert len(results) == 1
        assert len(executed) == 1
    
    def test_trigger_priority(self):
        """Test trigger priority ordering"""
        engine = AutomationEngine()
        order = []
        
        engine.register_trigger(TriggerType.FILE_SAVE, lambda ctx: True, ActionType.QUALITY_CHECK, priority=5)
        engine.register_trigger(TriggerType.FILE_SAVE, lambda ctx: True, ActionType.REFACTOR, priority=10)
        
        engine.register_action_handler(ActionType.QUALITY_CHECK, lambda ctx: order.append(1) or {'success': True})
        engine.register_action_handler(ActionType.REFACTOR, lambda ctx: order.append(2) or {'success': True})
        
        engine.fire_trigger(TriggerType.FILE_SAVE, {})
        assert order == [2, 1]  # Higher priority first
    
    def test_enable_disable(self):
        """Test enabling/disabling engine"""
        engine = AutomationEngine()
        engine.disable()
        assert engine.enabled is False
        engine.enable()
        assert engine.enabled is True
    
    def test_setup_default_triggers(self):
        """Test default triggers setup"""
        engine = AutomationEngine()
        engine.setup_default_triggers()
        assert len(engine.triggers[TriggerType.FILE_SAVE]) > 0
    
    def test_get_stats(self):
        """Test statistics"""
        engine = AutomationEngine()
        engine.register_trigger(TriggerType.FILE_SAVE, lambda ctx: True, ActionType.QUALITY_CHECK)
        engine.register_action_handler(ActionType.QUALITY_CHECK, lambda ctx: {'success': True})
        engine.fire_trigger(TriggerType.FILE_SAVE, {})
        
        stats = engine.get_stats()
        assert stats['triggers_fired'] == 1
        assert stats['actions_executed'] == 1


class TestAutomationPreferences:
    """Test automation preferences"""
    
    def test_initialization(self):
        """Test preferences initialization"""
        prefs = AutomationPreferences()
        assert prefs.get('auto_quality_check') is True
    
    def test_set_get_preference(self):
        """Test setting and getting preferences"""
        prefs = AutomationPreferences()
        prefs.set('auto_refactor', True)
        assert prefs.get('auto_refactor') is True
    
    def test_reset(self):
        """Test resetting preferences"""
        prefs = AutomationPreferences()
        prefs.set('auto_refactor', True)
        prefs.reset()
        assert prefs.get('auto_refactor') is False
