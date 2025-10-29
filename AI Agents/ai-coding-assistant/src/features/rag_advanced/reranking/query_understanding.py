"""
Query Understanding Module - Full Implementation

Uses LLM to understand and enhance search queries.
Provides query reformulation, intent classification, and context extraction.

Features:
- Query reformulation for clarity
- Intent classification (search, explain, debug, etc.)
- Entity extraction (functions, classes, variables)
- Context awareness
- Query decomposition for complex queries

Example:
    >>> understander = QueryUnderstanding(llm_interface)
    >>> enhanced = understander.understand_query("how to auth user?")
"""

from typing import List, Dict, Optional, Any, Tuple
import re
from pathlib import Path


class QueryUnderstanding:
    """
    Query understanding using LLM or rule-based methods.
    
    Features:
    - Query reformulation
    - Intent classification
    - Entity extraction
    - Context enhancement
    """
    
    # Query intents
    INTENTS = {
        'search': ['find', 'search', 'locate', 'where'],
        'explain': ['explain', 'what', 'how', 'why', 'describe'],
        'debug': ['fix', 'error', 'bug', 'issue', 'problem', 'debug'],
        'implement': ['create', 'implement', 'build', 'add', 'write'],
        'refactor': ['refactor', 'improve', 'optimize', 'clean'],
        'test': ['test', 'unit test', 'testing', 'verify']
    }
    
    # Programming entity patterns
    ENTITY_PATTERNS = {
        'function': r'\b[a-z_][a-z0-9_]*\(\)',
        'class': r'\b[A-Z][a-zA-Z0-9]*\b',
        'variable': r'\b[a-z_][a-z0-9_]*\b',
        'file': r'[\w/\\]+\.(py|js|ts|java|cpp|c|h|cs)$'
    }
    
    def __init__(
        self,
        llm_interface=None,
        use_llm: bool = True,
        fallback_to_rules: bool = True
    ):
        """
        Initialize query understanding.
        
        Args:
            llm_interface: LLM interface for advanced understanding
            use_llm: Whether to use LLM for query understanding
            fallback_to_rules: Fall back to rules if LLM unavailable
            
        Example:
            >>> understander = QueryUnderstanding(llm_interface)
        """
        self.llm_interface = llm_interface
        self.use_llm = use_llm and llm_interface is not None
        self.fallback_to_rules = fallback_to_rules
        
        print("QueryUnderstanding initialized:")
        print(f"  LLM interface: {'✓' if llm_interface else '✗'}")
        print(f"  Mode: {'LLM' if self.use_llm else 'Rule-based'}")
    
    def understand_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Understand query and extract information.
        
        Args:
            query: User query
            context: Optional context (language, file, etc.)
            
        Returns:
            Dictionary with query understanding
            
        Example:
            >>> result = understander.understand_query("how to authenticate user?")
            >>> print(result['intent'])  # 'explain'
            >>> print(result['reformulated'])  # "user authentication implementation"
        """
        result = {
            'original': query,
            'reformulated': query,
            'intent': 'search',
            'entities': {},
            'keywords': [],
            'language': context.get('language') if context else None,
            'confidence': 0.5
        }
        
        # Try LLM-based understanding
        if self.use_llm:
            try:
                llm_result = self._llm_understanding(query, context)
                result.update(llm_result)
                result['confidence'] = 0.9
                return result
            except Exception as e:
                print(f"Warning: LLM understanding failed: {e}")
                if not self.fallback_to_rules:
                    return result
        
        # Rule-based understanding
        result.update(self._rule_based_understanding(query, context))
        result['confidence'] = 0.7
        
        return result
    
    def reformulate_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Reformulate query for better search.
        
        Args:
            query: Original query
            context: Optional context
            
        Returns:
            Reformulated query
            
        Example:
            >>> reformulated = understander.reformulate_query("how do I auth?")
            >>> print(reformulated)  # "user authentication implementation"
        """
        understanding = self.understand_query(query, context)
        return understanding['reformulated']
    
    def classify_intent(self, query: str) -> str:
        """
        Classify query intent.
        
        Args:
            query: User query
            
        Returns:
            Intent label
        """
        query_lower = query.lower()
        
        # Check for intent keywords
        intent_scores = {}
        for intent, keywords in self.INTENTS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
        return 'search'  # Default
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract programming entities from query.
        
        Args:
            query: User query
            
        Returns:
            Dictionary of entities by type
        """
        entities = {}
        
        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = re.findall(pattern, query)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def decompose_query(
        self,
        query: str,
        max_subqueries: int = 3
    ) -> List[str]:
        """
        Decompose complex query into simpler sub-queries.
        
        Args:
            query: Complex query
            max_subqueries: Maximum number of sub-queries
            
        Returns:
            List of sub-queries
            
        Example:
            >>> subs = understander.decompose_query(
            ...     "Find JWT auth and also session management"
            ... )
            >>> print(subs)  # ["JWT authentication", "session management"]
        """
        # Split on conjunctions
        separators = [' and ', ' also ', ' plus ', ', ']
        parts = [query]
        
        for sep in separators:
            new_parts = []
            for part in parts:
                new_parts.extend(part.split(sep))
            parts = new_parts
        
        # Clean and filter
        subqueries = []
        for part in parts:
            clean = part.strip()
            if len(clean) > 5 and clean not in subqueries:
                subqueries.append(clean)
        
        return subqueries[:max_subqueries]
    
    def _llm_understanding(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Use LLM for query understanding."""
        # Construct prompt
        prompt = f"""Analyze this code search query and provide:
1. Reformulated query (clearer, more specific)
2. Intent (search/explain/debug/implement/refactor/test)
3. Key entities (functions, classes, files mentioned)
4. Important keywords

Query: "{query}"
"""
        
        if context:
            prompt += f"\nContext: {context}"
        
        prompt += """

Respond in this format:
REFORMULATED: <reformulated query>
INTENT: <intent>
ENTITIES: <comma-separated entities>
KEYWORDS: <comma-separated keywords>
"""
        
        # Call LLM
        try:
            response = self.llm_interface.generate(prompt, max_tokens=200)
            return self._parse_llm_response(response)
        except Exception as e:
            raise Exception(f"LLM call failed: {e}")
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        result = {}
        
        # Extract reformulated query
        if 'REFORMULATED:' in response:
            reformulated = response.split('REFORMULATED:')[1].split('\n')[0].strip()
            result['reformulated'] = reformulated
        
        # Extract intent
        if 'INTENT:' in response:
            intent = response.split('INTENT:')[1].split('\n')[0].strip().lower()
            if intent in self.INTENTS:
                result['intent'] = intent
        
        # Extract entities
        if 'ENTITIES:' in response:
            entities_str = response.split('ENTITIES:')[1].split('\n')[0].strip()
            entities = [e.strip() for e in entities_str.split(',') if e.strip()]
            result['entities'] = {'mentioned': entities}
        
        # Extract keywords
        if 'KEYWORDS:' in response:
            keywords_str = response.split('KEYWORDS:')[1].split('\n')[0].strip()
            keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
            result['keywords'] = keywords
        
        return result
    
    def _rule_based_understanding(
        self,
        query: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Rule-based query understanding."""
        result = {}
        
        # Classify intent
        result['intent'] = self.classify_intent(query)
        
        # Extract entities
        result['entities'] = self.extract_entities(query)
        
        # Extract keywords (simple: non-stop words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'how', 'to', 'do', 'i', 'can'}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        result['keywords'] = keywords
        
        # Reformulate query
        result['reformulated'] = self._reformulate_rule_based(query, result)
        
        return result
    
    def _reformulate_rule_based(
        self,
        query: str,
        understanding: Dict[str, Any]
    ) -> str:
        """Reformulate query using rules."""
        # Remove question words
        reformulated = re.sub(r'\b(how|what|where|when|why|can|do|does|is|are)\b', '', query, flags=re.IGNORECASE)
        
        # Remove "I" and "me"
        reformulated = re.sub(r'\b(i|me|my)\b', '', reformulated, flags=re.IGNORECASE)
        
        # Clean up
        reformulated = re.sub(r'\s+', ' ', reformulated).strip()
        
        # If too short, use keywords
        if len(reformulated) < 5 and understanding['keywords']:
            reformulated = ' '.join(understanding['keywords'][:5])
        
        # Fallback to original
        if not reformulated:
            reformulated = query
        
        return reformulated


if __name__ == "__main__":
    print("Query Understanding Module")
    print("=" * 60)
    print("\nThis module enhances queries using LLM or rules.")
    print("\nFeatures:")
    print("  - Query reformulation")
    print("  - Intent classification")
    print("  - Entity extraction")
    print("  - Query decomposition")
    print("\nExample usage:")
    print("""
    from features.rag_advanced.reranking import QueryUnderstanding
    
    understander = QueryUnderstanding(llm_interface)
    
    # Understand query
    result = understander.understand_query("how to auth user?")
    print(f"Intent: {result['intent']}")
    print(f"Reformulated: {result['reformulated']}")
    
    # Decompose complex query
    subs = understander.decompose_query("Find JWT auth and session management")
    """)
