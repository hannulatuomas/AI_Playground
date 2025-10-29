"""
Clarification Templates and Mechanisms

This module provides templates and utilities for agents to ask clarifying
questions before starting work. This ensures agents understand requirements
and context before proceeding with implementation.
"""

from typing import Dict, Any, List, Optional
from enum import Enum


class ClarificationType(Enum):
    """Types of clarification questions."""
    REQUIREMENT = "requirement"  # Clarifying project requirements
    APPROACH = "approach"  # Multiple possible approaches
    CONTEXT = "context"  # Missing or unclear context
    SCOPE = "scope"  # Clarifying scope and boundaries
    PREFERENCE = "preference"  # User preferences
    VALIDATION = "validation"  # Validating understanding


class ClarificationTemplate:
    """
    Template for generating clarification questions.
    
    Provides structured methods for agents to ask questions when:
    - Requirements are ambiguous
    - Multiple implementation approaches exist
    - Context is missing or incomplete
    - Scope needs definition
    """
    
    @staticmethod
    def format_question(
        question: str,
        context: Optional[str] = None,
        options: Optional[List[str]] = None,
        clarification_type: ClarificationType = ClarificationType.REQUIREMENT
    ) -> Dict[str, Any]:
        """
        Format a clarification question.
        
        Args:
            question: The main question to ask
            context: Additional context about why clarification is needed
            options: List of possible options (for choice questions)
            clarification_type: Type of clarification
            
        Returns:
            Formatted clarification dictionary
        """
        result = {
            'question': question,
            'type': clarification_type.value,
            'timestamp': None  # Set by agent when asked
        }
        
        if context:
            result['context'] = context
        
        if options:
            result['options'] = options
        
        return result
    
    @staticmethod
    def ambiguous_requirements(
        agent_name: str,
        task_description: str,
        ambiguous_aspects: List[str]
    ) -> str:
        """
        Template for unclear requirements.
        
        Args:
            agent_name: Name of the agent asking
            task_description: Brief task description
            ambiguous_aspects: List of unclear aspects
            
        Returns:
            Formatted clarification message
        """
        message = f"""### ❓ Clarification Needed

**Agent:** {agent_name}  
**Task:** {task_description}

I need clarification on the following aspects before proceeding:

"""
        for i, aspect in enumerate(ambiguous_aspects, 1):
            message += f"{i}. {aspect}\n"
        
        message += "\nPlease provide more details so I can proceed with confidence."
        
        return message
    
    @staticmethod
    def multiple_approaches(
        agent_name: str,
        task_description: str,
        approaches: List[Dict[str, str]]
    ) -> str:
        """
        Template for multiple possible approaches.
        
        Args:
            agent_name: Name of the agent
            task_description: Task description
            approaches: List of approaches with 'name', 'description', 'pros', 'cons'
            
        Returns:
            Formatted clarification message
        """
        message = f"""### 🤔 Multiple Approaches Available

**Agent:** {agent_name}  
**Task:** {task_description}

I've identified multiple ways to accomplish this task. Which approach would you prefer?

"""
        for i, approach in enumerate(approaches, 1):
            message += f"""
**Option {i}: {approach.get('name', f'Approach {i}')}**

{approach.get('description', '')}

**Pros:** {approach.get('pros', 'N/A')}  
**Cons:** {approach.get('cons', 'N/A')}

"""
        
        message += "Please select your preferred approach or suggest an alternative."
        
        return message
    
    @staticmethod
    def missing_context(
        agent_name: str,
        task_description: str,
        missing_info: List[str],
        impact: str
    ) -> str:
        """
        Template for missing context.
        
        Args:
            agent_name: Name of the agent
            task_description: Task description
            missing_info: List of missing information
            impact: Impact of missing information
            
        Returns:
            Formatted clarification message
        """
        message = f"""### ℹ️ Missing Context

**Agent:** {agent_name}  
**Task:** {task_description}

I'm missing some context that would help me do this better:

"""
        for i, info in enumerate(missing_info, 1):
            message += f"{i}. {info}\n"
        
        message += f"\n**Impact:** {impact}\n\n"
        message += "I can proceed with assumptions, or you can provide this information for better results."
        
        return message
    
    @staticmethod
    def validate_understanding(
        agent_name: str,
        task_description: str,
        understood_requirements: List[str],
        planned_actions: List[str]
    ) -> str:
        """
        Template for validating understanding.
        
        Args:
            agent_name: Name of the agent
            task_description: Task description
            understood_requirements: What the agent understood
            planned_actions: What the agent plans to do
            
        Returns:
            Formatted validation message
        """
        message = f"""### ✅ Validating My Understanding

**Agent:** {agent_name}  
**Task:** {task_description}

Before I proceed, let me confirm my understanding:

**What I Understand:**
"""
        for i, req in enumerate(understood_requirements, 1):
            message += f"{i}. {req}\n"
        
        message += "\n**What I Plan To Do:**\n"
        for i, action in enumerate(planned_actions, 1):
            message += f"{i}. {action}\n"
        
        message += "\nIs this correct? Please confirm or correct any misunderstandings."
        
        return message
    
    @staticmethod
    def project_context_missing(
        agent_name: str,
        task_description: str,
        can_proceed_without: bool = True
    ) -> str:
        """
        Template for missing project context.
        
        Args:
            agent_name: Name of the agent
            task_description: Task description
            can_proceed_without: Whether agent can proceed without context
            
        Returns:
            Formatted clarification message
        """
        message = f"""### 📁 Project Context Missing

**Agent:** {agent_name}  
**Task:** {task_description}

I couldn't find the `.project_ai` folder or `.codebase_root` marker for this project.

**Missing context includes:**
- Project goals and objectives
- Initial project plan
- Current task list
- Project-specific coding preferences

"""
        if can_proceed_without:
            message += """**I can proceed anyway, but:**
- I won't be aware of project-specific guidelines
- I might not align with project goals
- I won't have context about current priorities

**Recommendation:** Initialize the project first using a project_init agent, or provide the project path if working in an existing project.
"""
        else:
            message += """**I need this context to proceed properly.**

Please either:
1. Initialize the project using a project_init agent
2. Provide the correct project path
3. Create the .project_ai structure manually
"""
        
        return message
    
    @staticmethod
    def scope_clarification(
        agent_name: str,
        task_description: str,
        scope_questions: List[str]
    ) -> str:
        """
        Template for scope clarification.
        
        Args:
            agent_name: Name of the agent
            task_description: Task description
            scope_questions: Questions about scope
            
        Returns:
            Formatted clarification message
        """
        message = f"""### 🎯 Scope Clarification

**Agent:** {agent_name}  
**Task:** {task_description}

Before I start, I need to clarify the scope:

"""
        for i, question in enumerate(scope_questions, 1):
            message += f"{i}. {question}\n"
        
        message += "\nClarifying scope helps ensure I deliver exactly what you need."
        
        return message


