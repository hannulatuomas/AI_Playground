

"""
Web Development Project Initialization Agent

This agent handles web development project initialization with support for
JavaScript, TypeScript, HTML, CSS, and various web frameworks.
"""

from typing import Dict, Any, List, Optional
from ...base import ProjectInitBase


class WebJSTSProjectInitAgent(ProjectInitBase):
    """
    Web development-specific project initialization agent.
    
    Capabilities:
    - Initialize web projects (React, Vue, Angular, vanilla, etc.)
    - Create proper package.json and configuration files
    - Support for TypeScript
    - Webpack/Vite configuration
    - ESLint and Prettier setup
    """
    
    def __init__(
        self,
        name: str = "project_init_webdev",
        description: str = "Web development project initialization",
        llm_router: Optional[Any] = None,
        tool_registry: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        memory_manager: Optional[Any] = None
    ):
        super().__init__(
            name=name,
            description=description,
            language="JavaScript/TypeScript",
            llm_router=llm_router,
            tool_registry=tool_registry,
            config=config,
            memory_manager=memory_manager
        )
    
    def _get_project_types(self) -> List[str]:
        """Get supported web project types."""
        return [
            'vanilla',      # Vanilla HTML/CSS/JS
            'react',        # React application
            'vue',          # Vue.js application
            'angular',      # Angular application
            'nextjs',       # Next.js application
            'express',      # Express.js backend
            'fastify',      # Fastify backend
            'static',       # Static website
        ]
    
    def _get_project_structure(self, project_type: str) -> Dict[str, Any]:
        """Get directory structure for project type."""
        structures = {
            'vanilla': {
                'directories': [
                    'src',
                    'src/js',
                    'src/css',
                    'src/assets',
                    'public',
                ],
            },
            'react': {
                'directories': [
                    'src',
                    'src/components',
                    'src/hooks',
                    'src/utils',
                    'src/styles',
                    'public',
                    'tests',
                ],
            },
            'vue': {
                'directories': [
                    'src',
                    'src/components',
                    'src/composables',
                    'src/views',
                    'src/assets',
                    'public',
                ],
            },
            'express': {
                'directories': [
                    'src',
                    'src/routes',
                    'src/controllers',
                    'src/models',
                    'src/middleware',
                    'tests',
                ],
            },
        }
        
        return structures.get(project_type, structures['vanilla'])
    
    def _get_default_files(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Generate default web development configuration files."""
        files = {}
        project_type = config['project_type']
        use_typescript = config.get('use_typescript', True)
        
        # README.md
        files['README.md'] = f"""# {config['project_name']}

{config.get('description', 'A web development project')}

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

## Build

```bash
npm run build
```

## Author

{config.get('author', 'N/A')}

## License

{config.get('license', 'MIT')}
"""
        
        # package.json
        files['package.json'] = f"""{{
  "name": "{config['project_name'].lower().replace(' ', '-')}",
  "version": "0.1.0",
  "description": "{config.get('description', 'A web development project')}",
  "main": "index.js",
  "scripts": {{
{self._get_npm_scripts(project_type, use_typescript)}
  }},
  "keywords": [],
  "author": "{config.get('author', '')}",
  "license": "{config.get('license', 'MIT')}",
  "dependencies": {{
{self._get_dependencies(project_type)}
  }},
  "devDependencies": {{
{self._get_dev_dependencies(project_type, use_typescript)}
  }}
}}
"""
        
        # .gitignore
        files['.gitignore'] = """# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build
dist/
build/
.cache/

# Environment
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Testing
coverage/
.nyc_output/
"""
        
        # TypeScript config
        if use_typescript:
            files['tsconfig.json'] = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}
"""
        
        # ESLint config
        files['.eslintrc.json'] = """{
  "env": {
    "browser": true,
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended"
  ],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "indent": ["error", 2],
    "linebreak-style": ["error", "unix"],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}
"""
        
        # Prettier config
        files['.prettierrc'] = """{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
"""
        
        # Main entry point
        ext = 'ts' if use_typescript else 'js'
        if project_type == 'react':
            files[f'src/App.{ext}x'] = """import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Hello from {config['project_name']}!</h1>
    </div>
  );
}

export default App;
"""
        elif project_type == 'express':
            files[f'src/index.{ext}'] = """import express from 'express';

const app = express();
const port = process.env.PORT || 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Hello from {config['project_name']}!' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
"""
        
        return files
    
    def _get_npm_scripts(self, project_type: str, use_typescript: bool) -> str:
        """Get npm scripts for package.json."""
        scripts = {
            'react': [
                '    "dev": "vite",',
                '    "build": "vite build",',
                '    "preview": "vite preview",',
                '    "lint": "eslint src --ext .js,.jsx,.ts,.tsx"',
            ],
            'express': [
                '    "dev": "nodemon src/index.js",',
                '    "start": "node src/index.js",',
                '    "lint": "eslint src"',
            ],
        }
        
        default_scripts = [
            '    "dev": "vite",',
            '    "build": "vite build",',
            '    "lint": "eslint src"',
        ]
        
        return '\n'.join(scripts.get(project_type, default_scripts))
    
    def _get_dependencies(self, project_type: str) -> str:
        """Get dependencies for package.json."""
        deps = {
            'react': [
                '    "react": "^18.2.0",',
                '    "react-dom": "^18.2.0"',
            ],
            'vue': [
                '    "vue": "^3.3.0"',
            ],
            'express': [
                '    "express": "^4.18.0",',
                '    "dotenv": "^16.3.0"',
            ],
        }
        
        return '\n'.join(deps.get(project_type, []))
    
    def _get_dev_dependencies(self, project_type: str, use_typescript: bool) -> str:
        """Get dev dependencies for package.json."""
        common = [
            '    "eslint": "^8.50.0",',
            '    "prettier": "^3.0.0",',
            '    "vite": "^4.5.0"',
        ]
        
        if use_typescript:
            common.extend([
                ',',
                '    "typescript": "^5.2.0",',
                '    "@types/node": "^20.8.0"',
            ])
        
        if project_type == 'react':
            common.extend([
                ',',
                '    "@vitejs/plugin-react": "^4.1.0"',
            ])
        
        return '\n'.join(common)
    
    def _generate_language_rules(self, config: Dict[str, Any]) -> str:
        """Generate web development-specific rules."""
        return f"""## Web Development Rules

### JavaScript/TypeScript

1. **Language Version**: ES2020+
2. **Type System**: {"TypeScript" if config.get('use_typescript') else "JavaScript with JSDoc"}
3. **Module System**: ES Modules (import/export)

### Code Style

1. **Formatting**: Use Prettier for consistent formatting
2. **Linting**: Use ESLint for code quality
3. **Naming**: camelCase for variables/functions, PascalCase for components/classes
4. **Semicolons**: Always use semicolons
5. **Quotes**: Single quotes for strings

### Project Type: {config['project_type']}

### Frontend Best Practices

1. **Components**: Keep components small and focused
2. **State Management**: Use appropriate state management (Context, Redux, Zustand)
3. **Styling**: Use CSS modules or styled-components
4. **Accessibility**: Follow WCAG guidelines
5. **Performance**: Optimize bundle size and loading

### Backend Best Practices

1. **API Design**: Follow REST or GraphQL best practices
2. **Error Handling**: Use proper error handling middleware
3. **Validation**: Validate all inputs
4. **Security**: Use helmet.js, rate limiting, CORS
5. **Logging**: Use structured logging (winston, pino)

### Testing

1. **Unit Tests**: Jest or Vitest
2. **Component Tests**: React Testing Library or Vue Test Utils
3. **E2E Tests**: Playwright or Cypress
4. **Coverage**: Aim for >70% code coverage

### Build and Deploy

1. **Bundler**: Vite or Webpack
2. **Optimization**: Tree shaking, code splitting, lazy loading
3. **Environment**: Use environment variables
4. **CI/CD**: Automate builds and deployments

### Security

1. **XSS**: Sanitize user inputs
2. **CSRF**: Use CSRF tokens
3. **Authentication**: Use secure authentication (JWT, OAuth)
4. **Dependencies**: Regular security audits (npm audit)
"""
    
    def _get_language_specific_questions(self) -> List[Dict[str, Any]]:
        """Get web development-specific questions."""
        return [
            {
                'key': 'use_typescript',
                'question': 'Use TypeScript?',
                'type': 'bool',
                'default': True,
                'required': False
            },
            {
                'key': 'package_manager',
                'question': 'Package manager?',
                'type': 'choice',
                'options': ['npm', 'yarn', 'pnpm'],
                'default': 'npm',
                'required': False
            },
        ]


