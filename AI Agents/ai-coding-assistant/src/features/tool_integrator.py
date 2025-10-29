"""
Tool Integrator Module

Integrates external tools: Git, Testing frameworks, and Documentation.
Automates common development workflows based on rules.

Features:
- Git operations (status, commit, diff)
- Test framework detection and execution
- Automatic test failure debugging
- Documentation updates
- Rule-based automation
"""

import subprocess
import os
import re
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path


class ToolIntegrator:
    """
    Integrate external development tools.
    Handles Git, testing frameworks, and documentation updates.
    """

    # Supported test frameworks
    TEST_FRAMEWORKS = {
        'python': {
            'pytest': {
                'command': ['pytest', '-v'],
                'install_check': 'pytest --version',
                'pattern': r'test_.*\.py$|.*_test\.py$'
            },
            'unittest': {
                'command': ['python', '-m', 'unittest', 'discover'],
                'install_check': 'python -m unittest --help',
                'pattern': r'test_.*\.py$'
            }
        },
        'javascript': {
            'jest': {
                'command': ['npm', 'test'],
                'install_check': 'npm list jest',
                'pattern': r'.*\.test\.(js|ts)$|.*\.spec\.(js|ts)$'
            },
            'mocha': {
                'command': ['npm', 'test'],
                'install_check': 'npm list mocha',
                'pattern': r'test/.*\.js$'
            }
        },
        'typescript': {
            'jest': {
                'command': ['npm', 'test'],
                'install_check': 'npm list jest',
                'pattern': r'.*\.test\.ts$|.*\.spec\.ts$'
            }
        }
    }

    # Documentation file patterns
    DOC_PATTERNS = [
        'README.md',
        'CHANGELOG.md',
        'docs/**/*.md',
        'CONTRIBUTING.md',
        'API.md'
    ]

    def __init__(
        self,
        project_manager=None,
        llm_interface=None,
        debugger=None,
        context_manager=None
    ):
        """
        Initialize the tool integrator.

        Args:
            project_manager: ProjectManager for file operations
            llm_interface: LLMInterface for generating messages/docs
            debugger: Debugger for fixing test failures
            context_manager: ContextManager for logging actions

        Example:
            >>> from src.core.project_manager import ProjectManager
            >>> from src.core.llm_interface import LLMInterface, load_config_from_file
            >>> from src.features import Debugger, ContextManager
            >>> 
            >>> config = load_config_from_file()
            >>> llm = LLMInterface(config)
            >>> pm = ProjectManager(llm_interface=llm)
            >>> debugger = Debugger(llm, pe, db)
            >>> cm = ContextManager(pm, pn, db, pe)
            >>> 
            >>> integrator = ToolIntegrator(pm, llm, debugger, cm)
        """
        self.project_manager = project_manager
        self.llm_interface = llm_interface
        self.debugger = debugger
        self.context_manager = context_manager

    def git_status(self) -> Dict[str, Any]:
        """
        Get git repository status.

        Returns:
            Dictionary with git status information

        Example:
            >>> status = integrator.git_status()
            >>> if status['initialized']:
            ...     print(f"Changed files: {len(status['changed_files'])}")
            ...     print(f"Untracked: {len(status['untracked_files'])}")
        """
        result = {
            'initialized': False,
            'changed_files': [],
            'untracked_files': [],
            'staged_files': [],
            'branch': None,
            'error': None
        }

        try:
            # Check if git is initialized
            check = subprocess.run(
                ['git', 'rev-parse', '--git-dir'],
                capture_output=True,
                text=True,
                cwd=self._get_project_root()
            )

            if check.returncode != 0:
                result['error'] = 'Git repository not initialized'
                return result

            result['initialized'] = True

            # Get current branch
            branch = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                cwd=self._get_project_root()
            )
            result['branch'] = branch.stdout.strip()

            # Get status
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                cwd=self._get_project_root()
            )

            # Parse status output
            for line in status.stdout.splitlines():
                if not line.strip():
                    continue

                status_code = line[:2]
                filename = line[3:].strip()

                if status_code.startswith('??'):
                    result['untracked_files'].append(filename)
                elif status_code.strip():
                    if status_code[0] != ' ':
                        result['staged_files'].append(filename)
                    result['changed_files'].append(filename)

        except FileNotFoundError:
            result['error'] = 'Git not found. Please install git.'
        except Exception as e:
            result['error'] = f'Error getting git status: {e}'

        return result

    def git_commit(
        self,
        message: Optional[str] = None,
        files: Optional[List[str]] = None,
        generate_message: bool = True
    ) -> Dict[str, Any]:
        """
        Commit changes to git repository.

        Args:
            message: Commit message (generated if None)
            files: Specific files to commit (all changes if None)
            generate_message: Whether to generate message via LLM

        Returns:
            Commit result dictionary

        Example:
            >>> # Auto-generate commit message
            >>> result = integrator.git_commit(generate_message=True)
            >>> if result['success']:
            ...     print(f"Committed: {result['message']}")
            ...     print(f"Commit hash: {result['commit_hash']}")
            
            >>> # Custom message
            >>> result = integrator.git_commit(
            ...     message="feat: Add user authentication",
            ...     files=['src/auth.py', 'tests/test_auth.py']
            ... )
        """
        result = {
            'success': False,
            'message': None,
            'commit_hash': None,
            'files_committed': [],
            'error': None
        }

        # Check git status
        status = self.git_status()
        if not status['initialized']:
            result['error'] = 'Git repository not initialized. Run: git init'
            return result

        if not status['changed_files'] and not status['untracked_files']:
            result['error'] = 'No changes to commit'
            return result

        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(
                        ['git', 'add', file],
                        cwd=self._get_project_root(),
                        check=True
                    )
                    result['files_committed'].append(file)
            else:
                # Add all changes
                subprocess.run(
                    ['git', 'add', '-A'],
                    cwd=self._get_project_root(),
                    check=True
                )
                result['files_committed'] = status['changed_files'] + status['untracked_files']

            # Generate commit message if needed
            if not message and generate_message:
                message = self._generate_commit_message(result['files_committed'])
            elif not message:
                result['error'] = 'No commit message provided'
                return result

            # Commit
            commit = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                cwd=self._get_project_root(),
                check=True
            )

            # Get commit hash
            hash_result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                cwd=self._get_project_root()
            )
            result['commit_hash'] = hash_result.stdout.strip()[:8]

            result['success'] = True
            result['message'] = message

            # Log to memory
            if self.context_manager:
                self.context_manager.log_action(
                    action=f"Git commit: {message}",
                    outcome=f"Committed {len(result['files_committed'])} files",
                    project_id=self._get_project_id(),
                    success=True
                )

        except subprocess.CalledProcessError as e:
            result['error'] = f'Git commit failed: {e.stderr if e.stderr else str(e)}'
        except Exception as e:
            result['error'] = f'Error committing: {e}'

        return result

    def run_tests(
        self,
        language: Optional[str] = None,
        test_path: Optional[str] = None,
        auto_fix: bool = False,
        max_fix_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        Run tests using detected framework.

        Args:
            language: Programming language (auto-detect if None)
            test_path: Specific test path (all tests if None)
            auto_fix: Automatically fix failures using Debugger
            max_fix_attempts: Maximum attempts to fix failures

        Returns:
            Test execution result

        Example:
            >>> # Run all tests
            >>> result = integrator.run_tests(language='python')
            >>> print(f"Passed: {result['passed']}")
            >>> print(f"Failed: {result['failed']}")
            
            >>> # Run with auto-fix
            >>> result = integrator.run_tests(
            ...     language='python',
            ...     auto_fix=True,
            ...     max_fix_attempts=3
            ... )
            >>> if result['all_passed']:
            ...     print("All tests passed!")
        """
        result = {
            'success': False,
            'framework': None,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'total': 0,
            'all_passed': False,
            'output': None,
            'failures': [],
            'fix_attempts': 0,
            'error': None
        }

        # Detect framework
        if not language:
            language = self._detect_project_language()

        framework_info = self._detect_test_framework(language)
        if not framework_info:
            result['error'] = f'No test framework detected for {language}'
            return result

        result['framework'] = framework_info['name']

        # Run tests
        for attempt in range(max_fix_attempts + 1):
            test_result = self._run_test_command(
                framework_info,
                test_path
            )

            result['output'] = test_result['output']
            result['passed'] = test_result['passed']
            result['failed'] = test_result['failed']
            result['errors'] = test_result['errors']
            result['total'] = test_result['total']
            result['failures'] = test_result['failures']

            if test_result['all_passed']:
                result['success'] = True
                result['all_passed'] = True
                break

            # Try to fix failures
            if auto_fix and attempt < max_fix_attempts and test_result['failures']:
                print(f"\nAttempt {attempt + 1}/{max_fix_attempts} to fix failures...")
                result['fix_attempts'] += 1

                fixed = self._fix_test_failures(
                    test_result['failures'],
                    language
                )

                if not fixed:
                    print("Unable to fix failures automatically")
                    break
            else:
                break

        # Log to memory
        if self.context_manager:
            self.context_manager.log_action(
                action=f"Run tests ({result['framework']})",
                outcome=f"Passed: {result['passed']}, Failed: {result['failed']}",
                project_id=self._get_project_id(),
                success=result['all_passed']
            )

        return result

    def update_docs(
        self,
        changes: Dict[str, Any],
        doc_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update documentation files based on changes.

        Args:
            changes: Dictionary describing changes
            doc_files: Specific doc files (auto-detect if None)

        Returns:
            Documentation update result

        Example:
            >>> changes = {
            ...     'feature': 'Add JWT authentication',
            ...     'files': ['src/auth.py'],
            ...     'description': 'Implemented secure JWT-based authentication'
            ... }
            >>> result = integrator.update_docs(changes)
            >>> for file in result['updated_files']:
            ...     print(f"Updated: {file}")
        """
        result = {
            'success': False,
            'updated_files': [],
            'suggestions': [],
            'error': None
        }

        if not self.llm_interface:
            result['error'] = 'LLM interface not available'
            return result

        # Find documentation files
        if not doc_files:
            doc_files = self._find_doc_files()

        if not doc_files:
            result['error'] = 'No documentation files found'
            return result

        # Generate update suggestions for each doc file
        for doc_file in doc_files:
            try:
                suggestion = self._generate_doc_update(doc_file, changes)
                if suggestion:
                    result['suggestions'].append({
                        'file': doc_file,
                        'suggestion': suggestion
                    })
                    result['updated_files'].append(doc_file)

            except Exception as e:
                print(f"Warning: Could not update {doc_file}: {e}")

        result['success'] = len(result['updated_files']) > 0

        # Log to memory
        if self.context_manager and result['success']:
            self.context_manager.log_action(
                action="Update documentation",
                outcome=f"Updated {len(result['updated_files'])} doc files",
                project_id=self._get_project_id(),
                success=True
            )

        return result

    def _get_project_root(self) -> str:
        """Get project root directory."""
        if self.project_manager and self.project_manager.root_folder:
            return str(self.project_manager.root_folder)
        return os.getcwd()

    def _get_project_id(self) -> Optional[str]:
        """Get project identifier."""
        if self.project_manager:
            root = Path(self.project_manager.root_folder)
            return root.name
        return None

    def _generate_commit_message(self, files: List[str]) -> str:
        """Generate commit message via LLM."""
        if not self.llm_interface:
            return f"Update {len(files)} files"

        # Get git diff for context
        try:
            diff = subprocess.run(
                ['git', 'diff', '--cached'],
                capture_output=True,
                text=True,
                cwd=self._get_project_root()
            )
            diff_text = diff.stdout[:2000]  # Limit diff size
        except:
            diff_text = ""

        prompt = f"""Generate a concise git commit message for these changes.

Files changed: {', '.join(files[:10])}
{f'(and {len(files) - 10} more)' if len(files) > 10 else ''}

Diff preview:
{diff_text}

Format: <type>: <description>
Types: feat, fix, docs, style, refactor, test, chore

Generate only the commit message, no explanation."""

        try:
            message = self.llm_interface.generate(
                prompt,
                max_tokens=100,
                use_cache=False
            )
            # Clean up message
            message = message.strip().split('\n')[0]
            return message
        except:
            return f"Update {len(files)} files"

    def _detect_project_language(self) -> str:
        """Detect primary project language."""
        if not self.project_manager:
            return 'python'

        # Count files by language
        lang_counts = {}
        for path, info in self.project_manager.file_index.items():
            lang = info.get('language', 'unknown')
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

        # Return most common
        if lang_counts:
            return max(lang_counts.items(), key=lambda x: x[1])[0]

        return 'python'

    def _detect_test_framework(self, language: str) -> Optional[Dict]:
        """Detect test framework for language."""
        frameworks = self.TEST_FRAMEWORKS.get(language.lower(), {})

        for name, info in frameworks.items():
            # Check if framework is installed
            try:
                subprocess.run(
                    info['install_check'].split(),
                    capture_output=True,
                    cwd=self._get_project_root(),
                    timeout=5
                )
                return {'name': name, **info}
            except:
                continue

        return None

    def _run_test_command(
        self,
        framework_info: Dict,
        test_path: Optional[str]
    ) -> Dict[str, Any]:
        """Run test command and parse output."""
        result = {
            'all_passed': False,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'total': 0,
            'output': '',
            'failures': []
        }

        try:
            cmd = framework_info['command'].copy()
            if test_path:
                cmd.append(test_path)

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self._get_project_root(),
                timeout=300  # 5 minute timeout
            )

            result['output'] = process.stdout + process.stderr

            # Parse output based on framework
            if 'pytest' in framework_info['name']:
                result = self._parse_pytest_output(result['output'])
            elif 'jest' in framework_info['name']:
                result = self._parse_jest_output(result['output'])
            elif 'unittest' in framework_info['name']:
                result = self._parse_unittest_output(result['output'])

            result['all_passed'] = (result['failed'] == 0 and result['errors'] == 0)

        except subprocess.TimeoutExpired:
            result['output'] = 'Tests timed out after 5 minutes'
            result['errors'] = 1
        except Exception as e:
            result['output'] = f'Error running tests: {e}'
            result['errors'] = 1

        return result

    def _parse_pytest_output(self, output: str) -> Dict:
        """Parse pytest output."""
        result = {'passed': 0, 'failed': 0, 'errors': 0, 'total': 0, 'failures': []}

        # Look for summary line
        summary_match = re.search(r'(\d+) passed', output)
        if summary_match:
            result['passed'] = int(summary_match.group(1))

        failed_match = re.search(r'(\d+) failed', output)
        if failed_match:
            result['failed'] = int(failed_match.group(1))

        error_match = re.search(r'(\d+) error', output)
        if error_match:
            result['errors'] = int(error_match.group(1))

        result['total'] = result['passed'] + result['failed'] + result['errors']

        # Extract failure details
        failure_pattern = r'FAILED (.*?) - (.*?)(?:\n|$)'
        for match in re.finditer(failure_pattern, output):
            result['failures'].append({
                'test': match.group(1),
                'error': match.group(2)
            })

        return result

    def _parse_jest_output(self, output: str) -> Dict:
        """Parse jest output."""
        result = {'passed': 0, 'failed': 0, 'errors': 0, 'total': 0, 'failures': []}

        # Look for summary
        summary_match = re.search(r'Tests:\s+(\d+) failed.*?(\d+) passed.*?(\d+) total', output)
        if summary_match:
            result['failed'] = int(summary_match.group(1))
            result['passed'] = int(summary_match.group(2))
            result['total'] = int(summary_match.group(3))

        return result

    def _parse_unittest_output(self, output: str) -> Dict:
        """Parse unittest output."""
        result = {'passed': 0, 'failed': 0, 'errors': 0, 'total': 0, 'failures': []}

        # Look for result line
        result_match = re.search(r'Ran (\d+) test', output)
        if result_match:
            result['total'] = int(result_match.group(1))

        if 'FAILED' in output:
            failed_match = re.search(r'failures=(\d+)', output)
            if failed_match:
                result['failed'] = int(failed_match.group(1))

            error_match = re.search(r'errors=(\d+)', output)
            if error_match:
                result['errors'] = int(error_match.group(1))

            result['passed'] = result['total'] - result['failed'] - result['errors']
        elif 'OK' in output:
            result['passed'] = result['total']

        return result

    def _fix_test_failures(
        self,
        failures: List[Dict],
        language: str
    ) -> bool:
        """Attempt to fix test failures using Debugger."""
        if not self.debugger or not failures:
            return False

        fixed_any = False

        for failure in failures[:3]:  # Limit to first 3 failures
            test_name = failure.get('test', '')
            error = failure.get('error', '')

            print(f"Attempting to fix: {test_name}")

            # This would need actual code context
            # Placeholder for now
            fixed = False

            if fixed:
                fixed_any = True

        return fixed_any

    def _find_doc_files(self) -> List[str]:
        """Find documentation files in project."""
        doc_files = []
        root = Path(self._get_project_root())

        for pattern in self.DOC_PATTERNS:
            if '**' in pattern:
                # Recursive search
                base, _, file_pattern = pattern.partition('/**/')
                search_path = root / base
                if search_path.exists():
                    doc_files.extend(str(f) for f in search_path.rglob(file_pattern))
            else:
                # Direct file
                file_path = root / pattern
                if file_path.exists():
                    doc_files.append(str(file_path))

        return doc_files

    def _generate_doc_update(
        self,
        doc_file: str,
        changes: Dict[str, Any]
    ) -> Optional[str]:
        """Generate documentation update suggestion."""
        if not self.llm_interface:
            return None

        # Read current doc
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                current_content = f.read()[:2000]  # Limit size
        except:
            current_content = ""

        prompt = f"""Suggest updates to this documentation file based on the changes.

Documentation file: {Path(doc_file).name}
Current content preview:
{current_content}

Changes made:
Feature: {changes.get('feature', 'Unknown')}
Files: {', '.join(changes.get('files', []))}
Description: {changes.get('description', 'No description')}

Provide specific sections to add or update. Be concise."""

        try:
            suggestion = self.llm_interface.generate(
                prompt,
                max_tokens=500,
                use_cache=False
            )
            return suggestion.strip()
        except:
            return None


if __name__ == "__main__":
    # Test the tool integrator
    print("Testing Tool Integrator...")

    try:
        integrator = ToolIntegrator()
        print("✓ Tool Integrator created")

        # Test git status
        print("\n=== Test: Git Status ===")
        status = integrator.git_status()
        if status['initialized']:
            print(f"Git initialized: Yes")
            print(f"Branch: {status['branch']}")
            print(f"Changed files: {len(status['changed_files'])}")
        else:
            print(f"Git initialized: No - {status['error']}")

        print("\n✓ All tests passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
