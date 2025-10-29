"""
Query Expansion Module

Improves retrieval recall by generating query variations through:
- Synonym expansion (function → method, authenticate → auth)
- Language-specific term expansion
- LLM-based query reformulation
- Abbreviation expansion

Example:
    >>> expander = QueryExpander()
    >>> variations = expander.expand_query("JWT authentication")
    >>> print(variations)
    ['JWT authentication', 'JWT auth', 'JSON Web Token authentication', ...]
"""

from typing import List, Optional, Dict, Set
import re


class QueryExpander:
    """
    Expand queries to improve retrieval recall.
    
    Generates multiple variations of a query to handle:
    - Different terminology (function vs method)
    - Abbreviations (auth vs authentication)
    - Programming language variations
    """
    
    # Programming term synonyms
    SYNONYMS = {
        # Functions and methods
        'function': ['method', 'func', 'procedure', 'routine'],
        'method': ['function', 'func', 'member function'],
        'class': ['type', 'object', 'struct'],
        'variable': ['var', 'field', 'attribute', 'property'],
        'parameter': ['param', 'argument', 'arg'],
        
        # Operations
        'create': ['make', 'initialize', 'construct', 'new'],
        'delete': ['remove', 'destroy', 'drop'],
        'update': ['modify', 'change', 'edit', 'set'],
        'get': ['fetch', 'retrieve', 'read', 'find'],
        'set': ['assign', 'update', 'write'],
        
        # Authentication/Authorization
        'authenticate': ['auth', 'login', 'sign in', 'verify'],
        'authorize': ['authz', 'permission', 'access control'],
        'authentication': ['auth', 'login', 'signin'],
        'authorization': ['authz', 'permissions', 'access'],
        
        # Database
        'database': ['db', 'datastore', 'data store'],
        'query': ['search', 'find', 'select'],
        'table': ['relation', 'entity'],
        'record': ['row', 'entry', 'tuple'],
        
        # Common abbreviations
        'config': ['configuration', 'settings', 'setup'],
        'init': ['initialize', 'initialization', 'setup'],
        'util': ['utility', 'utilities', 'helper'],
        'admin': ['administrator', 'administration'],
        'impl': ['implementation', 'implement'],
        'mgr': ['manager', 'management'],
        'svc': ['service'],
        'ctrl': ['controller', 'control'],
        
        # Data structures
        'array': ['list', 'collection', 'sequence'],
        'list': ['array', 'collection', 'sequence'],
        'dict': ['dictionary', 'map', 'hashmap', 'object'],
        'set': ['collection', 'unique list'],
        
        # Async/Concurrency
        'async': ['asynchronous', 'non-blocking'],
        'sync': ['synchronous', 'blocking'],
        'thread': ['worker', 'task'],
        'lock': ['mutex', 'semaphore'],
        
        # Error handling
        'error': ['exception', 'failure', 'fault'],
        'exception': ['error', 'failure'],
        'handle': ['catch', 'manage', 'process'],
    }
    
    # Common programming acronyms
    ACRONYMS = {
        'JWT': 'JSON Web Token',
        'API': 'Application Programming Interface',
        'REST': 'Representational State Transfer',
        'CRUD': 'Create Read Update Delete',
        'SQL': 'Structured Query Language',
        'JSON': 'JavaScript Object Notation',
        'XML': 'Extensible Markup Language',
        'HTML': 'HyperText Markup Language',
        'CSS': 'Cascading Style Sheets',
        'HTTP': 'HyperText Transfer Protocol',
        'HTTPS': 'HTTP Secure',
        'URL': 'Uniform Resource Locator',
        'URI': 'Uniform Resource Identifier',
        'UUID': 'Universally Unique Identifier',
        'ORM': 'Object-Relational Mapping',
        'MVC': 'Model View Controller',
        'DTO': 'Data Transfer Object',
        'DAO': 'Data Access Object',
        'DI': 'Dependency Injection',
        'IoC': 'Inversion of Control',
        'TDD': 'Test-Driven Development',
        'BDD': 'Behavior-Driven Development',
    }
    
    # Language-specific term variations
    LANGUAGE_VARIANTS = {
        'python': {
            'function': ['def', 'lambda'],
            'class': ['class'],
            'variable': ['var', 'name'],
            'import': ['from', 'import'],
        },
        'javascript': {
            'function': ['function', 'arrow function', '=>'],
            'class': ['class', 'prototype'],
            'variable': ['var', 'let', 'const'],
            'import': ['import', 'require'],
        },
        'typescript': {
            'function': ['function', 'arrow function', '=>'],
            'class': ['class', 'interface', 'type'],
            'variable': ['var', 'let', 'const'],
            'import': ['import', 'require'],
        },
        'java': {
            'function': ['method'],
            'class': ['class', 'interface', 'enum'],
            'variable': ['field', 'variable'],
            'import': ['import'],
        },
        'csharp': {
            'function': ['method'],
            'class': ['class', 'struct', 'interface'],
            'variable': ['field', 'property'],
            'import': ['using'],
        },
    }
    
    def __init__(self, llm_interface=None, use_llm: bool = True):
        """
        Initialize query expander.
        
        Args:
            llm_interface: Optional LLM for advanced reformulation
            use_llm: Whether to use LLM for query reformulation
        """
        self.llm = llm_interface
        self.use_llm = use_llm and llm_interface is not None
        
        # Build reverse synonym map for efficient lookup
        self._reverse_synonyms = {}
        for term, synonyms in self.SYNONYMS.items():
            for syn in synonyms:
                if syn not in self._reverse_synonyms:
                    self._reverse_synonyms[syn] = []
                self._reverse_synonyms[syn].append(term)
    
    def expand_query(
        self,
        query: str,
        language: Optional[str] = None,
        max_expansions: int = 5,
        include_original: bool = True
    ) -> List[str]:
        """
        Generate query variations.
        
        Args:
            query: Original query
            language: Programming language context
            max_expansions: Maximum number of variations
            include_original: Include original query
            
        Returns:
            List of query variations
            
        Example:
            >>> expander = QueryExpander()
            >>> variations = expander.expand_query("auth function", language="python")
            >>> print(variations)
            ['auth function', 'authentication function', 'auth def', ...]
        """
        variations = set()
        
        # Always include original
        if include_original:
            variations.add(query)
        
        # Expand acronyms
        acronym_expansions = self._expand_acronyms(query)
        variations.update(acronym_expansions)
        
        # Expand synonyms
        synonym_expansions = self._expand_synonyms(query)
        variations.update(synonym_expansions)
        
        # Language-specific expansions
        if language:
            lang_expansions = self._expand_language_specific(query, language)
            variations.update(lang_expansions)
        
        # Abbreviation expansions
        abbrev_expansions = self._expand_abbreviations(query)
        variations.update(abbrev_expansions)
        
        # LLM-based reformulation (if available and enabled)
        if self.use_llm and len(variations) < max_expansions:
            try:
                llm_expansions = self.reformulate_with_llm(query, max_expansions - len(variations))
                variations.update(llm_expansions)
            except Exception as e:
                # LLM reformulation failed, continue without it
                pass
        
        # Limit to max expansions
        result = list(variations)[:max_expansions]
        
        return result
    
    def _expand_acronyms(self, query: str) -> Set[str]:
        """Expand acronyms in query."""
        expansions = set()
        
        for acronym, expansion in self.ACRONYMS.items():
            if acronym.lower() in query.lower():
                # Replace acronym with full form
                expanded = re.sub(
                    rf'\b{re.escape(acronym)}\b',
                    expansion,
                    query,
                    flags=re.IGNORECASE
                )
                if expanded != query:
                    expansions.add(expanded)
                
                # Also try lowercase version
                expanded_lower = re.sub(
                    rf'\b{re.escape(acronym)}\b',
                    expansion.lower(),
                    query,
                    flags=re.IGNORECASE
                )
                if expanded_lower != query and expanded_lower != expanded:
                    expansions.add(expanded_lower)
        
        return expansions
    
    def _expand_synonyms(self, query: str) -> Set[str]:
        """Expand synonyms in query."""
        expansions = set()
        words = query.lower().split()
        
        for i, word in enumerate(words):
            # Check if word has synonyms
            if word in self.SYNONYMS:
                for synonym in self.SYNONYMS[word]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    expansions.add(' '.join(new_words))
            
            # Check reverse synonyms
            elif word in self._reverse_synonyms:
                for synonym in self._reverse_synonyms[word]:
                    new_words = words.copy()
                    new_words[i] = synonym
                    expansions.add(' '.join(new_words))
        
        return expansions
    
    def _expand_language_specific(self, query: str, language: str) -> Set[str]:
        """Expand with language-specific terms."""
        expansions = set()
        language = language.lower()
        
        if language not in self.LANGUAGE_VARIANTS:
            return expansions
        
        variants = self.LANGUAGE_VARIANTS[language]
        words = query.lower().split()
        
        for i, word in enumerate(words):
            if word in variants:
                for variant in variants[word]:
                    new_words = words.copy()
                    new_words[i] = variant
                    expansions.add(' '.join(new_words))
        
        return expansions
    
    def _expand_abbreviations(self, query: str) -> Set[str]:
        """Expand common programming abbreviations."""
        expansions = set()
        
        # Common patterns
        abbreviations = {
            r'\bauth\b': 'authentication',
            r'\bconfig\b': 'configuration',
            r'\binit\b': 'initialize',
            r'\butil\b': 'utility',
            r'\bimpl\b': 'implementation',
            r'\bmgr\b': 'manager',
            r'\bctrl\b': 'controller',
            r'\bsvc\b': 'service',
            r'\brepo\b': 'repository',
            r'\bspec\b': 'specification',
            r'\bconn\b': 'connection',
            r'\breq\b': 'request',
            r'\bresp\b': 'response',
        }
        
        for abbrev, full in abbreviations.items():
            if re.search(abbrev, query, re.IGNORECASE):
                expanded = re.sub(abbrev, full, query, flags=re.IGNORECASE)
                if expanded != query:
                    expansions.add(expanded)
        
        return expansions
    
    def reformulate_with_llm(
        self,
        query: str,
        max_reformulations: int = 3
    ) -> List[str]:
        """
        Use LLM to generate alternative formulations.
        
        Args:
            query: Original query
            max_reformulations: Maximum number of reformulations
            
        Returns:
            List of reformulated queries
        """
        if not self.llm:
            return []
        
        try:
            prompt = f"""Generate {max_reformulations} alternative ways to search for code related to: "{query}"

Rules:
- Keep queries concise (5-10 words)
- Use programming terminology
- Focus on different aspects of the query
- Output one query per line
- Do not include numbers or bullet points

Examples:
Query: "JWT authentication"
Alternatives:
token based authentication
verify JSON web token
user authentication with JWT

Query: "{query}"
Alternatives:"""
            
            response = self.llm.query(prompt, max_tokens=100)
            
            if response.get('success'):
                text = response.get('response', '')
                # Parse lines
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                # Filter out empty or too long queries
                reformulations = [
                    line for line in lines 
                    if line and len(line.split()) <= 15 and not line[0].isdigit()
                ][:max_reformulations]
                
                return reformulations
        except Exception as e:
            # LLM query failed
            pass
        
        return []
    
    def get_synonyms(self, term: str) -> List[str]:
        """
        Get synonyms for a programming term.
        
        Args:
            term: Programming term
            
        Returns:
            List of synonyms
        """
        term_lower = term.lower()
        synonyms = []
        
        # Direct lookup
        if term_lower in self.SYNONYMS:
            synonyms.extend(self.SYNONYMS[term_lower])
        
        # Reverse lookup
        if term_lower in self._reverse_synonyms:
            synonyms.extend(self._reverse_synonyms[term_lower])
        
        return list(set(synonyms))
    
    def expand_with_context(
        self,
        query: str,
        file_context: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> List[str]:
        """
        Expand query using file context.
        
        Args:
            query: Original query
            file_context: List of file names for context
            language: Programming language
            
        Returns:
            Expanded queries
        """
        expansions = self.expand_query(query, language=language)
        
        # If we have file context, add variations with file-specific terms
        if file_context:
            for file_name in file_context[:5]:  # Limit context
                # Extract meaningful words from file name
                words = re.findall(r'[a-z]+', file_name.lower())
                for word in words:
                    if len(word) > 3:  # Skip short words
                        expansions.append(f"{query} {word}")
        
        return list(set(expansions))


if __name__ == "__main__":
    # Test query expansion
    print("Testing Query Expander...\\n")
    
    expander = QueryExpander()
    
    # Test 1: Basic expansion
    print("=== Test 1: Basic Expansion ===")
    query = "authentication function"
    expansions = expander.expand_query(query)
    print(f"Query: {query}")
    print(f"Expansions: {expansions}\\n")
    
    # Test 2: Acronym expansion
    print("=== Test 2: Acronym Expansion ===")
    query = "JWT auth"
    expansions = expander.expand_query(query)
    print(f"Query: {query}")
    print(f"Expansions: {expansions}\\n")
    
    # Test 3: Language-specific
    print("=== Test 3: Language-Specific ===")
    query = "function to connect database"
    expansions = expander.expand_query(query, language="python")
    print(f"Query: {query}")
    print(f"Language: python")
    print(f"Expansions: {expansions}\\n")
    
    # Test 4: Get synonyms
    print("=== Test 4: Get Synonyms ===")
    terms = ['function', 'auth', 'database']
    for term in terms:
        synonyms = expander.get_synonyms(term)
        print(f"{term}: {synonyms}")
    
    print("\\n✓ Query expansion tests completed!")
