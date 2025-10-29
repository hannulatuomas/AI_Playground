
"""
Context Management Module

Manages context throughout workflow execution, including:
- Context gathering from memory and vector database
- Context refinement and summarization
- Writing important context to files
- Context simplification for AI consumption
- Maintaining user intent and requirements
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import json


logger = logging.getLogger(__name__)


class ContextManager:
    """
    Manages context for workflow execution.
    
    Capabilities:
    - Gather context from multiple sources
    - Refine and summarize context
    - Store context in files
    - Create AI-friendly context representations
    - Track references (files, agents, console output)
    """
    
    def __init__(
        self,
        memory_manager: Optional[Any] = None,
        llm_router: Optional[Any] = None,
        context_storage_path: Optional[Path] = None
    ):
        """
        Initialize context manager.
        
        Args:
            memory_manager: Vector-enhanced memory manager
            llm_router: LLM router for context operations
            context_storage_path: Path to store context files
        """
        self.memory_manager = memory_manager
        self.llm_router = llm_router
        self.context_storage_path = context_storage_path or Path('./workflow_context')
        self.context_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("ContextManager initialized")
    
    def gather_context(
        self,
        prompt: str,
        specifications: Dict[str, Any],
        task_structure: Dict[str, Any],
        session_id: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Gather relevant context from all sources.
        
        Args:
            prompt: Original user prompt
            specifications: Extracted specifications
            task_structure: Decomposed task structure
            session_id: Session identifier
            additional_context: Additional context provided
            
        Returns:
            Dictionary with gathered context
        """
        logger.info("Gathering context from multiple sources")
        
        context = {
            'prompt': prompt,
            'specifications': specifications,
            'task_structure': task_structure,
            'recent_messages': [],
            'similar_tasks': [],
            'relevant_files': [],
            'agent_outputs': [],
            'additional': additional_context or {}
        }
        
        # Gather from memory if available
        if self.memory_manager and session_id:
            context.update(self._gather_from_memory(prompt, session_id))
        
        return context
    
    def _gather_from_memory(
        self,
        prompt: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Gather context from memory system.
        
        Args:
            prompt: User prompt
            session_id: Session identifier
            
        Returns:
            Context from memory
        """
        memory_context = {}
        
        try:
            # Get recent messages
            recent = self.memory_manager.get_conversation_history(
                session_id=session_id,
                limit=10
            )
            memory_context['recent_messages'] = recent
            
            # Get semantically similar past interactions
            if hasattr(self.memory_manager, 'semantic_search'):
                similar = self.memory_manager.semantic_search(
                    query=prompt,
                    n_results=5
                )
                memory_context['similar_tasks'] = similar
            
            # Get relevant file references
            if hasattr(self.memory_manager, 'search_file_references'):
                file_refs = self.memory_manager.search_file_references(
                    query=prompt,
                    n_results=5
                )
                memory_context['relevant_files'] = [
                    ref['metadata'].get('file_path', '') 
                    for ref in file_refs if 'metadata' in ref
                ]
            
            # Get relevant agent outputs
            if hasattr(self.memory_manager, 'search_agent_outputs'):
                outputs = self.memory_manager.search_agent_outputs(
                    query=prompt,
                    n_results=5
                )
                memory_context['agent_outputs'] = outputs
            
            logger.info("Successfully gathered context from memory")
            
        except Exception as e:
            logger.error(f"Failed to gather context from memory: {e}")
        
        return memory_context
    
    def refine_context(
        self,
        context: Dict[str, Any],
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Refine and summarize context to fit within token limits.
        
        Args:
            context: Raw context dictionary
            max_tokens: Maximum tokens for refined context
            
        Returns:
            Refined context
        """
        logger.info("Refining context")
        
        if not self.llm_router:
            return self._simple_refine(context, max_tokens)
        
        try:
            refinement_prompt = self._build_refinement_prompt(context)
            
            response = self.llm_router.query(
                prompt=refinement_prompt,
                temperature=0.2,
                agent_name='task_orchestrator'
            )
            
            refined_summary = response.get('response', '')
            
            return {
                'summary': refined_summary,
                'original_context': context,
                'refined': True
            }
            
        except Exception as e:
            logger.error(f"Context refinement failed: {e}")
            return self._simple_refine(context, max_tokens)
    
    def _build_refinement_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a prompt for context refinement.
        
        Args:
            context: Context to refine
            
        Returns:
            Refinement prompt
        """
        return f"""Summarize the following context into a concise, actionable format for AI agents.

**Original Prompt:**
{context.get('prompt', '')}

**Specifications:**
{json.dumps(context.get('specifications', {}), indent=2)}

**Recent Activity:**
{len(context.get('recent_messages', []))} recent messages
{len(context.get('similar_tasks', []))} similar past tasks
{len(context.get('relevant_files', []))} relevant files

**Instructions:**
Create a clear, concise summary that:
1. Preserves user intent and requirements
2. Highlights key constraints and preferences
3. Notes relevant past context
4. Identifies important files or resources
5. Provides actionable guidance for agents

Keep the summary under 500 words.
"""
    
    def _simple_refine(
        self,
        context: Dict[str, Any],
        max_tokens: int
    ) -> Dict[str, Any]:
        """
        Simple rule-based context refinement.
        
        Args:
            context: Context to refine
            max_tokens: Max tokens
            
        Returns:
            Refined context
        """
        # Estimate: ~4 chars per token
        max_chars = max_tokens * 4
        
        summary_parts = []
        
        if context.get('prompt'):
            summary_parts.append(f"Request: {context['prompt'][:200]}")
        
        if context.get('specifications', {}).get('goals'):
            goals = context['specifications']['goals']
            summary_parts.append(f"Goals: {', '.join(goals[:3])}")
        
        if context.get('recent_messages'):
            summary_parts.append(f"Recent activity: {len(context['recent_messages'])} messages")
        
        summary = " | ".join(summary_parts)[:max_chars]
        
        return {
            'summary': summary,
            'original_context': context,
            'refined': False
        }
    
    def store_context(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Store context to a file for reference.
        
        Args:
            workflow_id: Workflow identifier
            context: Context to store
            
        Returns:
            True if stored successfully
        """
        try:
            context_file = self.context_storage_path / f"{workflow_id}_context.json"
            
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Stored context for workflow {workflow_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store context: {e}")
            return False
    
    def load_context(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Load stored context from file.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Context dictionary or None
        """
        try:
            context_file = self.context_storage_path / f"{workflow_id}_context.json"
            
            if not context_file.exists():
                return None
            
            with open(context_file, 'r', encoding='utf-8') as f:
                context = json.load(f)
            
            logger.info(f"Loaded context for workflow {workflow_id[:8]}")
            return context
            
        except Exception as e:
            logger.error(f"Failed to load context: {e}")
            return None
    
    def track_reference(
        self,
        reference_type: str,
        reference_data: str,
        workflow_id: str
    ) -> bool:
        """
        Track a reference (file, agent output, etc.).
        
        Args:
            reference_type: Type of reference ('file', 'agent', 'console')
            reference_data: Reference data
            workflow_id: Workflow identifier
            
        Returns:
            True if tracked successfully
        """
        try:
            ref_file = self.context_storage_path / f"{workflow_id}_references.jsonl"
            
            reference = {
                'type': reference_type,
                'data': reference_data,
                'timestamp': str(datetime.now())
            }
            
            with open(ref_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reference) + '\n')
            
            logger.debug(f"Tracked {reference_type} reference for workflow {workflow_id[:8]}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track reference: {e}")
            return False
