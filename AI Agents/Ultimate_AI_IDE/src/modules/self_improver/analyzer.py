"""
Pattern Analyzer

Analyzes logs to identify patterns and issues.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter
from .logger import LogEntry


@dataclass
class ErrorPattern:
    """Identified error pattern."""
    error_type: str
    frequency: int
    common_contexts: List[str]
    affected_modules: List[str]
    sample_errors: List[str]


@dataclass
class SuccessPattern:
    """Identified success pattern."""
    action: str
    success_rate: float
    common_factors: List[str]
    best_practices: List[str]


class PatternAnalyzer:
    """Analyzes logs for patterns."""
    
    def __init__(self):
        """Initialize pattern analyzer."""
        pass
    
    def analyze_errors(self, logs: List[LogEntry]) -> List[ErrorPattern]:
        """
        Analyze error patterns.
        
        Args:
            logs: List of log entries
            
        Returns:
            List of ErrorPattern objects
        """
        # Filter errors
        errors = [log for log in logs if not log.success and log.error]
        
        if not errors:
            return []
        
        # Group by error type
        by_type: Dict[str, List[LogEntry]] = {}
        for entry in errors:
            err_type = entry.error_type or 'unknown'
            if err_type not in by_type:
                by_type[err_type] = []
            by_type[err_type].append(entry)
        
        # Analyze each type
        patterns = []
        for err_type, entries in by_type.items():
            pattern = self._analyze_error_type(err_type, entries)
            patterns.append(pattern)
        
        # Sort by frequency
        patterns.sort(key=lambda p: p.frequency, reverse=True)
        
        return patterns
    
    def _analyze_error_type(self, error_type: str, 
                           entries: List[LogEntry]) -> ErrorPattern:
        """Analyze specific error type."""
        # Get common contexts
        contexts = []
        for entry in entries:
            if entry.context:
                ctx_str = ', '.join(f"{k}={v}" for k, v in entry.context.items())
                contexts.append(ctx_str)
        
        common_contexts = [ctx for ctx, count in Counter(contexts).most_common(3)]
        
        # Get affected modules
        modules = [entry.module for entry in entries]
        affected_modules = [mod for mod, count in Counter(modules).most_common(5)]
        
        # Get sample errors
        sample_errors = [entry.error for entry in entries[:3] if entry.error]
        
        return ErrorPattern(
            error_type=error_type,
            frequency=len(entries),
            common_contexts=common_contexts,
            affected_modules=affected_modules,
            sample_errors=sample_errors
        )
    
    def analyze_successes(self, logs: List[LogEntry]) -> List[SuccessPattern]:
        """
        Analyze success patterns.
        
        Args:
            logs: List of log entries
            
        Returns:
            List of SuccessPattern objects
        """
        # Group by action
        by_action: Dict[str, List[LogEntry]] = {}
        for entry in logs:
            if entry.action not in by_action:
                by_action[entry.action] = []
            by_action[entry.action].append(entry)
        
        patterns = []
        for action, entries in by_action.items():
            if len(entries) < 5:  # Need enough data
                continue
            
            success_count = sum(1 for e in entries if e.success)
            success_rate = success_count / len(entries)
            
            if success_rate > 0.7:  # Only high success rates
                pattern = SuccessPattern(
                    action=action,
                    success_rate=success_rate,
                    common_factors=self._extract_success_factors(entries),
                    best_practices=self._extract_best_practices(entries)
                )
                patterns.append(pattern)
        
        patterns.sort(key=lambda p: p.success_rate, reverse=True)
        
        return patterns
    
    def _extract_success_factors(self, entries: List[LogEntry]) -> List[str]:
        """Extract common factors in successful entries."""
        successful = [e for e in entries if e.success]
        
        factors = []
        
        # Check for common context elements
        if successful:
            context_keys = set()
            for entry in successful:
                if entry.context:
                    context_keys.update(entry.context.keys())
            
            for key in context_keys:
                values = [e.context.get(key) for e in successful if e.context and key in e.context]
                if len(set(values)) == 1:  # Same value in all
                    factors.append(f"{key}={values[0]}")
        
        return factors[:5]
    
    def _extract_best_practices(self, entries: List[LogEntry]) -> List[str]:
        """Extract best practices from successful entries."""
        practices = []
        
        successful = [e for e in entries if e.success]
        
        if len(successful) > len(entries) * 0.8:
            practices.append("Consistent success rate indicates stable implementation")
        
        # Check for patterns in input data
        if successful:
            # This is simplified - in production, use more sophisticated analysis
            practices.append("Follow established patterns for this action")
        
        return practices
    
    def find_recurring_issues(self, logs: List[LogEntry], 
                             min_frequency: int = 3) -> List[Dict]:
        """
        Find recurring issues.
        
        Args:
            logs: List of log entries
            min_frequency: Minimum frequency to consider
            
        Returns:
            List of issue dictionaries
        """
        errors = [log for log in logs if not log.success and log.error]
        
        # Group by error message
        error_messages = [e.error for e in errors if e.error]
        error_counts = Counter(error_messages)
        
        recurring = []
        for error, count in error_counts.items():
            if count >= min_frequency:
                # Find first occurrence for context
                first_occurrence = next(e for e in errors if e.error == error)
                
                recurring.append({
                    'error': error,
                    'frequency': count,
                    'module': first_occurrence.module,
                    'error_type': first_occurrence.error_type
                })
        
        return sorted(recurring, key=lambda x: x['frequency'], reverse=True)
    
    def get_module_health(self, logs: List[LogEntry]) -> Dict[str, Dict]:
        """
        Get health metrics for each module.
        
        Args:
            logs: List of log entries
            
        Returns:
            Dictionary of module: metrics
        """
        by_module: Dict[str, List[LogEntry]] = {}
        for entry in logs:
            if entry.module not in by_module:
                by_module[entry.module] = []
            by_module[entry.module].append(entry)
        
        health = {}
        for module, entries in by_module.items():
            total = len(entries)
            successful = sum(1 for e in entries if e.success)
            failed = total - successful
            
            health[module] = {
                'total_operations': total,
                'successful': successful,
                'failed': failed,
                'success_rate': successful / total if total > 0 else 0,
                'health_status': self._determine_health_status(successful / total if total > 0 else 0)
            }
        
        return health
    
    def _determine_health_status(self, success_rate: float) -> str:
        """Determine health status from success rate."""
        if success_rate >= 0.9:
            return 'excellent'
        elif success_rate >= 0.75:
            return 'good'
        elif success_rate >= 0.5:
            return 'fair'
        else:
            return 'poor'
