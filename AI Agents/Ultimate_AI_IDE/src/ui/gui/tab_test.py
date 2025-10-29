"""
Testing Tab

Handles test generation, test execution, and bug fixing.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext

from .base import BaseTab, LabeledEntry, LabeledCombobox, OutputPanel, run_async


class TestTab(BaseTab):
    """Testing tab."""
    
    def setup_ui(self):
        """Setup testing UI."""
        # Create notebook for sub-tabs
        sub_notebook = ttk.Notebook(self)
        sub_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sub-tabs
        self.generate_tests_frame = self.create_generate_tests_tab()
        self.run_tests_frame = self.create_run_tests_tab()
        self.fix_bugs_frame = self.create_fix_bugs_tab()
        
        sub_notebook.add(self.generate_tests_frame, text="Generate Tests")
        sub_notebook.add(self.run_tests_frame, text="Run Tests")
        sub_notebook.add(self.fix_bugs_frame, text="Fix Bugs")
    
    def create_generate_tests_tab(self):
        """Create test generation tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Test Generation", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.test_file_path = LabeledEntry(path_frame, "Source File:", width=40)
        self.test_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_test_file
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.test_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "java"],
            width=20
        )
        self.test_language.pack(fill=tk.X, pady=5)
        
        self.test_framework = LabeledCombobox(
            input_frame,
            "Test Framework:",
            ["pytest", "unittest", "jest", "mocha", "junit"],
            width=20
        )
        self.test_framework.pack(fill=tk.X, pady=5)
        
        # Generate button
        ttk.Button(
            input_frame,
            text="Generate Tests",
            command=self.generate_tests,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Generated Tests", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.test_gen_output = scrolledtext.ScrolledText(
            output_frame,
            height=15,
            wrap=tk.WORD
        )
        self.test_gen_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_run_tests_tab(self):
        """Create test execution tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Run Tests", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Project path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.run_project_path = LabeledEntry(path_frame, "Project Path:", width=40)
        self.run_project_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_run_path
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        self.run_language = LabeledCombobox(
            input_frame,
            "Language:",
            ["python", "javascript", "typescript", "java"],
            width=20
        )
        self.run_language.pack(fill=tk.X, pady=5)
        
        # Run button
        ttk.Button(
            input_frame,
            text="Run Tests",
            command=self.run_tests,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Results section
        results_frame = ttk.LabelFrame(frame, text="Test Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Summary
        self.results_summary = ttk.Label(results_frame, text="No tests run yet")
        self.results_summary.pack(pady=5)
        
        # Detailed output
        self.test_run_output = OutputPanel(results_frame, height=12)
        self.test_run_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def create_fix_bugs_tab(self):
        """Create bug fixing tab."""
        frame = ttk.Frame(self)
        
        # Input section
        input_frame = ttk.LabelFrame(frame, text="Bug Information", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # File path
        path_frame = ttk.Frame(input_frame)
        path_frame.pack(fill=tk.X, pady=5)
        self.bug_file_path = LabeledEntry(path_frame, "File with Bug:", width=40)
        self.bug_file_path.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(
            path_frame,
            text="Browse...",
            command=self.browse_bug_file
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Label(input_frame, text="Error Message:").pack(anchor=tk.W, pady=(10, 5))
        self.bug_error = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            wrap=tk.WORD
        )
        self.bug_error.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Diagnose button
        ttk.Button(
            input_frame,
            text="Diagnose & Fix Bug",
            command=self.fix_bug,
            style="Accent.TButton"
        ).pack(pady=10)
        
        # Output section
        output_frame = ttk.LabelFrame(frame, text="Diagnosis & Fix", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.bug_output = OutputPanel(output_frame, height=12)
        self.bug_output.pack(fill=tk.BOTH, expand=True)
        
        return frame
    
    def browse_test_file(self):
        """Browse for source file."""
        path = self.select_file(
            "Select Source File",
            [("Python files", "*.py"), ("JavaScript files", "*.js"), ("All files", "*.*")]
        )
        if path:
            self.test_file_path.set(path)
    
    def browse_run_path(self):
        """Browse for project path."""
        path = self.select_directory("Select Project Directory")
        if path:
            self.run_project_path.set(path)
    
    def browse_bug_file(self):
        """Browse for file with bug."""
        path = self.select_file(
            "Select File with Bug",
            [("Python files", "*.py"), ("JavaScript files", "*.js"), ("All files", "*.*")]
        )
        if path:
            self.bug_file_path.set(path)
    
    def generate_tests(self):
        """Generate tests for file."""
        file_path = self.test_file_path.get().strip()
        language = self.test_language.get()
        framework = self.test_framework.get()
        
        if not file_path:
            self.show_error("Validation Error", "Source file path is required")
            return
        
        self.test_gen_output.delete("1.0", tk.END)
        self.test_gen_output.insert("1.0", f"Generating tests for {file_path}...\n")
        
        def generate():
            test_file = self.uaide.test_generator.generate_tests(
                file_path=file_path,
                language=language,
                framework=framework
            )
            # Format output
            output = f"# Generated Tests for {file_path}\n\n"
            output += f"Language: {test_file.language}\n"
            output += f"Framework: {test_file.framework}\n"
            output += f"Test Cases: {len(test_file.test_cases)}\n\n"
            
            for i, test_case in enumerate(test_file.test_cases, 1):
                output += f"## Test {i}: {test_case.name}\n"
                output += f"Description: {test_case.description}\n"
                output += f"```{language}\n{test_case.code}\n```\n\n"
            
            return output
        
        def callback(result, error=None):
            self.test_gen_output.delete("1.0", tk.END)
            if error:
                self.test_gen_output.insert("1.0", f"Error: {error}")
                self.show_error("Generation Failed", error)
            elif result:
                self.test_gen_output.insert("1.0", result)
                self.show_success("Success", "Tests generated successfully!")
            else:
                self.test_gen_output.insert("1.0", "Failed to generate tests")
        
        run_async(generate, callback)
    
    def run_tests(self):
        """Run tests."""
        project_path = self.run_project_path.get().strip()
        language = self.run_language.get()
        
        if not project_path:
            self.show_error("Validation Error", "Project path is required")
            return
        
        self.test_run_output.clear()
        self.test_run_output.append("Running tests...")
        self.results_summary.config(text="Running tests...")
        
        def run():
            return self.uaide.test_code(project_path=project_path)
        
        def callback(result, error=None):
            if error:
                self.test_run_output.append(f"\n❌ Error: {error}")
                self.results_summary.config(text="Test execution failed")
                self.show_error("Execution Failed", error)
            elif result and result.success:
                data = result.data
                total = data.get('total', 0)
                passed = data.get('passed', 0)
                failed = data.get('failed', 0)
                coverage = data.get('coverage', 0)
                
                summary = f"Tests: {passed}/{total} passed"
                if failed > 0:
                    summary += f", {failed} failed"
                summary += f" | Coverage: {coverage}%"
                
                self.results_summary.config(text=summary)
                self.test_run_output.append(f"\n✅ {result.message}")
                self.test_run_output.append(f"Total: {total}")
                self.test_run_output.append(f"Passed: {passed}")
                self.test_run_output.append(f"Failed: {failed}")
                self.test_run_output.append(f"Coverage: {coverage}%")
                
                if failed == 0:
                    self.show_success("Success", "All tests passed!")
                else:
                    self.show_info("Tests Complete", f"{failed} test(s) failed")
            else:
                msg = result.message if result else "Unknown error"
                self.test_run_output.append(f"\n❌ {msg}")
                self.results_summary.config(text="Test execution failed")
        
        run_async(run, callback)
    
    def fix_bug(self):
        """Diagnose and fix bug."""
        file_path = self.bug_file_path.get().strip()
        error_msg = self.bug_error.get("1.0", tk.END).strip()
        
        if not file_path:
            self.show_error("Validation Error", "File path is required")
            return
        
        if not error_msg:
            self.show_error("Validation Error", "Error message is required")
            return
        
        self.bug_output.clear()
        self.bug_output.append("Diagnosing bug...")
        
        def diagnose():
            # Read file content
            with open(file_path, 'r') as f:
                code = f.read()
            
            diagnosis = self.uaide.bug_fixer.diagnose_bug(
                error_message=error_msg,
                code=code,
                file_path=file_path
            )
            return diagnosis
        
        def callback(result, error=None):
            if error:
                self.bug_output.append(f"\n❌ Error: {error}")
                self.show_error("Diagnosis Failed", error)
            elif result:
                self.bug_output.append(f"\n✅ Diagnosis Complete")
                self.bug_output.append(f"\nRoot Cause: {result.root_cause}")
                self.bug_output.append(f"\nAffected Files: {', '.join(result.affected_files)}")
                self.bug_output.append(f"\nSuggested Fixes:")
                for i, fix in enumerate(result.suggested_fixes, 1):
                    self.bug_output.append(f"  {i}. {fix}")
                self.bug_output.append(f"\nConfidence: {result.confidence}%")
                self.show_success("Diagnosis Complete", "Bug diagnosis completed!")
            else:
                self.bug_output.append("\n❌ Failed to diagnose bug")
        
        run_async(diagnose, callback)
