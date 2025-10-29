
"""
Web Search Agent - Multi-engine web search capability.

This agent provides intelligent web search functionality across multiple
search engines (DuckDuckGo, Google, Bing, Langsearch) with rate limiting, 
error handling, and result processing.

Features:
- Multi-provider support with intelligent fallback
- DuckDuckGo (free, no API key required)
- Langsearch (may require API key)
- Google Custom Search (requires API key)
- Bing Search (requires API key)
- Automatic fallback to free providers when API keys are missing
- Graceful error handling and logging
"""

import time
import json
from typing import Dict, Any, List, Optional, Literal
from urllib.parse import quote_plus
import logging

from .base import Agent

# Import search libraries
try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


SearchEngine = Literal["duckduckgo", "google", "bing", "langsearch", "auto"]


class WebSearchAgent(Agent):
    """
    Production-ready Web Search Agent with Multi-Provider Support.
    
    Features:
        - Multi-engine support (DuckDuckGo, Google, Bing, Langsearch)
        - Intelligent search query formulation
        - Automatic fallback to free providers when API keys unavailable
        - Rate limiting and error handling
        - Result ranking and filtering
        - Structured result output
        - Caching for repeated queries
    
    Capabilities:
        - Perform web searches across multiple engines
        - Extract and rank search results
        - Handle pagination and result limits
        - Process and structure search results
        - Query refinement and optimization
        - Intelligent provider selection and fallback
    """
    
    SUPPORTED_ENGINES = ["duckduckgo", "google", "bing", "langsearch"]
    # Provider preference order (free providers first as fallback)
    DEFAULT_PROVIDER_PREFERENCE = ["duckduckgo", "langsearch", "google", "bing"]
    DEFAULT_MAX_RESULTS = 10
    RATE_LIMIT_DELAY = 1.0  # seconds between requests
    
    def __init__(
        self,
        name: str = "web_search",
        description: str = "Multi-engine web search agent",
        **kwargs
    ):
        """
        Initialize the WebSearch agent.
        
        Args:
            name: Agent name
            description: Agent description
            **kwargs: Additional configuration
        """
        super().__init__(name=name, description=description, **kwargs)
        
        self._last_request_time = 0.0
        self._search_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._failed_providers: List[str] = []  # Track failed providers for fallback
        self._check_dependencies()
        self._load_provider_preferences()
        
        self.logger.info("WebSearch Agent initialized with providers: %s", 
                        ', '.join(self.provider_preference))
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not DDGS_AVAILABLE:
            self.logger.warning(
                "duckduckgo-search not installed. Install with: pip install duckduckgo-search"
            )
        
        if not HTTPX_AVAILABLE and not REQUESTS_AVAILABLE:
            self.logger.warning(
                "No HTTP library available. Install httpx or requests."
            )
    
    def _load_provider_preferences(self) -> None:
        """Load provider preferences from config or use defaults."""
        web_search_config = self.config.get('web_search', {})
        
        # Load provider preference order
        self.provider_preference = web_search_config.get(
            'provider_preference', 
            self.DEFAULT_PROVIDER_PREFERENCE.copy()
        )
        
        # Validate that providers are supported
        self.provider_preference = [
            p for p in self.provider_preference 
            if p in self.SUPPORTED_ENGINES
        ]
        
        # Ensure at least DuckDuckGo (free) is in the list
        if 'duckduckgo' not in self.provider_preference:
            self.provider_preference.insert(0, 'duckduckgo')
        
        self.logger.debug("Provider preference order: %s", self.provider_preference)
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search task.
        
        Args:
            task: Search query or task description
            context: Execution context with optional parameters:
                - query: Search query (overrides task)
                - engine: Search engine to use
                - max_results: Maximum results to return
                - refine_query: Whether to use LLM to refine query
                - search_type: Type of search ('web', 'images', 'news', 'multi_engine')
                - engines: List of engines for multi-engine search
                
        Returns:
            Dictionary with search results and metadata
        """
        self._log_action("Web search task", task[:100])
        
        try:
            # Extract search parameters
            query = context.get('query', task)
            engine = context.get('engine', 'auto')
            max_results = context.get('max_results', self.DEFAULT_MAX_RESULTS)
            refine_query = context.get('refine_query', False)
            search_type = context.get('search_type', 'web')
            
            # Refine query if requested
            if refine_query and self.llm_router:
                refined = self._refine_search_query(query)
                if refined:
                    self.logger.info(f"Refined query: {query} -> {refined}")
                    query = refined
            
            # Handle different search types
            if search_type == 'images':
                results = self.search_images(query, max_results, engine)
                return self._build_success_result(
                    message=f"Found {len(results)} image results",
                    data={
                        'query': query,
                        'engine': engine,
                        'search_type': 'images',
                        'results': results,
                        'count': len(results)
                    }
                )
            
            elif search_type == 'news':
                results = self.search_news(query, max_results, engine)
                return self._build_success_result(
                    message=f"Found {len(results)} news results",
                    data={
                        'query': query,
                        'engine': engine,
                        'search_type': 'news',
                        'results': results,
                        'count': len(results)
                    }
                )
            
            elif search_type == 'multi_engine':
                engines = context.get('engines', ['duckduckgo', 'google', 'bing'])
                aggregated = self.aggregate_multi_engine_search(
                    query,
                    engines,
                    max_results
                )
                return self._build_success_result(
                    message=f"Aggregated {aggregated['total_results']} unique results from {len(engines)} engines",
                    data=aggregated
                )
            
            # Default: web search
            # Check cache
            cache_key = f"{engine}:{query}:{max_results}"
            if cache_key in self._search_cache:
                self.logger.info("Returning cached search results")
                return self._build_success_result(
                    message=f"Retrieved {len(self._search_cache[cache_key])} cached results",
                    data={
                        'query': query,
                        'engine': engine,
                        'results': self._search_cache[cache_key],
                        'cached': True
                    }
                )
            
            # Determine which engine to use
            if engine == 'auto':
                engine = self._select_best_engine()
            
            # Perform search
            results = self._perform_search(query, engine, max_results)
            
            # Cache results
            self._search_cache[cache_key] = results
            
            # Build response
            return self._build_success_result(
                message=f"Found {len(results)} results for query: {query}",
                data={
                    'query': query,
                    'engine': engine,
                    'search_type': 'web',
                    'results': results,
                    'count': len(results),
                    'cached': False
                },
                next_context={
                    'search_results': results,
                    'search_query': query
                }
            )
            
        except Exception as e:
            self.logger.exception("Web search failed")
            return self._build_error_result(f"Web search failed: {str(e)}", e)
    
    def _refine_search_query(self, query: str) -> Optional[str]:
        """
        Use LLM to refine search query for better results.
        
        Args:
            query: Original search query
            
        Returns:
            Refined query or None if refinement fails
        """
        try:
            prompt = f"""You are a search query optimization expert.
