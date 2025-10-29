
"""
Web Fetch Tool - Fetches and parses web content.

This tool provides async web fetching capabilities using httpx,
with BeautifulSoup for HTML parsing.
"""

import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

from .base import Tool


class WebFetchTool(Tool):
    """
    Tool for fetching and parsing web content.
    
    Capabilities:
    - Async HTTP requests using httpx
    - HTML parsing with BeautifulSoup
    - Text extraction from HTML
    - Timeout and retry support
    - Custom user agents
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the web fetch tool.
        
        Args:
            config: Configuration dictionary
            
        Raises:
            ImportError: If required packages are not installed
        """
        super().__init__(
            name='web_fetch',
            description='Fetch and parse web content from URLs',
            config=config
        )
        
        if not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx package is required for WebFetchTool. "
                "Install it with: pip install httpx"
            )
        
        self.timeout = self.config.get('web_timeout', 30)
        self.user_agent = self.config.get(
            'user_agent',
            'AI-Agent-Console/1.0 (+https://github.com/ai-agent-console)'
        )
    
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Fetch web content.
        
        Args:
            params: Dictionary with:
                - action: 'fetch' (fetch URL)
                - url: URL to fetch
                - parse: Whether to parse HTML (default: True)
                - extract_text: Whether to extract text (default: True)
                
        Returns:
            Dictionary with fetched content and metadata
        """
        self._log_invocation(params)
        
        action = params.get('action', 'fetch')
        
        if action == 'fetch':
            return self._fetch_url(params)
        elif action == 'parse':
            return self._parse_html(params)
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _fetch_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch content from a URL.
        
        Args:
            params: Fetch parameters
            
        Returns:
            Fetch result dictionary
        """
        self.validate_params(params, ['url'])
        
        url = params['url']
        parse = params.get('parse', True)
        extract_text = params.get('extract_text', True)
        
        try:
            # Use asyncio to run async fetch
            content = asyncio.run(self._async_fetch(url))
            
            result = {
                'url': url,
                'content': content,
                'length': len(content),
                'success': True
            }
            
            # Parse HTML if requested
            if parse and BS4_AVAILABLE:
                parsed = self._parse_html_content(content)
                result['parsed'] = parsed
                
                if extract_text:
                    result['text'] = parsed.get('text', '')
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return {
                'url': url,
                'content': None,
                'success': False,
                'error': str(e)
            }
    
    async def _async_fetch(self, url: str) -> str:
        """
        Async fetch URL content.
        
        Args:
            url: URL to fetch
            
        Returns:
            Content as string
        """
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {'User-Agent': self.user_agent}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    
    def _parse_html(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse HTML content.
        
        Args:
            params: Parse parameters with 'html' key
            
        Returns:
            Parsed HTML data
        """
        self.validate_params(params, ['html'])
        
        html = params['html']
        return self._parse_html_content(html)
    
    def _parse_html_content(self, html: str) -> Dict[str, Any]:
        """
        Parse HTML using BeautifulSoup.
        
        Args:
            html: HTML content
            
        Returns:
            Dictionary with parsed data
        """
        if not BS4_AVAILABLE:
            return {
                'text': html,
                'error': 'BeautifulSoup not available'
            }
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract links
            links = []
            for a in soup.find_all('a', href=True):
                links.append({
                    'text': a.get_text(strip=True),
                    'href': a['href']
                })
            
            # Extract title
            title = soup.title.string if soup.title else None
            
            return {
                'text': text,
                'title': title,
                'links': links[:50],  # Limit to first 50 links
                'link_count': len(links)
            }
            
        except Exception as e:
            self.logger.error(f"HTML parsing failed: {e}")
            return {
                'text': html,
                'error': str(e)
            }
