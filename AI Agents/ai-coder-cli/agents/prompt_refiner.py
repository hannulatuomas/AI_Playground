
"""
Prompt Refinement Agent

This agent refines and optimizes prompts for better LLM responses using:
- Chain-of-Thought (CoT) prompting
- Few-shot examples
- Structured prompt formatting
- Task decomposition
"""

from typing import Dict, Any, List

from .base import Agent


class PromptRefinerAgent(Agent):
    """
    Agent specialized for prompt refinement and optimization.
    
    Features:
    - Apply Chain-of-Thought reasoning
    - Add few-shot examples
    - Structure prompts with clear sections
    - Decompose complex tasks
    - Add constraints and requirements
    - Optimize for specific LLM providers
    """
    
    def __init__(
        self,
        name: str = "prompt_refiner",
        description: str = "Prompt refinement agent with CoT and few-shot",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
        
        self.refinement_techniques = [
            'chain_of_thought',
            'few_shot',
            'structured',
            'task_decomposition',
            'constraints'
        ]
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refine a prompt for better LLM performance.
        
        Args:
            task: Original prompt or request to refine
            context: Context with optional 'original_prompt', 'techniques', 'target_llm'
            
        Returns:
            Result with refined prompt
        """
        self._log_action("Starting prompt refinement", task[:100])
        
        try:
            # Get original prompt
            original_prompt = context.get('original_prompt', task)
            
            # Determine techniques to apply
            techniques = context.get('techniques', ['chain_of_thought', 'structured'])
            if isinstance(techniques, str):
                techniques = [techniques]
            
            # Apply refinement
            refined_prompt = self._refine_prompt(
                original_prompt,
                techniques,
                context
            )
            
            # Calculate improvement metrics
            metrics = self._calculate_metrics(original_prompt, refined_prompt)
            
            self._log_action("Prompt refined", f"Techniques: {', '.join(techniques)}")
            
            return self._build_success_result(
                message="Prompt successfully refined",
                data={
                    'original_prompt': original_prompt,
                    'refined_prompt': refined_prompt,
                    'techniques_applied': techniques,
                    'metrics': metrics
                },
                next_context={
                    'refined_prompt': refined_prompt,
                    'use_refined': True
                }
            )
            
        except Exception as e:
            self.logger.exception("Prompt refinement failed")
            return self._build_error_result(f"Refinement error: {str(e)}", e)
    
    def _refine_prompt(
        self,
        original_prompt: str,
        techniques: List[str],
        context: Dict[str, Any]
    ) -> str:
        """Apply refinement techniques to prompt."""
        prompt = original_prompt
        
        # Apply each technique in order
        for technique in techniques:
            if technique == 'chain_of_thought':
                prompt = self._apply_chain_of_thought(prompt, context)
            elif technique == 'few_shot':
                prompt = self._apply_few_shot(prompt, context)
            elif technique == 'structured':
                prompt = self._apply_structured_format(prompt, context)
            elif technique == 'task_decomposition':
                prompt = self._apply_task_decomposition(prompt, context)
            elif technique == 'constraints':
                prompt = self._apply_constraints(prompt, context)
        
        return prompt
    
    def _apply_chain_of_thought(self, prompt: str, context: Dict[str, Any]) -> str:
        """Apply Chain-of-Thought prompting."""
        cot_instruction = """
Think through this step-by-step:
1. Understand the requirements
2. Break down the problem
3. Consider edge cases
4. Plan the solution
5. Implement carefully

"""
        
        # Check if CoT is already present
        if 'step-by-step' in prompt.lower() or 'think through' in prompt.lower():
            return prompt
        
        return cot_instruction + prompt + "\n\nProvide your reasoning before the final answer."
    
    def _apply_few_shot(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add few-shot examples if available."""
        examples = context.get('examples', [])
        
        if not examples:
            # Generate generic examples based on task type
            examples = self._generate_examples(prompt)
        
        if not examples:
            return prompt
        
        examples_text = "Here are some examples:\n\n"
        for i, example in enumerate(examples[:3], 1):  # Limit to 3 examples
            examples_text += f"Example {i}:\n"
            examples_text += f"Input: {example.get('input', 'N/A')}\n"
            examples_text += f"Output: {example.get('output', 'N/A')}\n\n"
        
        return examples_text + "\nNow, for your task:\n" + prompt
    
    def _apply_structured_format(self, prompt: str, context: Dict[str, Any]) -> str:
        """Structure prompt with clear sections."""
        # Check if already structured
        if '###' in prompt or 'Task:' in prompt or 'Requirements:' in prompt:
            return prompt
        
        structured = f"""### Task
{prompt}

### Requirements
- Provide clear, accurate response
- Follow best practices
- Include necessary details
- Handle edge cases

### Output Format
Please provide your response in a clear, organized manner.
"""
        
        return structured
    
    def _apply_task_decomposition(self, prompt: str, context: Dict[str, Any]) -> str:
        """Decompose complex tasks into steps."""
        # Use LLM to decompose the task
        decomposition_prompt = f"""Break down this task into clear, actionable steps:

Task: {prompt}

Provide a numbered list of steps.
"""
        
        try:
            llm_result = self._get_llm_response(decomposition_prompt, temperature=0.3)
            steps = llm_result.get('response', '')
            
            return f"""### Task Breakdown
{steps}

### Original Task
{prompt}

### Instructions
Follow the steps above to complete the task.
"""
        except Exception as e:
            self.logger.warning(f"Task decomposition failed: {e}")
            return prompt
    
    def _apply_constraints(self, prompt: str, context: Dict[str, Any]) -> str:
        """Add constraints and guidelines."""
        constraints = context.get('constraints', [])
        
        if not constraints:
            # Default constraints
            constraints = [
                "Be concise and clear",
                "Provide accurate information",
                "Use proper formatting",
                "Explain your reasoning"
            ]
        
        constraints_text = "\n### Constraints\n"
        for constraint in constraints:
            constraints_text += f"- {constraint}\n"
        
        return prompt + "\n" + constraints_text
    
    def _generate_examples(self, prompt: str) -> List[Dict[str, str]]:
        """Generate example inputs/outputs based on prompt."""
        # This is a simplified version
        # In practice, you might want to use LLM to generate examples
        
        prompt_lower = prompt.lower()
        
        # Code generation examples
        if 'code' in prompt_lower or 'function' in prompt_lower:
            return [
                {
                    'input': 'Write a function to calculate factorial',
                    'output': 'def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)'
                }
            ]
        
        # Text processing examples
        if 'summarize' in prompt_lower or 'summary' in prompt_lower:
            return [
                {
                    'input': 'Summarize: The quick brown fox jumps over the lazy dog.',
                    'output': 'A fox jumps over a dog.'
                }
            ]
        
        return []
    
    def _calculate_metrics(self, original: str, refined: str) -> Dict[str, Any]:
        """Calculate improvement metrics."""
        return {
            'original_length': len(original),
            'refined_length': len(refined),
            'length_increase': len(refined) - len(original),
            'original_words': len(original.split()),
            'refined_words': len(refined.split()),
            'structure_added': '###' in refined and '###' not in original,
            'examples_added': 'Example' in refined and 'Example' not in original,
            'cot_added': 'step-by-step' in refined.lower() and 'step-by-step' not in original.lower()
        }

