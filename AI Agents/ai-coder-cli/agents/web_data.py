
"""
Web Data Agent - Fetches and processes web content.

This agent retrieves data from URLs, parses HTML, and extracts
structured information from web pages.
"""

from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

from .base import Agent


class WebDataAgent(Agent):
    """
    Agent that retrieves and processes web data.
    
    Capabilities:
    - Fetch content from URLs
    - Parse HTML with BeautifulSoup
    - Extract structured data
    - Handle various content types (HTML, JSON, text)
    - Support for timeouts and retries
    """
    
    def execute(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and process web data based on task description.
        
        Args:
            task: Task description (e.g., "Fetch data from URL")
            context: Execution context
            
        Returns:
            Dictionary with success status and fetched data
        """
        self._log_action("Starting web data fetch", task[:100])
        
        try:
            # Parse task to extract URLs and operations
            urls = self._extract_urls(task, context)
            
            if not urls:
                return self._build_error_result(
                    "No valid URLs found in task description"
                )
            
            # Get web fetch tool
            web_tool = self._get_tool('web_fetch')
            
            if not web_tool:
                return self._build_error_result(
                    "Web fetch tool not available"
                )
            
            # Fetch data from URLs
            results = []
            for url in urls:
                self._log_action(f"Fetching data from", url)
                
                fetch_result = self._fetch_url(web_tool, url, context)
                results.append({
                    'url': url,
                    'success': fetch_result['success'],
                    'data': fetch_result.get('data'),
                    'error': fetch_result.get('error')
                })
            
            # Check if any fetch succeeded
            successful_fetches = [r for r in results if r['success']]
            
            if not successful_fetches:
                return self._build_error_result(
                    f"Failed to fetch data from all {len(urls)} URLs",
                    Exception(str(results))
                )
            
            self._log_action(
                "Web data fetch complete",
                f"Successfully fetched {len(successful_fetches)}/{len(urls)} URLs"
            )
            
            return self._build_success_result(
                message=f"Successfully fetched data from {len(successful_fetches)} URLs",
                data={
                    'results': results,
                    'total_urls': len(urls),
                    'successful': len(successful_fetches)
                },
                next_context={
                    'web_data': results,
                    'urls_fetched': [r['url'] for r in successful_fetches]
                }
            )
            
        except Exception as e:
            self.logger.exception("Web data fetch failed")
            return self._build_error_result(f"Web data fetch failed: {str(e)}", e)
    
    def _extract_urls(self, task: str, context: Dict[str, Any]) -> List[str]:
        """
        Extract URLs from task description or context.
        
        Args:
            task: Task description
            context: Execution context
            
        Returns:
            List of valid URLs
        """
        import re
        
        urls = []
        
        # URL regex pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        
        # Extract from task
        found_urls = re.findall(url_pattern, task)
        urls.extend(found_urls)
        
        # Extract from context
        if 'urls' in context:
            context_urls = context['urls']
            if isinstance(context_urls, str):
                context_urls = [context_urls]
            urls.extend(context_urls)
        
        # Validate and deduplicate
        valid_urls = []
        seen = set()
        
        for url in urls:
            if url in seen:
                continue
            
            if self._is_valid_url(url):
                valid_urls.append(url)
                seen.add(url)
        
        return valid_urls
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _fetch_url(
        self,
        web_tool: Any,
        url: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Fetch data from a URL using the web fetch tool.
        
        Args:
            web_tool: WebFetchTool instance
            url: URL to fetch
            context: Execution context
            
        Returns:
            Result dictionary with fetched data
        """
        try:
            # Invoke web fetch tool
            result = web_tool.invoke({
                'action': 'fetch',
                'url': url,
                'parse': context.get('parse_html', True),
                'extract_text': context.get('extract_text', True)
            })
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
