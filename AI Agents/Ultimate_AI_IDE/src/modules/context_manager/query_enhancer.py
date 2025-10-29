"""
Query Enhancer

Enhances search queries for better retrieval accuracy.
Part of v1.6.0 - Advanced RAG & Retrieval.
"""

import logging
from typing import List, Dict, Set, Optional, Any
import re

logger = logging.getLogger(__name__)


class QueryEnhancer:
    """
    Query enhancement for better retrieval.
    
    Features:
    - Query expansion
    - Synonym expansion
    - LLM reformulation
    - Better recall
    """
    
    def __init__(self, ai_backend=None):
        """
        Initialize query enhancer.
        
        Args:
            ai_backend: AI backend for LLM reformulation
        """
        self.ai_backend = ai_backend
        
        # Programming synonyms
        self.synonyms = {
            'function': ['method', 'procedure', 'routine', 'def', 'func'],
            'class': ['object', 'type', 'struct', 'interface'],
            'variable': ['var', 'field', 'attribute', 'property'],
            'loop': ['iteration', 'for', 'while', 'foreach'],
            'condition': ['if', 'conditional', 'branch', 'switch', 'case'],
            'error': ['exception', 'bug', 'issue', 'problem', 'failure'],
            'test': ['unittest', 'spec', 'assertion', 'check'],
            'database': ['db', 'storage', 'persistence', 'data store'],
            'api': ['endpoint', 'service', 'interface', 'rest'],
            'authentication': ['auth', 'login', 'credentials', 'access'],
            'configuration': ['config', 'settings', 'options', 'preferences'],
            'validation': ['verify', 'check', 'validate', 'sanitize'],
            'optimization': ['optimize', 'improve', 'enhance', 'performance'],
            'refactor': ['restructure', 'reorganize', 'cleanup', 'improve'],
            'documentation': ['docs', 'readme', 'guide', 'manual'],
        }
        
        # Common programming patterns
        self.patterns = {
            'crud': ['create', 'read', 'update', 'delete', 'insert', 'select', 'modify', 'remove'],
            'http': ['get', 'post', 'put', 'delete', 'patch', 'request', 'response'],
            'async': ['async', 'await', 'promise', 'future', 'concurrent', 'parallel'],
            'data_structures': ['list', 'array', 'dict', 'map', 'set', 'tree', 'graph', 'queue', 'stack'],
        }
        
        logger.info("Initialized QueryEnhancer")
    
    def expand_query(self, query: str, max_expansions: int = 5) -> List[str]:
        """
        Expand query with related terms.
        
        Args:
            query: Original query
            max_expansions: Maximum number of expansions
            
        Returns:
            List of expanded queries
        """
        try:
            expansions = [query]  # Start with original
            
            # Extract key terms
            terms = self._extract_terms(query)
            
            # Add synonym expansions
            for term in terms:
                term_lower = term.lower()
                for key, synonyms in self.synonyms.items():
                    if term_lower == key or term_lower in synonyms:
                        # Create variations
                        for syn in synonyms[:2]:  # Limit to 2 synonyms per term
                            expanded = query.replace(term, syn)
                            if expanded not in expansions:
                                expansions.append(expanded)
                                if len(expansions) >= max_expansions:
                                    return expansions
            
            logger.debug(f"Expanded query to {len(expansions)} variations")
            return expansions
            
        except Exception as e:
            logger.error(f"Query expansion failed: {e}")
            return [query]
    
    def add_synonyms(self, query: str) -> str:
        """
        Add programming synonyms to query.
        
        Args:
            query: Original query
            
        Returns:
            Enhanced query with synonyms
        """
        try:
            terms = self._extract_terms(query)
            additional_terms = []
            
            for term in terms:
                term_lower = term.lower()
                for key, synonyms in self.synonyms.items():
                    if term_lower == key:
                        additional_terms.extend(synonyms[:2])
                    elif term_lower in synonyms:
                        additional_terms.append(key)
                        additional_terms.extend([s for s in synonyms if s != term_lower][:1])
            
            if additional_terms:
                enhanced = f"{query} ({' OR '.join(set(additional_terms))})"
                logger.debug(f"Added synonyms: {additional_terms}")
                return enhanced
            
            return query
            
        except Exception as e:
            logger.error(f"Synonym addition failed: {e}")
            return query
    
    def reformulate_with_llm(self, query: str, context: Optional[str] = None) -> List[str]:
        """
        Use LLM to reformulate query.
        
        Args:
            query: Original query
            context: Optional context
            
        Returns:
            List of reformulated queries
        """
        if not self.ai_backend:
            logger.warning("No AI backend available for LLM reformulation")
            return [query]
        
        try:
            prompt = f"""Given this search query, generate 3 alternative formulations that would help find relevant code:

Original query: {query}
{f'Context: {context}' if context else ''}

Generate 3 alternative queries that:
1. Use different technical terms
2. Focus on different aspects
3. Are more specific or more general

Return only the 3 queries, one per line."""

            response = self.ai_backend.query(prompt, max_tokens=200)
            
            # Parse response
            reformulations = [query]  # Include original
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip()
                # Remove numbering
                line = re.sub(r'^\d+[\.\)]\s*', '', line)
                if line and line != query:
                    reformulations.append(line)
            
            logger.debug(f"LLM reformulated query into {len(reformulations)} variations")
            return reformulations[:4]  # Original + 3 reformulations
            
        except Exception as e:
            logger.error(f"LLM reformulation failed: {e}")
            return [query]
    
    def enhance_query(
        self,
        query: str,
        use_synonyms: bool = True,
        use_expansion: bool = True,
        use_llm: bool = False,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enhance query using multiple techniques.
        
        Args:
            query: Original query
            use_synonyms: Add synonyms
            use_expansion: Expand query
            use_llm: Use LLM reformulation
            context: Optional context
            
        Returns:
            Dict with enhanced queries
        """
        result = {
            'original': query,
            'enhanced': query,
            'expansions': [],
            'reformulations': []
        }
        
        try:
            # Add synonyms
            if use_synonyms:
                result['enhanced'] = self.add_synonyms(query)
            
            # Expand query
            if use_expansion:
                result['expansions'] = self.expand_query(query)
            
            # LLM reformulation
            if use_llm:
                result['reformulations'] = self.reformulate_with_llm(query, context)
            
            logger.info(f"Enhanced query with {len(result['expansions'])} expansions and {len(result['reformulations'])} reformulations")
            return result
            
        except Exception as e:
            logger.error(f"Query enhancement failed: {e}")
            return result
    
    def _extract_terms(self, query: str) -> List[str]:
        """Extract key terms from query."""
        # Remove special characters and split
        terms = re.findall(r'\b\w+\b', query)
        # Filter out common words
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        return [t for t in terms if t.lower() not in stopwords and len(t) > 2]
    
    def detect_intent(self, query: str) -> str:
        """
        Detect query intent.
        
        Args:
            query: Search query
            
        Returns:
            Intent category
        """
        query_lower = query.lower()
        
        # Check for patterns
        if any(word in query_lower for word in ['how', 'implement', 'create', 'build']):
            return 'implementation'
        elif any(word in query_lower for word in ['fix', 'bug', 'error', 'issue', 'problem']):
            return 'debugging'
        elif any(word in query_lower for word in ['what', 'explain', 'describe', 'understand']):
            return 'explanation'
        elif any(word in query_lower for word in ['optimize', 'improve', 'performance', 'faster']):
            return 'optimization'
        elif any(word in query_lower for word in ['test', 'verify', 'check', 'validate']):
            return 'testing'
        elif any(word in query_lower for word in ['refactor', 'restructure', 'cleanup']):
            return 'refactoring'
        else:
            return 'general'
    
    def suggest_filters(self, query: str) -> Dict[str, List[str]]:
        """
        Suggest filters based on query.
        
        Args:
            query: Search query
            
        Returns:
            Suggested filters
        """
        filters = {
            'languages': [],
            'file_types': [],
            'patterns': []
        }
        
        query_lower = query.lower()
        
        # Detect languages
        language_keywords = {
            'python': ['python', 'py', 'django', 'flask', 'fastapi'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'typescript': ['typescript', 'ts'],
            'java': ['java', 'spring', 'maven'],
            'csharp': ['c#', 'csharp', 'dotnet', '.net'],
            'cpp': ['c++', 'cpp'],
            'go': ['golang', 'go'],
            'rust': ['rust'],
        }
        
        for lang, keywords in language_keywords.items():
            if any(kw in query_lower for kw in keywords):
                filters['languages'].append(lang)
        
        # Detect file types
        if any(word in query_lower for word in ['test', 'unittest', 'spec']):
            filters['file_types'].append('test')
        if any(word in query_lower for word in ['doc', 'readme', 'guide']):
            filters['file_types'].append('documentation')
        if any(word in query_lower for word in ['config', 'settings']):
            filters['file_types'].append('configuration')
        
        # Detect patterns
        for pattern_name, keywords in self.patterns.items():
            if any(kw in query_lower for kw in keywords):
                filters['patterns'].append(pattern_name)
        
        return filters
    
    def get_related_terms(self, term: str) -> List[str]:
        """
        Get related terms for a given term.
        
        Args:
            term: Search term
            
        Returns:
            List of related terms
        """
        related = []
        term_lower = term.lower()
        
        # Check synonyms
        for key, synonyms in self.synonyms.items():
            if term_lower == key:
                related.extend(synonyms)
            elif term_lower in synonyms:
                related.append(key)
                related.extend([s for s in synonyms if s != term_lower])
        
        # Check patterns
        for pattern_name, keywords in self.patterns.items():
            if term_lower in keywords:
                related.extend([k for k in keywords if k != term_lower])
        
        return list(set(related))
    
    def add_custom_synonym(self, term: str, synonyms: List[str]):
        """
        Add custom synonym mapping.
        
        Args:
            term: Base term
            synonyms: List of synonyms
        """
        self.synonyms[term.lower()] = synonyms
        logger.info(f"Added custom synonyms for '{term}': {synonyms}")
    
    def get_statistics(self) -> Dict[str, int]:
        """Get enhancer statistics."""
        return {
            'synonym_groups': len(self.synonyms),
            'total_synonyms': sum(len(syns) for syns in self.synonyms.values()),
            'pattern_groups': len(self.patterns),
            'total_patterns': sum(len(pats) for pats in self.patterns.values())
        }
