"""
Project Scaffolding Module

Creates new project structures with templates.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import json


class ProjectScaffolder:
    """Creates project scaffolds from templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize scaffolder.
        
        Args:
            templates_dir: Path to templates directory
        """
        if templates_dir is None:
            # Default to templates/ in this module
            self.templates_dir = Path(__file__).parent / 'templates'
        else:
            self.templates_dir = Path(templates_dir)
    
    def create_project(self, name: str, language: str, framework: Optional[str],
                      path: str, git_init: bool = True) -> bool:
        """
        Create a new project with scaffolding.
        
        Args:
            name: Project name
            language: Programming language
            framework: Framework (optional)
            path: Where to create project
            git_init: Initialize git repository
            
        Returns:
            True if successful, False otherwise
        """
        project_path = Path(path) / name
        
        # Check if directory already exists
        if project_path.exists():
            raise ValueError(f"Directory {project_path} already exists")
        
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create structure based on language and framework
            if language == 'python':
                self._create_python_project(project_path, name, framework)
            elif language in ['javascript', 'typescript']:
                self._create_js_project(project_path, name, language, framework)
            elif language == 'csharp':
                self._create_csharp_project(project_path, name, framework)
            elif language == 'cpp':
                self._create_cpp_project(project_path, name)
            elif language in ['shell', 'bash']:
                self._create_shell_project(project_path, name)
            else:
                # Generic project
                self._create_generic_project(project_path, name, language)
            
            # Initialize git if requested
            if git_init:
                self._init_git(project_path)
            
            return True
            
        except Exception as e:
            # Clean up on failure
            if project_path.exists():
                shutil.rmtree(project_path)
            raise e
    
    def _create_python_project(self, path: Path, name: str, 
                               framework: Optional[str]):
        """Create Python project structure."""
        # Create directories
        (path / 'src').mkdir()
        (path / 'tests').mkdir()
        (path / 'docs').mkdir()
        
        # Create __init__.py files
        (path / 'src' / '__init__.py').touch()
        (path / 'tests' / '__init__.py').touch()
        
        # Create main file based on framework
        if framework == 'fastapi':
            self._create_fastapi_structure(path, name)
        elif framework == 'flask':
            self._create_flask_structure(path, name)
        elif framework == 'django':
            self._create_django_structure(path, name)
        else:
            # Basic Python project
            main_file = path / 'src' / 'main.py'
            main_file.write_text(self._get_python_main_template(name))
        
        # Create requirements.txt
        req_file = path / 'requirements.txt'
        req_file.write_text(self._get_requirements_template(framework))
        
        # Create pyproject.toml
        pyproject = path / 'pyproject.toml'
        pyproject.write_text(self._get_pyproject_template(name))
        
        # Create .gitignore
        gitignore = path / '.gitignore'
        gitignore.write_text(self._get_python_gitignore())
        
        # Create README
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, 'python', framework))
    
    def _create_fastapi_structure(self, path: Path, name: str):
        """Create FastAPI project structure."""
        src = path / 'src'
        
        # Create subdirectories
        (src / 'api').mkdir()
        (src / 'api' / '__init__.py').touch()
        (src / 'api' / 'routes.py').write_text(self._get_fastapi_routes())
        
        (src / 'models').mkdir()
        (src / 'models' / '__init__.py').touch()
        
        (src / 'utils').mkdir()
        (src / 'utils' / '__init__.py').touch()
        
        # Create main.py
        main = src / 'main.py'
        main.write_text(self._get_fastapi_main(name))
    
    def _create_flask_structure(self, path: Path, name: str):
        """Create Flask project structure."""
        src = path / 'src'
        
        (src / 'templates').mkdir()
        (src / 'static').mkdir()
        (src / 'routes').mkdir()
        (src / 'routes' / '__init__.py').touch()
        
        # Create app.py
        app = src / 'app.py'
        app.write_text(self._get_flask_app(name))
    
    def _create_django_structure(self, path: Path, name: str):
        """Create Django project structure (minimal)."""
        # Note: In real scenario, would use django-admin startproject
        src = path / 'src'
        (src / name).mkdir()
        (src / name / '__init__.py').touch()
        
        readme = path / 'README.md'
        readme.write_text(f"# {name}\n\nDjango project. Run: django-admin startproject {name} .")
    
    def _create_js_project(self, path: Path, name: str, language: str,
                           framework: Optional[str]):
        """Create JavaScript/TypeScript project."""
        # Create directories
        (path / 'src').mkdir()
        (path / 'tests').mkdir()
        
        if framework == 'react':
            self._create_react_structure(path, name, language)
        elif framework == 'nextjs':
            self._create_nextjs_structure(path, name, language)
        elif framework == 'express':
            self._create_express_structure(path, name, language)
        else:
            # Basic JS/TS project
            if language == 'typescript':
                (path / 'src' / 'index.ts').write_text(self._get_ts_main())
                (path / 'tsconfig.json').write_text(self._get_tsconfig())
            else:
                (path / 'src' / 'index.js').write_text(self._get_js_main())
        
        # Create package.json
        pkg_json = path / 'package.json'
        pkg_json.write_text(self._get_package_json(name, language, framework))
        
        # Create .gitignore
        gitignore = path / '.gitignore'
        gitignore.write_text(self._get_js_gitignore())
        
        # Create README
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, language, framework))
    
    def _create_react_structure(self, path: Path, name: str, language: str):
        """Create React project structure."""
        src = path / 'src'
        
        (src / 'components').mkdir()
        (src / 'pages').mkdir()
        (src / 'hooks').mkdir()
        (src / 'utils').mkdir()
        
        ext = 'tsx' if language == 'typescript' else 'jsx'
        (src / f'App.{ext}').write_text(self._get_react_app(language))
        (src / f'index.{ext}').write_text(self._get_react_index(language))
        
        (path / 'public').mkdir()
        (path / 'public' / 'index.html').write_text(self._get_html_template(name))
    
    def _create_nextjs_structure(self, path: Path, name: str, language: str):
        """Create Next.js project structure."""
        src = path / 'src'
        
        (src / 'app').mkdir()
        (src / 'components').mkdir()
        
        ext = 'tsx' if language == 'typescript' else 'jsx'
        (src / 'app' / f'page.{ext}').write_text(self._get_nextjs_page(language))
        
        (path / 'public').mkdir()
    
    def _create_express_structure(self, path: Path, name: str, language: str):
        """Create Express.js project structure."""
        src = path / 'src'
        
        (src / 'routes').mkdir()
        (src / 'middleware').mkdir()
        (src / 'controllers').mkdir()
        
        ext = 'ts' if language == 'typescript' else 'js'
        (src / f'server.{ext}').write_text(self._get_express_server(language))
    
    def _create_csharp_project(self, path: Path, name: str, 
                               framework: Optional[str]):
        """Create C# project structure."""
        (path / 'src').mkdir()
        (path / 'tests').mkdir()
        
        # Create basic .csproj file
        csproj = path / f'{name}.csproj'
        csproj.write_text(self._get_csproj_template(name))
        
        # Create Program.cs
        program = path / 'src' / 'Program.cs'
        program.write_text(self._get_csharp_main(name))
        
        gitignore = path / '.gitignore'
        gitignore.write_text(self._get_csharp_gitignore())
        
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, 'csharp', framework))
    
    def _create_cpp_project(self, path: Path, name: str):
        """Create C++ project structure."""
        (path / 'src').mkdir()
        (path / 'include').mkdir()
        (path / 'tests').mkdir()
        
        # Create main.cpp
        main = path / 'src' / 'main.cpp'
        main.write_text(self._get_cpp_main())
        
        # Create CMakeLists.txt
        cmake = path / 'CMakeLists.txt'
        cmake.write_text(self._get_cmake_template(name))
        
        gitignore = path / '.gitignore'
        gitignore.write_text(self._get_cpp_gitignore())
        
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, 'cpp', None))
    
    def _create_shell_project(self, path: Path, name: str):
        """Create shell script project."""
        (path / 'scripts').mkdir()
        (path / 'tests').mkdir()
        
        main = path / 'scripts' / f'{name}.sh'
        main.write_text(self._get_shell_main(name))
        main.chmod(0o755)
        
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, 'shell', None))
    
    def _create_generic_project(self, path: Path, name: str, language: str):
        """Create generic project structure."""
        (path / 'src').mkdir()
        (path / 'tests').mkdir()
        (path / 'docs').mkdir()
        
        readme = path / 'README.md'
        readme.write_text(self._get_readme_template(name, language, None))
    
    def _init_git(self, path: Path):
        """Initialize git repository."""
        import subprocess
        try:
            subprocess.run(['git', 'init'], cwd=path, check=True, 
                          capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=path, check=True,
                          capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], 
                          cwd=path, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass  # Git not available or failed
    
    # Template methods
    def _get_python_main_template(self, name: str) -> str:
        return f'''"""
{name} - Main Module
"""


def main():
    """Main entry point."""
    print("Hello from {name}!")


if __name__ == "__main__":
    main()
'''
    
    def _get_requirements_template(self, framework: Optional[str]) -> str:
        if framework == 'fastapi':
            return 'fastapi>=0.104.0\nuvicorn>=0.24.0\npydantic>=2.5.0\n'
        elif framework == 'flask':
            return 'flask>=3.0.0\n'
        elif framework == 'django':
            return 'django>=4.2.0\n'
        else:
            return '# Add your dependencies here\n'
    
    def _get_pyproject_template(self, name: str) -> str:
        return f'''[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "A Python project"
requires-python = ">=3.12"
'''
    
    def _get_python_gitignore(self) -> str:
        return '''__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
env/
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
'''
    
    def _get_fastapi_main(self, name: str) -> str:
        return f'''"""
{name} - FastAPI Application
"""

from fastapi import FastAPI
from api import routes

app = FastAPI(title="{name}")

app.include_router(routes.router)


@app.get("/")
async def root():
    return {{"message": "Welcome to {name}"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _get_fastapi_routes(self) -> str:
        return '''"""
API Routes
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
'''
    
    def _get_flask_app(self, name: str) -> str:
        return f'''"""
{name} - Flask Application
"""

from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return 'Welcome to {name}!'


if __name__ == '__main__':
    app.run(debug=True)
'''
    
    def _get_package_json(self, name: str, language: str, 
                          framework: Optional[str]) -> str:
        pkg = {
            "name": name,
            "version": "0.1.0",
            "description": f"A {language} project",
            "main": "src/index.js" if language == 'javascript' else "src/index.ts",
            "scripts": {
                "start": "node src/index.js",
                "test": "echo \"Error: no test specified\" && exit 1"
            },
            "keywords": [],
            "author": "",
            "license": "MIT",
            "dependencies": {},
            "devDependencies": {}
        }
        
        if framework == 'react':
            pkg["dependencies"]["react"] = "^18.2.0"
            pkg["dependencies"]["react-dom"] = "^18.2.0"
        elif framework == 'express':
            pkg["dependencies"]["express"] = "^4.18.0"
        elif framework == 'nextjs':
            pkg["dependencies"]["next"] = "^14.0.0"
            pkg["dependencies"]["react"] = "^18.2.0"
            pkg["dependencies"]["react-dom"] = "^18.2.0"
        
        if language == 'typescript':
            pkg["devDependencies"]["typescript"] = "^5.3.0"
            pkg["devDependencies"]["@types/node"] = "^20.10.0"
        
        return json.dumps(pkg, indent=2)
    
    def _get_js_main(self) -> str:
        return '''console.log("Hello, World!");
'''
    
    def _get_ts_main(self) -> str:
        return '''console.log("Hello, World!");
'''
    
    def _get_tsconfig(self) -> str:
        return '''{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
'''
    
    def _get_react_app(self, language: str) -> str:
        if language == 'typescript':
            return '''import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Welcome to React + TypeScript</h1>
    </div>
  );
}

export default App;
'''
        else:
            return '''import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Welcome to React</h1>
    </div>
  );
}

export default App;
'''
    
    def _get_react_index(self, language: str) -> str:
        return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
'''
    
    def _get_nextjs_page(self, language: str) -> str:
        return '''export default function Home() {
  return (
    <main>
      <h1>Welcome to Next.js</h1>
    </main>
  );
}
'''
    
    def _get_express_server(self, language: str) -> str:
        if language == 'typescript':
            return '''import express, { Request, Response } from 'express';

const app = express();
const port = 3000;

app.use(express.json());

app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Welcome to Express + TypeScript' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
'''
        else:
            return '''const express = require('express');

const app = express();
const port = 3000;

app.use(express.json());

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to Express' });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
'''
    
    def _get_html_template(self, name: str) -> str:
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{name}</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
'''
    
    def _get_js_gitignore(self) -> str:
        return '''node_modules/
dist/
build/
.env
.env.local
.DS_Store
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.next/
out/
'''
    
    def _get_csproj_template(self, name: str) -> str:
        return f'''<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <RootNamespace>{name}</RootNamespace>
  </PropertyGroup>
</Project>
'''
    
    def _get_csharp_main(self, name: str) -> str:
        return f'''using System;

namespace {name}
{{
    class Program
    {{
        static void Main(string[] args)
        {{
            Console.WriteLine("Hello from {name}!");
        }}
    }}
}}
'''
    
    def _get_csharp_gitignore(self) -> str:
        return '''bin/
obj/
.vs/
*.user
*.suo
*.cache
'''
    
    def _get_cpp_main(self) -> str:
        return '''#include <iostream>

int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
'''
    
    def _get_cmake_template(self, name: str) -> str:
        return f'''cmake_minimum_required(VERSION 3.10)
project({name})

set(CMAKE_CXX_STANDARD 17)

add_executable({name} src/main.cpp)
'''
    
    def _get_cpp_gitignore(self) -> str:
        return '''build/
*.o
*.a
*.so
*.exe
CMakeCache.txt
CMakeFiles/
'''
    
    def _get_shell_main(self, name: str) -> str:
        return f'''#!/bin/bash
# {name} - Main Script

echo "Hello from {name}!"
'''
    
    def _get_readme_template(self, name: str, language: str, 
                            framework: Optional[str]) -> str:
        fw_text = f" ({framework})" if framework else ""
        return f'''# {name}

A {language}{fw_text} project.

## Installation

[Add installation instructions]

## Usage

[Add usage instructions]

## Development

[Add development instructions]

## License

MIT
'''
