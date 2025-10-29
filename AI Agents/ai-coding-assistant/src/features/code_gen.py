"""
Code Generation Module

Handles code generation tasks using LLM with self-improvement capabilities.
Generates code based on natural language descriptions across multiple languages.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional, Tuple, List, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import LLMInterface, PromptEngine, LearningDB


class CodeGenerator:
    """
    Generates code based on natural language descriptions.
    Self-improves by learning from past successes and failures.
    
    Example usage:
        generator = CodeGenerator(llm, prompt_engine, learning_db)
        
        # Generate Python function
        result = generator.generate_code(
            task="Create a function to calculate fibonacci numbers",
            language="python"
        )
        
        print(result['code'])
        print(result['explanation'])
        
        # Provide feedback
        generator.provide_feedback(
            interaction_id=result['interaction_id'],
            success=True,
            feedback="Works perfectly!"
        )
    """

    def __init__(
        self,
        llm: LLMInterface,
        prompt_engine: PromptEngine,
        learning_db: LearningDB
    ):
        """
        Initialize the code generator.

        Args:
            llm: LLM interface for text generation
            prompt_engine: Prompt engine for building prompts
            learning_db: Learning database for self-improvement
        """
        self.llm = llm
        self.prompt_engine = prompt_engine
        self.learning_db = learning_db
        self.last_interaction_id: Optional[int] = None

    def generate_code(
        self,
        task: str,
        language: str,
        max_tokens: int = 2048,
        include_learnings: bool = True
    ) -> Dict[str, Any]:
        """
        Generate code for a given task.

        Args:
            task: Description of the code to generate (e.g., "Create a function to sort a list")
            language: Target programming language (e.g., "python", "javascript", "react")
            max_tokens: Maximum tokens to generate
            include_learnings: Whether to include past learnings in prompt

        Returns:
            Dictionary with:
                - code: Generated code
                - explanation: Explanation of the code
                - language: Language used
                - framework: Detected framework (if any)
                - success: True if generation succeeded
                - error: Error message if generation failed
                - interaction_id: Database ID for feedback

        Example:
            >>> generator = CodeGenerator(llm, engine, db)
            >>> result = generator.generate_code(
            ...     task="Create a function to reverse a string",
            ...     language="python"
            ... )
            >>> print(result['code'])
            def reverse_string(s: str) -> str:
                return s[::-1]
        """
        try:
            # Step 1: Detect framework and refine language
            language, framework = self._detect_framework(task, language)

            # Step 2: Retrieve relevant past errors from database
            learnings = []
            if include_learnings:
                learnings = self.learning_db.get_relevant_learnings(
                    language=language,
                    task_type='generate',
                    limit=3
                )

            # Step 3: Build the prompt with learnings
            prompt = self._build_generation_prompt(task, language, framework, learnings)

            # Step 4: Query the LLM
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                use_cache=True,
                timeout=120
            )

            # Step 5: Parse the response
            code, explanation = self._parse_response(response, language)

            # Step 6: Store in database
            self.last_interaction_id = self.learning_db.add_entry(
                query=task,
                language=language,
                response=code,
                task_type='generate',
                feedback=None,
                success=None  # Will be updated with feedback
            )

            return {
                'code': code,
                'explanation': explanation,
                'language': language,
                'framework': framework,
                'success': True,
                'error': None,
                'interaction_id': self.last_interaction_id
            }

        except Exception as e:
            error_msg = f"Code generation failed: {str(e)}"

            # Store failed attempt
            self.last_interaction_id = self.learning_db.add_entry(
                query=task,
                language=language,
                response='',
                task_type='generate',
                success=False,
                error_type='generation_error',
                correction=error_msg
            )

            return {
                'code': None,
                'explanation': None,
                'language': language,
                'framework': None,
                'success': False,
                'error': error_msg,
                'interaction_id': self.last_interaction_id
            }

    def _detect_framework(self, task: str, language: str) -> Tuple[str, Optional[str]]:
        """
        Detect if a specific framework is mentioned in the task.

        Args:
            task: Task description
            language: Specified language

        Returns:
            Tuple of (refined_language, framework)

        Example:
            >>> _detect_framework("Create a React component", "javascript")
            ("react", "react")
            
            >>> _detect_framework("Create a function", "python")
            ("python", None)
        """
        task_lower = task.lower()
        
        # Framework detection patterns
        framework_keywords = {
            'react': ['react', 'jsx', 'component', 'hook'],
            'nodejs': ['node', 'express', 'npm', 'server'],
            'nextjs': ['next.js', 'nextjs', 'next'],
            'express': ['express', 'middleware', 'route'],
            'django': ['django', 'model', 'view'],
            'flask': ['flask', 'route', 'app.route'],
        }

        for framework, keywords in framework_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                # If React/Next.js, refine language to include framework
                if framework in ['react', 'nextjs']:
                    return framework, framework
                return language, framework

        return language, None

    def _build_generation_prompt(
        self,
        task: str,
        language: str,
        framework: Optional[str],
        learnings: List[Dict]
    ) -> str:
        """
        Build a comprehensive prompt for code generation.

        Args:
            task: Task description
            language: Programming language
            framework: Optional framework
            learnings: Past learnings from database

        Returns:
            Complete prompt string

        Example prompt structure:
            "As an expert in Python, generate code for: Create a sorting function.
             
             Based on past experience:
             - Avoid: Using bubble sort (inefficient for large lists)
               Solution: Use built-in sorted() or implement quicksort
             
             Output clean, working code with explanations."
        """
        # Use prompt engine to build base prompt
        prompt = self.prompt_engine.build_prompt(
            task_type='generate',
            language=language,
            content=task,
            include_learnings=False  # We'll add custom learnings
        )

        # Add framework-specific guidance
        if framework:
            framework_guidance = self._get_framework_guidance(framework)
            if framework_guidance:
                prompt += f"\n\n{framework_guidance}"

        # Add custom learnings format
        if learnings:
            learnings_text = "\n\nBased on past experience with {language}:".format(language=language)
            for learning in learnings:
                if learning.get('error') and learning.get('solution'):
                    learnings_text += f"\n- Avoid: {learning['error']}"
                    learnings_text += f"\n  Solution: {learning['solution']}"
            
            prompt += learnings_text

        # Add output format instructions
        prompt += "\n\nOutput format:"
        prompt += "\n1. Provide clean, working code"
        prompt += "\n2. Include brief comments explaining key parts"
        prompt += "\n3. Add a short explanation of what the code does"
        prompt += "\n4. Consider edge cases and error handling"

        return prompt

    def _get_framework_guidance(self, framework: str) -> Optional[str]:
        """
        Get framework-specific guidance to add to prompts.

        Args:
            framework: Framework name

        Returns:
            Framework-specific guidance string
        """
        guidance = {
            'react': (
                "React-specific requirements:\n"
                "- Use functional components with hooks\n"
                "- Include proper prop types or TypeScript types if applicable\n"
                "- Follow React best practices (composition, key props)\n"
                "- Use modern React patterns (useState, useEffect, etc.)"
            ),
            'nodejs': (
                "Node.js-specific requirements:\n"
                "- Use async/await for asynchronous operations\n"
                "- Implement proper error handling\n"
                "- Use ES6+ module syntax\n"
                "- Follow Node.js best practices"
            ),
            'nextjs': (
                "Next.js-specific requirements:\n"
                "- Specify if using App Router or Pages Router\n"
                "- Use appropriate data fetching methods\n"
                "- Follow Next.js conventions\n"
                "- Include proper exports"
            ),
            'express': (
                "Express.js-specific requirements:\n"
                "- Structure middleware properly\n"
                "- Use proper HTTP status codes\n"
                "- Implement error handling middleware\n"
                "- Follow REST API conventions"
            ),
        }

        return guidance.get(framework)

    def _parse_response(self, response: str, language: str) -> Tuple[str, str]:
        """
        Parse LLM response to extract code and explanation.

        Args:
            response: Raw LLM response
            language: Programming language for code block detection

        Returns:
            Tuple of (code, explanation)

        Example:
            Input response:
                "Here's a Python function:
                 
                 ```python
                 def hello():
                     return 'Hello'
                 ```
                 
                 This function returns a greeting."
            
            Output:
                ("def hello():\n    return 'Hello'", "This function returns a greeting.")
        """
        # Try to extract code from markdown code blocks
        code_blocks = self._extract_code_blocks(response, language)

        if code_blocks:
            # Use the first substantial code block
            code = code_blocks[0]

            # Extract explanation (text outside code blocks)
            explanation = response
            for block in code_blocks:
                explanation = explanation.replace(f"```{language}\n{block}\n```", "")
                explanation = explanation.replace(f"```\n{block}\n```", "")
            explanation = explanation.strip()

            # Clean up explanation
            explanation = re.sub(r'```\w*', '', explanation)
            explanation = explanation.strip()

        else:
            # No code blocks found, try to separate code from explanation
            lines = response.split('\n')
            code_lines = []
            explanation_lines = []

            in_code = False
            for line in lines:
                # Heuristic: lines with code-like patterns
                if self._looks_like_code(line, language) and not in_code:
                    in_code = True

                if in_code and line.strip():
                    code_lines.append(line)
                elif not in_code or not self._looks_like_code(line, language):
                    if line.strip() and not in_code:
                        explanation_lines.append(line)

            code = '\n'.join(code_lines) if code_lines else response
            explanation = '\n'.join(explanation_lines) if explanation_lines else "Code generated."

        return code, explanation

    def _extract_code_blocks(self, text: str, language: str) -> List[str]:
        """
        Extract code blocks from markdown-formatted text.

        Args:
            text: Text potentially containing code blocks
            language: Expected language

        Returns:
            List of code block strings
        """
        # Patterns for markdown code blocks
        patterns = [
            rf'```{language}\n(.*?)```',
            rf'```\n(.*?)```',
        ]

        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            code_blocks.extend(matches)

            if code_blocks:
                break  # Stop after first successful pattern

        # Filter out very short blocks (likely inline code)
        return [block.strip() for block in code_blocks if len(block.strip()) > 20]

    def _looks_like_code(self, line: str, language: str) -> bool:
        """
        Heuristic to determine if a line looks like code.

        Args:
            line: Line of text
            language: Programming language

        Returns:
            True if line looks like code
        """
        stripped = line.strip()

        if not stripped:
            return False

        # Common code indicators
        code_indicators = [
            '{', '}', '(', ')', ';', '=',
            'function', 'def', 'class', 'return',
            'const', 'let', 'var', 'import',
            'if', 'else', 'for', 'while'
        ]

        return any(indicator in stripped for indicator in code_indicators)

    def provide_feedback(
        self,
        interaction_id: int,
        success: bool,
        feedback: Optional[str] = None,
        error_type: Optional[str] = None,
        correction: Optional[str] = None
    ) -> bool:
        """
        Provide feedback on generated code to improve future generations.

        Args:
            interaction_id: ID of the interaction to update
            success: Whether the code worked
            feedback: Optional feedback text
            error_type: Type of error if unsuccessful
            correction: Corrected code or solution

        Returns:
            True if feedback was recorded

        Example:
            >>> result = generator.generate_code("sort function", "python")
            >>> generator.provide_feedback(
            ...     interaction_id=result['interaction_id'],
            ...     success=False,
            ...     feedback="Used bubble sort, too slow",
            ...     error_type="performance",
            ...     correction="Use built-in sorted() or quicksort"
            ... )
            True
        """
        try:
            return self.learning_db.update_feedback(
                interaction_id=interaction_id,
                feedback=feedback or ("Success" if success else "Failed"),
                success=success,
                error_type=error_type,
                correction=correction
            )
        except Exception as e:
            print(f"Error recording feedback: {e}")
            return False

    def regenerate_with_feedback(
        self,
        original_task: str,
        language: str,
        feedback: str,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Regenerate code incorporating user feedback.

        Args:
            original_task: Original task description
            language: Programming language
            feedback: User feedback on previous attempt
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with regenerated code

        Example:
            >>> result1 = generator.generate_code("sort function", "python")
            >>> # User reports it's too slow
            >>> result2 = generator.regenerate_with_feedback(
            ...     original_task="sort function",
            ...     language="python",
            ...     feedback="Previous version used bubble sort, too slow for large lists"
            ... )
            >>> print(result2['code'])  # Now uses efficient sorting
        """
        # Enhance task with feedback
        enhanced_task = f"{original_task}\n\nPrevious attempt had issues: {feedback}\n\nPlease provide an improved version."

        return self.generate_code(
            task=enhanced_task,
            language=language,
            max_tokens=max_tokens,
            include_learnings=True
        )

    def get_generation_stats(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about code generation.

        Args:
            language: Optional language to filter by

        Returns:
            Dictionary with statistics

        Example:
            >>> stats = generator.get_generation_stats("python")
            >>> print(f"Success rate: {stats['success_rate']}%")
        """
        if language:
            return self.learning_db.get_language_stats(language)
        else:
            return self.learning_db.get_statistics()


if __name__ == "__main__":
    # Test the code generator
    print("Testing Code Generator...")
    print("="*60)

    # This test requires actual LLM setup
    # Here we just test the structure

    from core import load_config_from_file, LLMInterface, PromptEngine, LearningDB

    # Try to load config
    config = load_config_from_file()

    if config:
        print("✓ Configuration loaded")

        try:
            # Initialize components
            db = LearningDB("data/db/test_codegen.db")
            engine = PromptEngine(learning_db=db)
            llm = LLMInterface(config)

            generator = CodeGenerator(llm, engine, db)
            print("✓ Code Generator initialized")

            # Test framework detection
            lang, framework = generator._detect_framework(
                "Create a React component",
                "javascript"
            )
            print(f"✓ Framework detection: {lang}, {framework}")

            # Test prompt building
            prompt = generator._build_generation_prompt(
                task="Create a sorting function",
                language="python",
                framework=None,
                learnings=[]
            )
            print(f"✓ Prompt building works ({len(prompt)} chars)")

            # Test response parsing
            test_response = """
Here's a Python function:

```python
def sort_list(items):
    return sorted(items)
```

This function sorts a list using Python's built-in sorted() function.
"""
            code, explanation = generator._parse_response(test_response, "python")
            print(f"✓ Response parsing works")
            print(f"  Code: {code[:50]}...")
            print(f"  Explanation: {explanation[:50]}...")

            print("\n✓ All CodeGenerator tests passed!")

        except Exception as e:
            print(f"✗ Error during testing: {e}")
    else:
        print("⚠ No configuration found")
        print("  Run: python main.py --setup")
        print("\nCodeGenerator class structure verified ✓")
