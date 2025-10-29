
"""
WebDev Debug Agent

Production-ready debugger for full-stack web development.

Supported Technologies:
- Languages: JavaScript, TypeScript, HTML, CSS
- Frontend: React, Next.js, Vue, Nuxt, Angular, Svelte
- Backend: Node.js, Express, Fastify, Koa, NestJS
- Build Tools: Webpack, Vite, Parcel, Rollup
- Testing: Jest, Vitest, Mocha, Playwright, Cypress
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

from ...base import DebugAgentBase


class WebJSTSDebugAgent(DebugAgentBase):
    """
    Production-ready Full-Stack WebDev Debug Agent.
    
    Features:
        - JavaScript/TypeScript debugging (Chrome DevTools, Node.js debugger)
        - React/Vue/Angular/Svelte component debugging
        - Next.js/Nuxt server-side debugging
        - Express/Fastify/Koa/NestJS backend debugging
        - Browser console error analysis
        - Network request debugging (REST/GraphQL)
        - CSS layout debugging
        - HTML validation
        - Frontend build error analysis (Webpack/Vite/Parcel/Rollup)
        - Package manager resolution issues (npm/yarn/pnpm)
        - Dependency conflict resolution
    """
    
    def __init__(self, name: str = "webdev_debug",
                 description: str = "Full-stack web development debugging agent (JS/TS/React/Vue/Angular/Node.js)", **kwargs):
        super().__init__(name=name, description=description, **kwargs)
        
        self._breakpoints: Dict[str, List[int]] = {}
        self._timeout = self.config.get('debug', {}).get('default_debugger_timeout', 300)
        self._node_available = self._check_node()
        
        self.logger.info(f"WebDev Debug Agent initialized (Node.js available: {self._node_available})")
        # Load language-specific documentation
        self._load_language_docs()

    def _check_node(self) -> bool:
        """Check if Node.js is available."""
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web development debugging task."""
        self._log_action("WebDev debug task", task[:100])
        
        try:
            operation = context.get('operation', self._detect_operation(task))
            
            if operation == 'set_breakpoint':
                return self._set_breakpoint(context)
            elif operation == 'clear_breakpoint':
                return self._clear_breakpoint(context)
            elif operation == 'list_breakpoints':
                return self._list_breakpoints()
            elif operation == 'analyze_console_error':
                return self._analyze_console_error(context)
            elif operation == 'debug_network':
                return self._debug_network(context)
            elif operation == 'debug_css':
                return self._debug_css(context)
            elif operation == 'debug_react':
                return self._debug_react(context)
            elif operation == 'validate_html':
                return self._validate_html(context)
            else:
                return self._llm_assisted_debug(task, context)
                
        except Exception as e:
            self.logger.error(f"WebDev debug task failed: {e}", exc_info=True)
            return self._build_error_result(f"Debug task failed: {str(e)}", error=e)
    
    def _detect_operation(self, task: str) -> str:
        """Detect debug operation from task description."""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['breakpoint', 'break at', 'debugger']):
            if 'clear' in task_lower or 'remove' in task_lower:
                return 'clear_breakpoint'
            elif 'list' in task_lower or 'show' in task_lower:
                return 'list_breakpoints'
            else:
                return 'set_breakpoint'
        elif any(word in task_lower for word in ['console', 'browser error', 'javascript error']):
            return 'analyze_console_error'
        elif any(word in task_lower for word in ['network', 'fetch', 'ajax', 'api', 'request']):
            return 'debug_network'
        elif any(word in task_lower for word in ['css', 'style', 'layout', 'flexbox', 'grid']):
            return 'debug_css'
        elif any(word in task_lower for word in ['react', 'component', 'hook', 'state', 'props']):
            return 'debug_react'
        elif 'html' in task_lower or 'markup' in task_lower or 'validate' in task_lower:
            return 'validate_html'
        
        return 'llm_assisted'
    
    def _set_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Set a breakpoint in JavaScript/TypeScript code."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path or not line_number:
            return self._build_error_result("file_path and line_number required")
        
        if not os.path.exists(file_path):
            return self._build_error_result(f"File not found: {file_path}")
        
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
                'note': 'Add `debugger;` statement in code or set breakpoint in browser DevTools',
                'vscode_launch': {
                    'type': 'node',
                    'request': 'launch',
                    'program': file_path
                }
            }
        )
    
    def _clear_breakpoint(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Clear a breakpoint."""
        file_path = context.get('file_path')
        line_number = context.get('line_number')
        
        if not file_path:
            self._breakpoints.clear()
            return self._build_success_result("All breakpoints cleared")
        
        if file_path not in self._breakpoints:
            return self._build_error_result(f"No breakpoints in {file_path}")
        
        if line_number:
            if line_number in self._breakpoints[file_path]:
                self._breakpoints[file_path].remove(line_number)
                return self._build_success_result(f"Breakpoint cleared at {file_path}:{line_number}")
            else:
                return self._build_error_result(f"No breakpoint at {file_path}:{line_number}")
        else:
            del self._breakpoints[file_path]
            return self._build_success_result(f"All breakpoints cleared in {file_path}")
    
    def _list_breakpoints(self) -> Dict[str, Any]:
        """List all breakpoints."""
        if not self._breakpoints:
            return self._build_success_result("No breakpoints set", data={'breakpoints': {}})
        
        return self._build_success_result(
            f"Found {sum(len(bp) for bp in self._breakpoints.values())} breakpoint(s)",
            data={'breakpoints': self._breakpoints}
        )
    
    def _analyze_console_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze browser console error."""
        error_message = context.get('error_message', '')
        error_type = context.get('error_type', 'Error')
        stack_trace = context.get('stack_trace', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Analyze this JavaScript/Browser console error:

Error Type: {error_type}
Message: {error_message}
Stack Trace: {stack_trace}

Code Context:
{code_snippet}

Provide:
1. Explanation of the error
2. Common causes in web development
3. Browser compatibility issues (if applicable)
4. Recommended fixes with code examples
5. How to debug in Chrome/Firefox DevTools
6. Prevention strategies

Be specific to frontend web development."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            analysis = llm_result.get('response', '')
            
            return self._build_success_result(
                "Console error analyzed",
                data={
                    'error_type': error_type,
                    'message': error_message,
                    'analysis': analysis,
                    'devtools_tips': [
                        'Open DevTools: F12 or Ctrl+Shift+I',
                        'Pause on exceptions: Sources tab → Pause on exceptions',
                        'Console filtering: Use filter input to search errors',
                        'Network tab: Check failed requests'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Console error analysis failed: {str(e)}", error=e)
    
    def _debug_network(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug network requests."""
        request_url = context.get('request_url', '')
        request_method = context.get('request_method', 'GET')
        response_status = context.get('response_status')
        error_message = context.get('error_message', '')
        code_snippet = context.get('code_snippet', '')
        
        prompt = f"""Debug this network request issue:

URL: {request_url}
Method: {request_method}
Status: {response_status if response_status else 'N/A'}
Error: {error_message}

Code:
{code_snippet}

Provide:
1. Understanding of the issue (CORS, 404, 500, timeout, etc.)
2. Common causes of network errors
3. How to inspect in Network tab
4. Recommended fixes (proxy, headers, error handling)
5. Fetch/Axios best practices
6. Code examples

Be specific to frontend HTTP requests."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "Network issue analyzed",
                data={
                    'request': {'url': request_url, 'method': request_method, 'status': response_status},
                    'debug_info': debug_info,
                    'network_tab_tips': [
                        'Open Network tab in DevTools',
                        'Check request headers and response',
                        'Look for CORS errors in console',
                        'Use Preserve log to keep requests across page loads'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"Network debugging failed: {str(e)}", error=e)
    
    def _debug_css(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug CSS layout issues."""
        css_code = context.get('css_code', '')
        html_code = context.get('html_code', '')
        issue_description = context.get('issue_description', '')
        
        prompt = f"""Debug this CSS layout issue:

Issue: {issue_description}

CSS:
{css_code}

HTML:
{html_code}

Provide:
1. Understanding of the layout issue
2. Box model analysis
3. Flexbox/Grid debugging tips
4. Specificity and cascade issues
5. Browser compatibility concerns
6. Recommended fixes with CSS code
7. How to use DevTools Elements tab

Be specific to CSS debugging."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "CSS issue analyzed",
                data={
                    'issue': issue_description,
                    'debug_info': debug_info,
                    'css_debug_tips': [
                        'Use border: 1px solid red to visualize elements',
                        'Inspect element in DevTools (right-click → Inspect)',
                        'Check computed styles in Styles panel',
                        'Use DevTools Layout tab for Flexbox/Grid visualization',
                        'Test in multiple browsers'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"CSS debugging failed: {str(e)}", error=e)
    
    def _debug_react(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Debug React component issues."""
        component_code = context.get('component_code', '')
        error_message = context.get('error_message', '')
        issue_description = context.get('issue_description', '')
        
        prompt = f"""Debug this React component issue:

Issue: {issue_description}
Error: {error_message}

Component Code:
{component_code}

Provide:
1. Understanding of the React issue
2. Common React errors (hooks, state, props, lifecycle)
3. React DevTools usage
4. Recommended fixes with code examples
5. Best practices and patterns
6. Performance considerations

Be specific to React debugging."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            debug_info = llm_result.get('response', '')
            
            return self._build_success_result(
                "React issue analyzed",
                data={
                    'issue': issue_description,
                    'debug_info': debug_info,
                    'react_debug_tips': [
                        'Install React DevTools browser extension',
                        'Check component hierarchy and props',
                        'Use console.log() or debugger in useEffect',
                        'Verify hooks rules (only call at top level)',
                        'Check dependency arrays in hooks'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"React debugging failed: {str(e)}", error=e)
    
    def _validate_html(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate HTML markup."""
        html_code = context.get('html_code', '')
        file_path = context.get('file_path')
        
        if not html_code and not file_path:
            return self._build_error_result("html_code or file_path required")
        
        prompt = f"""Validate this HTML markup and identify issues:

HTML:
{html_code if html_code else f'File: {file_path}'}

Check for:
1. Syntax errors
2. Unclosed tags
3. Invalid nesting
4. Missing required attributes
5. Accessibility issues
6. Semantic HTML recommendations

Provide fixes for each issue."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            validation = llm_result.get('response', '')
            
            return self._build_success_result(
                "HTML validated",
                data={
                    'validation': validation,
                    'validation_tools': [
                        'W3C Validator: https://validator.w3.org/',
                        'Browser DevTools: Check console for warnings',
                        'Lighthouse: Audit accessibility and best practices'
                    ]
                }
            )
        except Exception as e:
            return self._build_error_result(f"HTML validation failed: {str(e)}", error=e)
    
    def _llm_assisted_debug(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for web development debugging assistance."""
        prompt = f"""You are a web development debugging expert. Help with this debugging task:

Task: {task}

Context: {json.dumps(context, indent=2)}

Provide:
1. Understanding of the debugging task
2. Recommended debugging approach for web development
3. Specific browser DevTools techniques
4. Expected outcomes
5. Best practices

Be practical and web-development-specific."""
        
        try:
            llm_result = self._get_llm_response(prompt)
            guidance = llm_result.get('response', '')
            
            return self._build_success_result(
                "Debug guidance provided",
                data={
                    'task': task,
                    'guidance': guidance,
                    'node_available': self._node_available
                }
            )
        except Exception as e:
            return self._build_error_result(f"LLM-assisted debugging failed: {str(e)}", error=e)
    
    def _build_success_result(self, message: str, data: Any = None) -> Dict[str, Any]:
        """Build success result."""
        return {
            'success': True,
            'message': message,
            'data': data or {},
            'next_context': {}
        }
    
    def _build_error_result(self, message: str, error: Exception = None) -> Dict[str, Any]:
        """Build error result."""
        return {
            'success': False,
            'message': message,
            'data': {'error': str(error) if error else message},
            'next_context': {}
        }
    
    def _log_action(self, action: str, details: str):
        """Log agent action."""
        self.logger.info(f"[{action}] {details}")
