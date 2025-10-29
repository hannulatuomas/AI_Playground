"""
Automation Engine Module

Event-driven automation for common development tasks.
Automatically triggers actions based on project events.
"""

import time
from typing import Dict, List, Callable, Optional, Any
from enum import Enum
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of automation triggers"""
    FILE_SAVE = "file_save"
    FILE_CHANGE = "file_change"
    TEST_FAILURE = "test_failure"
    QUALITY_ISSUE = "quality_issue"
    LARGE_FILE = "large_file"
    BLOAT_DETECTED = "bloat_detected"
    CONTEXT_FULL = "context_full"
    BUILD_FAILURE = "build_failure"
    SECURITY_ISSUE = "security_issue"  # v1.5.0
    DEPENDENCY_OUTDATED = "dependency_outdated"  # v1.5.0
    TEMPLATE_ISSUE = "template_issue"  # v1.5.0
    MANUAL = "manual"


class ActionType(Enum):
    """Types of automated actions"""
    QUALITY_CHECK = "quality_check"
    REFACTOR = "refactor"
    BUG_FIX = "bug_fix"
    FILE_SPLIT = "file_split"
    BLOAT_CLEANUP = "bloat_cleanup"
    CONTEXT_PRUNE = "context_prune"
    RUN_TESTS = "run_tests"
    UPDATE_DOCS = "update_docs"
    SECURITY_SCAN = "security_scan"  # v1.5.0
    DEPENDENCY_UPDATE = "dependency_update"  # v1.5.0
    TEMPLATE_VALIDATE = "template_validate"  # v1.5.0


class AutomationEngine:
    """Manage automated workflows and triggers"""
    
    def __init__(self):
        """Initialize automation engine"""
        self.triggers = defaultdict(list)  # trigger_type -> list of rules
        self.action_handlers = {}  # action_type -> handler function
        self.enabled = True
        self.execution_log = []
        self.stats = {
            'triggers_fired': 0,
            'actions_executed': 0,
            'actions_failed': 0
        }
    
    def register_trigger(self, trigger_type: TriggerType, 
                        condition: Callable[[Dict], bool],
                        action: ActionType,
                        priority: int = 5,
                        enabled: bool = True):
        """
        Register an automation trigger
        
        Args:
            trigger_type: Type of trigger
            condition: Function that checks if action should be taken
            action: Action to execute
            priority: Priority (1-10, higher = more important)
            enabled: Whether trigger is enabled
        """
        rule = {
            'condition': condition,
            'action': action,
            'priority': priority,
            'enabled': enabled,
            'created_at': time.time()
        }
        
        self.triggers[trigger_type].append(rule)
        logger.info(f"Registered trigger: {trigger_type.value} -> {action.value}")
    
    def register_action_handler(self, action_type: ActionType, handler: Callable):
        """
        Register an action handler
        
        Args:
            action_type: Type of action
            handler: Function to handle the action
        """
        self.action_handlers[action_type] = handler
        logger.info(f"Registered action handler: {action_type.value}")
    
    def fire_trigger(self, trigger_type: TriggerType, context: Dict[str, Any]) -> List[Dict]:
        """
        Fire a trigger and execute matching actions
        
        Args:
            trigger_type: Type of trigger
            context: Context information
            
        Returns:
            List of execution results
        """
        if not self.enabled:
            logger.debug("Automation engine is disabled")
            return []
        
        self.stats['triggers_fired'] += 1
        results = []
        
        # Get all rules for this trigger type
        rules = self.triggers.get(trigger_type, [])
        
        # Sort by priority (highest first)
        rules = sorted(
            [r for r in rules if r['enabled']],
            key=lambda x: x['priority'],
            reverse=True
        )
        
        logger.info(f"Trigger fired: {trigger_type.value}, checking {len(rules)} rules")
        
        for rule in rules:
            try:
                # Check condition
                if rule['condition'](context):
                    logger.info(f"Condition met, executing action: {rule['action'].value}")
                    
                    # Execute action
                    result = self._execute_action(rule['action'], context)
                    results.append(result)
                    
                    if result['success']:
                        self.stats['actions_executed'] += 1
                    else:
                        self.stats['actions_failed'] += 1
                    
                    # Log execution
                    self._log_execution(trigger_type, rule['action'], result)
            
            except Exception as e:
                logger.error(f"Error processing rule: {e}")
                self.stats['actions_failed'] += 1
        
        return results
    
    def _execute_action(self, action_type: ActionType, context: Dict) -> Dict:
        """Execute an action"""
        if action_type not in self.action_handlers:
            return {
                'success': False,
                'action': action_type.value,
                'error': f'No handler registered for {action_type.value}'
            }
        
        try:
            handler = self.action_handlers[action_type]
            result = handler(context)
            
            return {
                'success': True,
                'action': action_type.value,
                'result': result,
                'timestamp': time.time()
            }
        
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {
                'success': False,
                'action': action_type.value,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _log_execution(self, trigger: TriggerType, action: ActionType, result: Dict):
        """Log action execution"""
        log_entry = {
            'trigger': trigger.value,
            'action': action.value,
            'success': result['success'],
            'timestamp': time.time()
        }
        
        if not result['success']:
            log_entry['error'] = result.get('error', 'Unknown error')
        
        self.execution_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.execution_log) > 1000:
            self.execution_log = self.execution_log[-500:]
    
    def setup_default_triggers(self):
        """Setup default automation triggers"""
        
        # Trigger 1: Quality check on file save
        self.register_trigger(
            TriggerType.FILE_SAVE,
            lambda ctx: ctx.get('file_path', '').endswith(('.py', '.js', '.ts')),
            ActionType.QUALITY_CHECK,
            priority=7
        )
        
        # Trigger 2: Refactor on quality issues
        self.register_trigger(
            TriggerType.QUALITY_ISSUE,
            lambda ctx: ctx.get('severity', '') in ['high', 'critical'],
            ActionType.REFACTOR,
            priority=8
        )
        
        # Trigger 3: Bug fix on test failure
        self.register_trigger(
            TriggerType.TEST_FAILURE,
            lambda ctx: ctx.get('failure_count', 0) > 0,
            ActionType.BUG_FIX,
            priority=9
        )
        
        # Trigger 4: Split large files
        self.register_trigger(
            TriggerType.LARGE_FILE,
            lambda ctx: ctx.get('line_count', 0) > 500,
            ActionType.FILE_SPLIT,
            priority=6
        )
        
        # Trigger 5: Cleanup bloat
        self.register_trigger(
            TriggerType.BLOAT_DETECTED,
            lambda ctx: ctx.get('bloat_count', 0) > 0,
            ActionType.BLOAT_CLEANUP,
            priority=5
        )
        
        # Trigger 6: Prune context when full
        self.register_trigger(
            TriggerType.CONTEXT_FULL,
            lambda ctx: ctx.get('token_usage', 0) > ctx.get('token_limit', 4000) * 0.8,
            ActionType.CONTEXT_PRUNE,
            priority=10
        )
        
        logger.info("Default triggers configured")
    
    def enable(self):
        """Enable automation engine"""
        self.enabled = True
        logger.info("Automation engine enabled")
    
    def disable(self):
        """Disable automation engine"""
        self.enabled = False
        logger.info("Automation engine disabled")
    
    def get_stats(self) -> Dict:
        """Get automation statistics"""
        return {
            **self.stats,
            'triggers_registered': sum(len(rules) for rules in self.triggers.values()),
            'actions_registered': len(self.action_handlers),
            'enabled': self.enabled
        }
    
    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        """Get recent execution log"""
        return self.execution_log[-limit:]
    
    def clear_log(self):
        """Clear execution log"""
        self.execution_log = []
        logger.info("Execution log cleared")
    
    def list_triggers(self) -> Dict[str, List[Dict]]:
        """List all registered triggers"""
        result = {}
        
        for trigger_type, rules in self.triggers.items():
            result[trigger_type.value] = [
                {
                    'action': rule['action'].value,
                    'priority': rule['priority'],
                    'enabled': rule['enabled']
                }
                for rule in rules
            ]
        
        return result
    
    def enable_trigger(self, trigger_type: TriggerType, action_type: ActionType):
        """Enable a specific trigger"""
        for rule in self.triggers.get(trigger_type, []):
            if rule['action'] == action_type:
                rule['enabled'] = True
                logger.info(f"Enabled trigger: {trigger_type.value} -> {action_type.value}")
    
    def disable_trigger(self, trigger_type: TriggerType, action_type: ActionType):
        """Disable a specific trigger"""
        for rule in self.triggers.get(trigger_type, []):
            if rule['action'] == action_type:
                rule['enabled'] = False
                logger.info(f"Disabled trigger: {trigger_type.value} -> {action_type.value}")
    
    def remove_trigger(self, trigger_type: TriggerType, action_type: ActionType):
        """Remove a trigger"""
        if trigger_type in self.triggers:
            self.triggers[trigger_type] = [
                rule for rule in self.triggers[trigger_type]
                if rule['action'] != action_type
            ]
            logger.info(f"Removed trigger: {trigger_type.value} -> {action_type.value}")
    
    def test_trigger(self, trigger_type: TriggerType, context: Dict) -> List[Dict]:
        """
        Test a trigger without executing actions
        
        Args:
            trigger_type: Type of trigger
            context: Context information
            
        Returns:
            List of actions that would be executed
        """
        rules = self.triggers.get(trigger_type, [])
        matching_actions = []
        
        for rule in rules:
            if rule['enabled'] and rule['condition'](context):
                matching_actions.append({
                    'action': rule['action'].value,
                    'priority': rule['priority']
                })
        
        return sorted(matching_actions, key=lambda x: x['priority'], reverse=True)


class AutomationPreferences:
    """User preferences for automation"""
    
    def __init__(self):
        """Initialize preferences"""
        self.preferences = {
            'auto_quality_check': True,
            'auto_refactor': False,  # Requires confirmation
            'auto_bug_fix': False,  # Requires confirmation
            'auto_file_split': True,
            'auto_bloat_cleanup': True,
            'auto_context_prune': True,
            'auto_test_on_save': False,
            'auto_docs_update': True,
            'notification_level': 'all'  # all, errors_only, none
        }
    
    def set(self, key: str, value: Any):
        """Set a preference"""
        if key in self.preferences:
            self.preferences[key] = value
            logger.info(f"Preference updated: {key} = {value}")
        else:
            logger.warning(f"Unknown preference: {key}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a preference"""
        return self.preferences.get(key, default)
    
    def get_all(self) -> Dict:
        """Get all preferences"""
        return self.preferences.copy()
    
    def reset(self):
        """Reset to defaults"""
        self.__init__()
        logger.info("Preferences reset to defaults")
