"""
Context Manager Module

Manages LLM context windows by intelligently selecting and prioritizing information.
Handles token budgets, context building, and memory integration for project-level operations.

Features:
- Intelligent context building with prioritization
- Token budget management and truncation
- Integration with project files, summaries, and history
- Memory of past actions and outcomes
- Optimal information selection for small context windows
"""

import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta


class ContextManager:
    """
    Manage LLM context windows with intelligent prioritization and truncation.
    Integrates project files, summaries, history, and user rules within token budgets.
    """

    def __init__(
        self,
        project_manager=None,
        project_navigator=None,
        learning_db=None,
        prompt_engine=None,
        rag_retriever=None
    ):
        """
        Initialize the context manager.

        Args:
            project_manager: ProjectManager instance for file access
            project_navigator: ProjectNavigator for context selection
            learning_db: LearningDB instance for history/learnings
            prompt_engine: PromptEngine for prompt building

        Example:
            >>> from src.core.project_manager import ProjectManager
            >>> from src.core.learning_db import LearningDB
            >>> from src.core.prompt_engine import PromptEngine
            >>> from src.features.project_nav import ProjectNavigator
            >>> 
            >>> pm = ProjectManager(llm_interface=llm)
            >>> pn = ProjectNavigator(pm, llm)
            >>> db = LearningDB()
            >>> pe = PromptEngine(learning_db=db, project_manager=pm)
            >>> 
            >>> context_mgr = ContextManager(pm, pn, db, pe)
        """
        self.project_manager = project_manager
        self.project_navigator = project_navigator
        self.learning_db = learning_db
        self.prompt_engine = prompt_engine
        self.rag_retriever = rag_retriever
        
        # Token estimation factor (words to tokens)
        self.words_per_token = 0.75
        
        # Priority weights for context elements
        self.priority_weights = {
            'task_description': 1.0,
            'user_rules': 0.9,
            'relevant_files': 0.8,
            'recent_history': 0.7,
            'learnings': 0.6,
            'general_context': 0.5
        }

    def build_context(
        self,
        task: str,
        max_tokens: int = 4000,
        user_rules: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        language: Optional[str] = None,
        relevant_files: Optional[List[str]] = None,
        include_history: bool = True,
        include_learnings: bool = True
    ) -> Dict[str, Any]:
        """
        Build optimized context for LLM within token budget.
        
        Prioritizes information in order:
        1. Task description
        2. User rules
        3. Relevant file summaries/chunks
        4. Recent action history
        5. Learnings from past interactions
        
        Truncates from least relevant when exceeding budget.

        Args:
            task: Task description (always included)
            max_tokens: Maximum tokens for entire context
            user_rules: Optional user-defined rules
            project_id: Optional project identifier for history
            language: Programming language for learnings
            relevant_files: Optional specific files to include
            include_history: Whether to include action history
            include_learnings: Whether to include past learnings

        Returns:
            Dictionary with context sections and metadata

        Example:
            >>> context = context_mgr.build_context(
            ...     task="Add JWT authentication to API",
            ...     max_tokens=4000,
            ...     user_rules=["Use best practices", "Add tests"],
            ...     project_id="my-web-app",
            ...     language="python",
            ...     include_history=True
            ... )
            >>> print(f"Total tokens: {context['total_tokens']}")
            >>> print(f"Sections: {list(context['sections'].keys())}")
        """
        context_sections = {}
        token_usage = {}
        
        # 1. Task description (always included, highest priority)
        task_text = f"Task: {task}"
        task_tokens = self._estimate_tokens(task_text)
        context_sections['task'] = {
            'content': task_text,
            'tokens': task_tokens,
            'priority': self.priority_weights['task_description']
        }
        token_usage['task'] = task_tokens
        tokens_used = task_tokens
        tokens_remaining = max_tokens - tokens_used
        
        # 2. User rules (high priority)
        if user_rules and tokens_remaining > 0:
            rules_text = "User Rules:\n" + "\n".join(f"- {rule}" for rule in user_rules)
            rules_tokens = self._estimate_tokens(rules_text)
            
            if rules_tokens <= tokens_remaining:
                context_sections['rules'] = {
                    'content': rules_text,
                    'tokens': rules_tokens,
                    'priority': self.priority_weights['user_rules']
                }
                token_usage['rules'] = rules_tokens
                tokens_used += rules_tokens
                tokens_remaining -= rules_tokens
        
        # 3. Relevant files (summaries or chunks)
        if tokens_remaining > 0:
            files_context = self._build_files_context(
                task=task,
                relevant_files=relevant_files,
                max_tokens=int(tokens_remaining * 0.5),  # Allocate 50% of remaining
                language=language
            )
            
            if files_context:
                context_sections['files'] = files_context
                token_usage['files'] = files_context['tokens']
                tokens_used += files_context['tokens']
                tokens_remaining -= files_context['tokens']
        
        # 4. Recent history
        if include_history and project_id and tokens_remaining > 0:
            history_context = self._build_history_context(
                project_id=project_id,
                task=task,
                max_tokens=int(tokens_remaining * 0.4),  # Allocate 40% of remaining
                time_window_days=7
            )
            
            if history_context:
                context_sections['history'] = history_context
                token_usage['history'] = history_context['tokens']
                tokens_used += history_context['tokens']
                tokens_remaining -= history_context['tokens']
        
        # 5. Learnings
        if include_learnings and language and tokens_remaining > 0:
            learnings_context = self._build_learnings_context(
                language=language,
                project_id=project_id,
                max_tokens=int(tokens_remaining * 0.5),  # Use remaining
                task=task
            )
            
            if learnings_context:
                context_sections['learnings'] = learnings_context
                token_usage['learnings'] = learnings_context['tokens']
                tokens_used += learnings_context['tokens']
                tokens_remaining -= learnings_context['tokens']
        
        # Build final context
        result = {
            'sections': context_sections,
            'total_tokens': tokens_used,
            'tokens_remaining': tokens_remaining,
            'max_tokens': max_tokens,
            'token_usage': token_usage,
            'truncated': tokens_used > max_tokens
        }
        
        # If over budget, truncate (shouldn't happen with proper allocation, but safety check)
        if result['truncated']:
            result = self._truncate_context(result, max_tokens)
        
        return result

    def format_context_for_prompt(self, context: Dict[str, Any]) -> str:
        """
        Format built context into a string for prompt injection.

        Args:
            context: Context dictionary from build_context()

        Returns:
            Formatted context string

        Example:
            >>> context = context_mgr.build_context(task="Add authentication")
            >>> prompt_context = context_mgr.format_context_for_prompt(context)
            >>> full_prompt = prompt_context + "\n\n" + user_prompt
        """
        parts = []
        sections = context['sections']
        
        # Add sections in priority order
        priority_order = ['task', 'rules', 'files', 'history', 'learnings']
        
        for section_name in priority_order:
            if section_name in sections:
                section = sections[section_name]
                content = section.get('content', '')
                
                if content:
                    parts.append(content)
        
        formatted = "\n\n".join(parts)
        
        # Add metadata comment
        metadata = (
            f"\n\n<!-- Context: {context['total_tokens']} tokens used "
            f"of {context['max_tokens']} available -->"
        )
        
        return formatted + metadata

    def log_action(
        self,
        action: str,
        outcome: str,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> int:
        """
        Log an action to memory for future reference.

        Args:
            action: Action performed (e.g., "edited file", "generated code")
            outcome: Outcome/result of the action
            project_id: Optional project identifier
            file_path: Optional file path affected
            details: Optional additional details
            success: Whether action was successful

        Returns:
            Action ID (database entry ID)

        Example:
            >>> action_id = context_mgr.log_action(
            ...     action="Added authentication to API",
            ...     outcome="Successfully implemented JWT auth",
            ...     project_id="my-web-app",
            ...     file_path="api/auth.py",
            ...     success=True
            ... )
        """
        if not self.learning_db:
            return -1

        # Format details as JSON string if provided
        details_str = None
        if details:
            import json
            try:
                details_str = json.dumps(details)
            except:
                details_str = str(details)

        # Store in learning DB as an action entry
        entry_id = self.learning_db.add_action(
            action=action,
            outcome=outcome,
            project_id=project_id,
            file_path=file_path,
            details=details_str,
            success=success
        )

        return entry_id

    def get_history(
        self,
        query: Optional[str] = None,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        time_window_days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve action history matching criteria.

        Args:
            query: Optional search query for actions
            project_id: Optional project filter
            file_path: Optional file filter
            time_window_days: Number of days to look back
            limit: Maximum entries to return

        Returns:
            List of action history entries

        Example:
            >>> # Get all changes to auth.py
            >>> history = context_mgr.get_history(
            ...     file_path="api/auth.py",
            ...     time_window_days=7
            ... )
            >>> for entry in history:
            ...     print(f"{entry['timestamp']}: {entry['action']}")
            
            >>> # Search for authentication-related actions
            >>> history = context_mgr.get_history(
            ...     query="authentication",
            ...     project_id="my-web-app"
            ... )
        """
        if not self.learning_db:
            return []

        return self.learning_db.get_action_history(
            query=query,
            project_id=project_id,
            file_path=file_path,
            time_window_days=time_window_days,
            limit=limit
        )

    def summarize_history(
        self,
        project_id: Optional[str] = None,
        file_path: Optional[str] = None,
        time_window_days: int = 7
    ) -> str:
        """
        Generate a summary of recent actions.

        Args:
            project_id: Optional project filter
            file_path: Optional file filter
            time_window_days: Number of days to look back

        Returns:
            Formatted summary string

        Example:
            >>> summary = context_mgr.summarize_history(
            ...     file_path="api/auth.py",
            ...     time_window_days=7
            ... )
            >>> print(summary)
            Recent changes to api/auth.py:
            - 2025-01-16: Added JWT authentication
            - 2025-01-15: Refactored login function
        """
        history = self.get_history(
            project_id=project_id,
            file_path=file_path,
            time_window_days=time_window_days,
            limit=10
        )

        if not history:
            return "No recent history found."

        summary_parts = []
        
        if file_path:
            summary_parts.append(f"Recent changes to {file_path}:")
        elif project_id:
            summary_parts.append(f"Recent actions in project {project_id}:")
        else:
            summary_parts.append("Recent actions:")

        for entry in history:
            timestamp = entry.get('timestamp', '')
            action = entry.get('action', '')
            success = entry.get('success', True)
            
            # Format timestamp
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    timestamp_str = dt.strftime('%Y-%m-%d')
                except:
                    timestamp_str = timestamp
            else:
                timestamp_str = "Unknown"
            
            # Add success indicator
            status = "✓" if success else "✗"
            summary_parts.append(f"- {timestamp_str} {status}: {action}")

        return "\n".join(summary_parts)

    def _build_files_context(
        self,
        task: str,
        relevant_files: Optional[List[str]],
        max_tokens: int,
        language: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Build context from relevant files within token budget.
        
        Uses RAG retrieval if available (semantic search), otherwise
        falls back to ProjectNavigator (keyword search).

        Args:
            task: Task description for relevance
            relevant_files: Specific files or None for auto-selection
            max_tokens: Token budget
            language: Optional language filter

        Returns:
            Files context dictionary or None
        """
        # Try RAG retrieval first (semantic search)
        if self.rag_retriever and not relevant_files:
            try:
                rag_results = self.rag_retriever.dynamic_retrieve(
                    query=task,
                    max_tokens=max_tokens,
                    threshold=0.7,
                    language_filter=language
                )
                
                if rag_results:
                    # Format RAG results
                    header = "Relevant code from codebase (semantic search):"
                    tokens_used = self._estimate_tokens(header)
                    content_parts = [header]
                    
                    for i, result in enumerate(rag_results, 1):
                        file_path = result['file_path']
                        content = result['content']
                        start_line = result.get('start_line', '')
                        end_line = result.get('end_line', '')
                        
                        if start_line and end_line:
                            chunk_header = f"\n[{i}] {file_path} (lines {start_line}-{end_line}):"
                        else:
                            chunk_header = f"\n[{i}] {file_path}:"
                        
                        chunk_text = f"{chunk_header}\n{content}"
                        chunk_tokens = self._estimate_tokens(chunk_text)
                        
                        if tokens_used + chunk_tokens <= max_tokens:
                            content_parts.append(chunk_text)
                            tokens_used += chunk_tokens
                    
                    content = "\n".join(content_parts)
                    
                    return {
                        'content': content,
                        'tokens': tokens_used,
                        'priority': self.priority_weights['relevant_files'],
                        'files_included': len(rag_results),
                        'method': 'rag'
                    }
            except Exception as e:
                # Fall back to traditional method if RAG fails
                print(f"Note: RAG retrieval failed ({e}), using keyword search")
        
        # Fallback: Traditional keyword-based or specified files
        if not self.project_manager and not self.project_navigator:
            return None

        files_to_include = []
        
        # Get relevant files
        if relevant_files:
            # Use provided files
            files_to_include = relevant_files
        elif self.project_navigator:
            # Auto-select relevant files
            context_files = self.project_navigator.get_relevant_context(
                task=task,
                max_files=5,
                use_llm_ranking=False,  # Use keyword for speed
                language_filter=language
            )
            files_to_include = [f['path'] for f in context_files]

        if not files_to_include:
            return None

        # Build file summaries
        files_content = []
        tokens_used = 0
        
        header = "Relevant project files:"
        tokens_used += self._estimate_tokens(header)
        files_content.append(header)
        
        for file_path in files_to_include:
            if tokens_used >= max_tokens:
                break
            
            # Get file summary
            summary = None
            if self.project_manager:
                try:
                    summary = self.project_manager.file_index.get(file_path, {}).get('summary')
                except:
                    pass
            
            if summary:
                file_text = f"\n{file_path}:\n  {summary}"
                file_tokens = self._estimate_tokens(file_text)
                
                if tokens_used + file_tokens <= max_tokens:
                    files_content.append(file_text)
                    tokens_used += file_tokens

        content = "\n".join(files_content)
        
        return {
            'content': content,
            'tokens': tokens_used,
            'priority': self.priority_weights['relevant_files'],
            'files_included': len(files_content) - 1,  # Minus header
            'method': 'keyword'
        }

    def _build_history_context(
        self,
        project_id: str,
        task: str,
        max_tokens: int,
        time_window_days: int
    ) -> Optional[Dict[str, Any]]:
        """
        Build context from recent action history.

        Args:
            project_id: Project identifier
            task: Current task for relevance
            max_tokens: Token budget
            time_window_days: Days to look back

        Returns:
            History context dictionary or None
        """
        if not self.learning_db:
            return None

        # Get recent history
        history = self.get_history(
            project_id=project_id,
            time_window_days=time_window_days,
            limit=10
        )

        if not history:
            return None

        history_content = []
        tokens_used = 0
        
        header = "Recent project actions:"
        tokens_used += self._estimate_tokens(header)
        history_content.append(header)
        
        for entry in history:
            if tokens_used >= max_tokens:
                break
            
            action = entry.get('action', '')
            outcome = entry.get('outcome', '')
            timestamp = entry.get('timestamp', '')
            
            # Format entry
            entry_text = f"\n- {action}"
            if outcome:
                entry_text += f": {outcome}"
            
            entry_tokens = self._estimate_tokens(entry_text)
            
            if tokens_used + entry_tokens <= max_tokens:
                history_content.append(entry_text)
                tokens_used += entry_tokens

        content = "\n".join(history_content)
        
        return {
            'content': content,
            'tokens': tokens_used,
            'priority': self.priority_weights['recent_history'],
            'entries_included': len(history_content) - 1
        }

    def _build_learnings_context(
        self,
        language: str,
        project_id: Optional[str],
        max_tokens: int,
        task: str
    ) -> Optional[Dict[str, Any]]:
        """
        Build context from past learnings.

        Args:
            language: Programming language
            project_id: Optional project filter
            max_tokens: Token budget
            task: Current task for relevance

        Returns:
            Learnings context dictionary or None
        """
        if not self.learning_db:
            return None

        # Get relevant learnings
        learnings = self.learning_db.get_relevant_learnings(
            language=language,
            project_id=project_id,
            limit=5
        )

        if not learnings:
            return None

        learnings_content = []
        tokens_used = 0
        
        header = "Learnings from past sessions:"
        tokens_used += self._estimate_tokens(header)
        learnings_content.append(header)
        
        for learning in learnings:
            if tokens_used >= max_tokens:
                break
            
            error = learning.get('error', '')
            solution = learning.get('solution', '')
            
            if error and solution:
                learning_text = f"\n- Issue: {error}\n  Solution: {solution}"
            elif error:
                learning_text = f"\n- Common issue: {error}"
            else:
                continue
            
            learning_tokens = self._estimate_tokens(learning_text)
            
            if tokens_used + learning_tokens <= max_tokens:
                learnings_content.append(learning_text)
                tokens_used += learning_tokens

        content = "\n".join(learnings_content)
        
        return {
            'content': content,
            'tokens': tokens_used,
            'priority': self.priority_weights['learnings'],
            'learnings_included': len(learnings_content) - 1
        }

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count from text.
        
        Uses simple heuristic: words / 0.75
        More accurate than character count, close to actual tokenization.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        if not text:
            return 0
        
        # Count words (split by whitespace)
        words = len(text.split())
        
        # Estimate tokens
        tokens = int(words / self.words_per_token)
        
        return max(1, tokens)  # Minimum 1 token

    def _truncate_context(
        self,
        context: Dict[str, Any],
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Truncate context to fit within token budget.
        
        Removes sections starting from lowest priority.

        Args:
            context: Context dictionary
            max_tokens: Maximum tokens allowed

        Returns:
            Truncated context dictionary
        """
        sections = context['sections']
        tokens_used = context['total_tokens']
        
        # Sort sections by priority (lowest first)
        sorted_sections = sorted(
            sections.items(),
            key=lambda x: x[1].get('priority', 0)
        )
        
        # Remove sections until under budget
        for section_name, section_data in sorted_sections:
            if tokens_used <= max_tokens:
                break
            
            # Don't remove task (highest priority)
            if section_name == 'task':
                continue
            
            # Remove section
            section_tokens = section_data.get('tokens', 0)
            del sections[section_name]
            tokens_used -= section_tokens
            
            if section_name in context['token_usage']:
                del context['token_usage'][section_name]
        
        # Update context
        context['sections'] = sections
        context['total_tokens'] = tokens_used
        context['tokens_remaining'] = max_tokens - tokens_used
        context['truncated'] = True
        
        return context


if __name__ == "__main__":
    # Test the context manager
    print("Testing Context Manager...")
    
    from src.core.learning_db import LearningDB
    
    try:
        db = LearningDB()
        context_mgr = ContextManager(learning_db=db)
        print("✓ Context Manager created")
        
        # Test building context
        print("\n=== Test: Build Context ===")
        context = context_mgr.build_context(
            task="Add authentication to API",
            max_tokens=2000,
            user_rules=["Use JWT", "Add tests"],
            language="python"
        )
        print(f"Total tokens: {context['total_tokens']}")
        print(f"Sections: {list(context['sections'].keys())}")
        
        # Test formatting
        print("\n=== Test: Format Context ===")
        formatted = context_mgr.format_context_for_prompt(context)
        print(f"Formatted length: {len(formatted)} characters")
        
        # Test action logging
        print("\n=== Test: Log Action ===")
        action_id = context_mgr.log_action(
            action="Added authentication",
            outcome="Successfully implemented JWT",
            project_id="test-project",
            success=True
        )
        print(f"Action logged with ID: {action_id}")
        
        # Test history retrieval
        print("\n=== Test: Get History ===")
        history = context_mgr.get_history(
            project_id="test-project",
            limit=5
        )
        print(f"Retrieved {len(history)} history entries")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
