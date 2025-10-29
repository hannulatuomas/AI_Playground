"""
Rule Manager

Manages coding rules and best practices.
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json


class RuleScope(Enum):
    """Rule scope levels."""
    GLOBAL = "global"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    PROJECT = "project"


class RuleCategory(Enum):
    """Rule categories."""
    STYLE = "style"
    ARCHITECTURE = "architecture"
    BEST_PRACTICES = "best_practices"
    QUALITY = "quality"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"


@dataclass
class Rule:
    """Coding rule."""
    id: int
    scope: RuleScope
    category: RuleCategory
    rule_text: str
    priority: int  # 1-10, higher = more important
    language: Optional[str] = None
    framework: Optional[str] = None
    project_id: Optional[str] = None


class RuleManager:
    """Manages coding rules."""
    
    def __init__(self, rules_file: str = "rules.json"):
        """
        Initialize rule manager.
        
        Args:
            rules_file: File to store rules
        """
        self.rules_file = Path(rules_file)
        self.rules: Dict[int, Rule] = {}
        self.next_id = 1
        self._load_rules()
        
        # Load default rules if no rules exist
        if not self.rules:
            self._load_default_rules()
    
    def add_rule(self, scope: RuleScope, category: RuleCategory,
                rule_text: str, priority: int = 5,
                language: Optional[str] = None,
                framework: Optional[str] = None,
                project_id: Optional[str] = None) -> Rule:
        """
        Add a new rule.
        
        Args:
            scope: Rule scope
            category: Rule category
            rule_text: Rule description
            priority: Priority (1-10)
            language: Language (for language-specific rules)
            framework: Framework (for framework-specific rules)
            project_id: Project ID (for project-specific rules)
            
        Returns:
            Created Rule object
        """
        rule = Rule(
            id=self.next_id,
            scope=scope,
            category=category,
            rule_text=rule_text,
            priority=priority,
            language=language,
            framework=framework,
            project_id=project_id
        )
        
        self.rules[self.next_id] = rule
        self.next_id += 1
        self._save_rules()
        
        return rule
    
    def get_rules(self, scope: Optional[RuleScope] = None,
                 category: Optional[RuleCategory] = None,
                 language: Optional[str] = None,
                 framework: Optional[str] = None,
                 project_id: Optional[str] = None) -> List[Rule]:
        """
        Get rules matching criteria.
        
        Args:
            scope: Filter by scope
            category: Filter by category
            language: Filter by language
            framework: Filter by framework
            project_id: Filter by project
            
        Returns:
            List of matching rules
        """
        filtered = []
        
        for rule in self.rules.values():
            if scope and rule.scope != scope:
                continue
            if category and rule.category != category:
                continue
            if language and rule.language and rule.language != language:
                continue
            if framework and rule.framework and rule.framework != framework:
                continue
            if project_id and rule.project_id and rule.project_id != project_id:
                continue
            
            filtered.append(rule)
        
        # Sort by priority (highest first)
        filtered.sort(key=lambda r: r.priority, reverse=True)
        
        return filtered
    
    def get_applicable_rules(self, language: str,
                           framework: Optional[str] = None,
                           project_id: Optional[str] = None) -> List[Rule]:
        """
        Get all applicable rules for a context.
        
        Args:
            language: Programming language
            framework: Framework
            project_id: Project ID
            
        Returns:
            List of applicable rules, sorted by priority
        """
        rules = []
        
        # Global rules
        rules.extend(self.get_rules(scope=RuleScope.GLOBAL))
        
        # Language-specific rules
        rules.extend(self.get_rules(scope=RuleScope.LANGUAGE, language=language))
        
        # Framework-specific rules
        if framework:
            rules.extend(self.get_rules(scope=RuleScope.FRAMEWORK, 
                                       language=language, framework=framework))
        
        # Project-specific rules
        if project_id:
            rules.extend(self.get_rules(scope=RuleScope.PROJECT, 
                                       project_id=project_id))
        
        # Remove duplicates and sort by priority
        seen = set()
        unique_rules = []
        for rule in rules:
            if rule.id not in seen:
                seen.add(rule.id)
                unique_rules.append(rule)
        
        unique_rules.sort(key=lambda r: (r.priority, r.scope.value), reverse=True)
        
        return unique_rules
    
    def format_rules_for_prompt(self, rules: List[Rule]) -> str:
        """
        Format rules for inclusion in AI prompt.
        
        Args:
            rules: List of rules
            
        Returns:
            Formatted string
        """
        if not rules:
            return ""
        
        formatted = "Follow these coding rules strictly:\n\n"
        
        # Group by category
        by_category: Dict[RuleCategory, List[Rule]] = {}
        for rule in rules:
            if rule.category not in by_category:
                by_category[rule.category] = []
            by_category[rule.category].append(rule)
        
        # Format each category
        for category, cat_rules in by_category.items():
            formatted += f"{category.value.replace('_', ' ').title()}:\n"
            for rule in cat_rules:
                formatted += f"  - {rule.rule_text}\n"
            formatted += "\n"
        
        formatted += "If a rule conflicts with the task, explain why and seek clarification."
        
        return formatted
    
    def inject_rules(self, prompt: str, language: str,
                    framework: Optional[str] = None,
                    project_id: Optional[str] = None) -> str:
        """
        Inject applicable rules into prompt.
        
        Args:
            prompt: Original prompt
            language: Programming language
            framework: Framework
            project_id: Project ID
            
        Returns:
            Prompt with rules injected
        """
        rules = self.get_applicable_rules(language, framework, project_id)
        rules_text = self.format_rules_for_prompt(rules)
        
        if not rules_text:
            return prompt
        
        return f"{rules_text}\n\n---\n\n{prompt}"
    
    def update_rule(self, rule_id: int, **updates) -> bool:
        """
        Update a rule.
        
        Args:
            rule_id: Rule ID
            **updates: Fields to update
            
        Returns:
            True if successful
        """
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self._save_rules()
        return True
    
    def delete_rule(self, rule_id: int) -> bool:
        """
        Delete a rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            True if successful
        """
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save_rules()
            return True
        return False
    
    def _load_rules(self):
        """Load rules from file."""
        if not self.rules_file.exists():
            return
        
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for rule_data in data.get('rules', []):
                rule = Rule(
                    id=rule_data['id'],
                    scope=RuleScope(rule_data['scope']),
                    category=RuleCategory(rule_data['category']),
                    rule_text=rule_data['rule_text'],
                    priority=rule_data['priority'],
                    language=rule_data.get('language'),
                    framework=rule_data.get('framework'),
                    project_id=rule_data.get('project_id')
                )
                self.rules[rule.id] = rule
                self.next_id = max(self.next_id, rule.id + 1)
                
        except Exception as e:
            print(f"Error loading rules: {e}")
    
    def _save_rules(self):
        """Save rules to file."""
        data = {
            'rules': [
                {
                    'id': rule.id,
                    'scope': rule.scope.value,
                    'category': rule.category.value,
                    'rule_text': rule.rule_text,
                    'priority': rule.priority,
                    'language': rule.language,
                    'framework': rule.framework,
                    'project_id': rule.project_id
                }
                for rule in self.rules.values()
            ]
        }
        
        try:
            self.rules_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.rules_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving rules: {e}")
    
    def _load_default_rules(self):
        """Load default rules."""
        from .defaults import DefaultRules
        
        defaults = DefaultRules.get_all_defaults()
        
        for lang, categories in defaults.items():
            for category, rules in categories.items():
                cat_enum = RuleCategory[category.upper()]
                
                for rule_text in rules:
                    self.add_rule(
                        scope=RuleScope.LANGUAGE,
                        category=cat_enum,
                        rule_text=rule_text,
                        priority=7,
                        language=lang
                    )
