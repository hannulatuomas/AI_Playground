"""
Learner

Learns from patterns and generates insights.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .logger import LogEntry
from .analyzer import ErrorPattern, SuccessPattern


@dataclass
class Insight:
    """Learning insight."""
    category: str  # 'error_prevention', 'optimization', 'best_practice'
    title: str
    description: str
    recommendation: str
    priority: str  # 'low', 'medium', 'high'
    evidence: List[str]


class Learner:
    """Learns from logs and generates insights."""
    
    def __init__(self, ai_backend):
        """
        Initialize learner.
        
        Args:
            ai_backend: AI backend for analysis
        """
        self.ai_backend = ai_backend
    
    def learn_from_errors(self, error_patterns: List[ErrorPattern]) -> List[Insight]:
        """
        Learn from error patterns.
        
        Args:
            error_patterns: List of error patterns
            
        Returns:
            List of insights
        """
        insights = []
        
        for pattern in error_patterns[:5]:  # Top 5 patterns
            insight = self._analyze_error_pattern(pattern)
            if insight:
                insights.append(insight)
        
        return insights
    
    def learn_from_successes(self, success_patterns: List[SuccessPattern]) -> List[Insight]:
        """
        Learn from success patterns.
        
        Args:
            success_patterns: List of success patterns
            
        Returns:
            List of insights
        """
        insights = []
        
        for pattern in success_patterns[:3]:  # Top 3 patterns
            insight = Insight(
                category='best_practice',
                title=f"Successful pattern for {pattern.action}",
                description=f"This action has {pattern.success_rate*100:.1f}% success rate",
                recommendation=f"Continue using current approach for {pattern.action}",
                priority='low',
                evidence=pattern.common_factors
            )
            insights.append(insight)
        
        return insights
    
    def _analyze_error_pattern(self, pattern: ErrorPattern) -> Optional[Insight]:
        """Analyze error pattern and generate insight."""
        # Determine priority based on frequency
        if pattern.frequency > 10:
            priority = 'high'
        elif pattern.frequency > 5:
            priority = 'medium'
        else:
            priority = 'low'
        
        # Generate recommendation
        recommendation = self._generate_recommendation(pattern)
        
        return Insight(
            category='error_prevention',
            title=f"Recurring error: {pattern.error_type}",
            description=f"This error occurred {pattern.frequency} times",
            recommendation=recommendation,
            priority=priority,
            evidence=pattern.sample_errors
        )
    
    def _generate_recommendation(self, pattern: ErrorPattern) -> str:
        """Generate recommendation for error pattern."""
        error_type = pattern.error_type.lower()
        
        if 'import' in error_type:
            return "Add import checking before code generation"
        elif 'syntax' in error_type:
            return "Validate syntax before saving code"
        elif 'type' in error_type:
            return "Add type checking and validation"
        elif 'file' in error_type or 'path' in error_type:
            return "Verify file paths exist before operations"
        elif 'permission' in error_type:
            return "Check file permissions before write operations"
        else:
            return f"Add error handling for {pattern.error_type}"
    
    def generate_improvement_suggestions(self, logs: List[LogEntry]) -> List[str]:
        """
        Generate improvement suggestions from logs.
        
        Args:
            logs: List of log entries
            
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Analyze error rate
        total = len(logs)
        errors = sum(1 for log in logs if not log.success)
        error_rate = errors / total if total > 0 else 0
        
        if error_rate > 0.2:
            suggestions.append("Error rate is high (>20%). Review error handling logic.")
        
        # Check for repeated errors
        error_messages = [log.error for log in logs if not log.success and log.error]
        from collections import Counter
        common_errors = Counter(error_messages).most_common(3)
        
        for error, count in common_errors:
            if count > 3:
                suggestions.append(f"Address recurring error: {error[:50]}...")
        
        # Check module health
        modules = set(log.module for log in logs)
        for module in modules:
            module_logs = [log for log in logs if log.module == module]
            module_errors = sum(1 for log in module_logs if not log.success)
            module_error_rate = module_errors / len(module_logs) if module_logs else 0
            
            if module_error_rate > 0.3:
                suggestions.append(f"Module '{module}' has high error rate. Needs attention.")
        
        return suggestions
    
    def identify_optimization_opportunities(self, logs: List[LogEntry]) -> List[Insight]:
        """
        Identify optimization opportunities.
        
        Args:
            logs: List of log entries
            
        Returns:
            List of optimization insights
        """
        insights = []
        
        # Check for slow operations (if timing data available)
        # This is a placeholder for more sophisticated analysis
        
        insight = Insight(
            category='optimization',
            title="Performance optimization opportunity",
            description="Some operations may benefit from caching or optimization",
            recommendation="Profile slow operations and implement caching where appropriate",
            priority='medium',
            evidence=["Multiple similar operations detected"]
        )
        insights.append(insight)
        
        return insights
