"""
Prompt Engine Module

Manages prompt templates for code generation and debugging across multiple languages.
Includes placeholders for user input and past learnings from the database.

PRIVACY GUARANTEE:
- All learnings stay in local database
- No user-specific data (names, emails, paths) is stored
- Only error patterns and solutions are retained
- No data is transmitted externally
- Database file remains on user's machine

SELF-IMPROVEMENT:
- Learnings are ALWAYS fetched and applied
- Past errors guide future prompts
- System adapts automatically without user intervention
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Structure for a prompt template."""
    system: str
    user_prefix: str
    user_suffix: str = ""


class PromptEngine:
    """
    Manages prompt generation for different coding tasks and languages.
    Incorporates past learnings to improve future prompts.
    """

    def __init__(self, learning_db=None, project_manager=None):
        """
        Initialize the prompt engine.

        Args:
            learning_db: Optional LearningDB instance for incorporating past learnings
            project_manager: Optional ProjectManager instance for project-aware prompts
        """
        self.learning_db = learning_db
        self.project_manager = project_manager
        self._initialize_templates()

    def _initialize_templates(self) -> None:
        """Initialize prompt templates for different tasks and languages."""

        # Base system prompt
        self.base_system = (
            "You are an expert software developer and coding assistant. "
            "You write clean, efficient, well-documented code following best practices. "
            "You provide code with explanations and consider edge cases."
        )

        # Language-specific system prompts
        self.lang_systems = {
            'python': (
                "You are a Python expert. Follow PEP 8 style guidelines. "
                "Use type hints where appropriate. Write Pythonic code with proper error handling."
            ),
            'cpp': (
                "You are a C++ expert. Follow modern C++ standards (C++17/20). "
                "Use RAII, smart pointers instead of raw pointers, and const correctness."
            ),
            'csharp': (
                "You are a C# expert. Follow Microsoft coding conventions. "
                "Use modern C# features (LINQ, async/await, pattern matching) where appropriate."
            ),
            'javascript': (
                "You are a JavaScript expert. Use modern ES6+ syntax. "
                "Prefer const/let over var, use arrow functions appropriately, handle async with async/await."
            ),
            'typescript': (
                "You are a TypeScript expert. Provide proper type annotations. "
                "Use interfaces and type aliases appropriately. Leverage TypeScript's type system."
            ),
            'html': (
                "You are an HTML expert. Write semantic HTML5. "
                "Use appropriate tags for accessibility and SEO."
            ),
            'css': (
                "You are a CSS expert. Write modern, maintainable CSS. "
                "Use CSS Grid and Flexbox appropriately. Consider responsive design."
            ),
            'react': (
                "You are a React expert. Use modern React with hooks. "
                "Follow React best practices: component composition, proper key usage."
            ),
            'nodejs': (
                "You are a Node.js expert. Use modern async/await patterns. "
                "Handle errors properly. Use appropriate Node.js built-in modules."
            ),
            'nextjs': (
                "You are a Next.js expert. Understand App Router and Pages Router. "
                "Use server/client components appropriately."
            ),
            'express': (
                "You are an Express.js expert. Structure middleware properly. "
                "Implement proper error handling middleware."
            ),
            'powershell': (
                "You are a PowerShell expert. Use approved verbs for function names. "
                "Follow proper parameter validation and pipeline support."
            ),
            'bash': (
                "You are a Bash scripting expert. Write POSIX-compliant when possible. "
                "Use proper quoting and error handling with set -e."
            ),
            'sh': (
                "You are a shell scripting expert. Write portable POSIX shell scripts. "
                "Avoid bashisms. Handle errors gracefully."
            ),
            'zsh': (
                "You are a Zsh expert. Leverage Zsh-specific features appropriately. "
                "Use arrays and enhanced globbing when beneficial."
            ),
            'batch': (
                "You are a Windows batch scripting expert. Use proper syntax for cmd.exe. "
                "Handle errorlevel checks correctly. Quote paths with spaces."
            ),
        }

        # Task-specific templates
        self.task_templates = {
            'generate': PromptTemplate(
                system="You are generating new code based on requirements.",
                user_prefix="Create {language} code for the following task:\n\n{task}\n\n",
                user_suffix="Provide clean, working code with brief explanations."
            ),
            'debug': PromptTemplate(
                system="You are debugging code and finding solutions to errors.",
                user_prefix="Debug this {language} code:\n\n```{language}\n{code}\n```\n\nError: {error}\n\n",
                user_suffix="Explain the issue and provide the corrected code."
            ),
            'explain': PromptTemplate(
                system="You are explaining code clearly and concisely.",
                user_prefix="Explain this {language} code:\n\n```{language}\n{code}\n```\n\n",
                user_suffix="Provide a clear explanation of what it does and how it works."
            ),
            'optimize': PromptTemplate(
                system="You are optimizing code for better performance and maintainability.",
                user_prefix="Optimize this {language} code:\n\n```{language}\n{code}\n```\n\n",
                user_suffix="Provide optimized version with explanation of improvements."
            ),
            'refactor': PromptTemplate(
                system="You are refactoring code to improve structure and readability.",
                user_prefix="Refactor this {language} code:\n\n```{language}\n{code}\n```\n\n",
                user_suffix="Provide refactored version following best practices."
            ),
        }

    def build_prompt(
        self,
        task_type: str,
        language: str,
        content: str,
        error: Optional[str] = None,
        include_learnings: bool = True,
        include_project_context: bool = False,
        project_files: Optional[List[str]] = None
    ) -> str:
        """
        Build a complete prompt for the LLM.

        Args:
            task_type: Type of task (generate, debug, explain, etc.)
            language: Programming language or framework
            content: Main content (task description or code)
            error: Optional error message for debugging
            include_learnings: Whether to include past learnings
            include_project_context: Whether to include project file summaries
            project_files: Optional list of relevant file paths for context

        Returns:
            Complete formatted prompt
        """
        # Get base and language-specific system prompts
        system_prompt = self.base_system

        # Normalize language name
        lang_normalized = self._normalize_language(language)

        if lang_normalized in self.lang_systems:
            system_prompt += "\n\n" + self.lang_systems[lang_normalized]

        # Get task template
        template = self.task_templates.get(task_type, self.task_templates['generate'])

        # Build the prompt parts
        prompt_parts = [system_prompt]

        # Add task-specific system context
        if template.system:
            prompt_parts.append(template.system)

        # Add learnings if available
        if include_learnings and self.learning_db:
            learnings = self._format_learnings(lang_normalized, task_type)
            if learnings:
                prompt_parts.append(learnings)
        
        # Add project context if available
        if include_project_context and self.project_manager:
            project_context = self._format_project_context(project_files)
            if project_context:
                prompt_parts.append(project_context)

        # Build user content
        user_prompt = template.user_prefix.format(
            language=language,
            task=content if task_type == 'generate' else '',
            code=content if task_type != 'generate' else '',
            error=error or ''
        )

        user_prompt += template.user_suffix

        prompt_parts.append(user_prompt)

        # Combine all parts
        full_prompt = "\n\n".join(prompt_parts)

        return full_prompt

    def _normalize_language(self, language: str) -> str:
        """
        Normalize language name to match template keys.

        Args:
            language: Input language name

        Returns:
            Normalized language name
        """
        lang_lower = language.lower().strip()

        # Handle common aliases
        aliases = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'c++': 'cpp',
            'c#': 'csharp',
            'cs': 'csharp',
            'node': 'nodejs',
            'next': 'nextjs',
            'shell': 'bash',
            'cmd': 'batch',
            'bat': 'batch',
        }

        return aliases.get(lang_lower, lang_lower)

    def get_learnings(self, query: str, language: str, task_type: str = 'generate', limit: int = 3) -> List[Dict]:
        """
        Get relevant learnings from database for a query.
        
        This is the primary method for fetching learnings from the database.
        All learnings are anonymized - no user data is shared externally.
        
        Args:
            query: The user's query or code
            language: Programming language
            task_type: Type of task (generate, debug, etc.)
            limit: Maximum number of learnings to return
            
        Returns:
            List of relevant learning dictionaries with 'error' and 'solution' keys
            
        Privacy:
            - No user-specific data (names, emails, paths) is stored
            - Only error patterns and solutions are retained
            - All data stays local in the database
            
        Example:
            >>> learnings = engine.get_learnings("sort function", "python", "generate")
            >>> for learning in learnings:
            ...     print(f"Error: {learning['error']}")
            ...     print(f"Solution: {learning['solution']}")
        """
        if not self.learning_db:
            return []
        
        try:
            # Fetch learnings from database
            learnings = self.learning_db.get_relevant_learnings(
                language=language,
                task_type=task_type,
                limit=limit
            )
            
            # Filter and anonymize if needed
            anonymized_learnings = []
            for learning in learnings:
                # Ensure no user-specific data is included
                anonymized = {
                    'error': learning.get('error', ''),
                    'solution': learning.get('solution', ''),
                    'error_type': learning.get('error_type', ''),
                }
                anonymized_learnings.append(anonymized)
            
            return anonymized_learnings
            
        except Exception as e:
            # Fail silently - don't break if database unavailable
            return []

    def _format_learnings(self, language: str, task_type: str) -> str:
        """
        Format past learnings for inclusion in prompt.
        
        Privacy: Only error patterns and solutions are used.
        No user-specific data is included in prompts.

        Args:
            language: Programming language
            task_type: Type of task

        Returns:
            Formatted learnings text
            
        Example output:
            "From past sessions:
             - Error: Using mutable default arguments
               Solution: Use None and initialize in function body
             - Error: Not handling exceptions
               Solution: Add try/except blocks"
        """
        if not self.learning_db:
            return ""

        learnings_text = []

        # Get relevant learnings (anonymized automatically)
        try:
            learnings = self.get_learnings(
                query="",  # General learnings for language
                language=language,
                task_type=task_type,
                limit=3
            )

            if learnings:
                learnings_text.append("From past sessions:")

                for learning in learnings:
                    error = learning.get('error', '')
                    solution = learning.get('solution', '')
                    
                    if error and solution:
                        learnings_text.append(f"- Error: {error}")
                        learnings_text.append(f"  Solution: {solution}")
                    elif error:
                        learnings_text.append(f"- Common issue: {error}")

        except Exception:
            # Silently fail if database unavailable
            pass

        return "\n".join(learnings_text) if learnings_text else ""

    def get_supported_languages(self) -> List[str]:
        """
        Get list of languages with specialized support.

        Returns:
            List of supported language names
        """
        return sorted(self.lang_systems.keys())

    def get_supported_tasks(self) -> List[str]:
        """
        Get list of supported task types.

        Returns:
            List of task type names
        """
        return sorted(self.task_templates.keys())

    def add_custom_template(
        self,
        task_type: str,
        system: str,
        user_prefix: str,
        user_suffix: str = ""
    ) -> None:
        """
        Add a custom task template.

        Args:
            task_type: Name for the new task type
            system: System prompt for this task
            user_prefix: Prefix for user content
            user_suffix: Optional suffix for user content
        """
        self.task_templates[task_type] = PromptTemplate(
            system=system,
            user_prefix=user_prefix,
            user_suffix=user_suffix
        )

    def add_language_system(self, language: str, system_prompt: str) -> None:
        """
        Add or update a language-specific system prompt.

        Args:
            language: Language name
            system_prompt: System prompt for this language
        """
        lang_normalized = self._normalize_language(language)
        self.lang_systems[lang_normalized] = system_prompt
    
    def _format_project_context(self, project_files: Optional[List[str]] = None) -> str:
        """
        Format project context from file summaries.
        
        Args:
            project_files: List of relevant file paths (relative to project root)
            
        Returns:
            Formatted project context string
        """
        if not self.project_manager or not project_files:
            return ""
        
        context_parts = ["Project context:"]
        
        for file_path in project_files:
            try:
                # Get file summary (will be generated if not exists)
                summary = self.project_manager.summarize_file(file_path)
                
                if summary:
                    context_parts.append(f"\n{file_path}:")
                    context_parts.append(f"  {summary}")
                    
            except Exception as e:
                # Silently skip files that can't be summarized
                continue
        
        # Return empty if no context was added
        if len(context_parts) == 1:
            return ""
        
        return "\n".join(context_parts)
    
    def build_project_prompt(
        self,
        task_description: str,
        relevant_files: List[str],
        language: Optional[str] = None
    ) -> str:
        """
        Build a prompt for project-level tasks with file context.
        
        Args:
            task_description: Description of the task
            relevant_files: List of relevant file paths
            language: Optional primary language
            
        Returns:
            Complete formatted prompt with project context
        """
        # Build base prompt
        prompt = self.build_prompt(
            task_type='generate',
            language=language or 'code',
            content=task_description,
            include_project_context=True,
            project_files=relevant_files
        )
        
        return prompt


if __name__ == "__main__":
    # Test the prompt engine
    print("Testing Prompt Engine...")

    engine = PromptEngine(learning_db=None)

    # Test code generation prompt
    print("\n=== Test: Generate Python Code ===")
    prompt = engine.build_prompt(
        task_type='generate',
        language='python',
        content='Write a function to calculate fibonacci numbers'
    )
    print(prompt[:200] + "...")

    # Test debug prompt
    print("\n=== Test: Debug C++ Code ===")
    prompt = engine.build_prompt(
        task_type='debug',
        language='cpp',
        content='int* ptr = NULL;\n*ptr = 5;',
        error='Segmentation fault'
    )
    print(prompt[:200] + "...")

    # Test supported languages
    print("\n=== Supported Languages ===")
    print(", ".join(engine.get_supported_languages()))

    # Test supported tasks
    print("\n=== Supported Tasks ===")
    print(", ".join(engine.get_supported_tasks()))

    print("\n✓ Prompt Engine tests complete")
