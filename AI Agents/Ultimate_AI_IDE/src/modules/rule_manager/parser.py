"""
Rule Parser

Parses rule definitions from various formats.
"""

from typing import List, Dict
from .manager import Rule, RuleScope, RuleCategory


class RuleParser:
    """Parses rule definitions."""
    
    def __init__(self):
        """Initialize parser."""
        pass
    
    def parse_from_text(self, text: str, scope: RuleScope,
                       category: RuleCategory, priority: int = 5) -> List[Rule]:
        """
        Parse rules from text format.
        
        Args:
            text: Text containing rules (one per line)
            scope: Rule scope
            category: Rule category
            priority: Default priority
            
        Returns:
            List of Rule objects
        """
        rules = []
        rule_id = 1
        
        for line in text.split('\n'):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Remove bullet points
            if line.startswith('-') or line.startswith('*'):
                line = line[1:].strip()
            
            rule = Rule(
                id=rule_id,
                scope=scope,
                category=category,
                rule_text=line,
                priority=priority
            )
            rules.append(rule)
            rule_id += 1
        
        return rules
    
    def parse_from_dict(self, data: Dict) -> Rule:
        """
        Parse rule from dictionary.
        
        Args:
            data: Dictionary with rule data
            
        Returns:
            Rule object
        """
        return Rule(
            id=data.get('id', 0),
            scope=RuleScope(data['scope']),
            category=RuleCategory(data['category']),
            rule_text=data['rule_text'],
            priority=data.get('priority', 5),
            language=data.get('language'),
            framework=data.get('framework'),
            project_id=data.get('project_id')
        )
    
    def parse_from_markdown(self, markdown: str, scope: RuleScope,
                           language: str = None) -> List[Rule]:
        """
        Parse rules from markdown format.
        
        Expected format:
        ## Category Name
        - Rule 1
        - Rule 2
        
        Args:
            markdown: Markdown text
            scope: Rule scope
            language: Language for rules
            
        Returns:
            List of Rule objects
        """
        rules = []
        rule_id = 1
        current_category = RuleCategory.BEST_PRACTICES
        
        for line in markdown.split('\n'):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for category header
            if line.startswith('##'):
                category_name = line[2:].strip().lower().replace(' ', '_')
                try:
                    current_category = RuleCategory[category_name.upper()]
                except KeyError:
                    # Default to best practices if unknown
                    current_category = RuleCategory.BEST_PRACTICES
                continue
            
            # Check for rule item
            if line.startswith('-') or line.startswith('*'):
                rule_text = line[1:].strip()
                
                rule = Rule(
                    id=rule_id,
                    scope=scope,
                    category=current_category,
                    rule_text=rule_text,
                    priority=5,
                    language=language
                )
                rules.append(rule)
                rule_id += 1
        
        return rules
