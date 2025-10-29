
"""
Web Development Code Editor Agent

This agent specializes in creating and editing web development files:
- HTML, CSS, JavaScript, TypeScript
- React components (JSX/TSX)
- Node.js applications
- Next.js applications
- Package.json management
"""

import re
import json
from pathlib import Path
from typing import Dict, Any, Optional

from ...base import CodeEditorBase


class WebJSTSCodeEditorAgent(CodeEditorBase):
    """
    Agent specialized for full-stack web development code editing.
    
    Features:
    - HTML5 structure awareness
    - CSS/SCSS/SASS/Tailwind styling
    - JavaScript/TypeScript (ES6+) support
    - Frontend Frameworks: React, Next.js, Vue, Nuxt, Angular, Svelte
    - Backend Frameworks: Express, Fastify, Koa, NestJS
    - API Libraries: Axios, Fetch API
    - Package Managers: npm, yarn, pnpm
    - Build Tools: Webpack, Vite, Parcel, Rollup, Turbopack
    - Testing: Jest, Vitest, Mocha, Jasmine
    """
    
    def __init__(
        self,
        name: str = "code_editor_webdev",
        description: str = "Full-stack web development code editor (HTML/CSS/JS/TS/React/Vue/Angular/Node.js)",
        **kwargs
    ):
        super().__init__(
            name=name,
            description=description,
            supported_extensions=[
                '.html', '.htm', '.css', '.scss', '.sass', '.less',
                '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',
                '.json', '.json5', '.jsonc',
                '.vue', '.svelte', '.astro',
                '.md', '.mdx'
            ],
            **kwargs
        )
        
        # Frontend frameworks
        self.frontend_frameworks = {
            'react': {
                'extensions': ['.jsx', '.tsx'],
                'patterns': ['React.', 'useState', 'useEffect', 'Component'],
                'files': ['App.jsx', 'App.tsx', 'index.jsx', 'index.tsx']
            },
            'nextjs': {
                'extensions': ['page.tsx', 'page.jsx', 'layout.tsx', 'layout.jsx', 'route.ts'],
                'patterns': ['next/', 'getServerSideProps', 'getStaticProps'],
                'files': ['next.config.js', 'next.config.mjs', 'app/layout.tsx']
            },
            'vue': {
                'extensions': ['.vue'],
                'patterns': ['<script setup>', 'defineComponent', 'ref(', 'reactive('],
                'files': ['App.vue', 'main.js']
            },
            'nuxt': {
                'extensions': ['.vue'],
                'patterns': ['nuxt', 'useAsyncData', 'useFetch'],
                'files': ['nuxt.config.ts', 'nuxt.config.js', 'app.vue']
            },
            'angular': {
                'extensions': ['.ts', '.component.ts', '.service.ts', '.module.ts'],
                'patterns': ['@Component', '@Injectable', '@NgModule', 'Angular'],
                'files': ['angular.json', 'app.module.ts', 'main.ts']
            },
            'svelte': {
                'extensions': ['.svelte'],
                'patterns': ['<script>', '$:', 'onMount'],
                'files': ['svelte.config.js', 'App.svelte']
            }
        }
        
        # Backend frameworks
        self.backend_frameworks = {
            'express': {
                'patterns': ['express()', 'app.get', 'app.post', 'require("express")'],
                'files': ['server.js', 'app.js', 'index.js']
            },
            'fastify': {
                'patterns': ['fastify()', 'server.get', 'require("fastify")'],
                'files': ['server.js', 'app.js']
            },
            'koa': {
                'patterns': ['new Koa()', 'ctx.body', 'require("koa")'],
                'files': ['server.js', 'app.js']
            },
            'nestjs': {
                'patterns': ['@Controller', '@Module', '@Injectable', 'NestFactory'],
                'files': ['main.ts', 'app.module.ts', 'nest-cli.json']
            }
        }
        
        # Build tools
        self.build_tools = {
            'webpack': ['webpack.config.js', 'webpack.config.ts'],
            'vite': ['vite.config.js', 'vite.config.ts'],
            'parcel': ['.parcelrc', 'parcel.config.js'],
            'rollup': ['rollup.config.js', 'rollup.config.ts'],
            'turbopack': ['turbo.json']
        }
        
        # Package managers
        self.package_managers = {
            'npm': 'package-lock.json',
            'yarn': 'yarn.lock',
            'pnpm': 'pnpm-lock.yaml'
        }
        
        # Load language-specific documentation
        self._load_language_docs()

    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web development code editing task."""
        self._log_action("Starting web development code editing", task[:100])
        
        try:
            operation = self._parse_task(task, context)
            
            if not operation:
                return self._build_error_result("Could not parse web dev task")
            
            if not self._is_webdev_file(operation['path']):
                return self._build_error_result(f"Not a web dev file: {operation['path']}")
            
            # Detect file type and framework
            file_info = self._analyze_file(operation['path'], task)
            operation.update(file_info)
            
            if operation['action'] == 'create':
                result = self._create_webdev_file(operation, task, context)
            elif operation['action'] == 'modify':
                result = self._modify_webdev_file(operation, task, context)
            else:
                return self._build_error_result(f"Unknown action: {operation['action']}")
            
            return result
            
        except Exception as e:
            self.logger.exception("Web dev code editing failed")
            return self._build_error_result(f"Web dev error: {str(e)}", e)
    
    def _parse_task(self, task: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse task to extract operation details."""
        if 'file_path' in context:
            return {
                'action': context.get('action', 'create'),
                'path': context['file_path'],
                'content': context.get('content')
            }
        
        # Parse from task
        pattern = r'(\w+)\s+(?:file\s+)?([a-zA-Z0-9_/\-]+\.(?:html|css|js|jsx|ts|tsx|json|vue|svelte))'
        match = re.search(pattern, task.lower())
        
        if match:
            action = 'create' if 'create' in match.group(1) else 'modify'
            return {
                'action': action,
                'path': match.group(2),
                'content': None
            }
        
        return None
    
    def _is_webdev_file(self, path: str) -> bool:
        """Check if path is a web development file."""
        return Path(path).suffix in self.supported_extensions
    
    def _analyze_file(self, path: str, task: str) -> Dict[str, Any]:
        """Analyze file to determine type and framework."""
        suffix = Path(path).suffix.lower()
        path_lower = path.lower()
        task_lower = task.lower()
        
        file_type = suffix[1:] if suffix else 'unknown'
        framework = None
        component_type = None
        
        # Detect framework
        if suffix in ['.jsx', '.tsx']:
            framework = 'react'
            if 'nextjs' in task_lower or 'next.js' in task_lower or '/app/' in path_lower:
                framework = 'nextjs'
            
            # Detect component type
            if 'page' in path_lower:
                component_type = 'page'
            elif 'layout' in path_lower:
                component_type = 'layout'
            elif 'component' in path_lower:
                component_type = 'component'
        elif suffix == '.vue':
            framework = 'vue'
        elif suffix == '.svelte':
            framework = 'svelte'
        elif suffix == '.json' and 'package.json' in path_lower:
            file_type = 'package.json'
        
        return {
            'file_type': file_type,
            'framework': framework,
            'component_type': component_type
        }
    
    def _create_webdev_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new web development file."""
        try:
            if not operation.get('content'):
                content = self._generate_webdev_content(operation, task, context)
            else:
                content = operation['content']
            
            # Validate JSON files
            if operation['file_type'] in ['json', 'package.json']:
                try:
                    json.loads(content)  # Validate JSON syntax
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON validation warning: {e}")
            
            # Write file
            file_path = Path(operation['path'])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self._log_action("Created web dev file", str(file_path))
            
            return self._build_success_result(
                message=f"Created {operation['file_type']} file: {file_path}",
                data={
                    'path': str(file_path),
                    'file_type': operation['file_type'],
                    'framework': operation.get('framework'),
                    'lines': len(content.splitlines())
                },
                next_context={'last_webdev_file': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to create web dev file: {str(e)}", e)
    
    def _modify_webdev_file(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Modify existing web development file."""
        try:
            file_path = Path(operation['path'])
            
            if not file_path.exists():
                return self._build_error_result(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Generate modification
            file_type = operation.get('file_type', 'file')
            prompt = f"""Modify this {file_type} code:

```{file_type}
{original_content}
```

Task: {task}

Generate the complete modified code.
"""
            
            llm_result = self._get_llm_response(prompt, temperature=0.7)
            modified_content = self._clean_code_blocks(llm_result.get('response', ''))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            return self._build_success_result(
                message=f"Modified {file_type} file: {file_path}",
                data={'path': str(file_path)}
            )
            
        except Exception as e:
            return self._build_error_result(f"Failed to modify web dev file: {str(e)}", e)
    
    def _generate_webdev_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate web development code using LLM."""
        file_type = operation.get('file_type', 'file')
        framework = operation.get('framework')
        component_type = operation.get('component_type')
        
        prompt = f"""Generate {file_type} code for: {operation['path']}

Task: {task}

"""
        
        # File-type specific requirements
        if file_type == 'html':
            prompt += """Requirements:
- Use HTML5 doctype and semantic tags
- Include proper meta tags
- Use descriptive class names
- Add ARIA labels for accessibility
"""
        elif file_type == 'css':
            prompt += """Requirements:
- Use modern CSS features (flexbox, grid)
- Add comments for sections
- Use consistent naming (BEM or similar)
- Include responsive design considerations
"""
        elif file_type in ['js', 'jsx', 'ts', 'tsx']:
            prompt += """Requirements:
- Use modern ES6+ syntax
- Add JSDoc comments for functions
- Use const/let (not var)
- Handle errors appropriately
"""
            
            if framework == 'react':
                prompt += """
- This is a React component
- Use functional components with hooks
- Follow React best practices
- Use proper prop types or TypeScript types
"""
            elif framework == 'nextjs':
                prompt += f"""
- This is a Next.js {"" if not component_type else component_type}
- Use Next.js App Router conventions
- Use 'use client' directive if client component
- Include proper exports (default export for pages)
"""
        elif file_type == 'package.json':
            prompt += """Requirements:
- Valid JSON format
- Include name, version, description
- Add appropriate scripts (dev, build, start)
- List dependencies and devDependencies
"""
        
        prompt += "\nGenerate ONLY the code, no markdown or explanations.\n"
        
        llm_result = self._get_llm_response(prompt, temperature=0.7)
        content = llm_result.get('response', '')
        
        return self._clean_code_blocks(content)
    
    def _clean_code_blocks(self, content: str) -> str:
        """Remove markdown code blocks."""
        # Try multiple patterns
        patterns = [
            r'```(?:html|css|javascript|js|jsx|typescript|ts|tsx|json)?\n?(.*?)\n?```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return content.strip()

    # Abstract method implementations (required by CodeEditorBase)
    def _generate_code_content(
        self,
        operation: Dict[str, Any],
        task: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate web code content."""
        return self._generate_web_content(operation, task, context)
    
    def _validate_syntax(self, code: str) -> Dict[str, Any]:
        """Validate web syntax."""
        return self._validate_web_syntax(code)
    
    def _apply_formatting(self, code: str) -> str:
        """Apply web formatting."""
        return self._apply_web_formatting(code)

