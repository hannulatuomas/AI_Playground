"""
Context Retriever

Retrieves relevant code context based on queries.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .embedder import EmbeddingIndex
from .summarizer import CodeSummarizer, CodeSummary


@dataclass
class RetrievedContext:
    """Retrieved context information."""
    files: List[str]
    summaries: List[CodeSummary]
    relevance_scores: List[float]
    total_tokens: int


class ContextRetriever:
    """Retrieves relevant context for queries."""
    
    def __init__(self, ai_backend):
        """
        Initialize context retriever.
        
        Args:
            ai_backend: AI backend
        """
        self.ai_backend = ai_backend
        self.index = EmbeddingIndex()
        self.summarizer = CodeSummarizer(ai_backend)
        self.summaries: Dict[str, CodeSummary] = {}
    
    def index_file(self, file_path: str, language: str = 'python'):
        """
        Index a file for retrieval.
        
        Args:
            file_path: Path to file
            language: Programming language
        """
        # Generate summary
        summary = self.summarizer.summarize_file(file_path, language)
        self.summaries[file_path] = summary
        
        # Create searchable text
        search_text = self._create_search_text(summary)
        
        # Add to index
        self.index.add(search_text, {
            'file_path': file_path,
            'language': language,
            'purpose': summary.purpose,
            'complexity': summary.complexity
        })
    
    def index_project(self, project_path: str, language: str = 'python'):
        """
        Index entire project.
        
        Args:
            project_path: Root path of project
            language: Programming language
        """
        from pathlib import Path
        
        root = Path(project_path)
        
        # Find code files
        extensions = {
            'python': ['.py'],
            'javascript': ['.js', '.jsx'],
            'typescript': ['.ts', '.tsx']
        }
        
        ext_list = extensions.get(language, ['.py'])
        
        for ext in ext_list:
            for file_path in root.rglob(f'*{ext}'):
                # Skip common directories
                if any(skip in file_path.parts for skip in 
                      ['__pycache__', 'node_modules', '.git', 'venv']):
                    continue
                
                try:
                    self.index_file(str(file_path), language)
                except Exception as e:
                    print(f"Error indexing {file_path}: {e}")
    
    def get_relevant_context(self, query: str, max_tokens: int = 2000,
                           top_k: int = 5) -> RetrievedContext:
        """
        Retrieve relevant context for query.
        
        Args:
            query: Query string
            max_tokens: Maximum tokens to return
            top_k: Number of files to retrieve
            
        Returns:
            RetrievedContext with relevant information
        """
        # Search index
        results = self.index.search(query, top_k=top_k)
        
        files = []
        summaries = []
        scores = []
        total_tokens = 0
        
        for result in results:
            file_path = result['file_path']
            score = result['similarity']
            
            if file_path in self.summaries:
                summary = self.summaries[file_path]
                
                # Estimate tokens (rough: 1 token ≈ 4 chars)
                summary_text = self.summarizer.format_summary(summary)
                tokens = len(summary_text) // 4
                
                if total_tokens + tokens <= max_tokens:
                    files.append(file_path)
                    summaries.append(summary)
                    scores.append(score)
                    total_tokens += tokens
                else:
                    break
        
        return RetrievedContext(
            files=files,
            summaries=summaries,
            relevance_scores=scores,
            total_tokens=total_tokens
        )
    
    def get_context_for_task(self, task_description: str,
                            max_tokens: int = 2000) -> str:
        """
        Get formatted context for a task.
        
        Args:
            task_description: Description of task
            max_tokens: Maximum tokens
            
        Returns:
            Formatted context string
        """
        context = self.get_relevant_context(task_description, max_tokens)
        
        if not context.summaries:
            return "No relevant context found."
        
        formatted = "Relevant code context:\n\n"
        
        for i, (summary, score) in enumerate(zip(context.summaries, 
                                                 context.relevance_scores)):
            formatted += f"--- File {i+1}: {summary.file_path} (relevance: {score:.2f}) ---\n"
            formatted += self.summarizer.format_summary(summary)
            formatted += "\n"
        
        return formatted
    
    def _create_search_text(self, summary: CodeSummary) -> str:
        """Create searchable text from summary."""
        text_parts = [
            summary.purpose,
            ' '.join(cls['name'] for cls in summary.classes),
            ' '.join(cls['description'] for cls in summary.classes),
            ' '.join(func['name'] for func in summary.functions),
            ' '.join(summary.imports)
        ]
        
        return ' '.join(text_parts)
    
    def clear_index(self):
        """Clear the index."""
        self.index.clear()
        self.summaries.clear()
    
    def get_stats(self) -> Dict[str, int]:
        """Get index statistics."""
        return {
            'indexed_files': self.index.size(),
            'total_summaries': len(self.summaries)
        }