# Helper functions for agents

def should_ask_clarification(
    context: Dict[str, Any],
    required_fields: List[str]
) -> bool:
    """
    Determine if clarification is needed based on missing required fields.
    
    Args:
        context: Execution context
        required_fields: List of required field names
        
    Returns:
        True if clarification is needed
    """
    for field in required_fields:
        if field not in context or not context[field]:
            return True
    return False


def format_clarification_response(
    questions: List[Dict[str, Any]],
    agent_name: str,
    task: str
) -> str:
    """
    Format multiple clarification questions into a single response.
    
    Args:
        questions: List of clarification question dictionaries
        agent_name: Name of the agent
        task: Task description
        
    Returns:
        Formatted response with all questions
    """
    response = f"""# Clarification Needed

**Agent:** {agent_name}  
**Task:** {task}

---

"""
    
    for i, q in enumerate(questions, 1):
        response += f"\n## Question {i}\n\n"
        response += f"**Type:** {q.get('type', 'general')}\n\n"
        
        if 'context' in q:
            response += f"**Context:** {q['context']}\n\n"
        
        response += f"{q['question']}\n\n"
        
        if 'options' in q and q['options']:
            response += "**Options:**\n"
            for opt in q['options']:
                response += f"- {opt}\n"
            response += "\n"
        
        response += "---\n"
    
    return response


def get_clarification_prompt(category: str) -> str:
    """
    Get a clarification prompt template by category.
    
    Args:
        category: Category of clarification (e.g., 'ambiguous_requirement', 'technical', etc.)
        
    Returns:
        Clarification prompt template as string
    """
    templates = {
        'ambiguous_requirement': "I need clarification on some ambiguous requirements before proceeding.",
        'technical': "I need clarification on some technical details.",
        'requirement': "I need clarification on the requirements.",
        'design': "I need clarification on the design approach.",
        'implementation': "I need clarification on the implementation details.",
        'scope': "I need clarification on the project scope.",
        'context': "I need more context to proceed effectively."
    }
    
    return templates.get(category, "I need clarification before proceeding.")


def format_clarification_request(question: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Format a clarification request with optional context.
    
    Args:
        question: The clarification question
        context: Optional context dictionary
        
    Returns:
        Formatted clarification request as string
    """
    request = f"### ❓ Clarification Request\n\n"
    request += f"**Question:** {question}\n\n"
    
    if context:
        request += "**Context:**\n"
        for key, value in context.items():
            request += f"- **{key}:** {value}\n"
        request += "\n"
    
    request += "Please provide additional information so I can proceed with confidence.\n"
    
    return request


def get_all_templates() -> Dict[str, str]:
    """
    Get all available clarification templates.
    
    Returns:
        Dictionary of template name to template string
    """
    return {
        'ambiguous_requirement': "Template for unclear or ambiguous requirements",
        'multiple_approaches': "Template for when multiple approaches are available",
        'missing_context': "Template for missing contextual information",
        'validate_understanding': "Template for validating understanding before proceeding",
        'project_context_missing': "Template for missing project context",
        'scope_clarification': "Template for clarifying project scope",
        'technical': "Template for technical clarifications",
        'requirement': "Template for requirement clarifications",
        'design': "Template for design clarifications",
        'implementation': "Template for implementation clarifications"
    }


def get_template_by_category(category: str) -> Dict[str, Any]:
    """
    Get template information by category.
    
    Args:
        category: Category name (e.g., 'technical', 'requirement', 'design')
        
    Returns:
        Template information dictionary
    """
    all_templates = get_all_templates()
    
    if category in all_templates:
        return {
            'category': category,
            'description': all_templates[category],
            'template': get_clarification_prompt(category)
        }
    else:
        return {}


# Export all
__all__ = [
    'ClarificationType',
    'ClarificationTemplate',
    'should_ask_clarification',
    'format_clarification_response',
    'get_clarification_prompt',
    'format_clarification_request',
    'get_all_templates',
    'get_template_by_category'
]