Refine the following search query to be more effective for web search engines.
Make it concise, specific, and use appropriate keywords.

Original query: {query}

Return ONLY the refined query, nothing else."""
            
            result = self._get_llm_response(prompt)
            if result.get('success', True):
                refined = result.get('response', '').strip()
                # Basic validation
                if refined and len(refined) > 2 and len(refined) < 200:
                    return refined
            
        except Exception as e:
            self.logger.warning(f"Query refinement failed: {e}")
        
        return None
    
    def _select_best_engine(self) -> str:
        """
        Select the best available search engine with intelligent fallback.
        
        Tries providers in preference order, skipping:
        - Providers that recently failed
        - Providers without required API keys
        - Providers without required dependencies
        
        Returns:
            Engine name (guaranteed to return a valid engine)
        """
        for provider in self.provider_preference:
            # Skip recently failed providers
            if provider in self._failed_providers:
                self.logger.debug("Skipping failed provider: %s", provider)
                continue
            
            # Check if provider is available
            if self._is_provider_available(provider):
                self.logger.debug("Selected provider: %s", provider)
                return provider
        
        # Fallback: use DuckDuckGo as last resort (always available, no API key needed)
        self.logger.warning("All preferred providers unavailable, falling back to DuckDuckGo")
        return "duckduckgo"
    
    def _is_provider_available(self, provider: str) -> bool:
        """
        Check if a search provider is available and configured.
        
        Args:
            provider: Provider name
            
        Returns:
            True if provider is available
        """
        if provider == "duckduckgo":
            # DuckDuckGo is always available (has HTTP fallback)
            return True
        
        elif provider == "langsearch":
            # Check if Langsearch is configured
            langsearch_config = self.config.get('web_search', {}).get('langsearch', {})
            api_key = langsearch_config.get('api_key')
            # Langsearch may work without API key (check if endpoint is available)
            return True  # Allow trying even without API key
        
        elif provider == "google":
            # Check if Google Custom Search is configured
            google_config = self.config.get('web_search', {}).get('google', {})
            api_key = google_config.get('api_key')
            search_engine_id = google_config.get('search_engine_id')
            return bool(api_key and search_engine_id)
        
        elif provider == "bing":
            # Check if Bing Search is configured
            bing_config = self.config.get('web_search', {}).get('bing', {})
            api_key = bing_config.get('api_key')
            return bool(api_key)
        
        return False
    
    def _perform_search(
        self,
        query: str,
        engine: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Perform search using specified engine with automatic fallback.
        
        Args:
            query: Search query
            engine: Search engine to use
            max_results: Maximum results to return
            
        Returns:
            List of search results
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        try:
            if engine == "duckduckgo":
                return self._search_duckduckgo(query, max_results)
            elif engine == "google":
                return self._search_google(query, max_results)
            elif engine == "bing":
                return self._search_bing(query, max_results)
            elif engine == "langsearch":
                return self._search_langsearch(query, max_results)
            else:
                raise ValueError(f"Unsupported search engine: {engine}")
        
        except Exception as e:
            self.logger.error(f"Search failed with {engine}: {e}")
            # Mark provider as failed
            if engine not in self._failed_providers:
                self._failed_providers.append(engine)
            
            # Try fallback to next available provider
            if engine != "duckduckgo":  # Avoid infinite loop
                self.logger.info("Attempting fallback to alternative provider...")
                fallback_engine = self._select_best_engine()
                if fallback_engine != engine:
                    return self._perform_search(query, fallback_engine, max_results)
            
            # If all else fails, return empty results
            self.logger.error("All search providers failed")
            return []
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - elapsed
            self.logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        if DDGS_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    search_results = ddgs.text(query, max_results=max_results)
                    
                    for idx, result in enumerate(search_results, 1):
                        if idx > max_results:
                            break
                        
                        results.append({
                            'rank': idx,
                            'title': result.get('title', ''),
                            'url': result.get('href', ''),
                            'snippet': result.get('body', ''),
                            'source': 'duckduckgo'
                        })
                
                self.logger.info(f"DuckDuckGo search returned {len(results)} results")
                return results
                
            except Exception as e:
                self.logger.error(f"DuckDuckGo search failed: {e}")
                # Fallback to HTTP method
        
        # HTTP fallback method
        return self._search_duckduckgo_http(query, max_results)
    
    def _search_duckduckgo_http(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Search DuckDuckGo using HTTP (fallback method).
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        try:
            # Use DuckDuckGo instant answer API
            url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json"
            
            if HTTPX_AVAILABLE:
                response = httpx.get(url, timeout=30.0)
                data = response.json()
            elif REQUESTS_AVAILABLE:
                response = requests.get(url, timeout=30)
                data = response.json()
            else:
                self.logger.error("No HTTP library available")
                return []
            
            # Process DuckDuckGo instant answer format
            abstract = data.get('Abstract', '')
            abstract_url = data.get('AbstractURL', '')
            
            if abstract and abstract_url:
                results.append({
                    'rank': 1,
                    'title': data.get('Heading', 'DuckDuckGo Result'),
                    'url': abstract_url,
                    'snippet': abstract,
                    'source': 'duckduckgo_api'
                })
            
            # Add related topics
            for idx, topic in enumerate(data.get('RelatedTopics', [])[:max_results-1], 2):
                if isinstance(topic, dict) and 'FirstURL' in topic:
                    results.append({
                        'rank': idx,
                        'title': topic.get('Text', '').split(' - ')[0],
                        'url': topic.get('FirstURL', ''),
                        'snippet': topic.get('Text', ''),
                        'source': 'duckduckgo_api'
                    })
            
            self.logger.info(f"DuckDuckGo HTTP search returned {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"DuckDuckGo HTTP search failed: {e}")
        
        return results
    
    def _search_google(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Google Custom Search API.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        # Check if API key is configured
        google_config = self.config.get('web_search', {}).get('google', {})
        api_key = google_config.get('api_key')
        search_engine_id = google_config.get('search_engine_id')
        
        if not api_key or not search_engine_id:
            self.logger.warning(
                "Google Custom Search API key or Search Engine ID not configured. "
                "Falling back to DuckDuckGo."
            )
            return self._search_duckduckgo(query, max_results)
        
        results = []
        
        try:
            # Google Custom Search API endpoint
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': min(max_results, 10)  # Google limits to 10 per request
            }
            
            if REQUESTS_AVAILABLE:
                response = requests.get(url, params=params, timeout=30)
            elif HTTPX_AVAILABLE:
                response = httpx.get(url, params=params, timeout=30.0)
            else:
                self.logger.error("No HTTP library available")
                return self._search_duckduckgo(query, max_results)
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                
                for idx, item in enumerate(items, 1):
                    results.append({
                        'rank': idx,
                        'title': item.get('title', ''),
                        'url': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'google'
                    })
                
                self.logger.info(f"Google search returned {len(results)} results")
            else:
                self.logger.error(f"Google search failed: HTTP {response.status_code}")
                return self._search_duckduckgo(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Google search failed: {e}")
            # Fallback to DuckDuckGo
            return self._search_duckduckgo(query, max_results)
        
        return results
    
    def _search_bing(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Bing Search API.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        # Check if API key is configured
        bing_config = self.config.get('web_search', {}).get('bing', {})
        api_key = bing_config.get('api_key')
        
        if not api_key:
            self.logger.warning(
                "Bing Search API key not configured. Falling back to DuckDuckGo."
            )
            return self._search_duckduckgo(query, max_results)
        
        results = []
        
        try:
            # Bing Web Search API endpoint
            url = "https://api.bing.microsoft.com/v7.0/search"
            headers = {'Ocp-Apim-Subscription-Key': api_key}
            params = {
                'q': query,
                'count': min(max_results, 50),  # Bing allows up to 50
                'responseFilter': 'Webpages'
            }
            
            if REQUESTS_AVAILABLE:
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif HTTPX_AVAILABLE:
                response = httpx.get(url, headers=headers, params=params, timeout=30.0)
            else:
                self.logger.error("No HTTP library available")
                return self._search_duckduckgo(query, max_results)
            
            if response.status_code == 200:
                data = response.json()
                web_pages = data.get('webPages', {}).get('value', [])
                
                for idx, page in enumerate(web_pages, 1):
                    results.append({
                        'rank': idx,
                        'title': page.get('name', ''),
                        'url': page.get('url', ''),
                        'snippet': page.get('snippet', ''),
                        'source': 'bing'
                    })
                
                self.logger.info(f"Bing search returned {len(results)} results")
            else:
                self.logger.error(f"Bing search failed: HTTP {response.status_code}")
                return self._search_duckduckgo(query, max_results)
                
        except Exception as e:
            self.logger.error(f"Bing search failed: {e}")
            # Fallback to DuckDuckGo
            return self._search_duckduckgo(query, max_results)
        
        return results
    
    def _search_langsearch(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using Langsearch API.
        
        Langsearch is a powerful search API that may require an API key
        but can also work without one for basic searches.
        
        Args:
            query: Search query
            max_results: Maximum results
            
        Returns:
            List of search results
        """
        results = []
        
        # Get Langsearch configuration
        langsearch_config = self.config.get('web_search', {}).get('langsearch', {})
        api_key = langsearch_config.get('api_key')
        endpoint = langsearch_config.get('endpoint', 'https://api.langsearch.io/v1/search')
        
        try:
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'AI-Agent-Console/1.0'
            }
            
            # Add API key if available
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            params = {
                'q': query,
                'limit': min(max_results, 50)
            }
            
            # Make request
            if HTTPX_AVAILABLE:
                response = httpx.get(endpoint, headers=headers, params=params, timeout=30.0)
            elif REQUESTS_AVAILABLE:
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            else:
                self.logger.error("No HTTP library available for Langsearch")
                raise ImportError("No HTTP library available")
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                
                # Parse Langsearch response format
                # Note: This is a generic implementation - adjust based on actual API response
                search_results = data.get('results', [])
                if isinstance(search_results, list):
                    for idx, result in enumerate(search_results[:max_results], 1):
                        results.append({
                            'rank': idx,
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'snippet': result.get('snippet', result.get('description', '')),
                            'source': 'langsearch'
                        })
                
                self.logger.info(f"Langsearch returned {len(results)} results")
            
            elif response.status_code == 401:
                self.logger.warning("Langsearch API key invalid or missing")
                raise ValueError("Langsearch authentication failed")
            
            elif response.status_code == 429:
                self.logger.warning("Langsearch rate limit exceeded")
                raise ValueError("Langsearch rate limit exceeded")
            
            else:
                self.logger.error(f"Langsearch failed: HTTP {response.status_code}")
                raise ValueError(f"Langsearch HTTP error: {response.status_code}")
        
        except Exception as e:
            self.logger.error(f"Langsearch search failed: {e}")
            # Don't fallback here - let _perform_search handle it
            raise
        
        return results
    
    def search_images(
        self,
        query: str,
        max_results: int = 10,
        engine: str = 'auto'
    ) -> List[Dict[str, Any]]:
        """
        Search for images.
        
        Args:
            query: Search query
            max_results: Maximum results
            engine: Search engine ('duckduckgo', 'google', 'bing', 'auto')
            
        Returns:
            List of image results
        """
        if engine == 'auto':
            engine = self._select_best_engine()
        
        self._apply_rate_limit()
        
        results = []
        
        if engine == 'duckduckgo' and DDGS_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    image_results = ddgs.images(query, max_results=max_results)
                    
                    for idx, img in enumerate(image_results, 1):
                        if idx > max_results:
                            break
                        
                        results.append({
                            'rank': idx,
                            'title': img.get('title', ''),
                            'url': img.get('image', ''),
                            'thumbnail': img.get('thumbnail', ''),
                            'source_url': img.get('url', ''),
                            'source': 'duckduckgo'
                        })
                    
                    self.logger.info(f"Image search returned {len(results)} results")
            except Exception as e:
                self.logger.error(f"DuckDuckGo image search failed: {e}")
        
        elif engine == 'google':
            google_config = self.config.get('web_search', {}).get('google', {})
            api_key = google_config.get('api_key')
            search_engine_id = google_config.get('search_engine_id')
            
            if api_key and search_engine_id:
                try:
                    url = "https://www.googleapis.com/customsearch/v1"
                    params = {
                        'key': api_key,
                        'cx': search_engine_id,
                        'q': query,
                        'searchType': 'image',
                        'num': min(max_results, 10)
                    }
                    
                    if REQUESTS_AVAILABLE:
                        response = requests.get(url, params=params, timeout=30)
                    elif HTTPX_AVAILABLE:
                        response = httpx.get(url, params=params, timeout=30.0)
                    else:
                        return results
                    
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', [])
                        
                        for idx, item in enumerate(items, 1):
                            results.append({
                                'rank': idx,
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'thumbnail': item.get('image', {}).get('thumbnailLink', ''),
                                'source_url': item.get('image', {}).get('contextLink', ''),
                                'source': 'google'
                            })
                        
                        self.logger.info(f"Google image search returned {len(results)} results")
                except Exception as e:
                    self.logger.error(f"Google image search failed: {e}")
        
        elif engine == 'bing':
            bing_config = self.config.get('web_search', {}).get('bing', {})
            api_key = bing_config.get('api_key')
            
            if api_key:
                try:
                    url = "https://api.bing.microsoft.com/v7.0/images/search"
                    headers = {'Ocp-Apim-Subscription-Key': api_key}
                    params = {
                        'q': query,
                        'count': min(max_results, 150)
                    }
                    
                    if REQUESTS_AVAILABLE:
                        response = requests.get(url, headers=headers, params=params, timeout=30)
                    elif HTTPX_AVAILABLE:
                        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
                    else:
                        return results
                    
                    if response.status_code == 200:
                        data = response.json()
                        images = data.get('value', [])
                        
                        for idx, img in enumerate(images, 1):
                            results.append({
                                'rank': idx,
                                'title': img.get('name', ''),
                                'url': img.get('contentUrl', ''),
                                'thumbnail': img.get('thumbnailUrl', ''),
                                'source_url': img.get('hostPageUrl', ''),
                                'source': 'bing'
                            })
                        
                        self.logger.info(f"Bing image search returned {len(results)} results")
                except Exception as e:
                    self.logger.error(f"Bing image search failed: {e}")
        
        return results
    
    def search_news(
        self,
        query: str,
        max_results: int = 10,
        engine: str = 'auto'
    ) -> List[Dict[str, Any]]:
        """
        Search for news articles.
        
        Args:
            query: Search query
            max_results: Maximum results
            engine: Search engine ('duckduckgo', 'bing', 'auto')
            
        Returns:
            List of news results
        """
        if engine == 'auto':
            engine = self._select_best_engine()
        
        self._apply_rate_limit()
        
        results = []
        
        if engine == 'duckduckgo' and DDGS_AVAILABLE:
            try:
                with DDGS() as ddgs:
                    news_results = ddgs.news(query, max_results=max_results)
                    
                    for idx, news in enumerate(news_results, 1):
                        if idx > max_results:
                            break
                        
                        results.append({
                            'rank': idx,
                            'title': news.get('title', ''),
                            'url': news.get('url', ''),
                            'snippet': news.get('body', ''),
                            'date': news.get('date', ''),
                            'source': 'duckduckgo'
                        })
                    
                    self.logger.info(f"News search returned {len(results)} results")
            except Exception as e:
                self.logger.error(f"DuckDuckGo news search failed: {e}")
        
        elif engine == 'bing':
            bing_config = self.config.get('web_search', {}).get('bing', {})
            api_key = bing_config.get('api_key')
            
            if api_key:
                try:
                    url = "https://api.bing.microsoft.com/v7.0/news/search"
                    headers = {'Ocp-Apim-Subscription-Key': api_key}
                    params = {
                        'q': query,
                        'count': min(max_results, 100)
                    }
                    
                    if REQUESTS_AVAILABLE:
                        response = requests.get(url, headers=headers, params=params, timeout=30)
                    elif HTTPX_AVAILABLE:
                        response = httpx.get(url, headers=headers, params=params, timeout=30.0)
                    else:
                        return results
                    
                    if response.status_code == 200:
                        data = response.json()
                        articles = data.get('value', [])
                        
                        for idx, article in enumerate(articles, 1):
                            results.append({
                                'rank': idx,
                                'title': article.get('name', ''),
                                'url': article.get('url', ''),
                                'snippet': article.get('description', ''),
                                'date': article.get('datePublished', ''),
                                'source': 'bing'
                            })
                        
                        self.logger.info(f"Bing news search returned {len(results)} results")
                except Exception as e:
                    self.logger.error(f"Bing news search failed: {e}")
        
        return results
    
    def aggregate_multi_engine_search(
        self,
        query: str,
        engines: List[str],
        max_results_per_engine: int = 5
    ) -> Dict[str, Any]:
        """
        Search across multiple engines and aggregate results.
        
        Args:
            query: Search query
            engines: List of engines to search
            max_results_per_engine: Max results per engine
            
        Returns:
            Dictionary with aggregated results
        """
        all_results = []
        engine_results = {}
        
        for engine in engines:
            try:
                results = self._perform_search(query, engine, max_results_per_engine)
                engine_results[engine] = {
                    'count': len(results),
                    'results': results
                }
                all_results.extend(results)
            except Exception as e:
                self.logger.error(f"Search failed for engine {engine}: {e}")
                engine_results[engine] = {
                    'count': 0,
                    'error': str(e)
                }
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return {
            'query': query,
            'engines_used': engines,
            'total_results': len(unique_results),
            'results_by_engine': engine_results,
            'aggregated_results': unique_results
        }
    
    def clear_cache(self) -> None:
        """Clear the search result cache."""
        self._search_cache.clear()
        self.logger.info("Search cache cleared")
    
    def get_cache_size(self) -> int:
        """
        Get the number of cached queries.
        
        Returns:
            Cache size
        """
        return len(self._search_cache)
