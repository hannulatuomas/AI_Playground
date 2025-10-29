"""
Enhanced Prompt Refinement Agent

This agent enhances prompts for language-specific agents by integrating:
- Language-specific best practices
- User preferences related to the language
- Additional role prompts emphasizing expertise
- Project-specific context

This ensures that all language-specific agents receive properly refined prompts
that include relevant context and guidelines.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

from .base import Agent


logger = logging.getLogger(__name__)


class EnhancedPromptRefiner(Agent):
    """
    Enhanced prompt refiner for language-specific agents.
    
    Features:
    - Loads language-specific best practices from markdown files
    - Integrates user preferences for the language
    - Adds role prompts emphasizing senior developer expertise
    - Applies Chain-of-Thought reasoning
    - Structures prompts for clarity
    """
    
    def __init__(
        self,
        name: str = "enhanced_prompt_refiner",
        description: str = "Enhanced prompt refinement with language-specific context",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        # Cache for loaded best practices and preferences
        self._best_practices_cache = {}
        self._user_preferences_cache = {}
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine a prompt with language-specific enhancements.
        
        Args:
            task: Original prompt or task description
            context: Context with 'language', 'agent_type', 'project_path', etc.
            
        Returns:
            Result with refined prompt
        """
        self._log_action("Starting enhanced prompt refinement", task[:100])
        
        try:
            # Extract language and agent type
            language = context.get('language', '').lower()
            agent_type = context.get('agent_type', 'generic')
            project_path = context.get('project_path')
            
            # Build enhanced prompt
            refined_prompt = self._build_enhanced_prompt(
                task, 
                language, 
                agent_type,
                project_path,
                context
            )
            
            self._log_action("Prompt enhanced", f"Language: {language}, Type: {agent_type}")
            
            return self._build_success_result(
                message="Prompt successfully enhanced with language-specific context",
                data={
                    'original_prompt': task,
                    'refined_prompt': refined_prompt,
                    'language': language,
                    'agent_type': agent_type,
                    'enhancements_applied': [
                        'role_prompt',
                        'best_practices',
                        'user_preferences',
                        'structured_format'
                    ]
                },
                next_context={
                    'refined_prompt': refined_prompt,
                    'use_enhanced': True
                }
            )
            
        except Exception as e:
            self.logger.exception("Enhanced prompt refinement failed")
            return self._build_error_result(f"Refinement error: {str(e)}", e)
    
    def _build_enhanced_prompt(
        self,
        original_task: str,
        language: str,
        agent_type: str,
        project_path: Optional[Path],
        context: Dict[str, Any]
    ) -> str:
        """Build an enhanced prompt with all refinements."""
        sections = []
        
        # 1. Role Prompt (emphasizing expertise)
        role_prompt = self._generate_role_prompt(language, agent_type)
        if role_prompt:
            sections.append(role_prompt)
        
        # 2. Language-Specific Best Practices
        best_practices = self._load_best_practices(language, agent_type)
        if best_practices:
            sections.append(f"### {language.title()} Best Practices\n\n{best_practices}")
        
        # 3. User Preferences
        user_prefs = self._load_user_preferences(language, agent_type)
        if user_prefs:
            sections.append(f"### User Preferences\n\n{user_prefs}")
        
        # 4. Project-Specific Context (if available)
        if project_path:
            project_context = self._load_project_context(project_path)
            if project_context:
                sections.append(f"### Project-Specific Guidelines\n\n{project_context}")
        
        # 5. Task Description (structured)
        task_section = f"""### Your Task

{original_task}

### Approach

Please think through this step-by-step:
1. Understand the requirements thoroughly
2. Consider the best practices and preferences above
3. Plan your implementation approach
4. Implement with careful attention to code quality
5. Verify your work meets all requirements"""
        
        sections.append(task_section)
        
        # Combine all sections
        return "\n\n---\n\n".join(sections)
    
    def _generate_role_prompt(self, language: str, agent_type: str) -> str:
        """Generate role prompt emphasizing expertise."""
        language_display = language.title() if language else "programming"
        
        role_prompts = {
            'code_editor': f"""# Role: Senior {language_display} Developer & AI Engineer

You are an experienced senior developer specializing in {language_display} with deep expertise in:
- Writing clean, maintainable, and efficient code
- Following industry best practices and design patterns
- Conducting thorough code reviews
- Architecting scalable solutions
- Applying AI engineering principles

You have 10+ years of experience in {language_display} development and are known for your:
- Attention to detail and code quality
- Clear communication and documentation
- Problem-solving skills
- Ability to mentor junior developers""",
            
            'code_planner': f"""# Role: Senior {language_display} Architect & AI Engineer

You are an experienced software architect specializing in {language_display} with expertise in:
- System design and architecture
- Breaking down complex problems
- Creating scalable and maintainable solutions
- Technical documentation
- Team leadership and planning""",
            
            'code_tester': f"""# Role: Senior {language_display} Test Engineer & AI Engineer

You are an experienced test engineer specializing in {language_display} with expertise in:
- Comprehensive test strategy development
- Unit, integration, and end-to-end testing
- Test-driven development (TDD)
- Quality assurance best practices
- Continuous integration and testing automation""",
            
            'debug_agent': f"""# Role: Senior {language_display} Developer & Debugging Expert

You are an experienced developer and debugging specialist in {language_display} with expertise in:
- Root cause analysis
- Performance profiling and optimization
- Memory management and leak detection
- Error handling and recovery strategies
- Systematic debugging methodologies""",
            
            'documentation': f"""# Role: Senior {language_display} Developer & Technical Writer

You are an experienced developer and technical writer specializing in {language_display} with expertise in:
- Clear and comprehensive documentation
- API documentation best practices
- Tutorial and guide creation
- Code comment conventions
- Knowledge transfer and education""",
        }
        
        return role_prompts.get(agent_type, f"""# Role: Expert {language_display} Developer & AI Engineer

You are an experienced senior developer specializing in {language_display} and an AI Engineer with deep technical expertise.""")
    
    def _load_best_practices(self, language: str, agent_type: str) -> Optional[str]:
        """Load language-specific best practices from markdown files."""
        if not language:
            return None
        
        # Check cache first
        cache_key = f"{language}_{agent_type}_practices"
        if cache_key in self._best_practices_cache:
            return self._best_practices_cache[cache_key]
        
        # Try to load from language-specific directory
        try:
            console_root = Path(__file__).parent.parent
            lang_dir = console_root / "agents" / "languages" / language
            
            # Try best_practices.md
            best_practices_file = lang_dir / "best_practices.md"
            if best_practices_file.exists():
                content = best_practices_file.read_text(encoding='utf-8')
                # Extract relevant section if possible
                content = self._extract_relevant_section(content, agent_type)
                self._best_practices_cache[cache_key] = content
                return content
        except Exception as e:
            logger.warning(f"Could not load best practices for {language}: {e}")
        
        return None
    
    def _load_user_preferences(self, language: str, agent_type: str) -> Optional[str]:
        """Load user preferences for the language."""
        if not language:
            return None
        
        # Check cache first
        cache_key = f"{language}_{agent_type}_prefs"
        if cache_key in self._user_preferences_cache:
            return self._user_preferences_cache[cache_key]
        
        try:
            console_root = Path(__file__).parent.parent
            lang_dir = console_root / "agents" / "languages" / language
            
            # Try various preference files
            pref_files = [
                "user_preferences.md",
                f"{agent_type}_preferences.md",
                "preferences.md"
            ]
            
            for pref_file in pref_files:
                pref_path = lang_dir / pref_file
                if pref_path.exists():
                    content = pref_path.read_text(encoding='utf-8')
                    self._user_preferences_cache[cache_key] = content
                    return content
        except Exception as e:
            logger.warning(f"Could not load user preferences for {language}: {e}")
        
        return None
    
    def _load_project_context(self, project_path: Path) -> Optional[str]:
        """Load project-specific guidelines from .project_ai."""
        try:
            project_ai_dir = project_path / ".project_ai"
            
            # Look for project_preferences.md or rules.md
            for rules_file in ["rules/project_preferences.md", "rules.md", "project_preferences.md"]:
                rules_path = project_ai_dir / rules_file
                if rules_path.exists():
                    return rules_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.debug(f"Could not load project context: {e}")
        
        return None
    
    def _extract_relevant_section(self, content: str, agent_type: str) -> str:
        """Extract relevant section from best practices based on agent type."""
        # Map agent types to section keywords
        section_keywords = {
            'code_editor': ['coding', 'style', 'formatting', 'conventions'],
            'code_tester': ['testing', 'test', 'quality assurance', 'QA'],
            'debug_agent': ['debugging', 'troubleshooting', 'error handling'],
            'documentation': ['documentation', 'comments', 'docstrings'],
            'code_planner': ['architecture', 'design', 'planning', 'structure'],
        }
        
        keywords = section_keywords.get(agent_type, [])
        
        # If no specific keywords or can't extract, return full content
        # In a more sophisticated implementation, we could parse markdown structure
        # For now, return full content
        return content


def refine_prompt_for_agent(
    prompt: str,
    language: str,
    agent_type: str,
    project_path: Optional[Path] = None,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Convenience function to refine a prompt for a language-specific agent.
    
    Args:
        prompt: Original prompt/task
        language: Programming language
        agent_type: Type of agent (code_editor, code_planner, etc.)
        project_path: Path to the project being worked on
        context: Additional context
        
    Returns:
        Refined prompt string
    """
    refiner = EnhancedPromptRefiner()
    
    ctx = context or {}
    ctx.update({
        'language': language,
        'agent_type': agent_type,
        'project_path': project_path
    })
    
    result = refiner.execute(prompt, ctx)
    
    if result.get('success'):
        return result['data']['refined_prompt']
    else:
        # If refinement fails, return original prompt
        logger.warning(f"Prompt refinement failed: {result.get('error')}")
        return prompt
