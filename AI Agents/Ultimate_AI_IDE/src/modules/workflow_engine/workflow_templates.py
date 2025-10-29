"""
Workflow Templates

Built-in workflow templates for common tasks.
"""

from typing import Dict, Any


class WorkflowTemplates:
    """Built-in workflow templates"""
    
    @staticmethod
    def get_template(name: str) -> Dict[str, Any]:
        """
        Get workflow template by name
        
        Args:
            name: Template name
            
        Returns:
            Workflow template dictionary
        """
        templates = {
            'feature_implementation': WorkflowTemplates.feature_implementation(),
            'bug_fix': WorkflowTemplates.bug_fix(),
            'refactoring': WorkflowTemplates.refactoring(),
            'documentation_update': WorkflowTemplates.documentation_update(),
            'release_preparation': WorkflowTemplates.release_preparation(),
            'quality_assurance': WorkflowTemplates.quality_assurance()
        }
        
        if name not in templates:
            raise ValueError(f"Unknown template: {name}")
        
        return templates[name]
    
    @staticmethod
    def list_templates() -> Dict[str, str]:
        """List available templates with descriptions"""
        return {
            'feature_implementation': 'Complete workflow for implementing a new feature',
            'bug_fix': 'Workflow for diagnosing and fixing bugs',
            'refactoring': 'Workflow for code refactoring',
            'documentation_update': 'Workflow for updating documentation',
            'release_preparation': 'Workflow for preparing a release',
            'quality_assurance': 'Workflow for quality checks'
        }
    
    @staticmethod
    def feature_implementation() -> Dict[str, Any]:
        """Feature implementation workflow"""
        return {
            'name': 'Feature Implementation',
            'description': 'Complete workflow for implementing a new feature',
            'version': '1.0',
            'on_error': 'stop',
            'variables': {
                'feature_name': '',
                'project_path': '',
                'test_required': True
            },
            'steps': [
                {
                    'name': 'analyze_feature',
                    'action': 'analyze_request',
                    'description': 'Analyze feature request and decompose into tasks',
                    'params': {
                        'feature': '$feature_name',
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'check_duplicates',
                    'action': 'check_existing_code',
                    'description': 'Check for duplicate functionality',
                    'depends_on': ['analyze_feature'],
                    'params': {
                        'feature': '$feature_name',
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'generate_code',
                    'action': 'generate_feature_code',
                    'description': 'Generate feature code',
                    'depends_on': ['check_duplicates'],
                    'params': {
                        'feature': '$feature_name',
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'validate_code',
                    'action': 'validate_syntax',
                    'description': 'Validate generated code',
                    'depends_on': ['generate_code'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'generate_tests',
                    'action': 'generate_unit_tests',
                    'description': 'Generate unit tests',
                    'depends_on': ['validate_code'],
                    'params': {
                        'feature': '$feature_name',
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'run_tests',
                    'action': 'run_test_suite',
                    'description': 'Run test suite',
                    'depends_on': ['generate_tests'],
                    'retry_count': 2,
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'quality_check',
                    'action': 'check_code_quality',
                    'description': 'Check code quality',
                    'depends_on': ['run_tests'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'refactor_if_needed',
                    'action': 'refactor_code',
                    'description': 'Refactor if quality issues found',
                    'depends_on': ['quality_check'],
                    'on_failure': 'continue',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'update_docs',
                    'action': 'update_documentation',
                    'description': 'Update documentation',
                    'depends_on': ['refactor_if_needed'],
                    'params': {
                        'feature': '$feature_name',
                        'project_path': '$project_path'
                    }
                }
            ]
        }
    
    @staticmethod
    def bug_fix() -> Dict[str, Any]:
        """Bug fix workflow"""
        return {
            'name': 'Bug Fix',
            'description': 'Workflow for diagnosing and fixing bugs',
            'version': '1.0',
            'on_error': 'stop',
            'variables': {
                'bug_description': '',
                'project_path': '',
                'error_log': ''
            },
            'steps': [
                {
                    'name': 'analyze_bug',
                    'action': 'analyze_error',
                    'description': 'Analyze bug and error logs',
                    'params': {
                        'bug': '$bug_description',
                        'error_log': '$error_log',
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'locate_issue',
                    'action': 'find_bug_location',
                    'description': 'Locate the source of the bug',
                    'depends_on': ['analyze_bug'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'generate_fix',
                    'action': 'generate_bug_fix',
                    'description': 'Generate bug fix',
                    'depends_on': ['locate_issue'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'validate_fix',
                    'action': 'validate_syntax',
                    'description': 'Validate fix syntax',
                    'depends_on': ['generate_fix'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'run_tests',
                    'action': 'run_test_suite',
                    'description': 'Run tests to verify fix',
                    'depends_on': ['validate_fix'],
                    'retry_count': 1,
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'add_regression_test',
                    'action': 'generate_regression_test',
                    'description': 'Add regression test',
                    'depends_on': ['run_tests'],
                    'params': {
                        'bug': '$bug_description',
                        'project_path': '$project_path'
                    }
                }
            ]
        }
    
    @staticmethod
    def refactoring() -> Dict[str, Any]:
        """Refactoring workflow"""
        return {
            'name': 'Code Refactoring',
            'description': 'Workflow for code refactoring',
            'version': '1.0',
            'on_error': 'rollback',
            'variables': {
                'project_path': '',
                'target_files': []
            },
            'steps': [
                {
                    'name': 'analyze_code',
                    'action': 'analyze_code_quality',
                    'description': 'Analyze code quality and complexity',
                    'params': {
                        'project_path': '$project_path',
                        'files': '$target_files'
                    }
                },
                {
                    'name': 'backup_code',
                    'action': 'create_backup',
                    'description': 'Create code backup',
                    'depends_on': ['analyze_code'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'run_tests_before',
                    'action': 'run_test_suite',
                    'description': 'Run tests before refactoring',
                    'depends_on': ['backup_code'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'refactor_code',
                    'action': 'refactor_code',
                    'description': 'Perform refactoring',
                    'depends_on': ['run_tests_before'],
                    'rollback_action': 'restore_backup',
                    'params': {
                        'project_path': '$project_path',
                        'files': '$target_files'
                    }
                },
                {
                    'name': 'run_tests_after',
                    'action': 'run_test_suite',
                    'description': 'Run tests after refactoring',
                    'depends_on': ['refactor_code'],
                    'on_failure': 'rollback',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'verify_quality',
                    'action': 'check_code_quality',
                    'description': 'Verify quality improvement',
                    'depends_on': ['run_tests_after'],
                    'params': {
                        'project_path': '$project_path'
                    }
                }
            ]
        }
    
    @staticmethod
    def documentation_update() -> Dict[str, Any]:
        """Documentation update workflow"""
        return {
            'name': 'Documentation Update',
            'description': 'Workflow for updating documentation',
            'version': '1.0',
            'on_error': 'continue',
            'variables': {
                'project_path': '',
                'update_readme': True,
                'update_api_docs': True,
                'update_changelog': True
            },
            'steps': [
                {
                    'name': 'scan_codebase',
                    'action': 'scan_project_structure',
                    'description': 'Scan codebase structure',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'update_readme',
                    'action': 'generate_readme',
                    'description': 'Update README.md',
                    'depends_on': ['scan_codebase'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'update_api_docs',
                    'action': 'generate_api_docs',
                    'description': 'Update API documentation',
                    'depends_on': ['scan_codebase'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'generate_docstrings',
                    'action': 'generate_docstrings',
                    'description': 'Generate missing docstrings',
                    'depends_on': ['scan_codebase'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'validate_docs',
                    'action': 'validate_documentation',
                    'description': 'Validate documentation',
                    'depends_on': ['update_readme', 'update_api_docs', 'generate_docstrings'],
                    'params': {
                        'project_path': '$project_path'
                    }
                }
            ]
        }
    
    @staticmethod
    def release_preparation() -> Dict[str, Any]:
        """Release preparation workflow"""
        return {
            'name': 'Release Preparation',
            'description': 'Workflow for preparing a release',
            'version': '1.0',
            'on_error': 'stop',
            'variables': {
                'project_path': '',
                'version': '',
                'release_notes': ''
            },
            'steps': [
                {
                    'name': 'run_full_tests',
                    'action': 'run_test_suite',
                    'description': 'Run full test suite',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'quality_check',
                    'action': 'check_code_quality',
                    'description': 'Run quality checks',
                    'depends_on': ['run_full_tests'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'check_bloat',
                    'action': 'detect_bloat',
                    'description': 'Check for code bloat',
                    'depends_on': ['quality_check'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'update_version',
                    'action': 'bump_version',
                    'description': 'Update version numbers',
                    'depends_on': ['check_bloat'],
                    'params': {
                        'project_path': '$project_path',
                        'version': '$version'
                    }
                },
                {
                    'name': 'update_changelog',
                    'action': 'update_changelog',
                    'description': 'Update CHANGELOG.md',
                    'depends_on': ['update_version'],
                    'params': {
                        'project_path': '$project_path',
                        'version': '$version',
                        'notes': '$release_notes'
                    }
                },
                {
                    'name': 'update_docs',
                    'action': 'update_documentation',
                    'description': 'Update documentation',
                    'depends_on': ['update_changelog'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'create_tag',
                    'action': 'create_git_tag',
                    'description': 'Create git tag',
                    'depends_on': ['update_docs'],
                    'params': {
                        'project_path': '$project_path',
                        'version': '$version'
                    }
                }
            ]
        }
    
    @staticmethod
    def quality_assurance() -> Dict[str, Any]:
        """Quality assurance workflow"""
        return {
            'name': 'Quality Assurance',
            'description': 'Comprehensive quality checks',
            'version': '1.0',
            'on_error': 'continue',
            'variables': {
                'project_path': ''
            },
            'steps': [
                {
                    'name': 'run_tests',
                    'action': 'run_test_suite',
                    'description': 'Run all tests',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'check_coverage',
                    'action': 'check_test_coverage',
                    'description': 'Check test coverage',
                    'depends_on': ['run_tests'],
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'analyze_quality',
                    'action': 'analyze_code_quality',
                    'description': 'Analyze code quality',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'detect_bloat',
                    'action': 'detect_bloat',
                    'description': 'Detect code bloat',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'check_complexity',
                    'action': 'check_complexity',
                    'description': 'Check code complexity',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'validate_structure',
                    'action': 'validate_project_structure',
                    'description': 'Validate project structure',
                    'params': {
                        'project_path': '$project_path'
                    }
                },
                {
                    'name': 'generate_report',
                    'action': 'generate_quality_report',
                    'description': 'Generate quality report',
                    'depends_on': [
                        'check_coverage',
                        'analyze_quality',
                        'detect_bloat',
                        'check_complexity',
                        'validate_structure'
                    ],
                    'params': {
                        'project_path': '$project_path'
                    }
                }
            ]
        }
