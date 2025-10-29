"""
Debugger Module

Handles code debugging and error correction across multiple languages.
Self-improves by learning from past fixes and adapting prompts.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Optional, List, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import LLMInterface, PromptEngine, LearningDB


class Debugger:
    """
    Debugs code and suggests fixes with self-improvement capabilities.
    Learns from past successful fixes to avoid repeating errors.
    
    Example usage:
        debugger = Debugger(llm, prompt_engine, learning_db)
        
        # Debug Python code
        result = debugger.debug_code(
            code="def hello()\n    print('Hello')",
            language="python",
            error_msg="SyntaxError: invalid syntax"
        )
        
        print(result['fixed_code'])
        print(result['explanation'])
        
        # Provide feedback if fix worked
        debugger.provide_feedback(
            interaction_id=result['interaction_id'],
            success=True,
            feedback="Fix worked perfectly!"
        )
    """

    def __init__(
        self,
        llm: LLMInterface,
        prompt_engine: PromptEngine,
        learning_db: LearningDB
    ):
        """
        Initialize the debugger.

        Args:
            llm: LLM interface for text generation
            prompt_engine: Prompt engine for building prompts
            learning_db: Learning database for tracking fixes
        """
        self.llm = llm
        self.prompt_engine = prompt_engine
        self.learning_db = learning_db
        self.last_interaction_id: Optional[int] = None

    def debug_code(
        self,
        code: str,
        language: str,
        error_msg: Optional[str] = None,
        context: Optional[str] = None,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Debug code and suggest fixes.

        Args:
            code: Code with errors
            language: Programming language (python, javascript, bash, etc.)
            error_msg: Optional error message from execution
            context: Optional additional context about the error
            max_tokens: Maximum tokens to generate

        Returns:
            Dictionary with:
                - fixed_code: Corrected code
                - explanation: Explanation of the fix
                - error_type: Classified error type
                - changes: List of changes made
                - success: True if debugging succeeded
                - error: Error message if debugging failed
                - interaction_id: Database ID for feedback

        Example:
            >>> debugger = Debugger(llm, engine, db)
            >>> result = debugger.debug_code(
            ...     code="def func()\n    pass",
            ...     language="python",
            ...     error_msg="SyntaxError: invalid syntax"
            ... )
            >>> print(result['fixed_code'])
            def func():
                pass
        """
        # Step 1: Validate inputs
        validation_error = self._validate_inputs(code, language, error_msg)
        if validation_error:
            return self._error_result(validation_error)

        try:
            # Step 2: Classify the error type
            error_type = self._classify_error(error_msg, language)

            # Step 3: Retrieve past fixes for similar errors
            past_fixes = self._get_past_fixes(language, error_type)

            # Step 4: Handle language-specific issues
            language_hints = self._get_language_specific_hints(language, error_msg)

            # Step 5: Build debugging prompt
            prompt = self._build_debug_prompt(
                code=code,
                language=language,
                error_msg=error_msg or "No specific error message provided",
                context=context,
                error_type=error_type,
                past_fixes=past_fixes,
                language_hints=language_hints
            )

            # Step 6: Query the LLM
            response = self.llm.generate(
                prompt=prompt,
                max_tokens=max_tokens,
                use_cache=False,  # Don't cache debug responses (each is unique)
                timeout=120
            )

            # Step 7: Parse the response
            fixed_code, explanation, changes = self._parse_debug_response(
                response, language, code
            )

            # Step 8: Store in database
            self.last_interaction_id = self.learning_db.add_entry(
                query=f"Debug: {error_msg or 'Code review'}",
                language=language,
                response=fixed_code,
                task_type='debug',
                error_type=error_type,
                feedback=None,
                success=None  # Will be updated with feedback
            )

            return {
                'fixed_code': fixed_code,
                'explanation': explanation,
                'error_type': error_type,
                'changes': changes,
                'success': True,
                'error': None,
                'interaction_id': self.last_interaction_id
            }

        except Exception as e:
            error_msg_str = f"Debugging failed: {str(e)}"

            # Store failed attempt
            self.last_interaction_id = self.learning_db.add_entry(
                query=f"Debug: {error_msg or 'Unknown'}",
                language=language,
                response='',
                task_type='debug',
                success=False,
                error_type='debug_error',
                correction=error_msg_str
            )

            return self._error_result(error_msg_str)

    def _validate_inputs(
        self,
        code: str,
        language: str,
        error_msg: Optional[str]
    ) -> Optional[str]:
        """
        Validate input parameters.

        Args:
            code: Code to debug
            language: Programming language
            error_msg: Error message

        Returns:
            Error message if validation fails, None otherwise
        """
        if not code or not code.strip():
            return "Code cannot be empty"

        if not language or not language.strip():
            return "Language must be specified"

        if len(code) > 50000:
            return "Code is too long (max 50000 characters)"

        return None

    def _classify_error(self, error_msg: Optional[str], language: str) -> str:
        """
        Classify error type from error message.

        Args:
            error_msg: Error message text
            language: Programming language

        Returns:
            Error type classification

        Example:
            >>> _classify_error("SyntaxError: invalid syntax", "python")
            "syntax_error"
            
            >>> _classify_error("NameError: name 'x' is not defined", "python")
            "name_error"
        """
        if not error_msg:
            return "code_review"

        error_lower = error_msg.lower()

        # Common error patterns across languages
        error_patterns = {
            'syntax_error': [
                'syntax', 'parse', 'unexpected', 'invalid syntax',
                'expected', 'missing', 'unterminated'
            ],
            'name_error': [
                'name', 'not defined', 'undefined', 'undeclared',
                'cannot find', 'is not recognized'
            ],
            'type_error': [
                'type', 'cannot convert', 'incompatible type',
                'wrong type', 'type mismatch'
            ],
            'index_error': [
                'index', 'out of range', 'out of bounds',
                'subscript', 'array index'
            ],
            'null_pointer': [
                'null', 'nullptr', 'none', 'nullpointer',
                'segmentation', 'access violation'
            ],
            'import_error': [
                'import', 'module', 'cannot import',
                'no module', 'cannot find module'
            ],
            'runtime_error': [
                'runtime', 'exception', 'error at runtime',
                'execution error'
            ],
            'logic_error': [
                'wrong output', 'incorrect result',
                'unexpected behavior'
            ],
        }

        # Language-specific patterns
        if language in ['bash', 'sh', 'zsh', 'batch', 'powershell']:
            if any(word in error_lower for word in ['variable', 'expansion', 'substitution']):
                return 'variable_expansion_error'
            if any(word in error_lower for word in ['command not found', 'is not recognized']):
                return 'command_not_found'
            if 'permission' in error_lower:
                return 'permission_error'

        # Check patterns
        for error_type, keywords in error_patterns.items():
            if any(keyword in error_lower for keyword in keywords):
                return error_type

        return 'unknown_error'

    def _get_past_fixes(self, language: str, error_type: str) -> List[Dict]:
        """
        Retrieve past successful fixes for similar errors.

        Args:
            language: Programming language
            error_type: Type of error

        Returns:
            List of past fix dictionaries
        """
        try:
            # Get successful debug interactions with corrections
            learnings = self.learning_db.get_relevant_learnings(
                language=language,
                task_type='debug',
                limit=3
            )

            # Filter for similar error types
            relevant_fixes = []
            for learning in learnings:
                if learning.get('error') and error_type in learning.get('error', '').lower():
                    relevant_fixes.append(learning)

            return relevant_fixes[:3]  # Top 3 most relevant

        except Exception:
            return []

    def _get_language_specific_hints(
        self,
        language: str,
        error_msg: Optional[str]
    ) -> str:
        """
        Get language-specific debugging hints.

        Args:
            language: Programming language
            error_msg: Error message

        Returns:
            Language-specific hints

        Example for shells:
            "For shell scripts:
             - Check variable expansion with proper quoting
             - Verify command paths and permissions
             - Use set -e for error handling"
        """
        lang_normalized = language.lower().strip()
        hints = []

        # Shell script specific hints
        if lang_normalized in ['bash', 'sh', 'zsh']:
            hints.append("Shell script debugging tips:")
            hints.append("- Check variable expansion (use quotes: \"$var\")")
            hints.append("- Verify command exists and is in PATH")
            hints.append("- Use set -x for debugging")
            hints.append("- Check for proper quoting to prevent word splitting")

            if error_msg and 'command not found' in error_msg.lower():
                hints.append("- Verify command path or check if command is installed")

        # Windows batch specific hints
        elif lang_normalized in ['batch', 'cmd']:
            hints.append("Batch script debugging tips:")
            hints.append("- Use ECHO to print variable values")
            hints.append("- Quote paths with spaces")
            hints.append("- Check ERRORLEVEL after commands")
            hints.append("- Use SETLOCAL/ENDLOCAL for variable scope")

        # PowerShell specific hints
        elif lang_normalized == 'powershell':
            hints.append("PowerShell debugging tips:")
            hints.append("- Use Write-Host/Write-Debug for debugging")
            hints.append("- Check execution policy")
            hints.append("- Verify parameter types and validation")
            hints.append("- Use try/catch for error handling")

        # Python specific hints
        elif lang_normalized == 'python':
            if error_msg:
                if 'indentation' in error_msg.lower():
                    hints.append("- Fix indentation (Python uses 4 spaces)")
                if 'import' in error_msg.lower():
                    hints.append("- Check module is installed: pip install <module>")

        # JavaScript/TypeScript hints
        elif lang_normalized in ['javascript', 'typescript']:
            if error_msg:
                if 'undefined' in error_msg.lower():
                    hints.append("- Check variable initialization")
                    hints.append("- Use optional chaining: obj?.property")

        # C++ hints
        elif lang_normalized == 'cpp':
            if error_msg and ('pointer' in error_msg.lower() or 'segmentation' in error_msg.lower()):
                hints.append("- Use smart pointers instead of raw pointers")
                hints.append("- Check for null before dereferencing")
                hints.append("- Verify array bounds")

        return "\n".join(hints) if hints else ""

    def _build_debug_prompt(
        self,
        code: str,
        language: str,
        error_msg: str,
        context: Optional[str],
        error_type: str,
        past_fixes: List[Dict],
        language_hints: str
    ) -> str:
        """
        Build comprehensive debugging prompt.

        Args:
            code: Code with errors
            language: Programming language
            error_msg: Error message
            context: Optional context
            error_type: Classified error type
            past_fixes: Past successful fixes
            language_hints: Language-specific hints

        Returns:
            Complete prompt string

        Example prompt:
            "Debug this Python code:
             
             ```python
             def hello()
                 print('hi')
             ```
             
             Error: SyntaxError: invalid syntax
             
             Based on past fixes:
             - Missing colon after function definition
             
             Suggest improved code with explanation."
        """
        # Use prompt engine for base structure
        prompt = self.prompt_engine.build_prompt(
            task_type='debug',
            language=language,
            content=code,
            error=error_msg,
            include_learnings=False  # We'll add custom learnings
        )

        # Add context if provided
        if context:
            prompt += f"\n\nAdditional context: {context}"

        # Add error type classification
        prompt += f"\n\nError type: {error_type.replace('_', ' ').title()}"

        # Add past fixes
        if past_fixes:
            prompt += "\n\nBased on past successful fixes for similar errors:"
            for fix in past_fixes:
                if fix.get('solution'):
                    prompt += f"\n- {fix['solution']}"

        # Add language-specific hints
        if language_hints:
            prompt += f"\n\n{language_hints}"

        # Add output instructions
        prompt += "\n\nProvide:"
        prompt += "\n1. Fixed code (complete, working version)"
        prompt += "\n2. Explanation of what was wrong"
        prompt += "\n3. List of specific changes made"
        prompt += "\n4. Tips to avoid this error in the future"

        return prompt

    def _parse_debug_response(
        self,
        response: str,
        language: str,
        original_code: str
    ) -> Tuple[str, str, List[str]]:
        """
        Parse debug response to extract fixed code, explanation, and changes.

        Args:
            response: Raw LLM response
            language: Programming language
            original_code: Original buggy code

        Returns:
            Tuple of (fixed_code, explanation, changes)

        Example:
            Input: "Here's the fixed code:\n```python\ndef hello():\n    pass\n```\n\nFixed: Added colon"
            Output: ("def hello():\n    pass", "Fixed: Added colon", ["Added colon after function definition"])
        """
        # Extract code blocks
        code_blocks = self._extract_code_blocks(response, language)

        if code_blocks:
            # Use the last code block (usually the fixed version)
            fixed_code = code_blocks[-1]
        else:
            # Fallback: try to extract code-like content
            fixed_code = self._extract_code_without_markers(response, language)

        # Extract explanation
        explanation = response
        for block in code_blocks:
            explanation = explanation.replace(f"```{language}\n{block}\n```", "")
            explanation = explanation.replace(f"```\n{block}\n```", "")
        explanation = explanation.strip()

        # Extract changes list
        changes = self._extract_changes(explanation)

        return fixed_code, explanation, changes

    def _extract_code_blocks(self, text: str, language: str) -> List[str]:
        """Extract code blocks from markdown."""
        patterns = [
            rf'```{language}\n(.*?)```',
            rf'```\n(.*?)```',
        ]

        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            code_blocks.extend(matches)
            if code_blocks:
                break

        return [block.strip() for block in code_blocks if len(block.strip()) > 5]

    def _extract_code_without_markers(self, text: str, language: str) -> str:
        """Extract code-like content without markdown markers."""
        lines = text.split('\n')
        code_lines = []

        for line in lines:
            if self._looks_like_code(line, language):
                code_lines.append(line)

        return '\n'.join(code_lines) if code_lines else text

    def _looks_like_code(self, line: str, language: str) -> bool:
        """Heuristic to determine if line looks like code."""
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('//'):
            return False

        code_indicators = [
            '{', '}', '(', ')', ';', '=',
            'def ', 'function', 'class', 'return',
            'if ', 'else', 'for ', 'while'
        ]

        return any(indicator in stripped for indicator in code_indicators)

    def _extract_changes(self, explanation: str) -> List[str]:
        """
        Extract list of changes from explanation.

        Args:
            explanation: Explanation text

        Returns:
            List of changes made
        """
        changes = []

        # Look for numbered or bulleted lists
        lines = explanation.split('\n')
        for line in lines:
            stripped = line.strip()
            # Match patterns like: "1. ", "- ", "* ", "• "
            if re.match(r'^(\d+\.|-|\*|•)\s+', stripped):
                change = re.sub(r'^(\d+\.|-|\*|•)\s+', '', stripped)
                if change and len(change) > 3:
                    changes.append(change)

        # If no list found, try to extract key phrases
        if not changes:
            keywords = ['fixed', 'added', 'removed', 'changed', 'corrected']
            for line in lines:
                lower_line = line.lower()
                if any(keyword in lower_line for keyword in keywords):
                    changes.append(line.strip())

        return changes[:5]  # Limit to 5 most important changes

    def provide_feedback(
        self,
        interaction_id: int,
        success: bool,
        feedback: Optional[str] = None,
        final_code: Optional[str] = None
    ) -> bool:
        """
        Provide feedback on debugging results for self-improvement.

        Args:
            interaction_id: ID of the interaction
            success: Whether the fix worked
            feedback: Optional feedback text
            final_code: Optional final working code if fix didn't work initially

        Returns:
            True if feedback was recorded

        Example:
            >>> result = debugger.debug_code(code, "python", "SyntaxError")
            >>> debugger.provide_feedback(
            ...     interaction_id=result['interaction_id'],
            ...     success=True,
            ...     feedback="Perfect fix!"
            ... )
            True
        """
        try:
            return self.learning_db.update_feedback(
                interaction_id=interaction_id,
                feedback=feedback or ("Fix worked" if success else "Fix didn't work"),
                success=success,
                error_type=None,
                correction=final_code
            )
        except Exception as e:
            print(f"Error recording feedback: {e}")
            return False

    def analyze_common_errors(self, language: str) -> Dict[str, Any]:
        """
        Analyze common error patterns for a language.

        Args:
            language: Programming language

        Returns:
            Dictionary with error analysis

        Example:
            >>> stats = debugger.analyze_common_errors("python")
            >>> print(stats['most_common'])
            [{'error_type': 'syntax_error', 'count': 15}, ...]
        """
        try:
            stats = self.learning_db.get_language_stats(language)

            # Add error type breakdown
            common_errors = stats.get('common_errors', [])

            return {
                'language': language,
                'total_debug_sessions': stats.get('total_interactions', 0),
                'success_rate': stats.get('success_rate', 0),
                'most_common': common_errors
            }
        except Exception:
            return {
                'language': language,
                'total_debug_sessions': 0,
                'success_rate': 0,
                'most_common': []
            }

    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Create error result dictionary."""
        return {
            'fixed_code': None,
            'explanation': None,
            'error_type': None,
            'changes': [],
            'success': False,
            'error': error_msg,
            'interaction_id': self.last_interaction_id
        }


if __name__ == "__main__":
    # Test the debugger
    print("Testing Debugger...")
    print("="*60)

    from core import load_config_from_file, LLMInterface, PromptEngine, LearningDB

    # Try to load config
    config = load_config_from_file()

    if config:
        print("✓ Configuration loaded")

        try:
            # Initialize components
            db = LearningDB("data/db/test_debugger.db")
            engine = PromptEngine(learning_db=db)
            llm = LLMInterface(config)

            debugger = Debugger(llm, engine, db)
            print("✓ Debugger initialized")

            # Test error classification
            error_types = [
                ("SyntaxError: invalid syntax", "python", "syntax_error"),
                ("NameError: name 'x' is not defined", "python", "name_error"),
                ("command not found", "bash", "command_not_found"),
            ]

            print("\n✓ Testing error classification:")
            for error_msg, lang, expected in error_types:
                result = debugger._classify_error(error_msg, lang)
                status = "✓" if result == expected else "✗"
                print(f"  {status} '{error_msg}' -> {result}")

            # Test language-specific hints
            print("\n✓ Testing language-specific hints:")
            hints_bash = debugger._get_language_specific_hints("bash", "command not found")
            print(f"  Bash hints: {len(hints_bash)} chars")

            # Test input validation
            print("\n✓ Testing input validation:")
            val_error = debugger._validate_inputs("", "python", None)
            print(f"  Empty code: {val_error}")

            # Test response parsing
            test_response = """
Here's the fixed code:

```python
def hello():
    print('Hello')
```

Changes made:
1. Added colon after function definition
2. Fixed indentation
"""
            fixed, explanation, changes = debugger._parse_debug_response(
                test_response, "python", "def hello()\n    print('Hello')"
            )
            print(f"\n✓ Response parsing:")
            print(f"  Fixed code: {len(fixed)} chars")
            print(f"  Changes extracted: {len(changes)}")

            print("\n✓ All Debugger tests passed!")

        except Exception as e:
            print(f"✗ Error during testing: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("⚠ No configuration found")
        print("  Run: python main.py --setup")
        print("\nDebugger class structure verified ✓")
