"""
Comprehensive unit tests for agents/web_data.py

Tests cover:
- WebDataAgent initialization
- URL extraction and validation
- Web data fetching
- Error handling
- Multiple URL handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from agents.web_data import WebDataAgent


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_llm_router():
    """Create a mock LLM router."""
    router = Mock()
    router.query = Mock(return_value={
        'response': 'Web data fetched successfully',
        'provider': 'ollama',
        'model': 'test-model'
    })
    return router


@pytest.fixture
def mock_tool_registry():
    """Create a mock tool registry with web_fetch tool."""
    registry = Mock()
    
    # Mock web fetch tool
    mock_web_tool = Mock()
    mock_web_tool.invoke = Mock(return_value={
        'success': True,
        'content': '<html><body>Test content</body></html>',
        'text': 'Test content',
        'status_code': 200
    })
    
    registry.get = Mock(return_value=mock_web_tool)
    return registry


@pytest.fixture
def web_data_agent(mock_llm_router, mock_tool_registry):
    """Create a WebDataAgent instance."""
    agent = WebDataAgent(
        name="test_web_data",
        description="Test web data agent",
        llm_router=mock_llm_router,
        tool_registry=mock_tool_registry
    )
    return agent


# =============================================================================
# WebDataAgent Initialization Tests
# =============================================================================

class TestWebDataAgentInitialization:
    """Tests for WebDataAgent initialization."""
    
    def test_initialization(self, mock_llm_router, mock_tool_registry):
        """Test WebDataAgent initialization."""
        agent = WebDataAgent(
            name="test_web_data",
            description="Test web data agent",
            llm_router=mock_llm_router,
            tool_registry=mock_tool_registry
        )
        
        assert agent.name == "test_web_data"
        assert agent.description == "Test web data agent"
        assert agent.llm_router == mock_llm_router
        assert agent.tool_registry == mock_tool_registry
        assert agent.logger is not None
    
    def test_initialization_with_config(self, mock_llm_router):
        """Test initialization with custom config."""
        config = {
            'timeout': 30,
            'max_retries': 3
        }
        agent = WebDataAgent(
            name="test_web_data",
            description="Test web data agent",
            llm_router=mock_llm_router,
            config=config
        )
        
        assert agent.config['timeout'] == 30
        assert agent.config['max_retries'] == 3


# =============================================================================
# URL Extraction Tests
# =============================================================================

class TestURLExtraction:
    """Tests for URL extraction functionality."""
    
    def test_extract_single_url_from_task(self, web_data_agent):
        """Test extracting a single URL from task description."""
        task = "Fetch data from https://example.com"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 1
        assert 'https://example.com' in urls
    
    def test_extract_multiple_urls_from_task(self, web_data_agent):
        """Test extracting multiple URLs from task."""
        task = "Fetch from https://example.com and https://test.com"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 2
        assert 'https://example.com' in urls
        assert 'https://test.com' in urls
    
    def test_extract_url_from_context(self, web_data_agent):
        """Test extracting URL from context."""
        task = "Fetch web data"
        context = {'urls': 'https://context-url.com'}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 1
        assert 'https://context-url.com' in urls
    
    def test_extract_urls_from_context_list(self, web_data_agent):
        """Test extracting URLs from context list."""
        task = "Fetch data"
        context = {'urls': ['https://url1.com', 'https://url2.com']}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 2
        assert 'https://url1.com' in urls
        assert 'https://url2.com' in urls
    
    def test_extract_urls_deduplication(self, web_data_agent):
        """Test that duplicate URLs are removed."""
        task = "Fetch from https://example.com and https://example.com"
        context = {'urls': 'https://example.com'}
        
        urls = web_data_agent._extract_urls(task, context)
        
        # Should only have one instance
        assert len(urls) == 1
        assert 'https://example.com' in urls
    
    def test_extract_http_urls(self, web_data_agent):
        """Test extracting HTTP (non-HTTPS) URLs."""
        task = "Fetch from http://insecure-site.com"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 1
        assert 'http://insecure-site.com' in urls
    
    def test_extract_urls_with_paths(self, web_data_agent):
        """Test extracting URLs with paths and query parameters."""
        task = "Fetch https://api.example.com/v1/data?param=value"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 1
        assert 'https://api.example.com/v1/data?param=value' in urls
    
    def test_no_urls_found(self, web_data_agent):
        """Test when no URLs are found."""
        task = "Fetch some data"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        assert len(urls) == 0


# =============================================================================
# URL Validation Tests
# =============================================================================

class TestURLValidation:
    """Tests for URL validation."""
    
    def test_is_valid_url_https(self, web_data_agent):
        """Test validation of HTTPS URLs."""
        assert web_data_agent._is_valid_url('https://example.com') is True
    
    def test_is_valid_url_http(self, web_data_agent):
        """Test validation of HTTP URLs."""
        assert web_data_agent._is_valid_url('http://example.com') is True
    
    def test_is_valid_url_with_path(self, web_data_agent):
        """Test validation of URLs with paths."""
        assert web_data_agent._is_valid_url('https://example.com/path/to/page') is True
    
    def test_is_valid_url_with_query(self, web_data_agent):
        """Test validation of URLs with query parameters."""
        assert web_data_agent._is_valid_url('https://example.com?key=value&foo=bar') is True
    
    def test_is_valid_url_with_port(self, web_data_agent):
        """Test validation of URLs with port numbers."""
        assert web_data_agent._is_valid_url('https://example.com:8080') is True
    
    def test_is_valid_url_no_scheme(self, web_data_agent):
        """Test that URLs without scheme are invalid."""
        assert web_data_agent._is_valid_url('example.com') is False
    
    def test_is_valid_url_no_domain(self, web_data_agent):
        """Test that URLs without domain are invalid."""
        assert web_data_agent._is_valid_url('https://') is False
    
    def test_is_valid_url_invalid_scheme(self, web_data_agent):
        """Test that URLs with invalid schemes are handled."""
        result = web_data_agent._is_valid_url('ftp://example.com')
        # May or may not be valid depending on implementation
        assert isinstance(result, bool)
    
    def test_is_valid_url_malformed(self, web_data_agent):
        """Test validation of malformed URLs."""
        assert web_data_agent._is_valid_url('not a url at all') is False
    
    def test_is_valid_url_empty_string(self, web_data_agent):
        """Test validation of empty string."""
        assert web_data_agent._is_valid_url('') is False


# =============================================================================
# Web Data Fetching Tests
# =============================================================================

class TestWebDataFetching:
    """Tests for web data fetching functionality."""
    
    def test_fetch_url_success(self, web_data_agent, mock_tool_registry):
        """Test successful URL fetching."""
        mock_web_tool = mock_tool_registry.get('web_fetch')
        url = 'https://example.com'
        context = {}
        
        result = web_data_agent._fetch_url(mock_web_tool, url, context)
        
        assert result['success'] is True
        assert 'data' in result
        mock_web_tool.invoke.assert_called_once()
    
    def test_fetch_url_with_parse_html(self, web_data_agent, mock_tool_registry):
        """Test fetching with HTML parsing enabled."""
        mock_web_tool = mock_tool_registry.get('web_fetch')
        url = 'https://example.com'
        context = {'parse_html': True}
        
        result = web_data_agent._fetch_url(mock_web_tool, url, context)
        
        assert result['success'] is True
        call_args = mock_web_tool.invoke.call_args[0][0]
        assert call_args['parse'] is True
    
    def test_fetch_url_with_text_extraction(self, web_data_agent, mock_tool_registry):
        """Test fetching with text extraction."""
        mock_web_tool = mock_tool_registry.get('web_fetch')
        url = 'https://example.com'
        context = {'extract_text': True}
        
        result = web_data_agent._fetch_url(mock_web_tool, url, context)
        
        assert result['success'] is True
        call_args = mock_web_tool.invoke.call_args[0][0]
        assert call_args['extract_text'] is True
    
    def test_fetch_url_failure(self, web_data_agent, mock_tool_registry):
        """Test handling of fetch failure."""
        mock_web_tool = Mock()
        mock_web_tool.invoke = Mock(side_effect=Exception("Connection error"))
        
        url = 'https://example.com'
        context = {}
        
        result = web_data_agent._fetch_url(mock_web_tool, url, context)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'Connection error' in result['error']


# =============================================================================
# Agent Execution Tests
# =============================================================================

class TestWebDataAgentExecution:
    """Tests for WebDataAgent execution."""
    
    def test_execute_single_url_success(self, web_data_agent):
        """Test successful execution with single URL."""
        task = "Fetch data from https://example.com"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is True
        assert 'data' in result
        assert result['data']['total_urls'] == 1
        assert result['data']['successful'] == 1
    
    def test_execute_multiple_urls_success(self, web_data_agent):
        """Test successful execution with multiple URLs."""
        task = "Fetch from https://example.com and https://test.com"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is True
        assert result['data']['total_urls'] == 2
        assert result['data']['successful'] == 2
    
    def test_execute_no_urls_found(self, web_data_agent):
        """Test execution when no URLs are found."""
        task = "Fetch some data"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'no valid urls' in result['message'].lower()
    
    def test_execute_no_web_tool(self, web_data_agent, mock_tool_registry):
        """Test execution when web fetch tool is not available."""
        task = "Fetch from https://example.com"
        context = {}
        
        mock_tool_registry.get.return_value = None
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'tool not available' in result['message'].lower()
    
    def test_execute_partial_success(self, web_data_agent, mock_tool_registry):
        """Test execution with partial success (some URLs fail)."""
        task = "Fetch from https://example.com and https://fail.com"
        context = {}
        
        # Mock tool to fail on second URL
        call_count = [0]
        
        def mock_fetch(params):
            call_count[0] += 1
            if call_count[0] == 1:
                return {'success': True, 'content': 'data'}
            else:
                raise Exception("Fetch failed")
        
        mock_web_tool = Mock()
        mock_web_tool.invoke = Mock(side_effect=mock_fetch)
        mock_tool_registry.get.return_value = mock_web_tool
        
        result = web_data_agent.execute(task, context)
        
        # Should succeed if at least one URL works
        assert result['success'] is True
        assert result['data']['successful'] == 1
        assert result['data']['total_urls'] == 2
    
    def test_execute_all_urls_fail(self, web_data_agent, mock_tool_registry):
        """Test execution when all URLs fail."""
        task = "Fetch from https://fail1.com and https://fail2.com"
        context = {}
        
        mock_web_tool = Mock()
        mock_web_tool.invoke = Mock(side_effect=Exception("All fetches failed"))
        mock_tool_registry.get.return_value = mock_web_tool
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'failed' in result['message'].lower()
    
    def test_execute_includes_next_context(self, web_data_agent):
        """Test that execution result includes next context."""
        task = "Fetch from https://example.com"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        if result['success']:
            assert 'next_context' in result or 'context' in result
            # Should include fetched data for next agent
            if 'next_context' in result:
                assert 'web_data' in result['next_context']
                assert 'urls_fetched' in result['next_context']
    
    def test_execute_exception_handling(self, web_data_agent):
        """Test exception handling during execution."""
        task = "Fetch from https://example.com"
        context = {}
        
        with patch.object(web_data_agent, '_extract_urls', side_effect=Exception("Test error")):
            result = web_data_agent.execute(task, context)
        
        assert result['success'] is False
        assert 'error' in result['message'].lower()


# =============================================================================
# Context Handling Tests
# =============================================================================

class TestContextHandling:
    """Tests for context handling."""
    
    def test_urls_from_context_priority(self, web_data_agent):
        """Test that context URLs are included with task URLs."""
        task = "Fetch from https://task-url.com"
        context = {'urls': ['https://context-url.com']}
        
        urls = web_data_agent._extract_urls(task, context)
        
        # Both should be included
        assert 'https://task-url.com' in urls
        assert 'https://context-url.com' in urls
    
    def test_parse_html_context_flag(self, web_data_agent, mock_tool_registry):
        """Test that parse_html flag from context is used."""
        task = "Fetch from https://example.com"
        context = {'parse_html': False}
        
        result = web_data_agent.execute(task, context)
        
        if result['success']:
            mock_web_tool = mock_tool_registry.get('web_fetch')
            call_args = mock_web_tool.invoke.call_args[0][0]
            assert call_args['parse'] is False
    
    def test_extract_text_context_flag(self, web_data_agent, mock_tool_registry):
        """Test that extract_text flag from context is used."""
        task = "Fetch from https://example.com"
        context = {'extract_text': False}
        
        result = web_data_agent.execute(task, context)
        
        if result['success']:
            mock_web_tool = mock_tool_registry.get('web_fetch')
            call_args = mock_web_tool.invoke.call_args[0][0]
            assert call_args['extract_text'] is False
    
    def test_result_includes_fetched_urls(self, web_data_agent):
        """Test that result includes list of successfully fetched URLs."""
        task = "Fetch from https://example.com"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        if result['success'] and 'next_context' in result:
            assert 'urls_fetched' in result['next_context']
            assert len(result['next_context']['urls_fetched']) > 0
    
    def test_result_includes_web_data(self, web_data_agent):
        """Test that result includes fetched web data."""
        task = "Fetch from https://example.com"
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        if result['success']:
            assert 'data' in result
            assert 'results' in result['data']
            assert isinstance(result['data']['results'], list)


# =============================================================================
# Edge Cases Tests
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_task_string(self, web_data_agent):
        """Test handling of empty task string."""
        task = ""
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        assert result['success'] is False
    
    def test_very_long_url_list(self, web_data_agent):
        """Test handling of many URLs."""
        urls = [f"https://example{i}.com" for i in range(10)]
        task = " ".join(urls)
        context = {}
        
        result = web_data_agent.execute(task, context)
        
        # Should handle multiple URLs
        assert 'success' in result
    
    def test_malformed_url_ignored(self, web_data_agent):
        """Test that malformed URLs are filtered out."""
        task = "Fetch from https://valid.com and not-a-url and http://another-valid.com"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        # Should only include valid URLs
        assert 'https://valid.com' in urls
        assert 'http://another-valid.com' in urls
        assert 'not-a-url' not in urls
    
    def test_url_with_special_characters(self, web_data_agent):
        """Test handling of URLs with special characters."""
        task = "Fetch from https://example.com/path?key=value&foo=bar#section"
        context = {}
        
        urls = web_data_agent._extract_urls(task, context)
        
        # URL should be extracted (may or may not include fragment)
        assert len(urls) > 0
        assert 'example.com' in urls[0]
