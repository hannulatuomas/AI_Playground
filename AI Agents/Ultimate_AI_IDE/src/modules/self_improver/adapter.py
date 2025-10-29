"""
Adapter

Adapts behavior based on insights.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .learner import Insight


@dataclass
class Adaptation:
    """Behavior adaptation."""
    adaptation_type: str  # 'prompt_update', 'parameter_change', 'rule_addition'
    target: str  # What to adapt
    change: str  # Description of change
    reason: str  # Why this adaptation
    priority: str


class Adapter:
    """Adapts system behavior based on insights."""
    
    def __init__(self):
        """Initialize adapter."""
        self.adaptations: List[Adaptation] = []
    
    def adapt_from_insights(self, insights: List[Insight]) -> List[Adaptation]:
        """
        Create adaptations from insights.
        
        Args:
            insights: List of insights
            
        Returns:
            List of adaptations
        """
        adaptations = []
        
        for insight in insights:
            if insight.category == 'error_prevention':
                adaptation = self._create_error_prevention_adaptation(insight)
            elif insight.category == 'optimization':
                adaptation = self._create_optimization_adaptation(insight)
            elif insight.category == 'best_practice':
                adaptation = self._create_best_practice_adaptation(insight)
            else:
                continue
            
            if adaptation:
                adaptations.append(adaptation)
                self.adaptations.append(adaptation)
        
        return adaptations
    
    def _create_error_prevention_adaptation(self, insight: Insight) -> Optional[Adaptation]:
        """Create adaptation for error prevention."""
        if 'import' in insight.title.lower():
            return Adaptation(
                adaptation_type='prompt_update',
                target='code_generation_prompt',
                change='Add: "Always check existing imports before adding new ones"',
                reason=insight.description,
                priority=insight.priority
            )
        
        elif 'syntax' in insight.title.lower():
            return Adaptation(
                adaptation_type='rule_addition',
                target='validation_rules',
                change='Add syntax validation before code saving',
                reason=insight.description,
                priority=insight.priority
            )
        
        else:
            return Adaptation(
                adaptation_type='prompt_update',
                target='general_prompt',
                change=f'Add error handling for: {insight.title}',
                reason=insight.description,
                priority=insight.priority
            )
    
    def _create_optimization_adaptation(self, insight: Insight) -> Optional[Adaptation]:
        """Create adaptation for optimization."""
        return Adaptation(
            adaptation_type='parameter_change',
            target='performance_settings',
            change=insight.recommendation,
            reason=insight.description,
            priority=insight.priority
        )
    
    def _create_best_practice_adaptation(self, insight: Insight) -> Optional[Adaptation]:
        """Create adaptation for best practice."""
        return Adaptation(
            adaptation_type='rule_addition',
            target='best_practices',
            change=insight.recommendation,
            reason=insight.description,
            priority='low'
        )
    
    def get_pending_adaptations(self) -> List[Adaptation]:
        """Get all pending adaptations."""
        return self.adaptations.copy()
    
    def apply_adaptation(self, adaptation: Adaptation) -> bool:
        """
        Apply an adaptation.
        
        Args:
            adaptation: Adaptation to apply
            
        Returns:
            True if successful
        """
        # In a real implementation, this would actually modify
        # prompts, rules, or parameters
        print(f"Applied adaptation: {adaptation.change}")
        return True
    
    def clear_adaptations(self):
        """Clear all adaptations."""
        self.adaptations.clear()
    
    def export_adaptations(self, output_file: str):
        """Export adaptations to file."""
        import json
        from dataclasses import asdict
        
        data = [asdict(a) for a in self.adaptations]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
