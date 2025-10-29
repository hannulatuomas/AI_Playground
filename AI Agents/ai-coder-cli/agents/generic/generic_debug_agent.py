

"""
Generic Debug Agent

Fallback debug agent for unsupported languages using LLM-based approaches.
"""

import os
import re
from typing import Dict, Any

from ..base import DebugAgentBase


class GenericDebugAgent(DebugAgentBase):
    """
    Generic debug agent for any language.
    
    This agent provides fallback debugging functionality for languages
    that don't have specific implementations. It uses LLM to analyze
    errors, stack traces, and provide debugging guidance.
    """
    
    def __init__(
        self,
        name: str = "debug_generic",
        description: str = "Generic debug agent for any language",
        **kwargs
    ):
        super().__init__(name=name, description=description, **kwargs)
    
    def _detect_debugger(self) -> str:
        """
        Return generic debugger identifier.
        """
        return 'generic'
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set a breakpoint (stored in memory for reference).
        """
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path or not line_number:
            return self._build_error_result("file_path and line_number required")
        
        # Validate file exists
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
        # Store breakpoint
        if file_path not in self._breakpoints:
            self._breakpoints[file_path] = []
        
        if line_number not in self._breakpoints[file_path]:
            self._breakpoints[file_path].append(line_number)
            self._breakpoints[file_path].sort()
        
        return self._build_success_result(
            f"Breakpoint set at {file_path}:{line_number}",
            data={
                'breakpoints': self._breakpoints,
                'file_path': file_path,
                'line_number': line_number,
                'note': 'This is a logical breakpoint for tracking. '
                       'Use language-specific debuggers for actual debugging.'
            }
        )
    
    def _analyze_stack_trace(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a stack trace using LLM.
        """
        stack_trace = context.get('stack_trace', '')
        
        if not stack_trace:
            return self._build_error_result("stack_trace required")
        
        # Use LLM to analyze the stack trace
        prompt = f"""Analyze this stack trace and provide debugging insights:

Stack Trace:
{stack_trace}

Provide:
1. Root cause identification
2. Affected code locations
3. Recommended fixes
4. Debugging strategy

Be specific and actionable."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            # Try to extract frames from stack trace
            frames = self._parse_generic_stack_trace(stack_trace)
            
            return self._build_success_result(
                "Stack trace analyzed",
                data={
                    'frames': frames,
                    'frame_count': len(frames),
                    'analysis': analysis
                }
            )
        except Exception as e:
            return self._build_error_result(
                f"Stack trace analysis failed: {str(e)}",
                error=e
            )
    
    def _parse_generic_stack_trace(self, stack_trace: str) -> list:
        """
        Attempt to parse stack trace frames generically.
        
        This tries to extract file paths and line numbers using
        common patterns across languages.
        """
        frames = []
        lines = stack_trace.split('\n')
        
        # Common patterns for stack traces
        patterns = [
            r'at\s+(.+?)\s+\((.+?):(\d+)',  # Java/C#-style
            r'File\s+"(.+?)",\s+line\s+(\d+)',  # Python-style
            r'(.+?):(\d+):(\d+)',  # Generic file:line:col
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) >= 2:
                        frames.append({
                            'file': match.group(1) if len(match.groups()) > 1 else 'unknown',
                            'line': match.group(2) if len(match.groups()) > 1 else match.group(1),
                            'context': line.strip()
                        })
                    break
        
        return frames
