
"""
Specification Extraction Module

Extracts goals, objectives, rules, constraints, preferences, and success measures
from user prompts. Uses LLM to understand user intent and organize requirements.
"""

import logging
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class SpecificationExtractor:
    """
    Extracts structured specifications from user prompts.
    
    Identifies and organizes:
    - Goals and objectives
    - Rules and constraints
    - User preferences
    - Success measures
    - Technical requirements
    """
    
    def __init__(self, llm_router: Optional[Any] = None):
        """
        Initialize specification extractor.
        
        Args:
            llm_router: LLM router for AI operations
        """
        self.llm_router = llm_router
        logger.info("SpecificationExtractor initialized")
    
    def extract(self, prompt: str) -> Dict[str, Any]:
        """
        Extract specifications from a prompt.
        
        Args:
            prompt: User's prompt
            
        Returns:
            Dictionary with extracted specifications
        """
        logger.info("Extracting specifications from prompt")
        
        if self.llm_router:
            return self._llm_extract(prompt)
        else:
            return self._rule_based_extract(prompt)
    
    def _llm_extract(self, prompt: str) -> Dict[str, Any]:
        """
        Use LLM to extract specifications.
        
        Args:
            prompt: User's prompt
            
        Returns:
            Extracted specifications
        """
        extraction_prompt = self._build_extraction_prompt(prompt)
        
        try:
            response = self.llm_router.query(
                prompt=extraction_prompt,
                temperature=0.2,
                agent_name='task_orchestrator'
            )
            
            specs = self._parse_extraction_response(response.get('response', ''))
            logger.info(f"Extracted {len(specs.get('goals', []))} goals and {len(specs.get('constraints', []))} constraints")
            
            return specs
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._rule_based_extract(prompt)
    
    def _build_extraction_prompt(self, prompt: str) -> str:
        """
        Build a prompt for LLM specification extraction.
        
        Args:
            prompt: User's prompt
            
        Returns:
            Extraction prompt
        """
        return f"""You are a requirements analysis expert. Extract and organize the specifications from the following user request.

**User Request:**
{prompt}

**Instructions:**
Identify and list:
1. **Goals**: What the user wants to achieve (high-level objectives)
2. **Constraints**: Limitations, restrictions, or rules that must be followed
3. **Preferences**: User's preferred approaches, tools, or styles
4. **Success Measures**: How to determine if the task is completed successfully
5. **Technical Requirements**: Specific technologies, frameworks, or tools mentioned

**Output Format:**

GOALS:
- [Goal 1]
- [Goal 2]
...

CONSTRAINTS:
- [Constraint 1]
- [Constraint 2]
...

PREFERENCES:
- [Preference 1]
- [Preference 2]
...

SUCCESS MEASURES:
- [Measure 1]
- [Measure 2]
...

TECHNICAL REQUIREMENTS:
- [Requirement 1]
- [Requirement 2]
...

Be specific and comprehensive. If a category has no items, write "None specified".
"""
    
    def _parse_extraction_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM extraction response.
        
        Args:
            response: LLM response text
            
        Returns:
            Structured specifications
        """
        specs = {
            'goals': [],
            'constraints': [],
            'preferences': [],
            'success_measures': [],
            'technical_requirements': []
        }
        
        current_section = None
        section_map = {
            'GOALS:': 'goals',
            'CONSTRAINTS:': 'constraints',
            'PREFERENCES:': 'preferences',
            'SUCCESS MEASURES:': 'success_measures',
            'TECHNICAL REQUIREMENTS:': 'technical_requirements'
        }
        
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line in section_map:
                current_section = section_map[line]
                continue
            
            # Add items to current section
            if current_section and line.startswith('-'):
                item = line[1:].strip()
                if item and item.lower() != 'none specified':
                    specs[current_section].append(item)
        
        return specs
    
    def _rule_based_extract(self, prompt: str) -> Dict[str, Any]:
        """
        Rule-based specification extraction (fallback).
        
        Args:
            prompt: User's prompt
            
        Returns:
            Extracted specifications
        """
        logger.info("Using rule-based extraction")
        
        specs = {
            'goals': [],
            'constraints': [],
            'preferences': [],
            'success_measures': [],
            'technical_requirements': []
        }
        
        prompt_lower = prompt.lower()
        
        # Extract goals (looking for action words)
        goal_keywords = ['create', 'build', 'implement', 'develop', 'make', 'setup']
        for keyword in goal_keywords:
            if keyword in prompt_lower:
                specs['goals'].append(f"Successfully {keyword} the requested components")
        
        if not specs['goals']:
            specs['goals'].append("Complete the requested task")
        
        # Extract constraints (looking for constraint words)
        constraint_keywords = {
            'must': 'Must follow specified requirements',
            'should': 'Should adhere to best practices',
            'don\'t': 'Avoid specified anti-patterns',
            'required': 'Meet all required specifications',
        }
        
        for keyword, constraint in constraint_keywords.items():
            if keyword in prompt_lower:
                specs['constraints'].append(constraint)
        
        # Extract technical requirements (looking for technology names)
        tech_keywords = [
            'python', 'javascript', 'typescript', 'java', 'c#', 'c++',
            'react', 'vue', 'angular', 'fastapi', 'django', 'flask',
            'node', 'express', 'sql', 'mongodb', 'postgres', 'mysql',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp'
        ]
        
        for tech in tech_keywords:
            if tech in prompt_lower:
                specs['technical_requirements'].append(f"Use {tech.title()}")
        
        # Default success measure
        specs['success_measures'].append("Code compiles/runs without errors")
        specs['success_measures'].append("Meets specified requirements")
        
        return specs
